from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional

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
def read_instruments(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    accuracy_class: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Instrument)
    if search:
        s = f"%{search}%"
        query = query.filter(
            or_(
                models.Instrument.manufacturer.ilike(s),
                models.Instrument.model.ilike(s),
                models.Instrument.serial_number.ilike(s),
                models.Instrument.test_location.ilike(s),
                models.Instrument.intended_location.ilike(s)
            )
        )
    if accuracy_class:
        query = query.filter(models.Instrument.accuracy_class == accuracy_class)

    instruments = query.order_by(models.Instrument.id.desc()).offset(skip).limit(limit).all()
    return instruments

@router.get("/{instrument_id}", response_model=schemas.Instrument)
def read_instrument(instrument_id: int, db: Session = Depends(get_db)):
    db_instrument = db.query(models.Instrument).filter(models.Instrument.id == instrument_id).first()
    if db_instrument is None:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return db_instrument

@router.put("/{instrument_id}", response_model=schemas.Instrument)
def update_instrument(instrument_id: int, update_data: schemas.InstrumentCreate, db: Session = Depends(get_db)):
    inst = db.query(models.Instrument).filter(models.Instrument.id == instrument_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")

    for key, val in update_data.model_dump().items():
        setattr(inst, key, val)

    db.commit()
    db.refresh(inst)
    return inst
