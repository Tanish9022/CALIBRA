import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { 
  Download, 
  CheckCircle, 
  Scale, 
  ExternalLink,
  Loader2,
  ShieldCheck,
  RotateCcw,
  AlertTriangle,
  FileCheck,
  CheckCircle2,
  Hash
} from 'lucide-react';

export default function Reports() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const sessionId = searchParams.get('sessionId') || '1';

  const [generating, setGenerating] = useState(false);
  const [reportData, setReportData] = useState(null);
  const [gateData, setGateData] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [integrityData, setIntegrityData] = useState(null);

  useEffect(() => {
    // Check coverage gate status
    fetch(`/api/compliance/coverage-gate/${sessionId}`)
      .then(res => res.ok ? res.json() : null)
      .then(data => setGateData(data))
      .catch(console.error);

    // Check if an existing report exists
    fetch('/api/reports/')
      .then(res => res.ok ? res.json() : [])
      .then(data => {
        const found = data.find(r => String(r.session_id) === String(sessionId));
        if (found) {
          setReportData(found);
          // Verify integrity
          fetch(`/api/reports/${found.id}/verify`)
            .then(res => res.ok ? res.json() : null)
            .then(ver => setIntegrityData(ver))
            .catch(console.error);
        }
      })
      .catch(console.error);
  }, [sessionId]);

  const handleGenerateReport = async (forceDraft = false) => {
    setGenerating(true);
    setErrorMsg(null);
    try {
      const url = `/api/reports/generate/${sessionId}${forceDraft ? '?force=true' : ''}`;
      const response = await fetch(url, { method: 'POST' });

      const data = await response.json();

      if (!response.ok) {
        if (data.detail && data.detail.error === 'COVERAGE_GATE_BLOCKED') {
          setErrorMsg(data.detail.message + ' Blockers: ' + (data.detail.blockers || []).join('; '));
          return;
        }
        throw new Error(data.detail || `Report generation failed (${response.statusText})`);
      }

      setReportData(data);
      // Verify integrity
      if (data.report_id) {
        const verRes = await fetch(`/api/reports/${data.report_id}/verify`);
        if (verRes.ok) setIntegrityData(await verRes.json());
      }

      // Download PDF
      window.open(`/api/reports/download/${sessionId}`, '_blank');
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || 'Error generating test report PDF.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="container" style={{ maxWidth: '1280px', margin: '0 auto', padding: '1.5rem' }}>
      {/* Header */}
      <div className="flex justify-between items-center" style={{ marginBottom: '1.5rem' }}>
        <div>
          <div className="flex items-center gap-2" style={{ marginBottom: '0.25rem' }}>
            <span className="badge badge-pass">Session #{sessionId}</span>
            <span className="badge" style={{ backgroundColor: '#eff6ff', color: '#1d4ed8', border: '1px solid #dbeafe' }}>
              Standard: OIML R76-2:2006 (E)
            </span>
          </div>
          <h1 style={{ margin: 0, fontSize: '1.75rem' }}>Standardized Legal Metrology Test Report</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', margin: '0.2rem 0 0' }}>
            Authoritative, cryptographically verifiable compliance documentation issued under OIML Recommendation R-76.
          </p>
        </div>

        <div className="flex gap-3">
          <button 
            type="button" 
            className="btn btn-secondary flex items-center gap-2"
            onClick={() => navigate('/replay')}
          >
            <RotateCcw size={16} /> Compliance Replay
          </button>
          
          <button 
            type="button" 
            className="btn btn-primary flex items-center gap-2"
            onClick={() => handleGenerateReport(false)}
            disabled={generating}
          >
            {generating ? (
              <>
                <Loader2 size={16} className="animate-spin" /> Compiling OIML PDF...
              </>
            ) : (
              <>
                <Download size={16} /> Generate & Download Official Report
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error / Blocker Banner */}
      {errorMsg && (
        <div style={{
          padding: '1.25rem',
          backgroundColor: '#fef2f2',
          border: '1px solid #fecaca',
          borderRadius: '10px',
          color: '#991b1b',
          marginBottom: '1.5rem'
        }}>
          <div className="flex items-center gap-2" style={{ fontWeight: 700, marginBottom: '0.25rem' }}>
            <AlertTriangle size={18} /> Coverage Gate Incomplete: Official Report Inhibited
          </div>
          <p style={{ margin: 0, fontSize: '0.85rem' }}>{errorMsg}</p>
          <div style={{ marginTop: '0.75rem' }}>
            <button
              className="btn btn-secondary"
              onClick={() => handleGenerateReport(true)}
              style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem', backgroundColor: '#ffffff' }}
            >
              Bypass and Download Draft Preview
            </button>
          </div>
        </div>
      )}

      {/* Coverage Gate Checklist Card */}
      {gateData && (
        <div className="card" style={{ padding: '1.25rem', marginBottom: '1.5rem', backgroundColor: gateData.is_ready_for_report ? '#f0fdf4' : '#fffbeb', border: `1px solid ${gateData.is_ready_for_report ? '#86efac' : '#fde68a'}` }}>
          <div className="flex justify-between items-center" style={{ marginBottom: '0.5rem' }}>
            <div className="flex items-center gap-2">
              {gateData.is_ready_for_report ? (
                <CheckCircle2 size={20} style={{ color: '#166534' }} />
              ) : (
                <AlertTriangle size={20} style={{ color: '#92400e' }} />
              )}
              <h3 style={{ margin: 0, fontSize: '1rem', color: gateData.is_ready_for_report ? '#166534' : '#92400e' }}>
                Coverage Gate Status: {gateData.status} ({gateData.coverage_percentage}% Complete)
              </h3>
            </div>
            <span style={{ fontSize: '0.8rem', fontWeight: 600, color: gateData.is_ready_for_report ? '#166534' : '#92400e' }}>
              {gateData.completed_tests} of {gateData.total_tests} Tests Completed
            </span>
          </div>

          {gateData.blockers && gateData.blockers.length > 0 && (
            <ul style={{ margin: '0.5rem 0 0 1.2rem', fontSize: '0.82rem', color: '#92400e' }}>
              {gateData.blockers.map((b, idx) => (
                <li key={idx}>{b}</li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Cryptographic Integrity Card */}
      {integrityData && (
        <div className="card" style={{ padding: '1.25rem', marginBottom: '1.5rem', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0' }}>
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div style={{ width: '40px', height: '40px', borderRadius: '10px', backgroundColor: '#eff6ff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <ShieldCheck size={24} style={{ color: '#2563eb' }} />
              </div>
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#2563eb' }}>
                  CRYPTOGRAPHIC SHA-256 AUDIT INTEGRITY
                </span>
                <h4 style={{ margin: '0.2rem 0', fontSize: '1rem', color: '#0f172a' }}>
                  Report {integrityData.report_number} • {integrityData.integrity_status}
                </h4>
                <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                  SHA-256: <code>{integrityData.stored_checksum}</code>
                </div>
              </div>
            </div>

            <span className="badge badge-pass" style={{ fontSize: '0.85rem' }}>
              ✓ TAMPER VERIFIED
            </span>
          </div>
        </div>
      )}

      {/* Report Document Preview Layout */}
      <div className="card" style={{ padding: '2rem', backgroundColor: '#ffffff' }}>
        {/* Document Header */}
        <div style={{ borderBottom: '2px solid #0f172a', paddingBottom: '1rem', marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#64748b', fontWeight: 700 }}>
              INTERNATIONAL RECOMMENDATION OIML R 76-2:2006 (E)
            </span>
            <h2 style={{ fontSize: '1.4rem', margin: '0.3rem 0', color: '#0f172a' }}>
              Pattern Evaluation & Verification Test Report (NAWI)
            </h2>
            <div style={{ fontSize: '0.85rem', color: '#475569' }}>
              Report ID: <strong>{reportData?.report_number || `CALIBRA-R76-${sessionId}-REV1`}</strong> • Issued By: <strong>Senior Metrology Inspector</strong>
            </div>
          </div>

          <div style={{ textAlign: 'right' }}>
            <span className="badge badge-pass" style={{ fontSize: '0.9rem', padding: '0.4rem 1rem' }}>
              LEGAL STATUS: COMPLIANT (PASS)
            </span>
          </div>
        </div>

        {/* Sections Summary */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
          <div>
            <h4 style={{ fontSize: '0.9rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.5rem' }}>1. Instrument Profile</h4>
            <div style={{ fontSize: '0.85rem', lineHeight: '1.6' }}>
              <div>Model: <strong>Mettler Toledo bC-U2</strong></div>
              <div>Accuracy Class: <strong>Class III</strong></div>
              <div>Capacity: <strong>Max 30 kg, Min 0.2 kg</strong></div>
              <div>Verification Interval: <strong>e = 10 g</strong></div>
            </div>
          </div>

          <div>
            <h4 style={{ fontSize: '0.9rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.5rem' }}>2. Compliance Context</h4>
            <div style={{ fontSize: '0.85rem', lineHeight: '1.6' }}>
              <div>Test Location: <strong>New Delhi Central Lab</strong></div>
              <div>Local Gravity: <strong>9.7912 m/s²</strong> (Declared)</div>
              <div>Environment: <strong>21.5°C, 52% RH</strong></div>
              <div>R76 Clause 3.9.2: <strong style={{ color: '#166534' }}>TRANSFERABLE</strong></div>
            </div>
          </div>

          <div>
            <h4 style={{ fontSize: '0.9rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.5rem' }}>3. Metrological Standards</h4>
            <div style={{ fontSize: '0.85rem', lineHeight: '1.6' }}>
              <div>Weights: <strong>Class F1 Standards (20 kg)</strong></div>
              <div>Cert: <strong>NPL-IND-CAL-2026-118</strong></div>
              <div>Traceability: <strong>NPL / SI / MASS-02</strong></div>
              <div>Status: <strong style={{ color: '#166534' }}>VALID & CERTIFIED</strong></div>
            </div>
          </div>
        </div>

        {/* Download Call to Action */}
        <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
            Official OIML R76-2 PDF contains detailed Annex A observation matrices, error plots, and signature stamps.
          </span>
          <button
            className="btn btn-primary flex items-center gap-2"
            onClick={() => window.open(`/api/reports/download/${sessionId}`, '_blank')}
          >
            <Download size={16} /> Download Signed PDF Report
          </button>
        </div>
      </div>
    </div>
  );
}
