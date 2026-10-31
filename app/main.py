import jwt
import json
import random
from passlib.context import CryptContext
from fastapi import FastAPI, Request, Depends, HTTPException, status, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import APIKeyCookie
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import engine, get_db
from app.models import Base, Booking, Store, User, Setting
from app.core.config import settings
from app.routers import stores, bookings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "SaaS_Super_Gizli_Anahtar_2026"
ALGORITHM = "HS256"
cookie_sec = APIKeyCookie(name="access_token", auto_error=False)

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)
templates = Jinja2Templates(directory="app/templates")

@app.on_event("startup")
def startup_db():
    db = next(get_db())
    if not db.query(User).first():
        db.add(User(username="admin", password_hash=pwd_context.hash("admin123"), role="admin"))
        db.add(User(username="esnaf", password_hash=pwd_context.hash("esnaf123"), role="esnaf"))
    if not db.query(Setting).first():
        db.add(Setting(app_name="Drop&Go Luggage", currency="₺", default_lang="tr"))
    db.commit()

def get_current_user(token: str = Depends(cookie_sec), db: Session = Depends(get_db)):
    if not token: raise HTTPException(status_code=401)
    try:
        token = token.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(User).filter(User.username == payload.get("sub")).first()
        if not user: raise HTTPException(status_code=401)
        return user
    except: raise HTTPException(status_code=401)

@app.exception_handler(401)
async def auth_exception_handler(request: Request, exc: HTTPException):
    return RedirectResponse(url="/login")

# --- ÇEVİRİ SÖZLÜKLERİ ---
LOGIN_TRANSLATIONS = {
    "tr": {"login_title": "Sisteme Giriş", "username": "Kullanıcı Adı", "password": "Şifre", "user_ph": "Kullanıcı adınızı girin", "login_btn": "Giriş Yap", "back_home": "Ana Vitrine Dön", "error_msg": "Hatalı kullanıcı adı veya şifre!"},
    "en": {"login_title": "System Login", "username": "Username", "password": "Password", "user_ph": "Enter your username", "login_btn": "Login", "back_home": "Back to Home", "error_msg": "Invalid username or password!"}
}
INDEX_TRANSLATIONS = {
    "tr": {"welcome": "SaaS Platformuna Hoş Geldiniz. Lütfen girmek istediğiniz paneli seçin.", "store_panel": "Esnaf Paneli", "store_desc": "Müşteri karekodlarını okutun, emanetleri teslim alın ve teslim edin.", "admin_panel": "Sistem Yöneticisi", "admin_desc": "Sisteme yeni kafe / emanet noktaları ekleyin ve tüm ağı yönetin.", "go_btn": "Panele Git", "api_link": "Geliştiriciler için API (Swagger) Ekranına Git"},
    "en": {"welcome": "Welcome to the SaaS Platform. Please select the panel you wish to enter.", "store_panel": "Store Panel", "store_desc": "Scan customer QR codes, receive and return luggage.", "admin_panel": "System Administrator", "admin_desc": "Add new stores to the system and manage the entire network.", "go_btn": "Go to Panel", "api_link": "Go to API Dashboard"}
}
DASHBOARD_TRANSLATIONS = {
    "tr": {"title": "Esnaf Paneli", "back_home": "Ana Vitrine Dön", "scan_title": "QR Kod Okut", "scan_desc": "Müşterinin telefonundaki kodu tarayın.", "scan_ph": "Örn: 238ed5f3...", "scan_btn": "İşlemi Tamamla", "table_title": "Rezervasyonlar", "th_ref": "Kodu", "th_bags": "Çanta", "th_status": "Durum", "th_action": "İşlem", "th_price": "Ücret", "empty": "Rezervasyon yok.", "st_pending": "Bekliyor", "st_stored": "Emanette", "st_retrieved": "Teslim Edildi", "drop": "Bırakma", "pickup": "Alınma", "stat_rev": "Toplam Ciro", "stat_bags": "Toplam Çanta", "stat_active": "İçerideki Çanta", "chart_title": "Haftalık İşlem Hacmi"},
    "en": {"title": "Store Panel", "back_home": "Back to Home", "scan_title": "Scan QR Code", "scan_desc": "Scan the customer's QR code.", "scan_ph": "e.g., 238ed5f3...", "scan_btn": "Complete", "table_title": "Bookings", "th_ref": "Ref", "th_bags": "Bags", "th_status": "Status", "th_action": "Action", "th_price": "Price", "empty": "No bookings.", "st_pending": "Pending", "st_stored": "Stored", "st_retrieved": "Retrieved", "drop": "Drop", "pickup": "Pickup", "stat_rev": "Total Revenue", "stat_bags": "Total Processed", "stat_active": "Bags Inside", "chart_title": "Weekly Volume"}
}
ADMIN_TRANSLATIONS = {
    "tr": {"title": "Yönetici Paneli", "back_home": "Ana Vitrine Dön", "add_title": "Yeni Emanet Noktası", "f_name": "Dükkan Adı", "f_name_ph": "Örn: Merkez Kafe", "f_addr": "Adres", "f_rate": "Saatlik Ücret", "f_btn": "Ekle", "table_title": "Aktif Noktalar", "th_id": "ID", "th_name": "Dükkan Adı", "th_addr": "Adres", "th_rate": "Ücret", "empty": "Dükkan yok.", "set_title": "Sistem Ayarları", "s_app": "Platform Adı", "s_cur": "Para Birimi", "s_lang": "Varsayılan Dil", "s_btn": "Ayarları Kaydet"},
    "en": {"title": "Admin Panel", "back_home": "Back to Home", "add_title": "Add Storage Point", "f_name": "Store Name", "f_name_ph": "e.g., Central Cafe", "f_addr": "Address", "f_rate": "Hourly Rate", "f_btn": "Add", "table_title": "Active Points", "th_id": "ID", "th_name": "Store Name", "th_addr": "Address", "th_rate": "Rate", "empty": "No stores.", "set_title": "System Settings", "s_app": "Platform Name", "s_cur": "Currency", "s_lang": "Default Lang", "s_btn": "Save Settings"}
}
TRANSLATIONS = {
    "tr": {"title": "Rezervasyon Biletiniz", "code": "Rezervasyon Kodu", "pending": "Bekliyor", "stored": "Emanette", "retrieved": "Teslim Edildi", "bags": "Çanta Sayısı", "price": "Mevcut Tutar", "home": "Ana Sayfaya Dön", "msg_pending": "Çantalarınızı teslim ediniz.", "msg_stored": "Çantalarınız güvende.", "msg_qr": "Lütfen bu QR kodu okutunuz.", "msg_used": "QR kod kullanılamaz."},
    "en": {"title": "Your Booking Ticket", "code": "Booking Reference", "pending": "Pending", "stored": "Stored", "retrieved": "Retrieved", "bags": "Bags Count", "price": "Total Price", "home": "Back to Home", "msg_pending": "Hand over your bags.", "msg_stored": "Your bags are safe.", "msg_qr": "Show this QR code.", "msg_used": "QR code is unavailable."}
}

