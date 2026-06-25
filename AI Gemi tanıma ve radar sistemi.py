Python 3.13.12 (tags/v3.13.12:1cbe481, Feb  3 2026, 18:22:25) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import cv2
from ultralytics import YOLO
import serial
import threading
import math
import numpy as np
import os
from ursina import *

# --- 1. SABİT VERİ TABANI ---
gemi_verileri = {
    "TCG_ANADOLU": {"tur": "Savas Gemisi (LHD)", "bayrak": "Turkiye", "boy": "231m", "yuk": "SIHA / Helikopter"},
    "MSC_GULSUN": {"tur": "Konteyner Gemisi", "bayrak": "Panama", "boy": "400m", "yuk": "23.756 Konteyner"},
    "COSTA_SMERALDA": {"tur": "Yolcu Gemisi (Cruise)", "bayrak": "Italya", "boy": "337m", "yuk": "6554 Yolcu"},
    "KNOCK_NEVIS": {"tur": "Petrol Tankeri", "bayrak": "Norvec", "boy": "458m", "yuk": "Ham Petrol"},
    "HANNAH_BODEN": {"tur": "Balikci Teknesi", "bayrak": "ABD", "boy": "30m", "yuk": "Kilic Baligi"}
}

PORT = 'COM4' # Burayı gerekirse yeni PC'nin Arduino portuna göre değiştir
try:
    ser = serial.Serial(PORT, 115200, timeout=1)
    print(f"BAŞARILI: {PORT} bağlandı.")
except:
    print("HATA: Arduino portu meşgul veya bağlı değil!")
    ser = None

model = YOLO('yolov8n.pt') 

# --- 2. ORB ÖZNİTELİK MANTIĞI VE ŞABLON EĞİTİMİ ---
orb = cv2.ORB_create(nfeatures=1000)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

referans_dosyalar = {
    "TCG_ANADOLU": "TCG_ANADOLU.jpeg",
    "MSC_GULSUN": "MSC_GULSUN.jpeg",
    "COSTA_SMERALDA": "COSTA_SMERALDA.jpeg",
    "KNOCK_NEVIS": "KNOCK_NEVIS.jpeg",
    "HANNAH_BODEN": "HANNAH_BODEN.jpeg"
}

referans_oznitelikler = {}
print("\n--- YZ PARMAK İZİ EĞİTİMİ BAŞLIYOR ---")
for gemi_id, dosya_adi in referans_dosyalar.items():
    if os.path.exists(dosya_adi):
        img = cv2.imread(dosya_adi, cv2.IMREAD_GRAYSCALE)
        kp, des = orb.detectAndCompute(img, None)
        referans_oznitelikler[gemi_id] = des
        print(f"[+] {gemi_id} şablonu başarıyla hafızaya alındı.")
    else:
        print(f"[-] DİKKAT: '{dosya_adi}' bulunamadı! Parmak izi takibi patlar.")
print("--------------------------------------\n")

def gemi_kimligi_tahmin_et_orb(frame, x1, y1, x2, y2):
    gemi_kesit = frame[max(0, y1):y2, max(0, x1):x2]
    if gemi_kesit.size == 0: return "MSC_GULSUN"
    
    gray_kesit = cv2.cvtColor(gemi_kesit, cv2.COLOR_BGR2GRAY)
    kp_kesit, des_kesit = orb.detectAndCompute(gray_kesit, None)
    
    if des_kesit is None or len(des_kesit) < 5:
        return "MSC_GULSUN"

    en_iyi_eslesme = "MSC_GULSUN"
    en_yuksek_skor = 0

    for gemi_id, des_referans in referans_oznitelikler.items():
        if des_referans is not None:
            try:
                matches = bf.match(des_kesit, des_referans)
                iyi_eslesmeler = [m for m in matches if m.distance < 65]
                skor = len(iyi_eslesmeler)

                if skor > en_yuksek_skor:
                    en_yuksek_skor = skor
                    en_iyi_eslesme = gemi_id
            except:
                pass
    return en_iyi_eslesme

