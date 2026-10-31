# Temel Python imajını kullanıyoruz
FROM python:3.11-slim

# Çalışma dizinini belirliyoruz
WORKDIR /app

# Gereksinim dosyasını kopyalayıp kütüphaneleri kuruyoruz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm proje dosyalarını imajın içine kopyalıyoruz
COPY . .

# FastAPI'nin çalışacağı port
EXPOSE 8000

# Sunucuyu başlatma komutu
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]