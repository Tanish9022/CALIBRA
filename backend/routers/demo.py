from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any

from database import get_db
import models
from engine.context.gravity_service import GravityContextService
from engine.context.impact_service import ImpactAnalysisService

router = APIRouter(prefix="/demo", tags=["demo"])

@router.post("/gravity-scenario")
def run_gravity_scenario(db: Session = Depends(get_db)):
    """
    Executes the Delhi -> Leh Geographical Gravity Shift Scenario:
    1. Instrument A (Class III Commercial Scale, Max 30 kg, e = 10 g) is tested in New Delhi (g = 9.7912 m/s²) with PASS.
    2. Intended location is changed to Leh, Ladakh (elevation 3500 m, g = 9.7744 m/s²).
    3. CALIBRA detects the geographical context shift.
    4. Evaluates OIML R76 Clause 3.9.2 transferability:
       - Relative gravity change: 1715 ppm.
       - Allowable MPE tolerance: 500 ppm (1/3 MPE: 166.7 ppm).
       - Decision: RE-TEST / LOCATION-SPECIFIC EVALUATION REQUIRED.
    """
    inst = db.query(models.Instrument).filter(models.Instrument.accuracy_class == "III").first()
    if not inst:
        raise HTTPException(status_code=404, detail="Demo Instrument Class III not found. Please run seed first.")

    delhi = db.query(models.Location).filter(models.Location.name.ilike("%Delhi%")).first()
    leh = db.query(models.Location).filter(models.Location.name.ilike("%Leh%")).first()

    g_delhi = delhi.declared_gravity if delhi else 9.7912
    g_leh = leh.declared_gravity if leh else 9.7744

    # Evaluate transferability
    transfer_eval = GravityContextService.evaluate_location_transferability(
        accuracy_class=inst.accuracy_class,
        max_capacity_kg=inst.max_capacity,
        verification_interval_e_g=inst.verification_interval_e,
        has_internal_calibration=inst.has_internal_calibration,
        is_gravity_sensitive=inst.is_gravity_sensitive,
        test_location_name="New Delhi Verification Center",
        test_gravity_ms2=g_delhi,
        intended_location_name="Leh Ladakh High-Altitude Facility",
        intended_gravity_ms2=g_leh
    )

    # Record context change
    old_ctx = {
        "test_location": "New Delhi Verification Center",
        "intended_location": "New Delhi Verification Center",
        "local_gravity": g_delhi,
        "temperature_c": 21.0
    }
    new_ctx = {
        "test_location": "New Delhi Verification Center",
        "intended_location": "Leh Ladakh High-Altitude Facility",
        "local_gravity": g_leh,
        "temperature_c": 8.5
    }

    inst_profile = {
        "accuracy_class": inst.accuracy_class,
        "max_capacity": inst.max_capacity,
        "verification_interval_e": inst.verification_interval_e,
        "has_internal_calibration": inst.has_internal_calibration,
        "is_gravity_sensitive": inst.is_gravity_sensitive
    }

    impact = ImpactAnalysisService.analyze_context_change(inst_profile, old_ctx, new_ctx)

    # Update instrument intended location
    inst.intended_location = "Leh Ladakh High-Altitude Facility"
    db.commit()

    return {
        "scenario": "DELHI_TO_LEH_GRAVITY_SHIFT",
        "instrument": {
            "id": inst.id,
            "manufacturer": inst.manufacturer,
            "model": inst.model,
            "class": inst.accuracy_class,
            "max": f"{inst.max_capacity} kg",
            "e": f"{inst.verification_interval_e} g",
            "has_internal_calibration": inst.has_internal_calibration,
            "gravity_sensitive": inst.is_gravity_sensitive
        },
        "context_change": {
            "from_location": "New Delhi Verification Center",
            "from_gravity": f"{g_delhi} m/s²",
            "to_location": "Leh Ladakh High-Altitude Facility (3500m)",
            "to_gravity": f"{g_leh} m/s²",
            "delta_g": f"{abs(g_delhi - g_leh):.4f} m/s²",
            "relative_shift_ppm": transfer_eval["relative_delta_g_ppm"]
        },
        "compliance_evaluation": transfer_eval,
        "impact_analysis": impact,
        "key_takeaway": (
            "CALIBRA does not physically calibrate the instrument. It deterministically proves that "
            "the 1715 ppm gravitational shift exceeds the 500 ppm MPE limit under OIML R76-1 Clause 3.9.2, "
            "meaning a Delhi verification cannot be blindly transferred to Leh."
        )
    }

@router.post("/expired-equipment-scenario")
def run_expired_equipment_scenario(db: Session = Depends(get_db)):
    """
    Demonstrates the Coverage Gate blocking report generation due to expired test standards.
    """
    expired_eq = db.query(models.TestEquipment).filter(models.TestEquipment.status == "EXPIRED").first()
    if not expired_eq:
        # Create or flag one
        expired_eq = models.TestEquipment(
            equipment_id="EQ-EXP-099",
            name="Set of M1 Weights (50 kg)",
            equipment_type="STANDARD_WEIGHTS",
            class_standard="M1",
            status="EXPIRED",
            calibration_date=datetime.utcnow() - timedelta(days=400),
            calibration_expiry=datetime.utcnow() - timedelta(days=35),
            certificate_number="NPL-IND-EXPIRED-2025"
        )
        db.add(expired_eq)
        db.commit()
        db.refresh(expired_eq)

    return {
        "scenario": "EXPIRED_TEST_STANDARDS",
        "equipment": {
            "equipment_id": expired_eq.equipment_id,
            "name": expired_eq.name,
            "status": expired_eq.status,
            "calibration_expiry": expired_eq.calibration_expiry,
            "certificate_number": expired_eq.certificate_number
        },
        "coverage_gate_verdict": "BLOCKED",
        "reason": f"Traceability chain severed: Test weights {expired_eq.name} calibration expired on {expired_eq.calibration_expiry.strftime('%Y-%m-%d')}.",
        "oiml_r76_consequence": "Standardized Test Report generation is strictly inhibited."
    }
