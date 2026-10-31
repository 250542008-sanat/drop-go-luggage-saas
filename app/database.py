# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Tüm API uç noktalarında kullanılacak veritabanı oturum başlatıcısı
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()