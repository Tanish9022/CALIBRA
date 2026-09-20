import os
import hashlib
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
import models
import schemas
from engine.report_generator import ReportGenerator
from engine.coverage_gate import CoverageGate
from engine.test_plan_service import TestPlanService

router = APIRouter(prefix="/reports", tags=["reports"])

REPORTS_DIR = "./reports_out"
os.makedirs(REPORTS_DIR, exist_ok=True)

@router.get("/", response_model=List[schemas.Report])
def list_reports(db: Session = Depends(get_db)):
    """
    Lists all issued standardized compliance test reports.
    """
    return db.query(models.Report).order_by(models.Report.id.desc()).all()

@router.get("/{report_id}", response_model=schemas.Report)
def get_report_by_id(report_id: int, db: Session = Depends(get_db)):
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.get("/{report_id}/verify")
def verify_report_integrity(report_id: int, db: Session = Depends(get_db)):
    """
    Cryptographically verifies the stored SHA-256 checksum against the physical PDF file.
    Ensures zero silent modification or post-generation tampering.
    """
    report = db.query(models.Report).filter(models.Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if not os.path.exists(report.pdf_path):
        return {
            "verified": False,
            "report_id": report.id,
            "report_number": report.report_number,
            "status": "FILE_NOT_FOUND",
            "error": f"Physical report file {report.pdf_path} could not be located on storage."
        }

    with open(report.pdf_path, "rb") as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()

    is_intact = (actual_hash == report.checksum_sha256)

    return {
        "verified": is_intact,
        "report_id": report.id,
        "report_number": report.report_number,
        "stored_checksum": report.checksum_sha256,
        "calculated_file_checksum": actual_hash,
        "integrity_status": "AUTHENTIC_AND_UNMODIFIED" if is_intact else "TAMPERED_OR_MODIFIED",
        "generated_at": report.generated_at,
        "ruleset_version": report.ruleset_version
    }

@router.post("/generate/{session_id}")
def generate_report(
    session_id: int,
    force: bool = Query(False, description="Bypass coverage gate for preview draft"),
    db: Session = Depends(get_db)
):
    session = db.query(models.TestSession).filter(models.TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    results = db.query(models.TestResult).filter(models.TestResult.test_session_id == session_id).all()
    observations = db.query(models.Observation).filter(models.Observation.test_session_id == session_id).all()
    equipment = db.query(models.TestEquipment).all()
    context = db.query(models.ComplianceContext).filter(models.ComplianceContext.test_session_id == session_id).first()
    if not context:
        context = db.query(models.ComplianceContext).filter(models.ComplianceContext.instrument_id == session.instrument_id).first()

    inst = session.instrument
    test_plan = TestPlanService.compile_test_plan(
        accuracy_class=inst.accuracy_class if inst else "III",
        max_capacity_kg=inst.max_capacity if inst else 30.0,
        verification_interval_e_g=inst.verification_interval_e if inst else 10.0,
        verification_type=session.verification_type or "INITIAL"
    )

    # Check Coverage Gate
    gate_eval = CoverageGate.evaluate_session_coverage(
        test_plan=test_plan,
        results=results,
        observations=observations,
        equipment_list=equipment
    )

    if not gate_eval["is_ready_for_report"] and not force:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "COVERAGE_GATE_BLOCKED",
                "message": "Cannot finalize official report: Mandatory OIML R76 test coverage incomplete or blocked.",
                "gate_status": gate_eval["status"],
                "blockers": gate_eval["blockers"],
                "coverage_pct": gate_eval["coverage_percentage"],
                "hint": "Resolve blockers or pass force=true for draft preview."
            }
        )

    # Determine revision number if re-issuing
    existing_reports = db.query(models.Report).filter(models.Report.session_id == session_id).all()
    rev_number = len(existing_reports) + 1
    report_num = f"CALIBRA-R76-{session.id:04d}-REV{rev_number}"

    filename = f"CALIBRA_Report_Session_{session_id}_Rev{rev_number}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)
    
    ReportGenerator.generate_pdf_report(
        session=session,
        results=results,
        filepath=filepath,
        context=context,
        equipment_list=equipment
    )

    # Compute SHA-256 hash
    with open(filepath, "rb") as f:
        checksum = hashlib.sha256(f.read()).hexdigest()

    # Save report record
    db_report = models.Report(
        session_id=session.id,
        report_number=report_num,
        revision=rev_number,
        ruleset_version=session.ruleset.version if session.ruleset else "OIML R76-1:2006",
        calculation_version="v1.0-decimal34",
        status="FINAL" if gate_eval["is_ready_for_report"] else "DRAFT",
        checksum_sha256=checksum,
        generated_by=session.started_by or "Technician",
        pdf_path=filepath,
        summary_json={
            "coverage_percentage": gate_eval["coverage_percentage"],
            "total_tests": gate_eval["total_tests"],
            "passed_tests": sum(1 for r in results if r.status == "PASS"),
            "failed_tests": sum(1 for r in results if r.status == "FAIL"),
            "is_transferable": getattr(context, "is_transferable", True) if context else True
        }
    )
    db.add(db_report)
    session.status = "COMPLETED"
    session.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(db_report)

    return {
        "status": "success",
        "report_id": db_report.id,
        "report_number": db_report.report_number,
        "checksum_sha256": checksum,
        "report_url": f"/reports/download/{session_id}?report_id={db_report.id}",
        "coverage": gate_eval
    }

@router.get("/download/{session_id}")
def download_report(session_id: int, report_id: Optional[int] = None, db: Session = Depends(get_db)):
    if report_id:
        report = db.query(models.Report).filter(models.Report.id == report_id).first()
        if report and os.path.exists(report.pdf_path):
            return FileResponse(report.pdf_path, media_type="application/pdf", filename=os.path.basename(report.pdf_path))

    # Fallback to newest for session
    newest = db.query(models.Report).filter(models.Report.session_id == session_id).order_by(models.Report.id.desc()).first()
    if newest and os.path.exists(newest.pdf_path):
        return FileResponse(newest.pdf_path, media_type="application/pdf", filename=os.path.basename(newest.pdf_path))

    # Check disk for old format
    old_path = os.path.join(REPORTS_DIR, f"report_session_{session_id}.pdf")
    if os.path.exists(old_path):
        return FileResponse(old_path, media_type="application/pdf", filename=f"CALIBRA_Report_{session_id}.pdf")

    raise HTTPException(status_code=404, detail="Report file not found")
