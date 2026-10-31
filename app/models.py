from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="esnaf")

class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    hourly_rate = Column(Float)

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    booking_reference = Column(String, unique=True, index=True)
    store_id = Column(Integer)
    customer_id = Column(Integer)
    customer_contact = Column(String, nullable=True)
    bags_count = Column(Integer)
    total_price = Column(Float)
    status = Column(String, default="pending")
    qr_code_data = Column(String)

# YENİ EKLENEN AYARLAR TABLOSU
class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    app_name = Column(String, default="Drop&Go Luggage")
    currency = Column(String, default="₺")
    default_lang = Column(String, default="tr")