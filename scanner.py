"""
BIST 15 dakikalık gün içi sinyal botu (BIST 500 Geniş Havuz + Modüler Mimari)
"""

import bisect
import json
import os
import sys
from datetime import datetime, timedelta, time as dtime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests

try:
    from tickers import HISSELER
except ImportError:
    HISSELER = ["THYAO.IS", "EREGL.IS", "GARAN.IS", "ASELS.IS", "BIMAS.IS"]

BAR_MIN = 15
DONCHIAN_N = 20
VOL_MULT = 1.5
ATR_N = 14
STOP_ATR = 2.0
MIN_STOP_PCT = 0.004
MAX_EXTEND_ATR = 1.0
TRAIL_ATR = 2.0
TRAIL_ATR_TIGHT = 1.0
BE_R = 1.0
PARTIAL_R = 2.0

ENTRY_START, ENTRY_END = dtime(10, 30), dtime(17, 0)
FLAT_TIME = dtime(17, 40)
MARKET_OPEN, MARKET_CLOSE = dtime(10, 0), dtime(18, 5)
MAX_BAR_AGE_MIN = 40

SERMAYE = 100_000
RISK_YUZDE = 0.01
MAX_POZ_YUZDE = 0.25
MAX_POZISYON = 3
GUNLUK_MAX_KAYIP_R = 2.0

COST = 0.001
SLIP = 0.001

TZ = ZoneInfo("Europe/Istanbul")
STATE_FILE = Path(__file__).with_name("positions.json")

TOKEN = "9294997364:AAGp_p4GEuWL1uYQiVBFlWzj3IYi5ff5OyI"
CHAT_ID = "8218088218"


