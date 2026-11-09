import numpy as np
import pandas as pd

def sma(s, n):
    return s.rolling(n).mean()

def atr(df, n=14):
    pc = df["Close"].shift(1)
    tr = pd.concat(
        [df["High"] - df["Low"], (df["High"] - pc).abs(), (df["Low"] - pc).abs()],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()

def donchian_breakout(df):
    """
    Daha önce test ettiğimiz en karlı ve net strateji:
    20 günlük en yüksek seviyenin kırılımı (Breakout) + Hacim Onayı
    """
    c = df["Close"]
    v = df["Volume"]
    h = df["High"]
    
    # 1. Trend Filtresi (200 günlük ortalamanın üstü)
    trend = c > sma(c, 200)
    
    # 2. Zirve Kırılımı (Donchian Breakout)
    zirve_20 = h.rolling(20).max().shift(1)
    kirilim = c > zirve_20
    
    # 3. Hacim Konformasyonu
    hacim = v > (sma(v, 20) * 1.5)
    
    entry = trend & kirilim & hacim
    
    # Çıkış: Fiyat 10 günlük en düşük seviyenin altına sarkarsa trend bitti çık
    exit_ = c < df["Low"].rolling(10).min().shift(1)
    
    return entry.astype(bool), exit_.astype(bool)

STRATEGIES = {
    "donchian_breakout": dict(
        fn=donchian_breakout, 
        stop_atr=2.2,  # İdeal stop mesafesi
        max_hold=50,   # Büyük trendleri sürmek için zaman tanı
        exit_text="Fiyat 10 günlük kanal tabanını aşağı kesti",
    )
}
