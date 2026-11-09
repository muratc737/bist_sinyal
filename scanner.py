import sys
import os
import requests
import yfinance as yf
import pandas as pd

# Telegram Bilgileri
TOKEN = "9294997364:AAGp_p4GEuWL1uYQiVBFlWzj3IYi5ff5OyI"
CHAT_ID = "8218088218"

def send_telegram(message):
    if not TOKEN:
        print("Telegram token veya chat id eksik!")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Telegram hata kodu: {response.text}")
    except Exception as e:
        print(f"Telegram bağlantı hatası: {e}")

def run_scan():
    print("15 dakikalık tarama başlatılıyor...")
    
    hisseler = ["THYAO.IS", "EREGL.IS", "GARAN.IS", "ASELS.IS", "BIMAS.IS"]
    
    for hisse in hisseler:
        try:
            # 15 dakikalık mum verisi çekiliyor
            df = yf.download(hisse, period="5d", interval="15m", progress=False)
            if df.empty or len(df) < 20:
                continue
            
            high_20 = df['High'].rolling(window=20).max()
            low_20 = df['Low'].rolling(window=20).min()
            
            current_close = df['Close'].iloc[-1]
            prev_high = high_20.iloc[-2]
            current_stop = low_20.iloc[-2]
            
            if hasattr(current_close, "item"):
                current_close = current_close.item()
            if hasattr(prev_high, "item"):
                prev_high = prev_high.item()
            if hasattr(current_stop, "item"):
                current_stop = current_stop.item()

            # Donchian Kırılım Şartı (15m)
            if current_close > prev_high:
                mesaj = (
                    f"🟢 Murat, {hisse} hissesinde 15m Donchian kırılımı var, al!\n\n"
                    f"• Son Fiyat: {current_close:.2f} TL\n"
                    f"• Stop Önerisi: {current_stop:.2f} TL\n\n"
                    f"Aldıktan sonra mutlaka stop koy."
                )
                send_telegram(mesaj)
                print(f"Sinyal gönderildi: {hisse}")
        except Exception as e:
            print(f"{hisse} taranırken hata: {e}")

if __name__ == "__main__":
    run_scan()
