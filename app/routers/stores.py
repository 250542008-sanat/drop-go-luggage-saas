from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Union

from app.database import get_db
from app.models import Store

router = APIRouter(prefix="/stores", tags=["Stores"])

class StoreCreateSchema(BaseModel):
    name: str
    address: str
    hourly_rate: Union[float, str]  # İster sayı ister metin gelsin, esnekçe kabul eder

@router.post("/", response_model=dict)
def create_store(store_data: StoreCreateSchema, db: Session = Depends(get_db)):
    try:
        # Gelen veri metin veya sayı olabilir; virgülü noktaya çevirip float'a dönüştürüyoruz
        rate_str = str(store_data.hourly_rate).replace(",", ".")
        parsed_rate = float(rate_str)
        
        new_store = Store(
            name=store_data.name,
            address=store_data.address,
            hourly_rate=parsed_rate
        )
        db.add(new_store)
        db.commit()
        db.refresh(new_store)
        return {"status": "success", "store_id": new_store.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list)
def get_stores(db: Session = Depends(get_db)):
    return db.query(Store).all()