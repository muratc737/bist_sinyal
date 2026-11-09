import argparse, datetime as dt, json, os, sys, time
from pathlib import Path
from zoneinfo import ZoneInfo
import pandas as pd
from backtest import evaluate, liquid, print_report
from strategies import STRATEGIES, atr

BASE = Path(__file__).parent
TICKERS = BASE / "tickers.txt"
REPORT = BASE / "strategy_report.json"
POSITIONS = BASE / "positions.json"
TZ = ZoneInfo("Europe/Istanbul")

def load_tickers():
    seen, out = set(), []
    for line in TICKERS.read_text(encoding="utf-8").splitlines():
        t = line.split("#")[0].strip().upper()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out

def download(tickers, years=3, chunk=80):
    import yfinance as yf
    data, missing = {}, []
    for i in range(0, len(tickers), chunk):
        part = tickers[i:i + chunk]
        raw = yf.download([t + ".IS" for t in part], period=f"{years}y", interval="1d", auto_adjust=True, group_by="ticker", threads=True, progress=False)
        for t in part:
            try: df = raw[t + ".IS"][["Open", "High", "Low", "Close", "Volume"]].dropna()
            except: continue
            if len(df) >= 250:
                if df.index.tz is not None: df.index = df.index.tz_localize(None)
                data[t] = df
    return data

def drop_incomplete(df):
    now = dt.datetime.now(TZ)
    if df.index[-1].date() == now.date() and now.time() < dt.time(18, 30):
        return df.iloc[:-1]
    return df

def send_telegram(text):
    token, chat = os.getenv("TELEGRAM_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat:
        print("[Telegram ayarlı değil]\n" + text)
        return False
    import requests
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={"chat_id": chat, "text": text}, timeout=20)
    time.sleep(0.5)
    return True

def cmd_backtest():
    data = download(load_tickers(), years=6)
    report = evaluate(data, save_path=REPORT)
    print_report(report)

def cmd_scan():
    # Backtest raporu olmasa bile donchian_breakout stratejisini doğrudan zorla çalıştırıyoruz
    enabled = list(STRATEGIES.keys())

    data = download(load_tickers(), years=3)
    pos = json.loads(POSITIONS.read_text(encoding="utf-8")) if POSITIONS.exists() else {}
    buys = sells = 0

    for t, df in data.items():
        df = drop_incomplete(df)
        if len(df) < 250: continue
        close, a, last_day = float(df["Close"].iloc[-1]), float(atr(df).iloc[-1]), df.index[-1]
        
        for name in enabled:
            spec = STRATEGIES[name]
            key = f"{name}|{t}"
            en, ex = spec["fn"](df)
            
            if key in pos:
                p = pos[key]
                held = int((df.index > pd.Timestamp(p["date"])).sum())
                reason = None
                
                if close <= p["stop"]: reason = f"Zarar Kes (Stop) Seviyesine Değdi ({p['stop']:.2f} TL)"
                elif bool(ex.iloc[-1]): reason = "Trend Zayıfladı / Kanal Tabanı Kırıldı"
                elif held >= spec["max_hold"]: reason = "Maksimum Bekleme Süresi Doldu"
                
                if reason:
                    chg = (close / p["ref"] - 1) * 100
                    send_telegram(f"🔴 Murat, elindeki {t} hissesini sat!\n\n• Kapanış: {close:.2f} TL\n• Performans: %{chg:+.1f}\n• Sebep: {reason}")
                    del pos[key]
                    sells += 1
            
            elif bool(en.iloc[-1]) and liquid(df):
                stop = close - spec["stop_atr"] * a
                pos[key] = dict(date=str(last_day.date()), ref=close, stop=stop)
                send_telegram(f"🟢 Murat, {t} hissesinde Donchian kırılımı var, al!\n\n• Son Fiyat: {close:.2f} TL\n• Stop Önerisi: {stop:.2f} TL\n\nAldıktan sonra mutlaka stop koy.")
                buys += 1

    POSITIONS.write_text(json.dumps(pos, indent=2), encoding="utf-8")
    send_telegram(f"📊 Tarama bitti Murat. {buys} yeni alım fırsatı, {sells} satış uyarısı buldum.")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["backtest", "scan", "test-telegram"])
    cmd = ap.parse_args().cmd
    if cmd == "backtest": cmd_backtest()
    elif cmd == "scan": cmd_scan()
    else: send_telegram("✅ Merhaba Murat, sistemin emrinde.")

if __name__ == "__main__":
    main()
