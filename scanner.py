"""
BIST 5 Dakikalık Gün İçi Sinyal Botu (BIST 500 Tam Liste + Gecikmesiz TradingView Verisi)
"""

import bisect
import json
import os
import sys
import time
from datetime import datetime, timedelta, time as dtime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import requests

# Gecikmesiz anlık veri için TradingView kütüphanesi
from tvDatafeed import TvDatafeed, Interval

# BIST 500 Hisselerinin Tamamı
HISSELER = [
    "ACSEL", "ADESE", "ADGYO", "AEFES", "AFYON", "AGESA", "AGHOL", "AGROT", "AGYO", "AHGAZ",
    "AKBNK", "AKCNS", "AKENR", "AKFGY", "AKFYE", "AKGRT", "AKMGY", "AKSA", "AKSEN", "AKSGY",
    "ALARK", "ALBRK", "ALCAR", "ALFAS", "ALKA", "ALKLC", "ALMAD", "ANELE", "ANGEN", "ANHYT",
    "ANSGR", "ARASE", "ARCLK", "ARENA", "ARSAN", "ARZUM", "ASELS", "ASTOR", "ATAKP", "ATATP",
    "ATEKS", "ATLAS", "AVGYO", "AVOD", "AYCES", "AYDEM", "AYEN", "AYGAZ", "AZTEK", "BAGFS",
    "BAKAB", "BALAT", "BANVT", "BARMA", "BASGZ", "BAYRK", "BEGYO", "BERA", "BEYAZ", "BIENY",
    "BIGCH", "BIMAS", "BINHO", "BIOEN", "BJKAS", "BLCYT", "BOSSA", "BRKO", "BRMEN", "BRSAN",
    "BRYAT", "BSOKE", "BTCIM", "BUCIM", "BURCE", "BURVA", "BVSAN", "CANTE", "CASA", "CCOLA",
    "CELHA", "CEMAS", "CEMTS", "CEOEM", "CIMSA", "CLEBI", "CMBTN", "CMENT", "CONSE", "COSMO",
    "CRDFA", "CRFSA", "CUSAN", "CVKMD", "CWENE", "DAGI", "DAPGM", "DARDL", "DENGE", "DERHL",
    "DERIM", "DESA", "DESPC", "DEVA", "DIRIT", "DITAS", "DMRGD", "DMSAS", "DNISI", "DOAS",
    "DOBUR", "DOCO", "DOGUB", "DOHOL", "DOKTA", "EDIP", "EGEEN", "EGEPO", "EGGUB", "EGPRO",
    "EGSER", "EKGYO", "EKIZ", "ELITE", "EMKEL", "ENKAI", "ENJSA", "ENSRI", "EPLAS", "ERCB",
    "EREGL", "ERSU", "ESCAR", "ESCOM", "ESEN", "ETILR", "EUKYO", "EUPWR", "EUREN", "EYYGY",
    "FADE", "FENER", "FLAP", "FMIZP", "FONET", "FORMT", "FORTE", "FROTO", "FRIGO", "GARAN",
    "GARFA", "GEDIK", "GENIL", "GEREL", "GESAN", "GLBMD", "GLRYH", "GLYHO", "GMTAS", "GOKNR",
    "GOLTS", "GOODY", "GOZDE", "GRNYO", "GRSEL", "GUBRF", "GWIND", "GZNMI", "HALKB", "HATSN",
    "HEDEF", "HEKTS", "HKTM", "HLGYO", "HTTBT", "HUBVC", "HUNER", "HURGZ", "ICBCT", "IDEAL",
    "IHEVA", "IHGZT", "IHLAS", "IHLGM", "IMASM", "INDES", "INFO", "INTEM", "INVEO", "IPEKE",
    "ISDMR", "ISGYO", "ISCTR", "ISMEN", "ITTFH", "IZFAS", "IZINV", "IZMDC", "JANTS", "KAPLM",
    "KAREL", "KARSN", "KARTN", "KARYE", "KATMR", "KAYSE", "KCAER", "KCHOL", "KENT", "KERVT",
    "KFEIN", "KGYO", "KLRHO", "KLGYO", "KLKIM", "KMPUR", "KNFRT", "KONYA", "KOPOL", "KORDS",
    "KOZAA", "KOZAL", "KRDMD", "KRONT", "KRSAN", "KRSTL", "KRTEK", "KUTPO", "KUYAS", "KZBGY",
    "LIDER", "LKMNH", "LOGO", "LUKSK", "MAALT", "MAKIM", "MAKTK", "MANAS", "MARKA", "MARTI",
    "MAVI", "MEDTR", "MEGAP", "MEKAG", "MERIT", "MERKO", "METUR", "MGROS", "MIPAZ", "MMCAS",
    "MNDRS", "MNDTR", "MOBTL", "MPARK", "MRSHL", "MSGYO", "MTRKS", "NETAS", "NIBAS", "NTGAZ",
    "NTHOL", "NUGYO", "NUHCM", "OBASE", "ODAS", "ONCSM", "ORMA", "OSMEN", "OSTIM", "OTKAR",
    "OYAKC", "OYLUM", "OYYO", "OZATD", "OZGYO", "OZKGY", "OZLTM", "PAMEL", "PAPIL", "PARSN",
    "PENGD", "PENTA", "PETKM", "PETUN", "PGSUS", "PNSUT", "POLHO", "POLTK", "PRKME", "PRZMA",
    "PSDTC", "PSGYO", "QUAGR", "QNBFB", "QNBFL", "RALYH", "RAYSG", "REEDR", "RNPOL", "RODRG",
    "ROYAL", "RTALB", "RUBNS", "SAFKR", "SAHOL", "SARKY", "SASA", "SAYAS", "SDTTR", "SEGYO",
    "SEKFK", "SEKUR", "SELGD", "SELVA", "SEYKM", "SILVR", "SISE", "SKBNK", "SMRTG", "SNGYO",
    "SNICA", "SNPAM", "SODSN", "SOKE", "SOKM", "SONME", "SRVGY", "SUMAS", "SUNTK", "SURGY",
    "SUWEN", "TABGD", "TARKM", "TATGD", "TAVHL", "TBORG", "TCELL", "TDGYO", "TEKTG", "TERA",
    "TETMT", "TEZOL", "TGSAS", "THYAO", "TIRE", "TKFEN", "TMPOL", "TMSN", "TOASO", "TRGYO",
    "TRILC", "TSKB", "TSPOR", "TTKOM", "TTRAK", "TUCLK", "TUKAS", "TUPRS", "TUREX", "TURGG",
    "UFUK", "ULAS", "ULKER", "ULUUN", "UNLU", "USAK", "VAKBN", "VAKFN", "VAKGY", "VBTYZ",
    "VERTU", "VERUS", "VESBE", "VESTL", "VKFYO", "VKGYO", "VKING", "YAPRK", "YATAS", "YAYLA",
    "YBTAS", "YEOTK", "YESIL", "YIGIT", "YKBNK", "YKSL", "YUNSA", "YYAPI", "YYLGD", "ZEDUR",
    "ZOREN"
]

