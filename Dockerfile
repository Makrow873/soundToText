FROM python:3.11-slim

# Ses işleme için FFmpeg'i kur
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Hugging Face Kuralı: 1000 ID'li bir kullanıcı oluştur
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Çalışma dizinini ayarla
WORKDIR /app

# Requirements dosyasını kopyala ve kütüphaneleri kur
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY --chown=user . .

# Geçici dosyalar (ses ve docx) için klasör oluştur ve izin ver
RUN mkdir -p uploads && chmod 777 uploads

# Uygulamayı Hugging Face'in zorunlu kıldığı 7860 portunda başlat
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--timeout", "300", "app:app"]
