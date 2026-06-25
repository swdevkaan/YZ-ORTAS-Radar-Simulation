# 🛰️ YZ-ORTAS: Yapay Zeka ve Bilgisayarlı Görü Destekli Otonom Hedef Kilitlemeli 3D Radar Simülasyon Sistemi

Bu proje; gerçek zamanlı nesne tespiti (YOLOv8), yapısal öznitelik esnetme/eşleştirme (ORB), mikrodenetleyici donanım entegrasyonu (Arduino) ve 3 boyutlu grafik simülasyonunu (Ursina Engine) bir araya getiren **hibrit bir otonom savunma ve takip sistemi** mekatronik projesidir.

---

## 👥 Proje Ekibi (Geliştiriciler)
Bu proje, aşağıda yer alan geliştirici ekibi tarafından ortaklaşa ve büyük bir özveriyle geliştirilmiştir:
* **[Muhammed Çağrı Güneş](https://github.com/CagriGunes46)** — *Proje Yöneticisi & Algoritma Geliştirici*
* **[Mustafa Kaan Çelik](https://github.com/swdevkaan)** — *Yazılım / Donanım Geliştirici*
* **[Özcan Lale](https://github.com/ozcanlale-prog)** — *Yazılım / Donanım Geliştirici*
* **[Enis Öngenç](https://github.com/25020091007EnisOngencc)** — *Yazılım / Donanım Geliştirici*

---

## 🚀 Proje Özeti & Çalışma Mantığı

Sistem, iki temel mod üzerinden donanım ve yazılımın çift yönlü (bidirectional) kusursuz haberleşmesiyle çalışır:

1. **Arama Modu (Search Mode):** Arduino'ya bağlı SG90 servo motor 0-180 derece arasında sürekli tarama yapar. HC-SR04 ultrasonik sensörü aldığı mesafe verilerini Python'a anlık aktarır ve Ursina 3D oyun motoru ekranında radar çizgisi dönerek canlı simülasyonu günceller.
2. **Hedef Kilitleme Modu (Target Locked):** Kamera açısına bir deniz aracı girdiğinde **YOLOv8** hedefi algılar. Kutu içerisindeki kesit anında **ORB Feature Matching** algoritması ile taranarak veri tabanındaki 5 farklı gemi modeliyle (`TCG_ANADOLU`, `MSC_GULSUN`, `COSTA_SMERALDA`, `KNOCK_NEVIS`, `HANNAH_BODEN`) parmak izi gibi eşleştirilir. 
   * Gemi kimliği tespit edildiği an Python, Arduino'ya seri port üzerinden **'S' (Stop)** komutu gönderir.
   * Arduino donanımı motoru **"zınk" diye durdurarak** sensörü hedefe kilitler.
   * Ursina 3D ekranında geminin orijinal görseli tam açı ve mesafesinde belirmeye başlar ve bilgi paneli kırmızıya dönerek teknik detayları ekrana basar. Target çekildiğinde sistem otomatik olarak arama moduna geri döner.

---

## 🛠️ Kullanılan Teknolojiler ##

### Yazılım (Software) ###
* **Python 3.13** (Ana Programlama Dili)
* **YOLOv8 (Ultralytics):** Real-time nesne tespiti modeli.
* **OpenCV:** Görüntü işleme ve bilgisayarlı görü altyapısı.
* **ORB (Oriented FAST and Rotated BRIEF):** Işık parlamalarından bağımsız, doku/geometri tabanlı kimlik tespiti algoritması.
* **Ursina Engine:** Python tabanlı gerçek zamanlı 3D grafik/simülasyon motoru.
* **PySerial:** Python ile Arduino arasında 115200 baud rate hızında seri haberleşme.

### Donanım (Hardware) ###
* Arduino Uno / Mega Mikrodenetleyici Kartı
* SG90 Servo Motor
* HC-SR04 Ultrasonik Mesafe Sensörü
* Kamera Modülü (Dahili/Harici)

---

## 📦 Kurulum ve Çalıştırma

Projeyi yerel bilgisayarınızda çalıştırmak için aşağıdaki adımları sırasıyla uygulayabilirsiniz:

### 1. Gerekli Python Kütüphanelerini Yükleyin
Kütüphaneleri Türkiye yansıtıcı sunucusunu kullanarak ışık hızında yüklemek için terminale veya CMD'ye şu komutu yazın:
```bash
pip install opencv-python ultralytics pyserial ursina numpy -i [https://pypi.tuna.tsinghua.edu.tr/simple](https://pypi.tuna.tsinghua.edu.tr/simple)
### 
2. Dosya Düzeni
Python kodunun (`GEMİ.py`) kusursuz çalışabilmesi ve parmak izi eşleştirmelerinin (ORB) patlamaması için klasör yapısının tam olarak aşağıdaki gibi olması şarttır:
📂 YZ-ORTAS-Radar-Simulation/
├── 📄 GEMİ.py                  # Ana Python kodumuz (Ursina & YOLO & ORB)
├── 📄 Arduino_Radar.ino        # Arduino'ya yüklenen kaynak kodumuz
├── 📄 yolov8n.pt               # İnternetten inen/atılan YOLO model dosyası
├── 📄 README.md                # Şu an okuduğunuz proje tanıtım belgesi
├── 🖼️ TCG_ANADOLU.jpeg         # Referans Gemi Fotoğrafı 1
├── 🖼️ MSC_GULSUN.jpeg          # Referans Gemi Fotoğrafı 2
├── 🖼️ COSTA_SMERALDA.jpeg      # Referans Gemi Fotoğrafı 3
├── 🖼️ KNOCK_NEVIS.jpeg         # Referans Gemi Fotoğrafı 4
└── 🖼️ HANNAH_BODEN.jpeg        # Referans Gemi Fotoğrafı 5
