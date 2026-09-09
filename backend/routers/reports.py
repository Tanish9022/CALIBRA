import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import get_db
import models
from engine.report_generator import ReportGenerator

router = APIRouter(prefix="/reports", tags=["reports"])

REPORTS_DIR = "./reports_out"
os.makedirs(REPORTS_DIR, exist_ok=True)

@router.post("/generate/{session_id}")
def generate_report(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.TestSession).filter(models.TestSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    results = db.query(models.TestResult).filter(models.TestResult.test_session_id == session_id).all()
    
    filepath = os.path.join(REPORTS_DIR, f"report_session_{session_id}.pdf")
    ReportGenerator.generate_pdf_report(session, results, filepath)
    
    return {"status": "success", "report_url": f"/reports/download/{session_id}"}

@router.get("/download/{session_id}")
def download_report(session_id: int):
    filepath = os.path.join(REPORTS_DIR, f"report_session_{session_id}.pdf")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(filepath, media_type="application/pdf", filename=f"CALIBRA_Report_{session_id}.pdf")