def send(msg: str) -> None:
    print(msg, "\n")
    if not TOKEN or not CHAT_ID:
        return
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      json={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except Exception:
        pass


def fetch_bist_data(ticker: str) -> pd.DataFrame:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=15m&range=30d"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return pd.DataFrame()
        data = res.json()
        result = data.get("chart", {}).get("result")
        if not result:
            return pd.DataFrame()
        res_dict = result[0]
        timestamps = res_dict.get("timestamp", [])
        quotes = res_dict.get("indicators", {}).get("quote", [{}])[0]
        if not timestamps or not quotes:
            return pd.DataFrame()
        df = pd.DataFrame({
            "Open": quotes.get("open", []),
            "High": quotes.get("high", []),
            "Low": quotes.get("low", []),
            "Close": quotes.get("close", []),
            "Volume": quotes.get("volume", [])
        }, index=pd.to_datetime(timestamps, unit="s"))
        df = df.dropna()
        if not df.empty:
            df.index = df.index.tz_localize("UTC").tz_convert(TZ)
        return df
    except Exception:
        return pd.DataFrame()


def fetch_bist_daily(ticker: str) -> pd.DataFrame:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=1y"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code != 200:
            return pd.DataFrame()
        data = res.json().get("chart", {}).get("result")
        if not data:
            return pd.DataFrame()
        res_dict = data[0]
        timestamps = res_dict.get("timestamp", [])
        quotes = res_dict.get("indicators", {}).get("quote", [{}])[0]
        df = pd.DataFrame({
            "Open": quotes.get("open", []),
            "High": quotes.get("high", []),
            "Low": quotes.get("low", []),
            "Close": quotes.get("close", []),
            "Volume": quotes.get("volume", [])
        }, index=pd.to_datetime(timestamps, unit="s"))
        return df.dropna()
    except Exception:
        return pd.DataFrame()


def closed_bars(df: pd.DataFrame, now: datetime) -> pd.DataFrame:
    return df[df.index + timedelta(minutes=BAR_MIN) <= now]


class DailyOK:
    def __init__(self, daily: pd.DataFrame):
        ok = (daily["Close"] > daily["Close"].rolling(50).mean()).shift(1)
        self.dates = [d.date() for d in daily.index]
        self.vals = [bool(v) if pd.notna(v) else False for v in ok.values]

    def __call__(self, d) -> bool:
        i = bisect.bisect_right(self.dates, d) - 1
        return self.vals[i] if i >= 0 else False


def add_ind(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    pc = df["Close"].shift(1)
    tr = pd.concat([df["High"] - df["Low"], (df["High"] - pc).abs(), (df["Low"] - pc).abs()],
                   axis=1).max(axis=1)
    df["atr"] = tr.rolling(ATR_N).mean()
    df["hh_prev"] = df["High"].rolling(DONCHIAN_N).max().shift(1)
    df["vol_avg"] = df["Volume"].rolling(DONCHIAN_N).mean().shift(1)
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    day = np.array([d for d in df.index.date])
    pv = (tp * df["Volume"]).groupby(day).cumsum()
    v = df["Volume"].groupby(day).cumsum()
    df["vwap"] = pv / v.replace(0, np.nan)
    return df


def entry_signal(df: pd.DataFrame, i: int, dok: DailyOK):
    r = df.iloc[i]
    ts = df.index[i]
    end = (ts + timedelta(minutes=BAR_MIN)).time()
    if not (ENTRY_START <= end <= ENTRY_END):
        return None
    if any(pd.isna(r[c]) for c in ("atr", "hh_prev", "vol_avg", "vwap")):
        return None
    if not dok(ts.date()):
        return None
    lvl = float(r["hh_prev"])
    c = float(r["Close"])
    atr = float(r["atr"])
    if c <= lvl:
        return None
    if r["Volume"] < VOL_MULT * r["vol_avg"]:
        return None
    if c <= r["vwap"]:
        return None
    if c - lvl > MAX_EXTEND_ATR * atr:
        return None
    risk = max(STOP_ATR * atr, MIN_STOP_PCT * c)
    return {"giris": c, "stop": c - risk, "risk": risk, "seviye": lvl, "atr": atr}


def new_position(sig: dict, ts: pd.Timestamp) -> dict:
    return {
        "giris": sig["giris"],
        "stop": sig["stop"],
        "risk": sig["risk"],
        "hh": sig["giris"],
        "kismi": False,
        "bildirilen_stop": sig["stop"],
        "son_ts": ts.isoformat()
    }


def step_position(pos: dict, o: float, h: float, l: float, atr: float):
    ev = []
    if o <= pos["stop"]:
        return o, ev
    if l <= pos["stop"]:
        return pos["stop"], ev
    pos["hh"] = max(pos["hh"], h)
    pr = (pos["hh"] - pos["giris"]) / pos["risk"]
    if not np.isnan(atr):
        mult = TRAIL_ATR_TIGHT if pr >= PARTIAL_R else TRAIL_ATR
        cand = pos["hh"] - mult * atr
        if pr >= BE_R:
            cand = max(cand, pos["giris"] * (1 + 2 * COST))
        if cand > pos["stop"]:
            pos["stop"] = cand
    if pr >= PARTIAL_R and not pos["kismi"]:
        pos["kismi"] = True
        ev.append("kismi")
    return None, ev


def load_state() -> dict:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def lot_hesapla(giris: float, risk: float) -> int:
    return int(min(SERMAYE * RISK_YUZDE / risk, SERMAYE * MAX_POZ_YUZDE / giris))


def handle_open_position(t: str, p: dict, df: pd.DataFrame, now: datetime, gun: dict) -> bool:
    son = pd.Timestamp(p["son_ts"])
    new = df[df.index > son]
    exit_px, kismi = None, False
    for ts, r in new.iterrows():
        exit_px, ev = step_position(p, float(r["Open"]), float(r["High"]), float(r["Low"]),
                                     float(r["atr"]) if pd.notna(r["atr"]) else np.nan)
        p["son_ts"] = ts.isoformat()
        kismi = kismi or ("kismi" in ev)
        if exit_px is not None:
            break

    if exit_px is not None:
        R = (exit_px - p["giris"]) / p["risk"]
        gun["r"] = round(gun["r"] + R, 2)
        send(f"🔴 {t}: STOP/SAT seviyesine değdi.\n• Çıkış ≈ {exit_px:.2f} TL | sonuç {R:+.1f}R")
        return True

    last_close = float(df["Close"].iloc[-1])
    if now.time() >= FLAT_TIME:
        R = (last_close - p["giris"]) / p["risk"]
        gun["r"] = round(gun["r"] + R, 2)
        send(f"⏰ {t}: GÜN SONU, pozisyonu KAPAT.")
        return True

    if kismi:
        send(f"💰 {t}: +{PARTIAL_R:.0f}R'ye ulaştı. YARISINI SAT.")
        p["bildirilen_stop"] = p["stop"]
    elif p["stop"] - p["bildirilen_stop"] >= 0.002 * last_close:
        send(f"🔄 {t}: STOP'U {p['stop']:.2f} TL'ye YUKARI TAŞI.")
        p["bildirilen_stop"] = p["stop"]
    return False


def scan(force: bool = False, now: datetime = None) -> None:
    now = now or datetime.now(TZ)
    if not force and (now.weekday() >= 5 or not (MARKET_OPEN <= now.time() <= MARKET_CLOSE)):
        print("Piyasa kapalı, tarama yapılmadı.")
        return

    state = load_state()
    before = json.dumps(state, sort_keys=True)
    today = str(now.date())
    gun = state.get("gun")
    if not gun or gun.get("tarih") != today:
        gun = {"tarih": today, "r": 0.0, "girilen": [], "kilit": False}
    poz = state.setdefault("pozisyon", {})
    son_bar = state.setdefault("son_bar", {})
    state["gun"] = gun

    print(f"BIST 500 havuzu taranıyor...")

    for t in HISSELER:
        try:
            raw_df = fetch_bist_data(t)
            if raw_df.empty:
                continue
            df = add_ind(closed_bars(raw_df, now))
            if len(df) < DONCHIAN_N + ATR_N + 2:
                continue
            
            daily_df = fetch_bist_daily(t)
            if daily_df.empty:
                continue
            dok = DailyOK(daily_df)
        except Exception:
            continue

        if t in poz:
            try:
                if handle_open_position(t, poz[t], df, now, gun):
                    del poz[t]
            except Exception:
                pass
            continue

        try:
            i = len(df) - 1
            ts = df.index[i]
            bar_end = ts + timedelta(minutes=BAR_MIN)
            if son_bar.get(t) == ts.isoformat():
                continue
            son_bar[t] = ts.isoformat()
            if (now - bar_end) > timedelta(minutes=MAX_BAR_AGE_MIN):
                continue
            if now.time() >= FLAT_TIME or t in gun["girilen"] or len(poz) >= MAX_POZISYON:
                continue
            if gun["r"] <= -GUNLUK_MAX_KAYIP_R:
                if not gun["kilit"]:
                    gun["kilit"] = True
                    send(f"🛑 Günlük kayıp limiti doldu.")
                continue

            sig = entry_signal(df, i, dok)
            if not sig:
                continue
            lot = lot_hesapla(sig["giris"], sig["risk"])
            if lot < 1:
                continue
            poz[t] = new_position(sig, ts)
            gun["girilen"].append(t)
            
            send(f"🟢 Murat, {t} için AL sinyali (BIST 500 Tarama, {bar_end:%H:%M})\n\n"
                 f"• Giriş referansı: {sig['giris']:.2f} TL\n"
                 f"• İlk STOP: {sig['stop']:.2f} TL\n"
                 f"• Önerilen adet: {lot}")
        except Exception:
            continue

    if json.dumps(state, sort_keys=True) != before:
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    if "--test" in sys.argv:
        send("✅ BIST 500 gün içi botu test mesajı")
    else:
        scan(force="--force" in sys.argv)


if __name__ == "__main__":
    main()
