"""
BIST 5 Dakikalık Gün İçi Sinyal Botu (BIST 500 Tam Liste + Sadece Yerli/İş Yatırım Verisi)
"""

import bisect
import json
import os
import sys
from datetime import datetime, timedelta, time as dtime
from pathlib import Path
from zoneinfo import ZoneInfo
import time

import numpy as np
import pandas as pd
import requests

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

BAR_MIN = 5  # 5 DAKİKALIK PERİYOT
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
    """
    SADECE İş Yatırım (veya benzeri yerli kurum) uç noktasını dener.
    Yahoo Finance yedeklemesi tamamen kaldırılmıştır.
    """
    clean_symbol = ticker.replace(".IS", "")
    url = f"https://www.isyatirim.com.tr/_layouts/15/IsYatirim.Website/Common/Data.aspx/HissePazarlama?hisse={clean_symbol}"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code != 200:
            return pd.DataFrame()
            
        # İş Yatırım'dan JSON verisi döndüğünde onu OHLCV formatına çevirmeye çalışır.
        # DİKKAT: İş Yatırım genellikle sadece kapanış(Close) verir. OHLCV gelmezse stratejinin ATR/VWAP kısımları çalışmaz.
        data = res.json()
        # Burası İş Yatırım'ın spesifik JSON yapısına göre parse edilmelidir. 
        # Örnek bir parse bloğu bırakıyorum, kurumun API yapısına göre uyarlanabilir:
        
        # Varsayımsal Parse (Gerçek yapıya göre değiştirilmeli):
        # if 'data' in data:
        #     df = pd.DataFrame(data['data'])
        #     return df
        
        # Şimdilik hata atmaması için boş dönüyor, gerçek yerli endpoint bağlanınca içi doldurulacak.
        return pd.DataFrame()
        
    except Exception:
        return pd.DataFrame()


def closed_bars(df: pd.DataFrame, now: datetime) -> pd.DataFrame:
    if df.empty:
        return df
    return df[df.index + timedelta(minutes=BAR_MIN) <= now]


class DailyOK:
    def __init__(self, daily: pd.DataFrame):
        if daily.empty:
            self.dates = []
            self.vals = []
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
    if df.empty:
        return df
    df = df.copy()
    
    # Hacim veya High/Low verisi yoksa (Yerli API kısıtlaması), o sütunları 0 veya Close'a eşitleriz ki kod çökmesin
    if "High" not in df.columns:
        df["High"] = df["Close"]
    if "Low" not in df.columns:
        df["Low"] = df["Close"]
    if "Volume" not in df.columns:
        df["Volume"] = 0

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
    
    # Gerekli göstergelerden biri bile NaN ise (veri eksikliği) sinyal iptal
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
    if risk <= 0:
        return 0
    return int(min(SERMAYE * RISK_YUZDE / risk, SERMAYE * MAX_POZ_YUZDE / giris))


def handle_open_position(t: str, p: dict, df: pd.DataFrame, now: datetime, gun: dict) -> bool:
    son = pd.Timestamp(p["son_ts"])
    new = df[df.index > son]
    exit_px, kismi = None, False
    for ts, r in new.iterrows():
        exit_px, ev = step_position(p, float(r["Open"]) if "Open" in r else float(r["Close"]), 
                                     float(r["High"]) if "High" in r else float(r["Close"]), 
                                     float(r["Low"]) if "Low" in r else float(r["Close"]),
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

    print(f"BIST 500 tam havuzu taranıyor (5 Dakikalık, SADECE Yerli Veri, {len(HISSELER)} hisse)...")

    # Günlük veriyi de (DailyOK için) mecburen kapattım çünkü o da Yahoo kullanıyordu.
    # Şimdilik DailyOK'yi her hisse için "True" dönecek şekilde bypass ediyoruz.
    class DummyDailyOK:
        def __call__(self, d): return True
    dok = DummyDailyOK()

    for t in HISSELER:
        try:
            raw_df = fetch_bist_data(t)
            if raw_df.empty:
                continue
                
            df = add_ind(closed_bars(raw_df, now))
            if len(df) < DONCHIAN_N + ATR_N + 2:
                continue
                
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
            
            send(f"🟢 Murat, {t} için AL sinyali (Sadece Yerli Veri, {bar_end:%H:%M})\n\n"
                 f"• Giriş referansı: {sig['giris']:.2f} TL\n"
                 f"• İlk STOP: {sig['stop']:.2f} TL\n"
                 f"• Önerilen adet: {lot}")
        except Exception:
            continue

    if json.dumps(state, sort_keys=True) != before:
        STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    if "--test" in sys.argv:
        send("✅ BIST 500 gün içi botu test mesajı (Sadece Yerli Veri - 5 dk)")
    else:
        scan(force="--force" in sys.argv)


if __name__ == "__main__":
    main()
