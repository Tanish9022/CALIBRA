from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models
import schemas

router = APIRouter(prefix="/instruments", tags=["instruments"])

@router.post("/", response_model=schemas.Instrument)
def create_instrument(instrument: schemas.InstrumentCreate, db: Session = Depends(get_db)):
    db_instrument = models.Instrument(**instrument.model_dump())
    db.add(db_instrument)
    db.commit()
    db.refresh(db_instrument)
    return db_instrument

@router.get("/", response_model=List[schemas.Instrument])
def read_instruments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    instruments = db.query(models.Instrument).offset(skip).limit(limit).all()
    return instruments

@router.get("/{instrument_id}", response_model=schemas.Instrument)
def read_instrument(instrument_id: int, db: Session = Depends(get_db)):
    db_instrument = db.query(models.Instrument).filter(models.Instrument.id == instrument_id).first()
    if db_instrument is None:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return db_instrument
