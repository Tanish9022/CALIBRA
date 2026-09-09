import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { 
  Download, 
  CheckCircle, 
  Scale, 
  ExternalLink,
  Loader2,
  ShieldCheck
} from 'lucide-react';

export default function Reports() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const sessionId = searchParams.get('sessionId') || '1';

  const [generating, setGenerating] = useState(false);
  const [reportGenerated, setReportGenerated] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleGenerateReport = async () => {
    setGenerating(true);
    setErrorMsg(null);
    try {
      // 1. Call POST /api/reports/generate/{sessionId} to build the PDF
      const response = await fetch(`/api/reports/generate/${sessionId}`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error(`Report generation failed (${response.statusText})`);
      }

      await response.json();
      setReportGenerated(true);

      // 2. Open or download the generated PDF
      window.open(`/api/reports/download/${sessionId}`, '_blank');
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || 'Error generating test report PDF.');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="animate-fade-in flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <div className="flex items-center gap-2" style={{ marginBottom: '0.25rem' }}>
            <span className="badge badge-pass">Session #{sessionId}</span>
            <span className="badge" style={{ backgroundColor: 'var(--primary-50)', color: 'var(--primary-700)', border: '1px solid var(--primary-100)' }}>
              Standard: OIML R76-2
            </span>
          </div>
          <h1>Standardized Test Report</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            Official Legal Metrology compliance document generated deterministically from verified evidence.
          </p>
        </div>

        <div className="flex gap-3">
          <button 
            type="button" 
            className="btn btn-secondary flex items-center gap-2"
            onClick={() => navigate(`/workspace?sessionId=${sessionId}`)}
          >
            Back to Workspace
          </button>
          <button 
            type="button" 
            className="btn btn-primary flex items-center gap-2"
            onClick={handleGenerateReport}
            disabled={generating}
          >
            {generating ? (
              <>
                <Loader2 size={16} className="animate-spin" /> Compiling OIML PDF...
              </>
            ) : (
              <>
                <Download size={16} /> Generate & Download PDF Report
              </>
            )}
          </button>
        </div>
      </div>

      {errorMsg && (
        <div style={{
          padding: '1rem',
          backgroundColor: 'var(--status-fail-bg)',
          color: 'var(--status-fail-text)',
          border: '1px solid var(--status-fail-border)',
          borderRadius: 'var(--radius-md)'
        }}>
          <strong>Report Error:</strong> {errorMsg}
        </div>
      )}

      {reportGenerated && (
        <div style={{
          padding: '1rem',
          backgroundColor: 'var(--status-pass-bg)',
          color: 'var(--status-pass-text)',
          border: '1px solid var(--status-pass-border)',
          borderRadius: 'var(--radius-md)'
        }} className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <CheckCircle size={18} />
            <span>Official Report for Session #{sessionId} generated successfully.</span>
          </div>
          <a 
            href={`/api/reports/download/${sessionId}`} 
            target="_blank" 
            rel="noreferrer"
            className="flex items-center gap-1"
            style={{ color: 'var(--status-pass-text)', fontWeight: 600, fontSize: '0.875rem', textDecoration: 'underline' }}
          >
            Open in new tab <ExternalLink size={14} />
          </a>
        </div>
      )}

      {/* Report Document Mockup Preview */}
      <div className="card" style={{ padding: '2.5rem', backgroundColor: 'white', border: '1px solid var(--border-color)', boxShadow: 'var(--shadow-md)' }}>
        
        {/* Report Header */}
        <div className="flex justify-between items-start pb-6" style={{ borderBottom: '2px solid var(--primary-600)' }}>
          <div>
            <div className="flex items-center gap-2">
              <Scale size={28} style={{ color: 'var(--primary-600)' }} />
              <h2 style={{ fontSize: '1.5rem', fontWeight: 700, margin: 0, color: 'var(--text-primary)' }}>CALIBRA</h2>
            </div>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
              Explainable Legal Metrology Compliance Engine • Non-Automatic Weighing Instruments
            </p>
          </div>

          <div style={{ textAlign: 'right' }}>
            <span className="badge badge-pass" style={{ fontSize: '0.875rem', padding: '0.35rem 0.85rem' }}>
              COMPLIANCE VERIFIED
            </span>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
              Format: OIML R76-2:2006 (E)
            </p>
          </div>
        </div>

        {/* Metadata Grid */}
        <div className="grid grid-cols-2 gap-6" style={{ margin: '2rem 0', padding: '1rem', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--radius-md)' }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>Inspection Session</span>
            <p style={{ fontWeight: 600, marginTop: '0.25rem' }}>Session ID: #{sessionId}</p>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Evaluator: Demo Technician</p>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Standard: OIML R76-1 / R76-2 Edition 2006</p>
          </div>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>Verification Date</span>
            <p style={{ fontWeight: 600, marginTop: '0.25rem' }}>{new Date().toLocaleDateString()} — Final Evaluation</p>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Status: DETERMINISTIC DECISION ARCHIVED</p>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Ruleset Checksum: <code>abc123hash</code> (Published)</p>
          </div>
        </div>

        {/* Section 1: Instrument Profile */}
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1.1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
            1. Instrument Identification & Metrological Characteristics
          </h3>
          <div className="grid grid-cols-3 gap-4" style={{ fontSize: '0.875rem' }}>
            <div>
              <span style={{ color: 'var(--text-secondary)' }}>Manufacturer:</span>
              <p style={{ fontWeight: 600 }}>Mettler Toledo</p>
            </div>
            <div>
              <span style={{ color: 'var(--text-secondary)' }}>Model Designation:</span>
              <p style={{ fontWeight: 600 }}>MS205DU</p>
            </div>
            <div>
              <span style={{ color: 'var(--text-secondary)' }}>Accuracy Class:</span>
              <p style={{ fontWeight: 600 }}>Class III (Medium)</p>
            </div>
            <div>
              <span style={{ color: 'var(--text-secondary)' }}>Maximum Capacity (Max):</span>
              <p style={{ fontWeight: 600 }}>30.000 kg</p>
            </div>
            <div>
              <span style={{ color: 'var(--text-secondary)' }}>Minimum Capacity (Min):</span>
              <p style={{ fontWeight: 600 }}>0.200 kg</p>
            </div>
            <div>
              <span style={{ color: 'var(--text-secondary)' }}>Verification Interval (e):</span>
              <p style={{ fontWeight: 600 }}>10.0 g (n = 3000)</p>
            </div>
          </div>
        </div>

        {/* Section 2: Summary of Results */}
        <div style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1.1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
            2. Summary of Metrological Verification Tests
          </h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ backgroundColor: 'var(--bg-color)', textAlign: 'left', borderBottom: '2px solid var(--border-color)' }}>
                <th style={{ padding: '0.75rem' }}>Test Item</th>
                <th style={{ padding: '0.75rem' }}>Clause</th>
                <th style={{ padding: '0.75rem' }}>Applied Load</th>
                <th style={{ padding: '0.75rem' }}>Observed Error</th>
                <th style={{ padding: '0.75rem' }}>Permissible MPE</th>
                <th style={{ padding: '0.75rem' }}>Result</th>
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '0.75rem', fontWeight: 500 }}>01 Administrative Examination</td>
                <td style={{ padding: '0.75rem', color: 'var(--text-secondary)' }}>R76-1 3.4</td>
                <td style={{ padding: '0.75rem' }}>Visual</td>
                <td style={{ padding: '0.75rem' }}>Conforming</td>
                <td style={{ padding: '0.75rem' }}>Mandatory markings</td>
                <td style={{ padding: '0.75rem' }}><span className="badge badge-pass">PASS</span></td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <td style={{ padding: '0.75rem', fontWeight: 500 }}>02 Construction & Security</td>
                <td style={{ padding: '0.75rem', color: 'var(--text-secondary)' }}>R76-1 3.9</td>
                <td style={{ padding: '0.75rem' }}>Visual/Mech</td>
                <td style={{ padding: '0.75rem' }}>Conforming</td>
                <td style={{ padding: '0.75rem' }}>Seals intact</td>
                <td style={{ padding: '0.75rem' }}><span className="badge badge-pass">PASS</span></td>
              </tr>
              <tr style={{ borderBottom: '1px solid var(--border-color)', backgroundColor: 'var(--primary-50)' }}>
                <td style={{ padding: '0.75rem', fontWeight: 600 }}>03 Weighing Performance</td>
                <td style={{ padding: '0.75rem', color: 'var(--text-secondary)' }}>R76-1 3.5.1</td>
                <td style={{ padding: '0.75rem', fontWeight: 600 }}>10.000 kg</td>
                <td style={{ padding: '0.75rem', fontWeight: 600, color: 'var(--primary-700)' }}>+8.000 g</td>
                <td style={{ padding: '0.75rem', fontWeight: 600 }}>±20.000 g</td>
                <td style={{ padding: '0.75rem' }}><span className="badge badge-pass">PASS</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Section 3: Evidence & Deterministic Attestation */}
        <div style={{ padding: '1rem', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
          <div className="flex items-center gap-2" style={{ marginBottom: '0.5rem' }}>
            <ShieldCheck size={18} style={{ color: 'var(--primary-600)' }} />
            <h4 style={{ margin: 0 }}>Deterministic Compliance Attestation</h4>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: 0 }}>
            Every derived decision in this report is backed by an immutable calculation lineage: 
            <code> Raw Observation → Unit Normalization → Indication Error Calculation → Applicable R76 Rule → Threshold Comparison → Decision</code>. 
            No speculative AI models are used for regulatory determinations.
          </p>
        </div>

        {/* Action Bar Footer */}
        <div className="flex justify-between items-center" style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border-color)' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            CALIBRA Report Engine • Generated on demand via ReportLab A4 Template
          </span>
          <button 
            type="button"
            className="btn btn-primary flex items-center gap-2"
            onClick={handleGenerateReport}
            disabled={generating}
          >
            <Download size={16} /> Download Official PDF Report
          </button>
        </div>

      </div>
    </div>
  );
}
