"""
BIST 15 dakikalık gün içi sinyal botu (BIST 500 Tam Liste + Telegram Destekli Backtest)
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

# BIST 500 Hisselerinin Tamamı Doğrudan Burada Tanımlıdır
HISSELER = [
    "ACSEL.IS", "ADESE.IS", "ADGYO.IS", "AEFES.IS", "AFYON.IS", "AGESA.IS", "AGHOL.IS", "AGROT.IS", "AGYO.IS", "AHGAZ.IS",
    "AKBNK.IS", "AKCNS.IS", "AKENR.IS", "AKFGY.IS", "AKFYE.IS", "AKGRT.IS", "AKMGY.IS", "AKSA.IS", "AKSEN.IS", "AKSGY.IS",
    "ALARK.IS", "ALBRK.IS", "ALCAR.IS", "ALFAS.IS", "ALKA.IS", "ALKLC.IS", "ALMAD.IS", "ANELE.IS", "ANGEN.IS", "ANHYT.IS",
    "ANSGR.IS", "ARASE.IS", "ARCLK.IS", "ARENA.IS", "ARSAN.IS", "ARZUM.IS", "ASELS.IS", "ASTOR.IS", "ATAKP.IS", "ATATP.IS",
    "ATEKS.IS", "ATLAS.IS", "AVGYO.IS", "AVOD.IS", "AYCES.IS", "AYDEM.IS", "AYEN.IS", "AYGAZ.IS", "AZTEK.IS", "BAGFS.IS",
    "BAKAB.IS", "BALAT.IS", "BANVT.IS", "BARMA.IS", "BASGZ.IS", "BAYRK.IS", "BEGYO.IS", "BERA.IS", "BEYAZ.IS", "BIENY.IS",
    "BIGCH.IS", "BIMAS.IS", "BINHO.IS", "BIOEN.IS", "BJKAS.IS", "BLCYT.IS", "BOSSA.IS", "BRKO.IS", "BRMEN.IS", "BRSAN.IS",
    "BRYAT.IS", "BSOKE.IS", "BTCIM.IS", "BUCIM.IS", "BURCE.IS", "BURVA.IS", "BVSAN.IS", "CANTE.IS", "CASA.IS", "CCOLA.IS",
    "CELHA.IS", "CEMAS.IS", "CEMTS.IS", "CEOEM.IS", "CIMSA.IS", "CLEBI.IS", "CMBTN.IS", "CMENT.IS", "CONSE.IS", "COSMO.IS",
    "CRDFA.IS", "CRFSA.IS", "CUSAN.IS", "CVKMD.IS", "CWENE.IS", "DAGI.IS", "DAPGM.IS", "DARDL.IS", "DENGE.IS", "DERHL.IS",
    "DERIM.IS", "DESA.IS", "DESPC.IS", "DEVA.IS", "DIRIT.IS", "DITAS.IS", "DMRGD.IS", "DMSAS.IS", "DNISI.IS", "DOAS.IS",
    "DOBUR.IS", "DOCO.IS", "DOGUB.IS", "DOHOL.IS", "DOKTA.IS", "EDIP.IS", "EGEEN.IS", "EGEPO.IS", "EGGUB.IS", "EGPRO.IS",
    "EGSER.IS", "EKGYO.IS", "EKIZ.IS", "ELITE.IS", "EMKEL.IS", "ENKAI.IS", "ENJSA.IS", "ENSRI.IS", "EPLAS.IS", "ERCB.IS",
    "EREGL.IS", "ERSU.IS", "ESCAR.IS", "ESCOM.IS", "ESEN.IS", "ETILR.IS", "EUKYO.IS", "EUPWR.IS", "EUREN.IS", "EYYGY.IS",
    "FADE.IS", "FENER.IS", "FLAP.IS", "FMIZP.IS", "FONET.IS", "FORMT.IS", "FORTE.IS", "FROTO.IS", "FRIGO.IS", "GARAN.IS",
    "GARFA.IS", "GEDIK.IS", "GENIL.IS", "GEREL.IS", "GESAN.IS", "GLBMD.IS", "GLRYH.IS", "GLYHO.IS", "GMTAS.IS", "GOKNR.IS",
    "GOLTS.IS", "GOODY.IS", "GOZDE.IS", "GRNYO.IS", "GRSEL.IS", "GUBRF.IS", "GWIND.IS", "GZNMI.IS", "HALKB.IS", "HATSN.IS",
    "HEDEF.IS", "HEKTS.IS", "HKTM.IS", "HLGYO.IS", "HTTBT.IS", "HUBVC.IS", "HUNER.IS", "HURGZ.IS", "ICBCT.IS", "IDEAL.IS",
    "IHEVA.IS", "IHGZT.IS", "IHLAS.IS", "IHLGM.IS", "IMASM.IS", "INDES.IS", "INFO.IS", "INTEM.IS", "INVEO.IS", "IPEKE.IS",
    "ISDMR.IS", "ISGYO.IS", "ISCTR.IS", "ISMEN.IS", "ITTFH.IS", "IZFAS.IS", "IZINV.IS", "IZMDC.IS", "JANTS.IS", "KAPLM.IS",
    "KAREL.IS", "KARSN.IS", "KARTN.IS", "KARYE.IS", "KATMR.IS", "KAYSE.IS", "KCAER.IS", "KCHOL.IS", "KENT.IS", "KERVT.IS",
    "KFEIN.IS", "KGYO.IS", "KLRHO.IS", "KLGYO.IS", "KLKIM.IS", "KMPUR.IS", "KNFRT.IS", "KONYA.IS", "KOPOL.IS", "KORDS.IS",
    "KOZAA.IS", "KOZAL.IS", "KRDMD.IS", "KRONT.IS", "KRSAN.IS", "KRSTL.IS", "KRTEK.IS", "KUTPO.IS", "KUYAS.IS", "KZBGY.IS",
    "LIDER.IS", "LKMNH.IS", "LOGO.IS", "LUKSK.IS", "MAALT.IS", "MAKIM.IS", "MAKTK.IS", "MANAS.IS", "MARKA.IS", "MARTI.IS",
    "MAVI.IS", "MEDTR.IS", "MEGAP.IS", "MEKAG.IS", "MERIT.IS", "MERKO.IS", "METUR.IS", "MGROS.IS", "MIPAZ.IS", "MMCAS.IS",
    "MNDRS.IS", "MNDTR.IS", "MOBTL.IS", "MPARK.IS", "MRSHL.IS", "MSGYO.IS", "MTRKS.IS", "NETAS.IS", "NIBAS.IS", "NTGAZ.IS",
    "NTHOL.IS", "NUGYO.IS", "NUHCM.IS", "OBASE.IS", "ODAS.IS", "ONCSM.IS", "ORMA.IS", "OSMEN.IS", "OSTIM.IS", "OTKAR.IS",
    "OYAKC.IS", "OYLUM.IS", "OYYO.IS", "OZATD.IS", "OZGYO.IS", "OZKGY.IS", "OZLTM.IS", "PAMEL.IS", "PAPIL.IS", "PARSN.IS",
    "PENGD.IS", "PENTA.IS", "PETKM.IS", "PETUN.IS", "PGSUS.IS", "PNSUT.IS", "POLHO.IS", "POLTK.IS", "PRKME.IS", "PRZMA.IS",
    "PSDTC.IS", "PSGYO.IS", "QUAGR.IS", "QNBFB.IS", "QNBFL.IS", "RALYH.IS", "RAYSG.IS", "REEDR.IS", "RNPOL.IS", "RODRG.IS",
    "ROYAL.IS", "RTALB.IS", "RUBNS.IS", "SAFKR.IS", "SAHOL.IS", "SARKY.IS", "SASA.IS", "SAYAS.IS", "SDTTR.IS", "SEGYO.IS",
    "SEKFK.IS", "SEKUR.IS", "SELGD.IS", "SELVA.IS", "SEYKM.IS", "SILVR.IS", "SISE.IS", "SKBNK.IS", "SMRTG.IS", "SNGYO.IS",
    "SNICA.IS", "SNPAM.IS", "SODSN.IS", "SOKE.IS", "SOKM.IS", "SONME.IS", "SRVGY.IS", "SUMAS.IS", "SUNTK.IS", "SURGY.IS",
    "SUWEN.IS", "TABGD.IS", "TARKM.IS", "TATGD.IS", "TAVHL.IS", "TBORG.IS", "TCELL.IS", "TDGYO.IS", "TEKTG.IS", "TERA.IS",
    "TETMT.IS", "TEZOL.IS", "TGSAS.IS", "THYAO.IS", "TIRE.IS", "TKFEN.IS", "TMPOL.IS", "TMSN.IS", "TOASO.IS", "TRGYO.IS",
    "TRILC.IS", "TSKB.IS", "TSPOR.IS", "TTKOM.IS", "TTRAK.IS", "TUCLK.IS", "TUKAS.IS", "TUPRS.IS", "TUREX.IS", "TURGG.IS",
    "UFUK.IS", "ULAS.IS", "ULKER.IS", "ULUUN.IS", "UNLU.IS", "USAK.IS", "VAKBN.IS", "VAKFN.IS", "VAKGY.IS", "VBTYZ.IS",
    "VERTU.IS", "VERUS.IS", "VESBE.IS", "VESTL.IS", "VKFYO.IS", "VKGYO.IS", "VKING.IS", "YAPRK.IS", "YATAS.IS", "YAYLA.IS",
    "YBTAS.IS", "YEOTK.IS", "YESIL.IS", "YIGIT.IS", "YKBNK.IS", "YKSL.IS", "YUNSA.IS", "YYAPI.IS", "YYLGD.IS", "ZEDUR.IS",
    "ZOREN.IS"
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


def fetch_bist_data(ticker: str, period: str = "30d") -> pd.DataFrame:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=15m&range={period}"
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

    def __call__(self
