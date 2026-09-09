import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { 
  HelpCircle, 
  FileText, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Activity, 
  ArrowRight,
  Loader2
} from 'lucide-react';

export default function TestWorkspace() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const sessionId = searchParams.get('sessionId') || '1';

  const [load, setLoad] = useState('10');
  const [indication, setIndication] = useState('10.008');
  const [result, setResult] = useState(null);
  const [showEvidence, setShowEvidence] = useState(false);
  const [loading, setLoading] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleCalculate = async () => {
    setLoading(true);
    setErrorMsg(null);
    try {
      // 1. Create Observation
      const resObs = await fetch(`/api/sessions/${sessionId}/observations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          test_definition_id: 1, // Weighing Performance WP-01
          raw_value: parseFloat(load),
          raw_unit: 'kg',
          sequence_no: 1,
          metadata_json: {
            indication: parseFloat(indication),
            indication_unit: 'kg'
          }
        })
      });

      if (!resObs.ok) {
        throw new Error(`Failed to record observation (${resObs.statusText})`);
      }
      const observation = await resObs.json();

      // 2. Evaluate Observation via Compliance Engine
      const resEval = await fetch(`/api/compliance/evaluate_weighing/${observation.id}`, {
        method: 'POST'
      });

      if (!resEval.ok) {
        throw new Error(`Compliance evaluation failed (${resEval.statusText})`);
      }
      const evaluation = await resEval.json();

      setResult({
        status: evaluation.status,
        error: evaluation.evidence.calculation.error,
        mpe: evaluation.evidence.rule.threshold,
        evidenceId: `EV-${evaluation.evidence_id}`,
        evidenceData: evaluation.evidence,
        decisionReason: evaluation.evidence.decision.requires_review 
          ? (evaluation.evidence.rule.code ? "Configuration review required by R76 ruleset" : "Manual verification needed")
          : (evaluation.status === 'PASS' 
              ? "Observed error is within Maximum Permissible Error (MPE) limit."
              : "Observed absolute error exceeds the applicable verified MPE limit.")
      });

    } catch (error) {
      console.error(error);
      setErrorMsg(error.message || 'Error communicating with compliance engine.');
    } finally {
      setLoading(false);
    }
  };

  const handleFailDemo = () => {
    setLoad('10');
    setIndication('10.035'); // 35g error -> Exceeds Class III 20g MPE -> FAIL
    setResult(null);
    setShowEvidence(false);
  };

  const handlePassDemo = () => {
    setLoad('10');
    setIndication('10.008'); // 8g error -> Within Class III 20g MPE -> PASS
    setResult(null);
    setShowEvidence(false);
  };

  const handleGenerateReport = async () => {
    setReportLoading(true);
    setErrorMsg(null);
    try {
      // 1. Generate Report on Backend
      const res = await fetch(`/api/reports/generate/${sessionId}`, {
        method: 'POST'
      });

      if (!res.ok) {
        throw new Error(`Report generation failed (${res.statusText})`);
      }

      // 2. Open PDF in a new tab
      window.open(`/api/reports/download/${sessionId}`, '_blank');
    } catch (err) {
      console.error(err);
      setErrorMsg(err.message || 'Error generating test report PDF.');
    } finally {
      setReportLoading(false);
    }
  };

  const handleCompleteTest = async () => {
    // Generate report in background if possible and navigate to the report summary page
    try {
      await fetch(`/api/reports/generate/${sessionId}`, { method: 'POST' });
    } catch {
      // Ignore background compilation errors
    }
    navigate(`/reports?sessionId=${sessionId}`);
  };

  const formatNumber = (num, decimals = 3) => {
    if (num === null || num === undefined || isNaN(num)) return '0.000';
    return Number(num).toFixed(decimals);
  };

  return (
    <div className="animate-fade-in flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <div className="flex items-center gap-2" style={{ marginBottom: '0.25rem' }}>
            <span className="badge badge-pass">Session #{sessionId}</span>
            <span className="badge" style={{ backgroundColor: 'var(--primary-50)', color: 'var(--primary-700)', border: '1px solid var(--primary-100)' }}>
              Test 03: Weighing Performance (WP-01)
            </span>
          </div>
          <h1>Test Workspace</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            Record raw metrological observations, execute live normalization, and verify against OIML R76 MPE limits.
          </p>
        </div>

        <div className="flex gap-3">
          <button 
            type="button" 
            className="btn btn-secondary flex items-center gap-1"
            onClick={handlePassDemo}
          >
            Load Passing Data (+8g)
          </button>
          <button 
            type="button" 
            className="btn btn-secondary flex items-center gap-1"
            onClick={handleFailDemo}
          >
            Load Failing Data (+35g)
          </button>
          <button 
            type="button" 
            className="btn btn-primary flex items-center gap-2"
            onClick={handleCompleteTest}
          >
            Complete Test & View Report <ArrowRight size={16} />
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
          <strong>Engine Error:</strong> {errorMsg}
        </div>
      )}

      <div className="grid grid-cols-2 gap-6" style={{ alignItems: 'start' }}>
        
        {/* Left Pane - Data Entry & Test Battery */}
        <div className="flex flex-col gap-6">
          <div className="card">
            <h3 style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '1.25rem' }}>
              Observation Entry
            </h3>
            
            <div className="grid grid-cols-2 gap-4" style={{ marginBottom: '1.25rem' }}>
              <div className="form-group">
                <label className="form-label">Reference Standard Load (kg)</label>
                <input 
                  type="number" 
                  step="any" 
                  className="form-input" 
                  value={load} 
                  onChange={(e) => setLoad(e.target.value)} 
                />
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Standard test weight applied</span>
              </div>
              <div className="form-group">
                <label className="form-label">Observed Indication (kg)</label>
                <input 
                  type="number" 
                  step="any" 
                  className="form-input" 
                  value={indication} 
                  onChange={(e) => setIndication(e.target.value)} 
                />
                <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Instrument display reading</span>
              </div>
            </div>
            
            <div className="flex justify-between items-center">
              <button 
                className="btn btn-primary flex items-center gap-2" 
                onClick={handleCalculate} 
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader2 size={16} className="animate-spin" /> Evaluating with R76 Engine...
                  </>
                ) : (
                  <>
                    <Activity size={16} /> Validate & Calculate Compliance
                  </>
                )}
              </button>

              <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                Deterministic Rule Evaluation • R76-1 3.5.1
              </span>
            </div>
          </div>

          {/* Test Battery Progress List */}
          <div className="card">
            <h3 style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>
              Test Battery Progress
            </h3>
            <div className="flex flex-col gap-2">
              
              <div className="flex justify-between items-center" style={{ padding: '0.6rem 0.8rem', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--radius-md)' }}>
                <div>
                  <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>01 Administrative Examination</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block' }}>R76-1 3.4 Inscriptions</span>
                </div>
                <span className="badge badge-pass flex items-center gap-1"><CheckCircle size={12} /> COMPLETE</span>
              </div>

              <div className="flex justify-between items-center" style={{ padding: '0.6rem 0.8rem', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--radius-md)' }}>
                <div>
                  <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>02 Construction & Security</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block' }}>R76-1 3.9 Security seals</span>
                </div>
                <span className="badge badge-pass flex items-center gap-1"><CheckCircle size={12} /> COMPLETE</span>
              </div>

              <div className="flex justify-between items-center" style={{ padding: '0.6rem 0.8rem', backgroundColor: 'var(--primary-50)', border: '1px solid var(--primary-200)', borderRadius: 'var(--radius-md)' }}>
                <div>
                  <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--primary-700)' }}>03 Weighing Performance</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--primary-600)', display: 'block' }}>R76-1 3.5.1 Errors of indication</span>
                </div>
                <span className="badge" style={{ backgroundColor: 'white', color: 'var(--primary-700)', border: '1px solid var(--primary-300)' }}>
                  {result ? 'TESTED' : 'IN PROGRESS'}
                </span>
              </div>

              <div className="flex justify-between items-center" style={{ padding: '0.6rem 0.8rem', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--radius-md)' }}>
                <div>
                  <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>04 Repeatability</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block' }}>R76-1 3.6.1 Spread</span>
                </div>
                <span className="badge" style={{ backgroundColor: 'white', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' }}>PENDING</span>
              </div>

              <div className="flex justify-between items-center" style={{ padding: '0.6rem 0.8rem', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--radius-md)' }}>
                <div>
                  <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>05 Eccentricity</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block' }}>R76-1 3.6.2 Corner loading</span>
                </div>
                <span className="badge" style={{ backgroundColor: 'white', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' }}>PENDING</span>
              </div>

            </div>
          </div>
        </div>

        {/* Right Pane - Results & Evidence */}
        <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '1.25rem' }}>
            Compliance Decision & Evidence
          </h3>
          
          {result ? (
            <div className="animate-slide-down flex flex-col gap-6">
              
              {/* Decision Box with Proper Semantic Colors */}
              <div style={{ 
                padding: '1.75rem', 
                borderRadius: 'var(--radius-md)',
                backgroundColor: result.status === 'PASS' 
                  ? 'var(--status-pass-bg)' 
                  : (result.status === 'REVIEW' ? 'var(--status-review-bg)' : 'var(--status-fail-bg)'),
                border: `1px solid ${
                  result.status === 'PASS' 
                    ? 'var(--status-pass-border)' 
                    : (result.status === 'REVIEW' ? 'var(--status-review-border)' : 'var(--status-fail-border)')
                }`,
                textAlign: 'center'
              }}>
                <div className="flex items-center justify-center gap-2" style={{ marginBottom: '0.5rem' }}>
                  {result.status === 'PASS' && <CheckCircle size={32} color="var(--status-pass-text)" />}
                  {result.status === 'FAIL' && <XCircle size={32} color="var(--status-fail-text)" />}
                  {result.status === 'REVIEW' && <AlertTriangle size={32} color="var(--status-review-text)" />}
                  
                  <span style={{ 
                    fontSize: '2rem', 
                    fontWeight: 700, 
                    color: result.status === 'PASS' 
                      ? 'var(--status-pass-text)' 
                      : (result.status === 'REVIEW' ? 'var(--status-review-text)' : 'var(--status-fail-text)')
                  }}>
                    {result.status === 'REVIEW' ? 'REVIEW REQUIRED' : result.status}
                  </span>
                </div>

                <p style={{
                  fontSize: '0.875rem',
                  fontWeight: 500,
                  marginTop: '0.5rem',
                  color: result.status === 'PASS' 
                    ? 'var(--status-pass-text)' 
                    : (result.status === 'REVIEW' ? 'var(--status-review-text)' : 'var(--status-fail-text)')
                }}>
                  {result.decisionReason}
                </p>
                
                {/* Metrics comparison */}
                <div className="flex justify-center gap-8 text-secondary" style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px dashed rgba(0,0,0,0.1)' }}>
                  <div className="flex flex-col">
                    <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>Observed Error</span>
                    <span style={{ fontSize: '1.1rem', fontWeight: 700 }}>
                      {result.error > 0 ? '+' : ''}{formatNumber(result.error, 3)} g
                    </span>
                  </div>

                  <div className="flex flex-col">
                    <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>Applicable MPE Limit</span>
                    <span style={{ fontSize: '1.1rem', fontWeight: 700 }}>
                      ±{formatNumber(result.mpe, 3)} g
                    </span>
                  </div>

                  {result.status === 'FAIL' && result.mpe && (
                    <div className="flex flex-col">
                      <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600, color: 'var(--status-fail-text)' }}>Exceedance</span>
                      <span style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--status-fail-text)' }}>
                        +{formatNumber(Math.abs(result.error) - result.mpe, 3)} g
                      </span>
                    </div>
                  )}

                  {result.status === 'PASS' && result.mpe && (
                    <div className="flex flex-col">
                      <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600, color: 'var(--status-pass-text)' }}>Margin</span>
                      <span style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--status-pass-text)' }}>
                        {formatNumber(result.mpe - Math.abs(result.error), 3)} g (Compliant)
                      </span>
                    </div>
                  )}
                </div>
                
                <div className="flex justify-center gap-4" style={{ marginTop: '1.5rem' }}>
                  <button 
                    type="button"
                    className="btn btn-secondary flex items-center gap-2" 
                    onClick={() => setShowEvidence(!showEvidence)}
                  >
                    <HelpCircle size={16} /> {showEvidence ? 'Hide Evidence' : 'WHY? (Explain Decision)'}
                  </button>
                  <button 
                    type="button"
                    className="btn btn-secondary flex items-center gap-2" 
                    onClick={handleGenerateReport}
                    disabled={reportLoading}
                  >
                    {reportLoading ? (
                      <>
                        <Loader2 size={16} className="animate-spin" /> Generating PDF...
                      </>
                    ) : (
                      <>
                        <FileText size={16} /> Generate & View Report
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Evidence Chain Drawer */}
              {showEvidence && (
                <div className="animate-fade-in p-4" style={{ backgroundColor: 'var(--bg-color)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                  <div className="flex justify-between items-center" style={{ marginBottom: '1rem' }}>
                    <h4 style={{ margin: 0, color: 'var(--primary-700)' }}>
                      Evidence Chain <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>({result.evidenceId})</span>
                    </h4>
                    <span className="badge" style={{ backgroundColor: 'white', color: 'var(--primary-600)', border: '1px solid var(--primary-200)' }}>
                      OIML R76:2006 Deterministic Lineage
                    </span>
                  </div>

                  <div className="flex flex-col gap-3 relative">
                    
                    {/* Vertical connecting line */}
                    <div style={{ position: 'absolute', left: '15px', top: '20px', bottom: '20px', width: '2px', backgroundColor: 'var(--border-color)' }}></div>
                    
                    {/* Step 1: Raw Input */}
                    <div className="flex gap-4 items-center" style={{ position: 'relative', zIndex: 1 }}>
                      <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: 'var(--surface-color)', border: '2px solid var(--primary-500)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 'bold' }}>1</div>
                      <div className="flex-1 p-3 card" style={{ padding: '0.75rem' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>Raw Observation Source</span>
                        <p style={{ fontWeight: 500, margin: '0.2rem 0 0 0' }}>
                          Applied Reference Load: <strong>{formatNumber(result.evidenceData.raw_input.load, 3)} {result.evidenceData.raw_input.load_unit}</strong> • Indication: <strong>{formatNumber(result.evidenceData.raw_input.indication, 3)} {result.evidenceData.raw_input.indication_unit}</strong>
                        </p>
                      </div>
                    </div>

                    {/* Step 2: Normalization & Error */}
                    <div className="flex gap-4 items-center" style={{ position: 'relative', zIndex: 1 }}>
                      <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: 'var(--surface-color)', border: '2px solid var(--primary-500)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 'bold' }}>2</div>
                      <div className="flex-1 p-3 card" style={{ padding: '0.75rem' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>Normalization & Calculation</span>
                        <p style={{ fontWeight: 500, margin: '0.2rem 0 0 0' }}>
                          Formula: <code>Error = Indication - Load</code> = <strong>{result.error > 0 ? '+' : ''}{formatNumber(result.error, 3)} {result.evidenceData.calculation.unit}</strong> (Normalized to grams)
                        </p>
                      </div>
                    </div>

                    {/* Step 3: Rule Evaluation */}
                    <div className="flex gap-4 items-center" style={{ position: 'relative', zIndex: 1 }}>
                      <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: 'var(--surface-color)', border: '2px solid var(--primary-500)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 'bold' }}>3</div>
                      <div className="flex-1 p-3 card" style={{ padding: '0.75rem' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>Applicable R76 Standard Rule</span>
                        <p style={{ fontWeight: 500, margin: '0.2rem 0 0 0' }}>
                          Rule: <strong>{result.evidenceData.rule.code}</strong> (Class III Medium Accuracy)
                        </p>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', margin: '0.2rem 0 0 0' }}>
                          Load Region: {formatNumber(result.evidenceData.raw_input.load * 1000 / result.evidenceData.instrument_profile.e, 0)}e (500e &lt; m ≤ 2000e) → MPE Threshold: <strong>±{formatNumber(result.evidenceData.rule.threshold, 3)} {result.evidenceData.calculation.unit}</strong>
                        </p>
                      </div>
                    </div>

                    {/* Step 4: Decision */}
                    <div className="flex gap-4 items-center" style={{ position: 'relative', zIndex: 1 }}>
                      <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: 'var(--surface-color)', border: '2px solid var(--primary-500)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 'bold' }}>4</div>
                      <div className="flex-1 p-3 card" style={{ padding: '0.75rem' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>Compliance Decision</span>
                        <p style={{ 
                          fontWeight: 600, 
                          margin: '0.2rem 0 0 0',
                          color: result.status === 'PASS' ? 'var(--status-pass-text)' : (result.status === 'REVIEW' ? 'var(--status-review-text)' : 'var(--status-fail-text)')
                        }}>
                          |{formatNumber(result.error, 3)} g| {result.status === 'PASS' ? '≤' : '>'} {formatNumber(result.mpe, 3)} g → <strong>{result.status}</strong>
                        </p>
                      </div>
                    </div>

                  </div>
                </div>
              )}

            </div>
          ) : (
            <div className="flex flex-col items-center justify-center flex-1 text-secondary" style={{ padding: '3rem 1rem', textAlign: 'center' }}>
              <Activity size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
              <h4 style={{ margin: 0 }}>Awaiting Observation Entry</h4>
              <p style={{ fontSize: '0.875rem', maxWidth: '360px', marginTop: '0.5rem' }}>
                Enter reference load and observed indication, then click <strong>"Validate & Calculate"</strong> to execute the deterministic OIML R76 evaluation.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
