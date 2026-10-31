# app/core/config.py

class Settings:
    PROJECT_NAME: str = "Drop&Go Luggage Storage"
    PROJECT_VERSION: str = "1.0.0"
    
    # Alıcının kolayca değiştirebileceği ticari ayarlar
    CURRENCY_SYMBOL: str = "$"
    BASE_HOURLY_RATE: float = 5.0  # Saatlik varsayılan ücret
    
    # Veritabanı (Şimdilik SQLite, canlıya alırken alıcı bunu PostgreSQL URL'si ile değiştirecek)
    DATABASE_URL: str = "sqlite:///./luggage_saas.db"

settings = Settings()