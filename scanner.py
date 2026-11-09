"""
BIST 15 dakikalık gün içi sinyal botu (BIST 500 Geniş Havuz + Yerli/Güvenli Veri Kaynağı)
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

# ---------------- AYARLAR ----------------
HISSELER = [
    "THYAO.IS", "EREGL.IS", "GARAN.IS", "ASELS.IS", "BIMAS.IS", "KCHOL.IS", "TUPRS.IS", "AKBNK.IS", "SAHOL.IS", "FROTO.IS",
    "ISCTR.IS", "YKBNK.IS", "SISE.IS", "PGSUS.IS", "TCELL.IS", "BJKAS.IS", "PETKM.IS", "SASA.IS", "HEKTS.IS", "KRDMD.IS",
    "TOASO.IS", "ARCLK.IS", "ENKAI.IS", "ODAS.IS", "KOZAA.IS", "KOZAL.IS", "MGROS.IS", "SOKM.IS", "BERA.IS", "GESAN.IS",
    "EUPWR.IS", "ASTOR.IS", "KONTR.IS", "ALARK.IS", "ENJSA.IS", "OYAKC.IS", "TTKOM.IS", "VAKBN.IS", "HALKB.IS", "ALBRK.IS",
    "ALFAS.IS", "ASUZU.IS", "AYDEM.IS", "BAGFS.IS", "BOBET.IS", "BRSAN.IS", "BUCIM.IS", "CANTE.IS", "CCOLA.IS", "CEMTS.IS",
    "CIMSA.IS", "DEVA.IS", "DOAS.IS", "DOHOL.IS", "ECILC.IS", "ECZYT.IS", "EGEEN.IS", "EKGYO.IS", "EYYGY.IS", "GLYHO.IS",
    "GOKNR.IS", "GUBRF.IS", "GWIND.IS", "IPEKE.IS", "ISDMR.IS", "ISGYO.IS", "IZMDC.IS", "KCAER.IS", "KMPUR.IS", "KONYA.IS",
    "KORDS.IS", "KZBGY.IS", "MAVI.IS", "OTKAR.IS", "PENTA.IS", "PSGYO.IS", "QUAGR.IS", "REEDR.IS", "SDTTR.IS", "SKBNK.IS",
    "SMRTG.IS", "TAVHL.IS", "TKFEN.IS", "TMSN.IS", "TSKB.IS", "TTRAK.IS", "ULKER.IS", "VESBE.IS", "VESTL.IS", "YEOTK.IS",
    "YYLGD.IS", "ZOREN.IS", "AEFES.IS", "AGHOL.IS", "AHGAZ.IS", "AKCNS.IS", "AKFGY.IS", "AKFYE.IS", "AKSA.IS", "AKSEN.IS",
    "ACSEL.IS", "ADESE.IS", "AGESA.IS", "AGYO.IS", "AKENR.IS", "AKMGY.IS", "ALCAR.IS", "ALKA.IS", "ALMAD.IS", "ANELE.IS",
    "ANGEN.IS", "ARASE.IS", "ARENA.IS", "ARSAN.IS", "ARZUM.IS", "ATAKP.IS", "ATEKS.IS", "ATLAS.IS", "AVGYO.IS", "AVOD.IS",
    "AYCES.IS", "AYEN.IS", "AYGAZ.IS", "AZTEK.IS", "BANVT.IS", "BARMA.IS", "BASGZ.IS", "BAYRK.IS", "BEGYO.IS", "BIENY.IS",
    "BIGCH.IS", "BIOEN.IS", "BLCYT.IS", "BOSSA.IS", "BRKO.IS", "BRMEN.IS", "BRYAT.IS", "BUGRA.IS", "BURCE.IS", "BURVA.IS",
    "BVSAN.IS", "CAFIN.IS", "CLEBI.IS", "CMBTN.IS", "CMENT.IS", "CONSE.IS", "COSMO.IS", "CRDFA.IS", "CRFSA.IS", "CUSAN.IS",
    "DAGI.IS", "DAPGM.IS", "DARDL.IS", "DENGE.IS", "DERIM.IS", "DESA.IS", "DESPC.IS", "DGNMO.IS", "DIRIT.IS", "DITAS.IS",
    "DMRGD.IS", "DMSAS.IS", "DNISI.IS", "DOBUR.IS", "DOCO.IS", "DOGUB.IS", "DOKTA.IS", "DURDO.IS", "DYOBY.IS", "DZGYO.IS",
    "EDIP.IS", "EGEPO.IS", "EGGUB.IS", "EGPRO.IS", "EGSER.IS", "EKIZ.IS", "ELITE.IS", "EMKEL.IS", "ENSRI.IS", "EPLAS.IS",
    "ERCB.IS", "ERSU.IS", "ESCAR.IS", "ESCOM.IS", "ESEN.IS", "ETILR.IS", "EUKYO.IS", "EUPWR.IS", "FADE.IS", "FENER.IS",
    "FLAP.IS", "FMIZP.IS", "FONET.IS", "FORMT.IS", "FORTE.IS", "FRIGO.IS", "GARFA.IS", "GEDIK.IS", "GENIL.IS", "GEREL.IS",
    "GESAN.IS", "GLBMD.IS", "GLRYH.IS", "GMTAS.IS", "GOLTS.IS", "GOODY.IS", "GOZDE.IS", "GRNYO.IS", "GRSEL.IS", "GZNMI.IS",
    "HATSN.IS", "HEDEF.IS", "HKTM.IS", "HLGYO.IS", "HTTBT.IS", "HUBVC.IS", "HUNER.IS", "HURGZ.IS", "ICBCT.IS", "IDEAL.IS",
    "IHEVA.IS", "IHGZT.IS", "IHLAS.IS", "IHLGM.IS", "IMASM.IS", "INDES.IS", "INFO.IS", "INTEM.IS", "INVEO.IS", "ITTFH.IS",
    "IZFAS.IS", "JANTS.IS", "KAPLM.IS", "KAREL.IS", "KARSN.IS", "KARTN.IS", "KARYE.IS", "KATMR.IS", "KAYSE.IS", "KENT.IS",
    "KERVT.IS", "KERVN.IS", "KFEIN.IS", "KGYO.IS", "KLRHO.IS", "KLGYO.IS", "KNFRT.IS", "KOPOL.IS", "KRONT.IS", "KRSAN.IS",
    "KRSTL.IS", "KRTEK.IS", "KUTPO.IS", "KUYAS.IS", "LIDER.IS", "LKMNH.IS", "LOGO.IS", "LUKSK.IS", "MAALT.IS", "MAKIM.IS",
    "MAKTK.IS", "MANAS.IS", "MARKA.IS", "MARTI.IS", "MEGAP.IS", "MEKAG.IS", "MERIT.IS", "MERKO.IS", "METUR.IS", "MIPAZ.IS",
    "MMCAS.IS", "MNDRS.IS", "MNDTR.IS", "MOBTL.IS", "MPARK.IS", "MRSHL.IS", "MSGYO.IS", "MTRKS.IS", "NETAS.IS", "NIBAS.IS",
    "NTGAZ.IS", "NTHOL.IS", "NUGYO.IS", "NUHCM.IS", "OBASE.IS", "ONCSM.IS", "ORMA.IS", "OSMEN.IS", "OSTIM.IS", "OYLUM.IS",
    "OYYO.IS", "OZATD.IS", "OZGYO.IS", "OZKGY.IS", "OZLTM.IS", "PAMEL.IS", "PAPIL.IS", "PARSN.IS", "PENGD.IS", "PETUN.IS",
    "PNSUT.IS", "POLHO.IS", "POLTK.IS", "PRKME.IS", "PRZMA.IS", "PSDTC.IS", "QNBFB.IS", "QNBFL.IS", "RALYH.IS", "RAYSG.IS",
    "RNPOL.IS", "RODRG.IS", "ROYAL.IS", "RTALB.IS", "RUBNS.IS", "SAFKR.IS", "SARKY.IS", "SAYAS.IS", "SEGYO.IS", "SEKFK.IS",
    "SEKUR.IS", "SELGD.IS", "SELVA.IS", "SEYKM.IS", "SILVR.IS", "SNGYO.IS", "SNICA.IS", "SNPAM.IS", "SODSN.IS", "SOKE.IS",
    "SONME.IS", "SRVGY.IS", "SUMAS.IS", "SUNTK.IS", "SURGY.IS", "SUWEN.IS", "TABGD.IS", "TARKM.IS", "TATGD.IS", "TAVHL.IS",
    "TBORG.IS", "TDGYO.IS", "TEKTG.IS", "TERA.IS", "TETMT.IS", "TEZOL.IS", "TGSAS.IS", "TIRE.IS", "TMPOL.IS", "TRGYO.IS",
    "TRILC.IS", "TSPOR.IS", "TUCLK.IS", "TUKAS.IS", "TUPRS.IS", "TUREX.IS", "TURGG.IS", "UFUK.IS", "ULAS.IS", "ULKER.IS",
    "ULUUN.IS", "UNLU.IS", "USAK.IS", "VAKFN.IS", "VAKGY.IS", "VBTYZ.IS", "VERTU.IS", "VERUS.IS", "VKFYO.IS", "VKGYO.IS",
    "VKING.IS", "YAPRK.IS", "YATAS.IS", "YAYLA.IS", "YBTAS.IS", "YESIL.IS", "YIGIT.IS", "YKSL.IS", "YUNSA.IS", "YYAPI.IS", "ZEDUR.IS"
]

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
STATE_FILE = Path(__file__).with_name("pozisyonlar.json")

TOKEN = "9294997364:AAGp_p4GEuWL1uYQiVBFlWzj3IYi5ff5OyI"
CHAT_ID = "8218088218"
# -----------------------------------------


def send(msg: str) -> None:
    print(msg, "\n")
    if not TOKEN or not CHAT_ID:
        print("(Telegram token veya chat id eksik!)\n")
        return
    try:
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                          json={"chat_id": CHAT_ID, "text": msg}, timeout=15)
        if r.status_code != 200:
            print(f"Telegram hata: {r.text}")
    except Exception as e:
        print(f"Telegram bağlantı hatası: {e}")


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
    return {"giris": sig["giris"], "stop": sig["stop"], "risk": sig["risk"],
