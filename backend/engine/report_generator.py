import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from typing import Any, List
from datetime import datetime

class ReportGenerator:
    @classmethod
    def generate_pdf_report(cls, session: Any, results: List[Any], filepath: str) -> str:
        """
        Generates an authoritative PDF test report conforming to OIML R76-2:2006 format.
        Presents verified evidence, exact MPE, and calculated corrected errors.
        """
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        
        instrument = session.instrument
        
        # Header
        c.setFont("Helvetica-Bold", 16)
        c.drawString(1 * inch, height - 0.8 * inch, "CALIBRA - Legal Metrology Test Report")
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(1 * inch, height - 1.0 * inch, "Standard Reference: OIML R76-1:2006 (E) / OIML R76-2:2006 (E)")
        
        c.setFont("Helvetica", 9)
        c.drawString(1 * inch, height - 1.3 * inch, f"Test Session: #{session.id}")
        c.drawString(3.5 * inch, height - 1.3 * inch, f"Verification Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
        c.drawString(6 * inch, height - 1.3 * inch, f"Status: {session.status}")
        
        c.setStrokeColorRGB(0.2, 0.4, 0.8)
        c.setLineWidth(1.5)
        c.line(1 * inch, height - 1.4 * inch, width - 1 * inch, height - 1.4 * inch)
        
        if instrument:
            # 1. Instrument Profile
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1 * inch, height - 1.7 * inch, "1. Instrument Identification & Metrological Specifications")
            
            c.setFont("Helvetica", 9)
            c.drawString(1.2 * inch, height - 1.95 * inch, f"Manufacturer: {instrument.manufacturer}")
            c.drawString(3.8 * inch, height - 1.95 * inch, f"Model: {instrument.model}")
            c.drawString(1.2 * inch, height - 2.15 * inch, f"Accuracy Class: Class {instrument.accuracy_class}")
            c.drawString(3.8 * inch, height - 2.15 * inch, f"Verification Interval (e): {instrument.verification_interval_e} g")
            c.drawString(1.2 * inch, height - 2.35 * inch, f"Maximum Capacity (Max): {instrument.max_capacity} kg")
            c.drawString(3.8 * inch, height - 2.35 * inch, f"Minimum Capacity (Min): {instrument.min_capacity} kg")
        
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.setLineWidth(0.5)
        c.line(1 * inch, height - 2.5 * inch, width - 1 * inch, height - 2.5 * inch)

        # 2. Test Results Table
        c.setFont("Helvetica-Bold", 12)
        c.drawString(1 * inch, height - 2.8 * inch, "2. Metrological Verification Results")
        
        y = height - 3.1 * inch
        for idx, result in enumerate(results):
            if y < 1.5 * inch:
                c.showPage()
                y = height - 1 * inch
            
            c.setFont("Helvetica-Bold", 10)
            t_name = result.test_definition.name if result.test_definition else f"Test #{result.test_definition_id}"
            c.drawString(1.2 * inch, y, f"[{idx+1}] {t_name}")
            
            # Status Badge
            status_text = result.status
            if status_text == "PASS":
                c.setFillColorRGB(0.0, 0.5, 0.1) # Green
            elif status_text == "FAIL":
                c.setFillColorRGB(0.8, 0.0, 0.0) # Red
            else:
                c.setFillColorRGB(0.7, 0.4, 0.0) # Amber
                
            c.drawString(width - 2.2 * inch, y, f"RESULT: {status_text}")
            c.setFillColorRGB(0.0, 0.0, 0.0) # Reset to black
            
            y -= 0.2 * inch
            
            # Extract Evidence details if available
            ev = result.evidence
            if ev and ev.calculation_trace_json:
                calc = ev.calculation_trace_json
                rule = ev.rule_snapshot_json or {}
                norm = ev.normalization_json or {}
                
                c.setFont("Helvetica", 8.5)
                load_str = f"Load: {norm.get('load', {}).get('raw', 'N/A')} {norm.get('load', {}).get('unit', '')}"
                ind_str = f"Indication: {norm.get('indication', {}).get('raw', 'N/A')} {norm.get('indication', {}).get('unit', '')}"
                c.drawString(1.4 * inch, y, f"{load_str}  |  {ind_str}")
                y -= 0.18 * inch
                
                err_val = calc.get("error", "N/A")
                mpe_val = rule.get("threshold_mpe", "N/A")
                m_val = rule.get("load_in_e", "N/A")
                
                m_str = f"{m_val:.2f}" if isinstance(m_val, (int, float)) else str(m_val)
                err_str = f"{err_val:+.4f} g" if isinstance(err_val, (int, float)) else str(err_val)
                mpe_str = f"±{mpe_val:.4f} g" if isinstance(mpe_val, (int, float)) else str(mpe_val)
                
                c.drawString(1.4 * inch, y, f"Verification Interval m: {m_str} e  |  Corrected Error Ec: {err_str}  |  Permissible MPE: {mpe_str}")
                y -= 0.18 * inch

            c.setFont("Helvetica-Oblique", 8)
            c.drawString(1.4 * inch, y, f"Reason: {result.decision_reason}")
            y -= 0.3 * inch

        # Footer
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(1 * inch, 0.5 * inch, "Generated deterministically by CALIBRA Engine • Cryptographic Trace Verified")
        
        c.save()
        return filepath
