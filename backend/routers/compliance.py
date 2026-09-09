from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

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
    
    # Extract indication from metadata (for this MVP demo)
    if not obs.metadata_json or "indication" not in obs.metadata_json:
        raise HTTPException(status_code=400, detail="Missing indication in observation metadata")
        
    indication = obs.metadata_json["indication"]
    ind_unit = obs.metadata_json.get("indication_unit", obs.raw_unit)
    
    # 1. Calculation & Normalization
    trace = CalculationEngine.process_observation(
        raw_load=obs.raw_value, 
        load_unit=obs.raw_unit, 
        raw_indication=indication, 
        ind_unit=ind_unit, 
        base_unit="g"
    )
    
    error_g = trace["calculation"]["error"]
    
    # Normalizing instrument 'e' to grams for comparison (assuming e is given in grams for demo)
    e_g = instrument.verification_interval_e
    
    # 2. Rule Evaluation
    evaluation = RuleEngine.evaluate_mpe_rule(
        accuracy_class=instrument.accuracy_class,
        load=trace["normalization"]["load"]["normalized"],
        e=e_g,
        error=error_g
    )
    
    # 3. Evidence Generation
    evidence_data = EvidenceBuilder.build_evidence(instrument, obs, trace, evaluation)
    
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
    
    # Persist Result
    status = "REVIEW" if evaluation["evaluation"].get("requires_review") else ("PASS" if evaluation["evaluation"]["passed"] else "FAIL")
    
    db_result = models.TestResult(
        test_session_id=session.id,
        test_definition_id=obs.test_definition_id,
        status=status,
        calculated_values_json=trace,
        decision_reason=evaluation.get("error", "Automated MPE check"),
        evidence_id=db_evidence.id
    )
    db.add(db_result)
    db.commit()
    
    return {
        "status": status,
        "evidence_id": db_evidence.id,
        "evidence": evidence_data
    }
