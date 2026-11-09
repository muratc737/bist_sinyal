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
        "giris": sig["giris"], "stop": sig["stop"], "risk": sig["risk"],
        "hh": sig["giris"], "kismi": False, "bildirilen_stop": sig["stop"],
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


def run_backtest() -> None:
    print(f"BIST 500 geçmiş veriler ile Backtest çalıştırılıyor...")
    all_R, all_days = [], set()
    for t in HISSELER:
        try:
            df = add_ind(fetch_bist_data(t, period="59d"))
            if df.empty:
                continue
            dok = DailyOK(fetch_bist_daily(t))
        except Exception:
            continue
        pos, girilen, trades = None, set(), []
        for i in range(len(df)):
            r = df.iloc[i]
            ts = df.index[i]
            all_days.add(ts.date())
            if pos is not None:
                px, _ = step_position(pos, float(r["Open"]), float(r["High"]), float(r["Low"]),
                                     float(r["atr"]) if pd.notna(r["atr"]) else np.nan)
                if px is None and (ts + timedelta(minutes=BAR_MIN)).time() >= FLAT_TIME:
                    px = float(r["Close"])
                if px is not None:
                    cost_r = 2 * (COST + SLIP) * pos["giris"] / pos["risk"]
                    trades.append((px - pos["giris"]) / pos["risk"] - cost_r)
                    pos = None
                continue
            if (ts.date(), t) in girilen:
                continue
            sig = entry_signal(df, i, dok)
            if sig:
                pos = new_position(sig, ts)
                girilen.add((ts.date(), t))
        all_R.extend(trades)
    
    if all_R:
        a = np.array(all_R)
        w, lo = a[a > 0], a[a <= 0]
        pf = w.sum() / abs(lo.sum()) if lo.sum() < 0 else float("inf")
        msg = (f"📊 BIST 500 Backtest Sonucu:\n\n"
               f"• Toplam İşlem: {len(a)}\n"
               f"• Kazanma Oranı: {len(w)/len(a):.0%}\n"
               f"• İşlem Başı Ortalama: {a.mean():+.2f}R\n"
               f"• Toplam R: {a.sum():+.1f}R\n"
               f"• Profit Factor: {pf:.2f}")
        send(msg)
    else:
        send("📊 BIST 500 Backtest tamamlandı: Seçilen aralıkta kriterlere uyan işlem bulunamadı.")


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

    print(f"BIST 500 tam havuzu taranıyor ({len(HISSELER)} hisse)...")

    for t in HISSELER:
        try:
            raw_df = fetch_bist_data(t, period="30d")
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
    if "--backtest" in sys.argv:
        run_backtest()
    elif "--test" in sys.argv:
        send("✅ BIST 500 gün içi botu test mesajı")
    else:
        scan(force="--force" in sys.argv)


if __name__ == "__main__":
    main()
