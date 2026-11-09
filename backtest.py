import json
import numpy as np
import pandas as pd
from strategies import STRATEGIES, atr

COST_PER_SIDE = 0.0015
MIN_TURNOVER_TL = 40_000_000  # Likiditeyi artırdık: Günlük en az 40 Milyon TL hacim
OOS_YEARS = 2

MIN_TRADES_IN = 30
MIN_TRADES_OOS = 10
MIN_PROFIT_FACTOR = 1.30     # Kazançlar, kayıplardan net %30 fazla olmalı
MIN_WIN_RATE_OOS = 0.35

def liquid(df):
    if len(df) < 300:
        return False
    turnover = (df["Close"] * df["Volume"]).tail(60).median()
    return bool(turnover >= MIN_TURNOVER_TL)

def run_trades(df, entry, exit_sig, stop_atr, max_hold, cost=COST_PER_SIDE):
    o = df["Open"].to_numpy(float)
    h = df["High"].to_numpy(float)
    l = df["Low"].to_numpy(float)
    c = df["Close"].to_numpy(float)
    a = atr(df).to_numpy(float)
    en = entry.to_numpy(bool)
    ex = exit_sig.to_numpy(bool)
    idx = df.index
    n = len(df)
    out = []
    i = 0
    while i < n - 1:
        if not en[i]:
            i += 1
            continue
        k = i + 1
        ep = o[k]
        if not np.isfinite(ep) or ep <= 0:
            i += 1
            continue
        
        current_stop = ep - stop_atr * a[i] if np.isfinite(a[i]) else ep * 0.9
        highest_seen = ep
        
        xp, xi = None, None
        j = k
        while j < n:
            if h[j] > highest_seen:
                highest_seen = h[j]
                new_stop = highest_seen - stop_atr * a[j]
                if new_stop > current_stop:
                    current_stop = new_stop
            
            if l[j] <= current_stop:
                xp, xi = min(o[j], current_stop), j
                break
                
            if j - k + 1 >= max_hold:
                xp, xi = c[j], j
                break
                
            if ex[j]:
                if j + 1 < n:
                    xp, xi = o[j + 1], j + 1
                else:
                    xp, xi = c[j], j
                break
            j += 1
            
        if xp is None:
            break
        out.append(dict(entry_date=idx[k], exit_date=idx[xi],
                        ret=xp / ep - 1 - 2 * cost, bars=xi - k + 1))
        i = xi
    return pd.DataFrame(out, columns=["entry_date", "exit_date", "ret", "bars"])

def stats(rets):
    r = np.asarray(rets, float)
    n = len(r)
    if n == 0:
        return dict(n=0, win_rate=0.0, avg_win=0.0, avg_loss=0.0, pf=0.0, expectancy=0.0)
    w, lo = r[r > 0], r[r <= 0]
    pf = w.sum() / abs(lo.sum()) if lo.sum() < 0 else 99.0
    return dict(n=int(n), win_rate=float(len(w)/n), avg_win=float(w.mean()) if len(w) else 0.0,
                avg_loss=float(lo.mean()) if len(lo) else 0.0, pf=float(min(pf, 99.0)), expectancy=float(r.mean()))

def evaluate(data, save_path=None):
    cutoff = pd.Timestamp.today().normalize() - pd.DateOffset(years=OOS_YEARS)
    report = {}
    for name, spec in STRATEGIES.items():
        frames = []
        for t, df in data.items():
            if not liquid(df): continue
            en, ex = spec["fn"](df)
            tr = run_trades(df, en, ex, spec["stop_atr"], spec["max_hold"])
            if len(tr):
                tr["ticker"] = t
                frames.append(tr)
        allt = pd.concat(frames) if frames else pd.DataFrame(columns=["entry_date", "exit_date", "ret", "bars", "ticker"])
        ins = allt[allt["entry_date"] < cutoff]
        oos = allt[allt["entry_date"] >= cutoff]
        s_in, s_oos = stats(ins["ret"]), stats(oos["ret"])
        enabled = (s_in["n"] >= MIN_TRADES_IN and s_oos["n"] >= MIN_TRADES_OOS and 
                   s_in["expectancy"] > 0 and s_oos["expectancy"] > 0 and 
                   s_in["pf"] >= MIN_PROFIT_FACTOR and s_oos["pf"] >= MIN_PROFIT_FACTOR and 
                   s_oos["win_rate"] >= MIN_WIN_RATE_OOS)
        report[name] = dict(enabled=bool(enabled), in_sample=s_in, out_of_sample=s_oos, avg_bars=float(allt["bars"].mean()) if len(allt) else 0.0)
    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    return report

def print_report(report):
    print(f"{'strateji':22} {'dönem':6} {'işlem':>6} {'kazanma%':>9} {'ort.kazanç%':>12} {'ort.kayıp%':>11} {'PF':>5} {'beklenti%':>10}")
    for name, r in report.items():
        for label, key in (("IS", "in_sample"), ("OOS", "out_of_sample")):
            s = r[key]
            print(f"{name:22} {label:6} {s['n']:6d} {s['win_rate']*100:9.1f} {s['avg_win']*100:12.2f} {s['avg_loss']*100:11.2f} {s['pf']:5.2f} {s['expectancy']*100:10.2f}")
        print(f"{'':22} -> {'AKTİF (Sinyal Üretir)' if r['enabled'] else 'KAPALI (Şartları Sağlamadı)'}")