def get_sys_data(db: Session):
    sys = db.query(Setting).first()
    return {"project_name": sys.app_name if sys else "Drop&Go", "currency": sys.currency if sys else "₺", "sys": sys}

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, lang: str = "tr", error: str = None, db: Session = Depends(get_db)):
    t = LOGIN_TRANSLATIONS.get(lang, LOGIN_TRANSLATIONS["tr"])
    data = get_sys_data(db)
    return templates.TemplateResponse(request=request, name="login.html", context={"project_name": data["project_name"], "t": t, "lang": lang, "error": error})

@app.post("/login")
def login_post(request: Request, db: Session = Depends(get_db), username: str = Form(...), password: str = Form(...), lang: str = "tr"):
    user = db.query(User).filter(User.username == username).first()
    t = LOGIN_TRANSLATIONS.get(lang, LOGIN_TRANSLATIONS["tr"])
    if not user or not pwd_context.verify(password, user.password_hash):
        data = get_sys_data(db)
        return templates.TemplateResponse(request=request, name="login.html", context={"project_name": data["project_name"], "t": t, "lang": lang, "error": t["error_msg"]})
    token = jwt.encode({"sub": user.username, "role": user.role}, SECRET_KEY, algorithm=ALGORITHM)
    resp = RedirectResponse(url=f"/admin?lang={lang}" if user.role == "admin" else f"/dashboard?lang={lang}", status_code=302)
    resp.set_cookie(key="access_token", value=f"Bearer {token}", httponly=True)
    return resp

