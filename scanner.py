"""
BIST 5 Dakikalık Gün İçi Sinyal Botu (BIST 500 Tam Liste + Gecikmesiz TradingView Verisi + Anti-Ban Koruması)
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

from tvDatafeed import TvDatafeed, Interval

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

# TVDatafeed başlatılıyor (Hata loglarını gizlemek için sessiz moda alındı)
import logging
logging.getLogger("tvDatafeed.main").setLevel(logging.CRITICAL)

try:
    # Kendi hesabın varsa buraya girebilirsin: TvDatafeed(username='kullanici', password='sifre')
    tv = TvDatafeed()
except:
    tv = None

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
    if not tv:
        return pd.DataFrame()
    # Hata alınca çökmek yerine 3 kere tekrar deneme (Anti-Ban koruması)
    for deneme in range(3):
        try:
            df = tv.get_hist(symbol=ticker, exchange='BIST', interval=interval, n_bars=n_bars)
            if df is not None and not df.empty:
                df = df.rename(columns={
                    "symbol": "Symbol", "open": "Open", "high": "High", 
                    "low": "Low", "close": "Close", "volume": "Volume"
                })
                df.index = df.index.tz_localize("UTC").tz_convert(TZ) if df.index.tz is None else df.index.tz_convert(TZ)
                return df.dropna()
        except Exception:
            time.sleep(1) # Hata alırsa 1 saniye nefes al ve tekrar dene
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
    return {"giris": sig["giris"], "stop": sig["stop"], "
