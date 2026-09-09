from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict, List

from database import get_db
import models
from engine.calculation import CalculationEngine
from engine.rules import RuleEngine
from engine.evidence import EvidenceBuilder

router = APIRouter(prefix="/compliance", tags=["compliance"])

@router.post("/evaluate_weighing/{observation_id}")
def evaluate_weighing_observation(observation_id: int, db: Session = Depends(get_db)):
    obs = db.query(models.Observation).filter(models.Observation.id == observation_id).first()
    if not obs:
        raise HTTPException(status_code=404, detail="Observation not found")
        
    session = obs.session
    instrument = session.instrument
    
    # Extract metadata fields
    meta = obs.metadata_json or {}
    if "indication" not in meta:
        raise HTTPException(status_code=400, detail="Missing 'indication' in observation metadata.")
        
    indication = meta["indication"]
    ind_unit = meta.get("indication_unit", obs.raw_unit)
    delta_l = meta.get("delta_l")
    delta_l_unit = meta.get("delta_l_unit", obs.raw_unit) if delta_l is not None else None
    e0 = meta.get("e0")
    e0_unit = meta.get("e0_unit", obs.raw_unit) if e0 is not None else None
    verification_type = meta.get("verification_type", "INITIAL")

    # Instrument parameter unit resolution
    config = instrument.configuration_json or {}
    e_unit = config.get("e_unit", "g")
    max_unit = config.get("max_unit", "kg")
    min_unit = config.get("min_unit", "kg")

    try:
        # 1. Calculation & Unit Normalization (Exact Decimal)
        trace = CalculationEngine.process_observation(
            raw_load=obs.raw_value,
            load_unit=obs.raw_unit,
            raw_indication=indication,
            ind_unit=ind_unit,
            raw_e=instrument.verification_interval_e,
            e_unit=e_unit,
            raw_delta_l=delta_l,
            delta_l_unit=delta_l_unit,
            raw_e0=e0,
            e0_unit=e0_unit,
            base_unit="g"
        )
        
        load_g = trace["_internal_decimals"]["norm_load"]
        e_g = trace["_internal_decimals"]["norm_e"]
        error_g = trace["_internal_decimals"]["corrected_error"]
        
        # Pop _internal_decimals so trace is purely JSON serializable
        clean_trace = {k: v for k, v in trace.items() if k != "_internal_decimals"}
        
        max_g = CalculationEngine.normalize(instrument.max_capacity, max_unit, "g")
        min_g = CalculationEngine.normalize(instrument.min_capacity, min_unit, "g") if instrument.min_capacity is not None else None

        # 2. Rule Evaluation
        evaluation = RuleEngine.evaluate_mpe_rule(
            accuracy_class=instrument.accuracy_class,
            load_norm=load_g,
            e_norm=e_g,
            error_norm=error_g,
            max_norm=max_g,
            min_norm=min_g,
            verification_type=verification_type
        )
    except Exception as ex:
        evaluation = {
            "applicable_rule": "OIML R76-1:2006",
            "status": "INVALID",
            "error_code": "CALCULATION_OR_VALIDATION_ERROR",
            "error": str(ex),
            "evaluation": {"passed": False, "requires_review": True, "error_code": "CALCULATION_OR_VALIDATION_ERROR"}
        }
        trace = {"calculation": {"error": 0.0, "unit": "g"}, "normalization": {}}

    # 3. Evidence Generation
    evidence_data = EvidenceBuilder.build_evidence(
        instrument=instrument,
        observation=obs,
        trace=clean_trace,
        evaluation=evaluation,
        verification_type=verification_type
    )

    # Persist Evidence
    db_evidence = models.Evidence(
        input_snapshot_json=evidence_data["raw_input"],
        normalization_json=evidence_data["normalization"],
        calculation_trace_json=evidence_data["calculation"],
        rule_snapshot_json=evidence_data["rule"],
        decision_snapshot_json=evidence_data["decision"]
    )
    db.add(db_evidence)
    db.flush()

    # Determine status
    if evaluation.get("status") == "INVALID":
        status = "INVALID"
        reason = evaluation.get("error", "Metrological validity check failed")
    elif evaluation.get("evaluation", {}).get("requires_review"):
        status = "REVIEW"
        reason = evaluation.get("error", "Configuration review required")
    else:
        status = "PASS" if evaluation.get("evaluation", {}).get("passed") else "FAIL"
        reason = evidence_data["decision"]["explanation"]

    db_result = models.TestResult(
        test_session_id=session.id,
        test_definition_id=obs.test_definition_id,
        status=status,
        calculated_values_json=clean_trace,
        decision_reason=reason,
        evidence_id=db_evidence.id
    )
    db.add(db_result)
    db.commit()

    return {
        "status": status,
        "evidence_id": db_evidence.id,
        "evidence": evidence_data
    }

@router.post("/evaluate_repeatability/{session_id}")
def evaluate_repeatability(session_id: int, db: Session = Depends(get_db)):
    """
    OIML R76-1:2006 Clause 3.6.1 Repeatability evaluation endpoint.
    """
    session = db.query(models.TestSession).filter(models.TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Query all repeatability observations for this session
    # (Assuming test definition code RP-01)
    repeatability_def = db.query(models.TestDefinition).filter(models.TestDefinition.code == "RP-01").first()
    if not repeatability_def:
        return {
            "status": "NOT_IMPLEMENTED",
            "reason": "Test definition RP-01 (Repeatability) not yet provisioned in test catalog."
        }
        
    obs_list = db.query(models.Observation).filter(
        models.Observation.test_session_id == session_id,
        models.Observation.test_definition_id == repeatability_def.id
    ).all()

    if len(obs_list) < 3:
        return {
            "status": "INVALID",
            "error_code": "INSUFFICIENT_OBSERVATIONS",
            "reason": f"OIML R76-1 requires at least 3 repeat weighings. Found {len(obs_list)}."
        }

    config = session.instrument.configuration_json or {}
    e_unit = config.get("e_unit", "g")
    e_g = CalculationEngine.normalize(session.instrument.verification_interval_e, e_unit, "g")
    load_g = CalculationEngine.normalize(obs_list[0].raw_value, obs_list[0].raw_unit, "g")
    
    inds_g = [
        CalculationEngine.normalize(o.metadata_json.get("indication", o.raw_value), o.metadata_json.get("indication_unit", o.raw_unit), "g")
        for o in obs_list
    ]

    res = RuleEngine.evaluate_repeatability_rule(
        accuracy_class=session.instrument.accuracy_class,
        load_in_g=load_g,
        e_in_g=e_g,
        observations_in_g=inds_g,
        verification_type="INITIAL"
    )
    return res
