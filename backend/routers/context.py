from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from database import get_db
import models
import schemas
from engine.context.gravity_service import GravityContextService
from engine.context.impact_service import ImpactAnalysisService

router = APIRouter(prefix="/compliance-context", tags=["compliance-context"])

class SomiglianaRequest(BaseModel):
    latitude_deg: float
    elevation_m: Optional[float] = 0.0

class TransferabilityRequest(BaseModel):
    accuracy_class: str = "III"
    max_capacity_kg: float = 30.0
    verification_interval_e_g: float = 10.0
    has_internal_calibration: bool = False
    is_gravity_sensitive: bool = True
    test_location_name: str = "New Delhi Laboratory"
    test_gravity_ms2: float = 9.7912
    intended_location_name: str = "Leh High-Altitude Facility"
    intended_gravity_ms2: float = 9.7744

class ImpactAnalysisRequest(BaseModel):
    instrument_id: int
    old_context: Dict[str, Any]
    new_context: Dict[str, Any]

@router.get("/locations", response_model=List[schemas.Location])
def get_reference_locations(db: Session = Depends(get_db)):
    """
    Returns reference metrological testing locations (Delhi, Leh, Mumbai, Zurich, Singapore, etc.)
    """
    return db.query(models.Location).all()

@router.post("/estimate-gravity")
def estimate_gravity(req: SomiglianaRequest):
    """
    Estimates theoretical gravitational acceleration using the Somigliana 1980 / WGS84 formula
    with free-air elevation reduction.
    """
    try:
        return GravityContextService.estimate_gravity_somigliana(req.latitude_deg, req.elevation_m or 0.0)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.post("/evaluate-transferability")
def evaluate_transferability(req: TransferabilityRequest):
    """
    Evaluates OIML R76-1:2006 Clause 3.9.2 location transferability.
    Determines whether a test performed at test_location is legally valid at intended_location.
    """
    try:
        return GravityContextService.evaluate_location_transferability(
            accuracy_class=req.accuracy_class,
            max_capacity_kg=req.max_capacity_kg,
            verification_interval_e_g=req.verification_interval_e_g,
            has_internal_calibration=req.has_internal_calibration,
            is_gravity_sensitive=req.is_gravity_sensitive,
            test_location_name=req.test_location_name,
            test_gravity_ms2=req.test_gravity_ms2,
            intended_location_name=req.intended_location_name,
            intended_gravity_ms2=req.intended_gravity_ms2
        )
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))

@router.post("/impact-analysis")
def analyze_impact(req: ImpactAnalysisRequest, db: Session = Depends(get_db)):
    """
    Evaluates the metrological impact of an environmental or location change on an instrument.
    """
    inst = db.query(models.Instrument).filter(models.Instrument.id == req.instrument_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")

    profile = {
        "accuracy_class": inst.accuracy_class,
        "max_capacity": inst.max_capacity,
        "verification_interval_e": inst.verification_interval_e,
        "has_internal_calibration": inst.has_internal_calibration,
        "is_gravity_sensitive": inst.is_gravity_sensitive
    }

    res = ImpactAnalysisService.analyze_context_change(profile, req.old_context, req.new_context)
    return res

@router.post("/", response_model=schemas.ComplianceContext)
def create_or_update_context(ctx: schemas.ComplianceContextCreate, db: Session = Depends(get_db)):
    """
    Saves or updates compliance context for an instrument/session.
    """
    # Evaluate transferability
    inst = None
    if ctx.instrument_id:
        inst = db.query(models.Instrument).filter(models.Instrument.id == ctx.instrument_id).first()
    
    acc_class = inst.accuracy_class if inst else "III"
    max_cap = inst.max_capacity if inst else 30.0
    e_val = inst.verification_interval_e if inst else 10.0
    has_cal = inst.has_internal_calibration if inst else False
    is_grav = inst.is_gravity_sensitive if inst else True

    # Check test location vs intended location
    test_loc = db.query(models.Location).filter(models.Location.name == ctx.test_location).first()
    int_loc = db.query(models.Location).filter(models.Location.name == ctx.intended_location).first()

    g_test = test_loc.declared_gravity if test_loc else ctx.local_gravity
    g_int = int_loc.declared_gravity if int_loc else ctx.local_gravity

    trans = GravityContextService.evaluate_location_transferability(
        accuracy_class=acc_class,
        max_capacity_kg=max_cap,
        verification_interval_e_g=e_val,
        has_internal_calibration=has_cal,
        is_gravity_sensitive=is_grav,
        test_location_name=ctx.test_location,
        test_gravity_ms2=g_test,
        intended_location_name=ctx.intended_location,
        intended_gravity_ms2=g_int
    )

    db_ctx = models.ComplianceContext(
        instrument_id=ctx.instrument_id,
        test_session_id=ctx.test_session_id,
        test_location=ctx.test_location,
        intended_location=ctx.intended_location,
        latitude=ctx.latitude,
        longitude=ctx.longitude,
        elevation=ctx.elevation,
        local_gravity=ctx.local_gravity,
        gravity_source=ctx.gravity_source,
        temperature_c=ctx.temperature_c,
        humidity_pct=ctx.humidity_pct,
        equipment_calibration_status=ctx.equipment_calibration_status,
        is_transferable=trans["is_transferable"],
        transferability_status=trans["decision"],
        transferability_reason=trans["reason"],
        rule_set_version=ctx.rule_set_version
    )
    db.add(db_ctx)
    db.commit()
    db.refresh(db_ctx)
    return db_ctx
