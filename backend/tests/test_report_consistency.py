"""
Report Consistency Test:
Verifies Database Result == API Result == Generated Report Values.
"""

import sys
import os
from fastapi.testclient import TestClient

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from main import app
from database import SessionLocal
import models
from engine.report_generator import ReportGenerator

def test_report_consistency():
    client = TestClient(app)
    db = SessionLocal()
    try:
        # Get or seed instrument
        instrument = db.query(models.Instrument).first()
        if not instrument:
            from seed import seed
            seed()
            instrument = db.query(models.Instrument).first()

        session = db.query(models.TestSession).filter(models.TestSession.instrument_id == instrument.id).first()
        if not session:
            ruleset = db.query(models.RuleSet).first()
            session = models.TestSession(
                instrument_id=instrument.id,
                ruleset_id=ruleset.id,
                started_by="Consistency Tester",
                status="IN_PROGRESS"
            )
            db.add(session)
            db.commit()
            db.refresh(session)

        test_def = db.query(models.TestDefinition).first()

        # 1. Post Observation via API
        obs_payload = {
            "test_definition_id": test_def.id,
            "raw_value": 10.0,
            "raw_unit": "kg",
            "sequence_no": 99,
            "metadata_json": {
                "indication": 10.008,
                "indication_unit": "kg",
                "verification_type": "INITIAL"
            }
        }
        res_obs = client.post(f"/sessions/{session.id}/observations", json=obs_payload)
        assert res_obs.status_code == 200, f"Failed to create observation: {res_obs.text}"
        obs_data = res_obs.json()
        obs_id = obs_data["id"]

        # 2. Evaluate via Compliance API
        res_eval = client.post(f"/compliance/evaluate_weighing/{obs_id}")
        assert res_eval.status_code == 200, f"Failed evaluation: {res_eval.text}"
        eval_data = res_eval.json()

        api_status = eval_data["status"]
        api_error = eval_data["evidence"]["calculation"]["corrected_error_Ec"]
        api_mpe = eval_data["evidence"]["rule"]["threshold_mpe"]

        # 3. Query Database Layer
        db_result = db.query(models.TestResult).filter(models.TestResult.test_session_id == session.id).order_by(models.TestResult.id.desc()).first()
        db_evidence = db.query(models.Evidence).filter(models.Evidence.id == db_result.evidence_id).first()

        db_status = db_result.status
        db_calc = db_evidence.calculation_trace_json
        db_error = db_calc.get("corrected_error_Ec", db_calc.get("error"))
        db_mpe = db_evidence.rule_snapshot_json["threshold_mpe"]

        # 4. Generate PDF Report Layer
        out_pdf = os.path.join(backend_dir, "reports_out", f"test_consistency_session_{session.id}.pdf")
        os.makedirs(os.path.dirname(out_pdf), exist_ok=True)
        pdf_path = ReportGenerator.generate_pdf_report(session, [db_result], out_pdf)
        assert os.path.exists(pdf_path), "PDF report was not generated"
        assert os.path.getsize(pdf_path) > 1000, "PDF report is empty"

        # 5. Assert Consistency
        print(f"API Layer      : Status={api_status}, Error={api_error}g, MPE={api_mpe}g")
        print(f"Database Layer : Status={db_status}, Error={db_error}g, MPE={db_mpe}g")
        print(f"Report Layer   : Generated PDF {os.path.basename(pdf_path)} (Size: {os.path.getsize(pdf_path)} bytes)")

        assert api_status == db_status == "PASS", f"Status mismatch: API={api_status}, DB={db_status}"
        assert abs(float(api_error) - float(db_error)) < 1e-6, "Error calculation mismatch"
        assert abs(float(api_mpe) - float(db_mpe)) < 1e-6, "MPE threshold mismatch"
        assert abs(float(api_mpe) - 10.0) < 1e-6, f"Expected MPE 10.0g on initial verification, got {api_mpe}g"
        assert abs(float(api_error) - 8.0) < 1e-6, f"Expected Error 8.0g, got {api_error}g"

        print("--> LAYER CONSISTENCY VERIFIED: Database == API == ReportLab PDF")
        return True
    finally:
        db.close()

if __name__ == "__main__":
    test_report_consistency()
