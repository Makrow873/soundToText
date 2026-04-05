# Temel imaj olarak Python kullanalım
FROM python:3.11-slim

# Gerekli sistem paketlerini (ffmpeg ve node.js) kuralım
RUN apt-get update && apt-get install -y \
    ffmpeg \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# docx modülünü global olarak kuralım
RUN npm install -g docx

# Çalışma dizinini ayarlayalım
WORKDIR /app

# Python bağımlılıklarını kopyalayıp kuralım
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyalayalım
COPY . .

# Gunicorn ile uygulamayı başlatalım (Zaman aşımını uzun tutuyoruz)
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--timeout", "300", "app:app"]
