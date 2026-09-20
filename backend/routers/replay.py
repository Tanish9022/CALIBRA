from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from database import get_db
import models
from engine.replay_service import ComplianceReplayService

router = APIRouter(prefix="/replay", tags=["replay"])

@router.get("/session/{session_id}")
def get_session_replay(session_id: int, db: Session = Depends(get_db)):
    """
    Reconstructs the full immutable metrological replay chain for a test session.
    """
    session = db.query(models.TestSession).filter(models.TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Test session not found")

    results = db.query(models.TestResult).filter(models.TestResult.test_session_id == session_id).all()
    context = db.query(models.ComplianceContext).filter(models.ComplianceContext.test_session_id == session_id).first()
    if not context:
        context = db.query(models.ComplianceContext).filter(models.ComplianceContext.instrument_id == session.instrument_id).first()

    replay_data = ComplianceReplayService.reconstruct_session_replay(
        session=session,
        results=results,
        context=context,
        active_ruleset_version="OIML R76-1:2006"
    )

    return replay_data

@router.get("/report/{report_id}")
def get_report_replay(report_id: int, db: Session = Depends(get_db)):
    """
    Reconstructs the full compliance replay from an issued report.
    """
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    session = report.session
    if not session:
        raise HTTPException(status_code=404, detail="Associated session not found")

    results = db.query(models.TestResult).filter(models.TestResult.test_session_id == session.id).all()
    context = db.query(models.ComplianceContext).filter(models.ComplianceContext.test_session_id == session.id).first()

    replay_data = ComplianceReplayService.reconstruct_session_replay(
        session=session,
        results=results,
        context=context,
        active_ruleset_version="OIML R76-1:2006"
    )

    replay_data["report_metadata"] = {
        "report_number": report.report_number,
        "revision": report.revision,
        "status": report.status,
        "checksum_sha256": report.checksum_sha256,
        "generated_by": report.generated_by,
        "generated_at": report.generated_at
    }

    return replay_data
