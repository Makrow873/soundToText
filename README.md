# 🎙️ Ses → Metin → Word Dönüştürücü

Ses dosyalarını Whisper yapay zekası ile metne çevirir ve Word belgesi olarak sunar.

## 📁 Dosya Yapısı

```
proje/
├── app.py              ← Flask backend
├── requirements.txt    ← Python bağımlılıkları
├── README.md
└── templates/
    └── index.html      ← Web arayüzü
```

## ⚙️ Kurulum

### 1. Python bağımlılıkları

```bash
pip install -r requirements.txt
```

### 2. FFmpeg (ses işleme için zorunlu)

```bash
# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg

# Windows
# https://ffmpeg.org/download.html → PATH'e ekleyin
```

### 3. Node.js + docx (Word belgesi oluşturmak için)

```bash
# Node.js: https://nodejs.org (v18+)
npm install -g docx
```

## 🚀 Çalıştırma

```bash
python app.py
```

Tarayıcıda açın: **http://localhost:5000**

## 🎯 Kullanım

1. Ses dosyasını sürükle-bırak veya seç
2. Model ve dil seçin (Türkçe için "Medium" önerilir)
3. **Transkripsiyon Başlat** butonuna tıklayın
4. İşlem tamamlandığında **Word Olarak İndir** butonuna tıklayın

## 📊 Model Karşılaştırması

| Model  | Hız       | Doğruluk    | RAM   |
|--------|-----------|-------------|-------|
| tiny   | ⚡⚡⚡ Çok hızlı | Düşük   | ~1 GB |
| base   | ⚡⚡ Hızlı     | İyi ✓   | ~1 GB |
| small  | ⚡ Orta       | Daha iyi | ~2 GB |
| medium | 🐢 Yavaş     | Yüksek  | ~5 GB |
| large  | 🐢🐢 Çok yavaş | En yüksek | ~10 GB |

**Türkçe için medium veya large önerilir.**

## 🔒 Gizlilik

Tüm işlem yerel makinenizde yapılır. Ses dosyaları sunucuya gönderilmez (sunucu = kendi bilgisayarınız).

## 🛠️ Desteklenen Formatlar

MP3, WAV, M4A, OGG, FLAC, WEBM, MP4, MKV, AVI, MOV, AAC, WMA
