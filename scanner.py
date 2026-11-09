"""
BIST 15 dakikalık gün içi sinyal botu (BIST 500 Geniş Havuz + Toplu Veri Çekme)
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
import yfinance as yf

# ---------------- AYARLAR ----------------
# BIST 500 Geniş ve Likit Havuz (Güncel BIST 100 + BIST 300 / Yan Tahta Ağırlıklı Semboller)
HISSELER = [
    # BIST 30 & 100 Ana Hisseler
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
    # Genişletilmiş BIST Yan Tahtalar ve Likit Hisseler (BIST 500 Havuzu)
    "ACSEL.IS", "ADESE.IS", "AEFES.IS", "AGESA.IS", "AGYO.IS", "AKENR.IS", "AKMGY.IS", "AKSEN.IS", "ALCAR.IS", "ALKA.IS",
    "ALMAD.IS", "ANELE.IS", "ANGEN.IS", "ARASE.IS", "ARENA.IS", "ARSAN.IS", "ARZUM.IS", "ATAKP.IS", "ATEKS.IS", "ATLAS.IS",
    "AVGYO.IS", "AVOD.IS", "AYCES.IS", "AYEN.IS", "AYGAZ.IS", "AZTEK.IS", "BANVT.IS", "BARMA.IS", "BASGZ.IS", "BAYRK.IS",
    "BEGYO.IS", "BIENY.IS", "BIGCH.IS", "BIOEN.IS", "BJKAS.IS", "BLCYT.IS", "BOSSA.IS", "BRKO.IS", "BRMEN.IS", "BRYAT.IS",
    "BUGRA.IS", "BURCE.IS", "BURVA.IS", "BVSAN.IS", "CAFIN.IS", "CLEBI.IS", "CMBTN.IS", "CMENT.IS", "CONSE.IS", "COSMO.IS",
    "CRDFA.IS", "CRFSA.IS", "CUSAN.IS", "DAGI.IS", "DAPGM.IS", "DARDL.IS", "DENGE.IS", "DERIM.IS", "DESA.IS", "DESPC.IS",
    "DGNMO.IS", "DIRIT.IS", "DITAS.IS", "DMRGD.IS", "DMSAS.IS", "DNISI.IS", "DOBUR.IS", "DOCO.IS", "DOGUB.IS", "DOKTA.IS",
    "DURDO.IS", "DYOBY.IS", "DZGYO.IS", "EDIP.IS", "EGEPO.IS", "EGGUB.IS", "EGPRO.IS", "EGSER.IS", "EKIZ.IS", "ELITE.IS",
    "EMKEL.IS", "ENSRI.IS", "EPLAS.IS", "ERCB.IS", "ERSU.IS", "ESCAR.IS", "ESCOM.IS", "ESEN.IS", "ETILR.IS", "EUKYO.IS",
    "EUPWR.IS", "Evyap", "FADE.IS", "FENER.IS", "FLAP.IS", "FMIZP.IS", "FONET.IS", "FORMT.IS", "FORTE.IS", "FRIGO.IS",
    "GARFA.IS", "GEDIK.IS", "GENIL.IS", "GEREL.IS", "GESAN.IS", "GLBMD.IS", "GLRYH.IS", "GMTAS.IS", "GOLTS.IS", "GOODY.IS",
    "GOZDE.IS", "GRNYO.IS", "GRSEL.IS", "GZNMI.IS", "HALKB.IS", "HATSN.IS", "HEDEF.IS", "HKTM.IS", "HLGYO.IS", "HTTBT.IS",
    "HUBVC.IS", "HUNER.IS", "HURGZ.IS", "ICBCT.IS", "IDEAL.IS", "IHEVA.IS", "IHGZT.IS", "IHLAS.IS", "IHLGM.IS", "IMASM.IS",
    "INDES.IS", "INFO.IS", "INTEM.IS", "INVEO.IS", "ITTFH.IS", "IZFAS.IS", "JANTS.IS", "KAPLM.IS", "KAREL.IS", "KARSN.IS",
    "KARTN.IS", "KARYE.IS", "KATMR.IS", "KAYSE.IS", "KENT.IS", "KERVT.IS", "KERVN.IS", "KFEIN.IS", "KGYO.IS", "KLRHO.IS",
    "KLGYO.IS", "KMPUR.IS", "KNFRT.IS", "KONTR.IS", "KOPOL.IS", "KORDS.IS", "KRONT.IS", "KRSAN.IS", "KRSTL.IS", "KRTEK.IS",
    "KUTPO.IS", "KUYAS.IS", "LIDER.IS", "LKMNH.IS", "LOGO.IS", "LUKSK.IS", "MAALT.IS", "MAFAB.IS", "MAKIM.IS", "MAKTK.IS",
    "MANAS.IS", "MARKA.IS", "MARTI.IS", "MEGAP.IS", "MEKAG.IS", "MEMUR.IS", "MERIT.IS", "MERKO.IS", "METUR.IS", "MIPAZ.IS",
    "MMCAS.IS", "MNDRS.IS", "MNDTR.IS", "MOBTL.IS", "MPARK.IS", "MRSHL.IS", "MSGYO.IS", "MTRKS.IS", "MIPAZ.IS", "Naten",
    "NETAS.IS", "NIBAS.IS", "NTGAZ.IS", "NTHOL.IS", "NUGYO.IS", "NUHCM.IS", "OBASE.IS", "ODAS.IS", "ONCSM.IS", "ORMA.IS",
    "OSMEN.IS", "OSTIM.IS", "OTKAR.IS", "OYAKC.IS", "OYLUM.IS", "OYYO.IS", "OZATD.IS", "OZGYO.IS", "OZKGY.IS", "OZLTM.IS",
    "PAMEL.IS", "PAPIL.IS", "PARSN.IS", "PENGD.IS", "PENTA.IS", "PETUN.IS", "PNSUT.IS", "POLHO.IS", "POLTK.IS", "PRKME.IS",
    "PRZMA.IS", "PSDTC.IS", "PSGYO.IS", "QNBFB.IS", "QNBFL.IS", "RALYH.IS", "RAYSG.IS", "REEDR.IS", "RNPOL.IS", "RODRG.IS",
    "ROYAL.IS", "RTALB.IS", "RUBNS.IS", "SAFKR.IS", "	", "SARKY.IS", "SASA.IS", "SAYAS.IS", "SEGYO.IS", "SEKFK.IS",
    "SEKUR.IS", "SELGD.IS", "SELVA.IS", "SEYKM.IS", "SILVR.IS", "SNGYO.IS", "SNICA.IS", "SNPAM.IS", "SODSN.IS", "SOKE.IS",
    "SONME.IS", "SRVGY.IS", "SUMAS.IS", "SUNTK.IS", "SURGY.IS", "SUWEN.IS", "TABGD.IS", "TARKM.IS", "TATGD.IS", "TAVHL.IS",
    "TBORG.IS", "TCELL.IS", "TDGYO.IS", "TEKTG.IS", "TERA.IS", "TETMT.IS", "TEZOL.IS", "TGSAS.IS", "THYAO.IS", "TIRE.IS",
    "TKFEN.IS", "TMPOL.IS", "TMSN.IS", "TOASO.IS", "TRGYO.IS", "TRILC.IS", "TSPOR.IS", "TTKOM.IS", "TTRAK.IS", "TUCLK.IS",
    "TUKAS.IS", "TUPRS.IS", "TUREX.IS", "TURGG.IS", "UFUK.IS", "ULAS.IS", "ULKER.IS", "ULUUN.IS", "UNLU.IS", "USAK.IS",
    "VAKBN.IS", "VAKFN.IS", "VAKGY.IS", "VBTYZ.IS", "VERTU.IS", "VERUS.IS", "VESBE.IS", "VESTL.IS", "VKFYO.IS", "VKGYO.IS",
    "VKING.IS", "YAPRK.IS", "YATAS.IS", "YAYLA.IS", "YBTAS.IS", "YEOTK.IS", "YESIL.IS", "YIGIT.IS", "YKBNK.IS", "YKSL.IS",
    "YUNSA.IS", "YYAPI.IS", "ZEDUR.IS", "ZOREN.IS"
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


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        raise ValueError("veri yok")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df[["Open", "High", "Low", "Close", "Volume"]].dropna()


def fetch_batch_15m(tickers: list, period: str = "30d") -> dict:
    """Tüm hisseleri tek seferde (batch) indirerek hız kazanır."""
    data = {}
    try:
        df_all = yf.download(tickers, period=period, interval="15m", auto_adjust=True, progress=False, group_by='ticker', threads=True)
        for t in tickers:
            try:
                df = df_all[t].dropna() if len(tickers) > 1 else df_all.dropna()
                if not df.empty:
                    if df.index.tz is None:
                        df.index = df.index.tz_localize("UTC")
                    df.index = df.index.tz_convert(TZ)
                    data[t] = _clean(df)
            except Exception:
                continue
    except Exception as e:
        print(f"Toplu veri çekme hatası: {e}")
    return data


def fetch_daily(t: str) -> pd.DataFrame:
    return _clean(yf.download(t, period="1y", interval="1d", auto_adjust=True, progress=False))


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
            "hh": sig["giris"], "kismi": False, "bildirilen_stop": sig["stop"],
            "son_ts": ts.isoformat()}


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
        send(f"🔴 {t}: STOP/SAT seviyesine değdi.\n"
             f"• Çıkış ≈ {exit_px:.2f} TL | giriş {p['giris']:.2f} | sonuç {R:+.1f}R")
        return True

    last_close = float(df["Close"].iloc[-1])
    if now.time() >= FLAT_TIME:
        R = (last_close - p["giris"]) / p["risk"]
        gun["r"] = round(gun["r"] + R, 2)
        send(f"⏰ {t}: GÜN SONU, pozisyonu KAPAT.\n• Son fiyat {last_close:.2f}")
        return True

    if kismi:
        send(f"💰 {t}: +{PARTIAL_R:.0f}R'ye ulaştı. POZİSYONUN YARISINI SAT.")
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
    all_data = fetch_batch_15m(HISSELER)

    for t, raw_df in all_data.items():
        try:
            df = add_ind(closed_bars(raw_df, now))
            if len(df) < DONCHIAN_N + ATR_N + 2:
                continue
            dok = DailyOK(fetch_daily(t))
        except Exception as e:
            continue

        if t in poz:
            if handle_open_position(t, poz[t], df, now, gun):
                del poz[t]
            continue

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

    if json.dumps(state, sort_keys=True) != before:
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    if "--test" in sys.argv:
        send("✅ BIST 500 gün içi botu test mesajı")
    else:
        scan(force="--force" in sys.argv)


if __name__ == "__main__":
    main()