# --- 3. 3D SAHNE KURULUMU (URSINA) ---
app = Ursina()
Sky()
Deniz = Entity(model='plane', scale=100, texture='water', color=color.cyan)
Yazi = Text(text="Sistem Baslatiliyor...", position=(-0.85, 0.45), scale=1.1, color=color.black)
# 2D resmi 3D dünyada tutacak "QUAD" modeli
Gemi_3D = Entity(model='quad', scale=(6, 4), position=(0, 2, 0), double_sided=True, enabled=False)

def gemi_3d_modeli_guncelle(gemi_id):
    dosya_adi = f"{gemi_id}.jpeg"
    if os.path.exists(dosya_adi):
        Gemi_3D.texture = dosya_adi
    if gemi_id == "HANNAH_BODEN":
        Gemi_3D.scale = (5, 4)
    else:
        Gemi_3D.scale = (7, 4)

# --- 4. ARDUINO RADAR OKUMA ---
aci, mesafe = 0, 0
def veri_oku():
    global aci, mesafe
    while True:
        if ser is not None and ser.in_waiting > 0:
            try:
                line = ser.read_until(b'.').decode('utf-8').strip().replace('.', '')
                parcalar = line.split(',')
                if len(parcalar) == 2:
                    aci = int(parcalar[0])
                    mesafe = int(parcalar[1])
                    if 0 < mesafe < 100:
                        rad = math.radians(aci)
                        Gemi_3D.x = math.sin(rad) * (mesafe / 5)
                        Gemi_3D.z = math.cos(rad) * (mesafe / 5)
                        Gemi_3D.rotation_y = aci
            except: pass

threading.Thread(target=veri_oku, daemon=True).start()

# --- 5. ANA DÖNGÜ (DURDURMA/ÇALIŞTIRMA MANTIĞI) ---
kamera = cv2.VideoCapture(0, cv2.CAP_DSHOW) # Donmayı engelleyen DirectShow api
son_durum = "BOS" 

def update():
    global aci, mesafe, Yazi, son_durum
    
    ret, frame = kamera.read()
    if ret:
        results = model(frame, stream=True, verbose=False, conf=0.35)
        teshis_edilen_id = None
        
        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) == 8: 
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    teshis_edilen_id = gemi_kimligi_tahmin_et_orb(frame, x1, y1, x2, y2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, teshis_edilen_id, (x1, y1-10), 
...                                 cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
...                     break
...         
...         if teshis_edilen_id: # GEMİ GÖRÜLDÜĞÜ AN!
...             # ARDUINO'YA "DUR" (STOP) MESAJI GÖNDER
...             if ser is not None and son_durum != "DUR":
...                 ser.write(b'S') 
...                 son_durum = "DUR"
...                 
...             info = gemi_verileri[teshis_edilen_id]
...             gemi_3d_modeli_guncelle(teshis_edilen_id)
...             Gemi_3D.enabled = True
...             
...             Yazi.text = (f"!!! HEDEF KILITLENDI !!!\n"
...                          f"OTOMATIK TESHIS: {teshis_edilen_id}\n"
...                          f"--------------------------\n"
...                          f"Tur: {info['tur']}\n"
...                          f"Bayrak: {info['bayrak']}\n"
...                          f"Boy: {info['boy']}\n"
...                          f"Yuk: {info['yuk']}\n"
...                          f"Mesafe: {mesafe} cm\n"
...                          f"Radar Acisi: {aci}")
...             Yazi.color = color.red
...         else: # GEMİ YOKSA VEYA ÇEKİLDİYSE!
...             # ARDUINO'YA "DÖNMEYE DEVAM ET" (RUN) MESAJI GÖNDER
...             if ser is not None and son_durum != "DON":
...                 ser.write(b'R')
...                 son_durum = "DON"
...                 
...             Gemi_3D.enabled = False
...             Yazi.text = f"Radar Taraniyor... Aci: {aci}"
...             Yazi.color = color.black
... 
...         cv2.imshow("Kamera Takip", frame)
...         cv2.waitKey(1)
...     else:
...         Yazi.text = "HATA: Kamera Acilamiyor!"
...         Yazi.color = color.red
... 