BAR_MIN = 5  
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

# TvDatafeed başlatılıyor (Guest modu şifresiz bedava bağlantı kurar)
tv = TvDatafeed()

def send(msg: str) -> None:
    print(msg, "\n")
    if not TOKEN or not CHAT_ID:
        return
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                      json={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except Exception:
        pass


def fetch_tv_data(ticker: str, interval=Interval.in_5_minute, n_bars=60) -> pd.DataFrame:
    try:
        df = tv.get_hist(symbol=ticker, exchange='BIST', interval=interval, n_bars=n_bars)
        if df is None or df.empty:
            return pd.DataFrame()
        
        df = df.rename(columns={
            "symbol": "Symbol", "open": "Open", "high": "High", 
            "low": "Low", "close": "Close", "volume": "Volume"
        })
        df.index = df.index.tz_localize("UTC").tz_convert(TZ) if df.index.tz is None else df.index.tz_convert(TZ)
        return df.dropna()
    except Exception:
        return pd.DataFrame()


def closed_bars(df: pd.DataFrame, now: datetime) -> pd.DataFrame:
    if df.empty:
        return df
    return df[df.index + timedelta(minutes=BAR_MIN) <= now]


class DailyOK:
    def __init__(self, daily: pd.DataFrame):
        if daily.empty:
            self.dates, self.vals = [], []
            return
        ok = (daily["Close"] > daily["Close"].rolling(50).mean()).shift(1)
        self.dates = [d.date() for d in daily.index]
        self.vals = [bool(v) if pd.notna(v) else False for v in ok.values]

    def __call__(self, d) -> bool:
        if not self.dates:
            return False
        i = bisect.bisect_right(self.dates, d) - 1
        return self.vals[i] if i >= 0 else False


def add_ind(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    pc = df["Close"].shift(1)
    tr = pd.concat([df["High"] - df["Low"], (df["High"] - pc).abs(), (df["Low"] - pc).abs()], axis=1).max(axis=1)
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
    lvl, c, atr = float(r["hh_prev"]), float(r["Close"]), float(r["atr"])
    if c <= lvl or r["Volume"] < VOL_MULT * r["vol_avg"] or c <= r["vwap"] or c - lvl > MAX_EXTEND_ATR * atr:
        return None
    risk = max(STOP_ATR * atr, MIN_STOP_PCT * c)
    return {"giris": c, "stop": c - risk, "risk": risk, "seviye": lvl, "atr": atr}


def new_position(sig: dict, ts: pd.Timestamp) -> dict:
    return {"giris": sig["giris"], "stop": sig["stop"], "risk": sig["risk"], "hh": sig["giris"], "kismi": False, "bildirilen_stop": sig["stop"], "son_ts": ts.isoformat()}


def step_position(pos: dict, o: float, h: float, l: float, atr: float):
    ev = []
    if o <= pos["stop"]: return o, ev
    if l <= pos["stop"]: return pos["stop"], ev
    pos["hh"] = max(pos["hh"], h)
    pr = (pos["hh"] - pos["giris"]) / pos["risk"]
    if not np.isnan(atr):
        mult = TRAIL_ATR_TIGHT if pr >= PARTIAL_R else TRAIL_ATR
        cand = max(pos["hh"] - mult * atr, pos["giris"] * (1 + 2 * COST)) if pr >= BE_R else pos["hh"] - mult * atr
        if cand > pos["stop"]: pos["stop"] = cand
    if pr >= PARTIAL_R and not pos["kismi"]:
        pos["kismi"] = True
        ev.append("kismi")
    return None, ev


def load_state() -> dict:
    try: return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except: return {}


def lot_hesapla(giris: float, risk: float) -> int:
    return int(min(SERMAYE * RISK_YUZDE / risk, SERMAYE * MAX_POZ_YUZDE / giris))


def handle_open_position(t: str, p: dict, df: pd.DataFrame, now: datetime, gun: dict) -> bool:
    son = pd.Timestamp(p["son_ts"])
    new = df[df.index > son]
    exit_px, kismi = None, False
    for ts, r in new.iterrows():
        exit_px, ev = step_position(p, float(r["Open"]), float(r["High"]), float(r["Low"]), float(r["atr"]) if pd.notna(r["atr"]) else np.nan)
        p["son_ts"] = ts.isoformat()
        kismi = kismi or ("kismi" in ev)
        if exit_px is not None: break

    if exit_px is not None:
        R = (exit_px - p["giris"]) / p["risk"]
        gun["r"] = round(gun["r"] + R, 2)
        send(f"🔴 {t}: STOP/SAT.\n• Çıkış ≈ {exit_px:.2f} TL | {R:+.1f}R")
        return True

    last_close = float(df["Close"].iloc[-1])
    if now.time() >= FLAT_TIME:
        R = (last_close - p["giris"]) / p["risk"]
        gun["r"] = round(gun["r"] + R, 2)
        send(f"⏰ {t}: GÜN SONU KAPAT.")
        return True

    if kismi:
        send(f"💰 {t}: +{PARTIAL_R:.0f}R! YARISINI SAT.")
        p["bildirilen_stop"] = p["stop"]
    elif p["stop"] - p["bildirilen_stop"] >= 0.002 * last_close:
        send(f"🔄 {t}: STOP'U {p['stop']:.2f} TL'ye TAŞI.")
        p["bildirilen_stop"] = p["stop"]
    return False


def scan(force: bool = False, now: datetime = None) -> None:
    now = now or datetime.now(TZ)
    if not force and (now.weekday() >= 5 or not (MARKET_OPEN <= now.time() <= MARKET_CLOSE)):
        return

    state = load_state()
    today = str(now.date())
    gun = state.get("gun", {})
    if gun.get("tarih") != today: gun = {"tarih": today, "r": 0.0, "girilen": [], "kilit": False}
    poz, son_bar = state.setdefault("pozisyon", {}), state.setdefault("son_bar", {})
    state["gun"] = gun

    print(f"BIST 500 Taranıyor (Gecikmesiz 5 Dk, {len(HISSELER)} hisse)...")

    for t in HISSELER:
        try:
            raw_df = fetch_tv_data(t, Interval.in_5_minute, 60)
            if raw_df.empty: continue
            df = add_ind(closed_bars(raw_df, now))
            if len(df) < DONCHIAN_N + ATR_N + 2: continue
            
            daily_df = fetch_tv_data(t, Interval.in_daily, 60)
            dok = DailyOK(daily_df)
        except Exception:
            continue

        if t in poz:
            if handle_open_position(t, poz[t], df, now, gun): del poz[t]
            continue

        try:
            i = len(df) - 1
            ts = df.index[i]
            bar_end = ts + timedelta(minutes=BAR_MIN)
            if son_bar.get(t) == ts.isoformat() or (now - bar_end) > timedelta(minutes=MAX_BAR_AGE_MIN): continue
            son_bar[t] = ts.isoformat()
            if now.time() >= FLAT_TIME or t in gun["girilen"] or len(poz) >= MAX_POZISYON: continue
            if gun["r"] <= -GUNLUK_MAX_KAYIP_R:
                if not gun["kilit"]: gun["kilit"] = True; send("🛑 Günlük kayıp limiti doldu.")
                continue

            sig = entry_signal(df, i, dok)
            if not sig: continue
            lot = lot_hesapla(sig["giris"], sig["risk"])
            if lot < 1: continue
            poz[t] = new_position(sig, ts)
            gun["girilen"].append(t)
            
            send(f"🟢 Murat, {t} için AL sinyali (Gecikmesiz, {bar_end:%H:%M})\n\n"
                 f"• Giriş referansı: {sig['giris']:.2f} TL\n"
                 f"• İlk STOP: {sig['stop']:.2f} TL\n"
                 f"• Önerilen adet: {lot}")
        except Exception:
            pass
        time.sleep(0.1) # Kütüphaneyi boğmamak için ufak bekleme

    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    if "--test" in sys.argv: send("✅ Gecikmesiz BIST 500 botu test mesajı")
    else: scan(force="--force" in sys.argv)
