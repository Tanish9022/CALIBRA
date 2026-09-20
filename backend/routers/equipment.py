from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
import models
import schemas

router = APIRouter(prefix="/equipment", tags=["equipment"])

@router.get("/", response_model=List[schemas.TestEquipment])
def list_equipment(db: Session = Depends(get_db)):
    """
    Returns all registered laboratory test standards and equipment.
    """
    return db.query(models.TestEquipment).all()

@router.post("/", response_model=schemas.TestEquipment)
def create_equipment(eq: schemas.TestEquipmentCreate, db: Session = Depends(get_db)):
    """
    Registers new standard weights or calibration equipment.
    """
    existing = db.query(models.TestEquipment).filter(models.TestEquipment.equipment_id == eq.equipment_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Equipment with ID {eq.equipment_id} already exists")

    db_eq = models.TestEquipment(**eq.model_dump())
    db.add(db_eq)
    db.commit()
    db.refresh(db_eq)
    return db_eq

@router.get("/validate/{equipment_id}")
def validate_equipment_calibration(equipment_id: str, db: Session = Depends(get_db)):
    """
    Validates calibration expiration for a test equipment.
    """
    eq = db.query(models.TestEquipment).filter(models.TestEquipment.equipment_id == equipment_id).first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")

    is_expired = False
    if eq.calibration_expiry and eq.calibration_expiry < datetime.utcnow():
        is_expired = True

    status = "EXPIRED" if is_expired else eq.status

    return {
        "equipment_id": eq.equipment_id,
        "name": eq.name,
        "class_standard": eq.class_standard,
        "status": status,
        "is_valid": status == "VALID",
        "calibration_expiry": eq.calibration_expiry,
        "certificate_number": eq.certificate_number,
        "traceability_reference": eq.traceability_reference
    }