@app.get("/logout")
def logout():
    resp = RedirectResponse(url="/")
    resp.delete_cookie("access_token")
    return resp

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, lang: str = None, db: Session = Depends(get_db)):
    data = get_sys_data(db)
    lang = lang or (data["sys"].default_lang if data["sys"] else "tr")
    t = INDEX_TRANSLATIONS.get(lang, INDEX_TRANSLATIONS["tr"])
    return templates.TemplateResponse(request=request, name="index.html", context={"project_name": data["project_name"], "t": t, "lang": lang})

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(request: Request, lang: str = "tr", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["esnaf", "admin"]: raise HTTPException(status_code=403)
    t = DASHBOARD_TRANSLATIONS.get(lang, DASHBOARD_TRANSLATIONS["tr"])
    all_bookings = db.query(Booking).order_by(Booking.id.desc()).all()
    data = get_sys_data(db)
    total_rev = sum(b.total_price for b in all_bookings if b.total_price)
    total_bags = sum(b.bags_count for b in all_bookings if b.bags_count)
    active_bags = sum(b.bags_count for b in all_bookings if b.status in ["pending", "stored"])
    chart_labels = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"] if lang == "tr" else ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    chart_data = [12, 19, 15, 25, 22, 30, 28]
    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "project_name": data["project_name"], "currency": data["currency"], "bookings": all_bookings, "t": t, "lang": lang,
        "stats": {"rev": total_rev, "bags": total_bags, "active": active_bags}, "chart_labels_json": json.dumps(chart_labels), "chart_data_json": json.dumps(chart_data)
    })

@app.get("/admin", response_class=HTMLResponse)
def get_admin_panel(request: Request, lang: str = "tr", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin": return RedirectResponse(url=f"/dashboard?lang={lang}")
    t = ADMIN_TRANSLATIONS.get(lang, ADMIN_TRANSLATIONS["tr"])
    all_stores = db.query(Store).order_by(Store.id.desc()).all()
    data = get_sys_data(db)
    return templates.TemplateResponse(request=request, name="admin.html", context={"project_name": data["project_name"], "sys": data["sys"], "stores": all_stores, "t": t, "lang": lang})

@app.get("/ticket/{reference}", response_class=HTMLResponse)
def get_ticket(request: Request, reference: str, lang: str = "tr", db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.booking_reference == reference).first()
    if not booking: return HTMLResponse(content="<h2>Bilet bulunamadı / Ticket not found.</h2>", status_code=404)
    t = TRANSLATIONS.get(lang, TRANSLATIONS["tr"])
    data = get_sys_data(db)
    return templates.TemplateResponse(request=request, name="customer.html", context={"project_name": data["project_name"], "currency": data["currency"], "booking": booking, "t": t, "current_lang": lang})

class SettingsUpdate(BaseModel):
    app_name: str; currency: str; default_lang: str

@app.post("/api/settings")
def update_settings(data: SettingsUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin": raise HTTPException(status_code=403)
    sys = db.query(Setting).first()
    sys.app_name = data.app_name; sys.currency = data.currency; sys.default_lang = data.default_lang
    db.commit()
    return {"status": "ok"}

# --- YENİ EKLENEN QR İŞLEM MOTORU ---
class ScanRequest(BaseModel):
    qr_code: str

@app.post("/api/scan")
def process_qr_code(data: ScanRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ["esnaf", "admin"]: raise HTTPException(status_code=403)
    booking = db.query(Booking).filter(Booking.booking_reference == data.qr_code).first()
    
    if not booking:
        raise HTTPException(status_code=404, detail="Bilet bulunamadı")
        
    # Durumları otomatik ilerlet: Bekliyor -> Emanette -> Teslim Edildi
    if booking.status == "pending":
        booking.status = "stored"
    elif booking.status == "stored":
        booking.status = "retrieved"
        
    db.commit()
    return {"status": "ok", "new_status": booking.status}

# --- YENİ EKLENEN DEMO BİLET ÜRETİCİ ---
@app.get("/api/demo-bilet")
def create_demo_booking(db: Session = Depends(get_db)):
    import uuid
    ref = str(uuid.uuid4())[:8].upper() # Örn: A8F93BD1
    bags = random.randint(1, 5)         # 1 ile 5 arası rastgele çanta
    price = bags * 45.0                 # Çanta başı fiyat
    
    new_booking = Booking(booking_reference=ref, store_id=1, bags_count=bags, total_price=price, status="pending")
    db.add(new_booking)
    db.commit()
    return RedirectResponse(url="/dashboard")

app.include_router(stores.router)
app.include_router(bookings.router)