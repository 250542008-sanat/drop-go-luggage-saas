# app/schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Dükkan (Kafe) eklerken istenecek veriler
from pydantic import BaseModel
from typing import Optional

class StoreCreate(BaseModel):
    name: str
    address: str
    hourly_rate: float

# Dükkan (Kafe) bilgisi dışarıya (API'ye) dönerken gösterilecek veriler
class StoreResponse(StoreCreate):
    id: int

    class Config:
        from_attributes = True

# Rezervasyon oluştururken istenecek veriler
# app/schemas.py (BookingCreate sınıfı)
from pydantic import BaseModel
from typing import Optional

class BookingCreate(BaseModel):
    store_id: int
    customer_id: int
    bags_count: int
    customer_contact: Optional[str] = None  # YENİ EKLENEN ALAN

# Rezervasyon bilgisi dönerken gösterilecek veriler
class BookingResponse(BookingCreate):
    id: int
    booking_reference: str
    qr_code_data: str
    status: str
    total_price: float

    class Config:
        from_attributes = True

        # app/schemas.py dosyasının en altına eklenecek:
class BookingScan(BaseModel):
    qr_code_data: str