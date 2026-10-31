# app/routers/bookings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import json

from app.database import get_db
from app.models import Booking, Store
from app.schemas import BookingCreate

router = APIRouter(prefix="/bookings", tags=["Bookings"])

# --- BİLDİRİM MOTORU (SMS / E-POSTA SİMÜLASYONU) ---
def send_notification(contact_info: str, reference_code: str):
    if not contact_info:
        return
        
    ticket_url = f"http://127.0.0.1:8000/ticket/{reference_code}"
    
    # Ürünü satın alan kişi buraya kendi SMTP veya SMS API kodlarını yazacaktır.
    print("\n" + "="*50)
    print(" 📧 SİSTEM BİLDİRİMİ TETİKLENDİ (E-POSTA / SMS) ")
    print("="*50)
    print(f"Alıcı     : {contact_info}")
    print(f"Mesaj     : Drop&Go'yu tercih ettiğiniz için teşekkürler!")
    print(f"            Rezervasyon biletinize ve QR kodunuza aşağıdaki linkten ulaşabilirsiniz:")
    print(f"            {ticket_url}")
    print("="*50 + "\n")


@router.post("/", response_model=dict)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    store = db.query(Store).filter(Store.id == booking.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Emanet noktası (Store) bulunamadı")

    short_uuid = str(uuid.uuid4())[:8].upper()
    
    qr_data = {
        "reference": short_uuid,
        "store_id": booking.store_id,
        "action": "validate_luggage"
    }
    qr_json = json.dumps(qr_data)

    new_booking = Booking(
        booking_reference=short_uuid,
        store_id=booking.store_id,
        customer_id=booking.customer_id,
        customer_contact=booking.customer_contact, # İletişim bilgisini kaydediyoruz
        bags_count=booking.bags_count,
        qr_code_data=qr_json
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    # Rezervasyon başarıyla oluştuğunda bildirimi gönderiyoruz
    send_notification(new_booking.customer_contact, new_booking.booking_reference)

    return {
        "status": "success",
        "booking_reference": new_booking.booking_reference,
        "qr_code_data": qr_json
    }

# (Dosyanın altındaki scan rotası vb. aynı kalacak)
# app/routers/bookings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime
import math

from app.database import get_db
from app.models import Booking, Store
from app.schemas import BookingCreate, BookingResponse, BookingScan

router = APIRouter(
    prefix="/bookings",
    tags=["Rezervasyonlar ve QR Kod (Bookings)"]
)

@router.post("/", response_model=BookingResponse)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    # Önce dükkanın sistemde var olup olmadığını kontrol edelim
    store = db.query(Store).filter(Store.id == booking.store_id).first()
    if not store:
        raise HTTPException(status_code=404, detail="Emanet noktası (Store) bulunamadı")

    # Yeni rezervasyon oluşturma ve QR kodu üretme
    new_booking = Booking(
        booking_reference=str(uuid.uuid4())[:8].upper(), # Örn: 8A4B2C9F
        qr_code_data=str(uuid.uuid4()), # Kameraya okutulacak gizli eşsiz veri
        store_id=booking.store_id,
        customer_id=booking.customer_id,
        bags_count=booking.bags_count,
        status="pending", # Bekliyor
        total_price=0.0 # Çanta alınırken hesaplanacak
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

@router.get("/", response_model=List[BookingResponse])
def get_all_bookings(db: Session = Depends(get_db)):
    bookings = db.query(Booking).all()
    return bookings

@router.post("/scan", response_model=BookingResponse)
def scan_qr_code(scan_data: BookingScan, db: Session = Depends(get_db)):
    # 1. Okutulan QR Kod ile veritabanında rezervasyonu bul
    booking = db.query(Booking).filter(Booking.qr_code_data == scan_data.qr_code_data).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Geçersiz QR Kod. Sistemde bulunamadı.")
    
    # 2. Çanta Bırakma (Emanete Alma)
    if booking.status == "pending":
        booking.status = "stored"
        booking.drop_off_time = datetime.utcnow() # Çantanın bırakıldığı anı kaydet
        
    # 3. Çanta Teslim Alma ve Fiyat Hesaplama
    elif booking.status == "stored":
        booking.status = "retrieved"
        booking.pick_up_time = datetime.utcnow() # Çantanın alındığı anı kaydet
        
        # Süreyi hesapla
        time_diff = booking.pick_up_time - booking.drop_off_time
        # math.ceil ile süreyi her zaman yukarı yuvarlıyoruz (örn: 10 dakika = 1 saat)
        hours = math.ceil(time_diff.total_seconds() / 3600) 
        if hours == 0:
            hours = 1
            
        # Dükkanın saatlik ücretini bul
        store = db.query(Store).filter(Store.id == booking.store_id).first()
        rate = store.hourly_rate if store and store.hourly_rate > 0 else 5.0
        
        # Toplam fiyatı yaz (Saat x Ücret x Çanta Sayısı)
        booking.total_price = hours * rate * booking.bags_count
        
    else:
        raise HTTPException(status_code=400, detail="Bu çanta zaten teslim edilmiş.")
        
    db.commit()
    db.refresh(booking)
    return booking