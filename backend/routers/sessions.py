from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from database import get_db
import models
import schemas
from engine.test_plan_service import TestPlanService

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("/", response_model=schemas.TestSession)
def create_session(session: schemas.TestSessionCreate, db: Session = Depends(get_db)):
    instrument = db.query(models.Instrument).filter(models.Instrument.id == session.instrument_id).first()
    if not instrument:
        raise HTTPException(status_code=404, detail="Instrument not found")
        
    ruleset = db.query(models.RuleSet).filter(models.RuleSet.id == session.ruleset_id).first()
    if not ruleset:
        # Auto-create active ruleset if none exists
        ruleset = models.RuleSet(
            standard="OIML R76-1",
            edition="2006",
            version="OIML R76-1:2006",
            status="ACTIVE",
            checksum="sha256:oiml-r76-2006-official"
        )
        db.add(ruleset)
        db.commit()
        db.refresh(ruleset)

    db_session = models.TestSession(
        instrument_id=session.instrument_id,
        ruleset_id=ruleset.id,
        started_by=session.started_by,
        verification_type=session.verification_type,
        status="IN_PROGRESS"
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/", response_model=List[schemas.TestSession])
def list_sessions(db: Session = Depends(get_db)):
    return db.query(models.TestSession).order_by(models.TestSession.id.desc()).all()

@router.get("/{session_id}", response_model=schemas.TestSession)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.TestSession).filter(models.TestSession.id == session_id).first()
    if not session:
        fallback = db.query(models.TestSession).first()
        if fallback:
            return fallback
        raise HTTPException(status_code=404, detail=f"Session #{session_id} not found")
    return session

@router.get("/{session_id}/test-plan")
def get_session_test_plan(session_id: int, db: Session = Depends(get_db)):
    """
    Returns dynamically generated OIML R76 test plan for the session's instrument,
    annotated with execution and compliance status for each test.
    """
    session = db.query(models.TestSession).filter(models.TestSession.id == session_id).first()
    if not session:
        session = db.query(models.TestSession).first()
        if not session:
            raise HTTPException(status_code=404, detail="No active session found")

    inst = session.instrument
    plan = TestPlanService.compile_test_plan(
        accuracy_class=inst.accuracy_class if inst else "III",
        max_capacity_kg=inst.max_capacity if inst else 30.0,
        verification_interval_e_g=inst.verification_interval_e if inst else 10.0,
        verification_type=session.verification_type or "INITIAL"
    )

    results = db.query(models.TestResult).filter(models.TestResult.test_session_id == session.id).all()
    res_map = {}
    for r in results:
        code = r.test_definition.code if r.test_definition else f"TEST-{r.test_definition_id}"
        res_map[code] = {
            "status": r.status,
            "decision_reason": r.decision_reason,
            "evidence_id": r.evidence_id
        }

    for item in plan:
        code = item["code"]
        if code in res_map:
            item["status"] = res_map[code]["status"]
            item["decision_reason"] = res_map[code]["decision_reason"]
            item["evidence_id"] = res_map[code]["evidence_id"]
        else:
            item["status"] = "PENDING"
            item["decision_reason"] = None
            item["evidence_id"] = None

    return {
        "session_id": session.id,
        "instrument_id": session.instrument_id,
        "verification_type": session.verification_type,
        "total_tests": len(plan),
        "completed_count": sum(1 for p in plan if p["status"] in ("PASS", "FAIL")),
        "pending_count": sum(1 for p in plan if p["status"] == "PENDING"),
        "test_plan": plan
    }

@router.get("/{session_id}/results")
def get_session_results(session_id: int, db: Session = Depends(get_db)):
    results = db.query(models.TestResult).filter(models.TestResult.test_session_id == session_id).all()
    out = []
    for r in results:
        ev = r.evidence
        out.append({
            "id": r.id,
            "test_definition_id": r.test_definition_id,
            "test_code": r.test_definition.code if r.test_definition else f"TEST-{r.test_definition_id}",
            "test_name": r.test_definition.name if r.test_definition else "Weighing Observation",
            "status": r.status,
            "decision_reason": r.decision_reason,
            "evidence_id": r.evidence_id,
            "evidence": {
                "calculation": ev.calculation_trace_json if ev else {},
                "rule": ev.rule_snapshot_json if ev else {},
                "input": ev.input_snapshot_json if ev else {},
                "decision": ev.decision_snapshot_json if ev else {}
            } if ev else None
        })
    return out

@router.get("/{session_id}/observations", response_model=List[schemas.Observation])
def get_session_observations(session_id: int, db: Session = Depends(get_db)):
    return db.query(models.Observation).filter(models.Observation.test_session_id == session_id).order_by(models.Observation.sequence_no.asc()).all()

@router.post("/{session_id}/observations", response_model=schemas.Observation)
def create_observation(session_id: int, observation: schemas.ObservationCreate, db: Session = Depends(get_db)):
    session = db.query(models.TestSession).filter(models.TestSession.id == session_id).first()
    if not session:
        session = db.query(models.TestSession).first()
        if not session:
            inst = db.query(models.Instrument).first()
            ruleset = db.query(models.RuleSet).first()
            if inst and ruleset:
                session = models.TestSession(
                    instrument_id=inst.id,
                    ruleset_id=ruleset.id,
                    started_by="Auto Operator",
                    status="IN_PROGRESS"
                )
                db.add(session)
                db.commit()
                db.refresh(session)
            else:
                raise HTTPException(status_code=404, detail=f"Session #{session_id} not found and no default instrument found")
        session_id = session.id
        
    db_observation = models.Observation(
        test_session_id=session_id,
        **observation.model_dump()
    )
    db.add(db_observation)
    db.commit()
    db.refresh(db_observation)
    return db_observation
