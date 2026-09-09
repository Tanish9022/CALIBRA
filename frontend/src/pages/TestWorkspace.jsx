import React, { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { HelpCircle, FileText, CheckCircle, XCircle, Activity } from 'lucide-react';

export default function TestWorkspace() {
  const [searchParams] = useSearchParams();
  const sessionId = searchParams.get('sessionId') || 1; // Fallback to 1 for demo if navigated directly

  const [load, setLoad] = useState('10');
  const [indication, setIndication] = useState('10.008');
  const [result, setResult] = useState(null);
  const [showEvidence, setShowEvidence] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleCalculate = async () => {
    setLoading(true);
    try {
      // 1. Create Observation
      const resObs = await fetch(`/api/sessions/${sessionId}/observations`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          test_definition_id: 1, // Assuming Weighing Performance is ID 1
          raw_value: parseFloat(load),
          raw_unit: 'kg',
          sequence_no: 1,
          metadata_json: {
            indication: parseFloat(indication),
            indication_unit: 'kg'
          }
        })
      });
      const observation = await resObs.json();

      // 2. Evaluate Observation
      const resEval = await fetch(`/api/compliance/evaluate_weighing/${observation.id}`, {
        method: 'POST'
      });
      const evaluation = await resEval.json();

      setResult({
        status: evaluation.status,
        error: evaluation.evidence.calculation.error,
        mpe: evaluation.evidence.rule.threshold,
        evidenceId: `EV-${evaluation.evidence_id}`,
        evidenceData: evaluation.evidence
      });

    } catch (error) {
      console.error(error);
      alert('Error communicating with compliance engine.');
    } finally {
      setLoading(false);
    }
  };

  const handleFailDemo = () => {
    setLoad('10');
    setIndication('10.012'); // 12g error -> FAIL
    // The user still needs to click Validate & Calculate to run it through the backend
  };

  return (
    <div className="animate-fade-in flex-col flex" style={{ height: 'calc(100vh - 4rem)' }}>
      <div className="flex justify-between items-center" style={{ marginBottom: '1.5rem' }}>
        <h1>Test Workspace: Weighing Performance <span style={{fontSize: '0.875rem', color: 'var(--text-secondary)'}}>Session #{sessionId}</span></h1>
        <div className="flex gap-4">
          <button className="btn btn-secondary" onClick={handleFailDemo}>Load Failing Demo Data</button>
          <button className="btn btn-primary">Complete Test</button>
        </div>
      </div>

      <div className="flex gap-6 flex-1">
        {/* Left Pane - Data Entry */}
        <div className="card" style={{ flex: '1 1 40%', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>Observation Entry</h3>
          
          <div className="grid grid-cols-2 gap-4" style={{ marginBottom: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Reference Load (kg)</label>
              <input type="number" step="any" className="form-input" value={load} onChange={(e) => setLoad(e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Indication (kg)</label>
              <input type="number" step="any" className="form-input" value={indication} onChange={(e) => setIndication(e.target.value)} />
            </div>
          </div>
          
          <button className="btn btn-primary" onClick={handleCalculate} disabled={loading} style={{ alignSelf: 'flex-start' }}>
            {loading ? 'Processing via Backend...' : 'Validate & Calculate'}
          </button>

          {/* Test Plan Progress */}
          <div style={{ marginTop: 'auto' }}>
            <h4 style={{ marginBottom: '0.5rem' }}>Test Plan Progress</h4>
            <div className="flex flex-col gap-2">
              <div className="flex justify-between items-center" style={{ padding: '0.5rem', backgroundColor: 'var(--bg-color)', borderRadius: 'var(--radius-md)' }}>
                <span style={{ fontSize: '0.875rem' }}>01 Administrative</span>
                <span className="badge badge-pass">DONE</span>
              </div>
              <div className="flex justify-between items-center" style={{ padding: '0.5rem', backgroundColor: 'var(--primary-50)', border: '1px solid var(--primary-100)', borderRadius: 'var(--radius-md)' }}>
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--primary-700)' }}>03 Weighing Performance</span>
                <span className="badge" style={{ backgroundColor: 'white', color: 'var(--primary-600)', border: '1px solid var(--primary-200)' }}>IN PROGRESS</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Pane - Results & Evidence */}
        <div className="card" style={{ flex: '1 1 60%', display: 'flex', flexDirection: 'column', overflowY: 'auto' }}>
          <h3 style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>Live Validation</h3>
          
          {result ? (
            <div className="animate-slide-down flex flex-col gap-6">
              
              <div style={{ 
                padding: '1.5rem', 
                borderRadius: 'var(--radius-md)',
                backgroundColor: result.status === 'PASS' ? 'var(--status-pass-bg)' : 'var(--status-fail-bg)',
                border: `1px solid ${result.status === 'PASS' ? 'var(--status-pass-border)' : 'var(--status-fail-border)'}`,
                textAlign: 'center'
              }}>
                <div className="flex items-center justify-center gap-2" style={{ marginBottom: '0.5rem' }}>
                  {result.status === 'PASS' ? <CheckCircle size={32} color="var(--status-pass-text)" /> : <XCircle size={32} color="var(--status-fail-text)" />}
                  <span style={{ fontSize: '2rem', fontWeight: 700, color: result.status === 'PASS' ? 'var(--status-pass-text)' : 'var(--status-fail-text)' }}>
                    {result.status}
                  </span>
                </div>
                
                <div className="flex justify-center gap-6 text-secondary" style={{ marginTop: '1rem' }}>
                  <div className="flex flex-col">
                    <span style={{ fontSize: '0.75rem', textTransform: 'uppercase' }}>Observed Error</span>
                    <span style={{ fontWeight: 600 }}>{result.error > 0 ? '+' : ''}{result.error} g</span>
                  </div>
                  <div className="flex flex-col">
                    <span style={{ fontSize: '0.75rem', textTransform: 'uppercase' }}>Applicable Limit</span>
                    <span style={{ fontWeight: 600 }}>±{result.mpe} g</span>
                  </div>
                </div>
                
                {result.status === 'FAIL' && (
                  <p style={{ marginTop: '1rem', fontSize: '0.875rem', color: 'var(--status-fail-text)', fontWeight: 500 }}>
                    Reason: Observed absolute error exceeds the applicable verified limit.
                  </p>
                )}
                
                <div className="flex justify-center gap-4" style={{ marginTop: '1.5rem' }}>
                  <button className="btn btn-secondary flex items-center gap-2" onClick={() => setShowEvidence(!showEvidence)}>
                    <HelpCircle size={16} /> WHY?
                  </button>
                  <button className="btn btn-secondary flex items-center gap-2" onClick={() => window.open(`/api/reports/download/${sessionId}`, '_blank')}>
                    <FileText size={16} /> GENERATE REPORT
                  </button>
                </div>
              </div>

              {showEvidence && (
                <div className="animate-fade-in p-4" style={{ backgroundColor: 'var(--bg-color)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                  <h4 style={{ marginBottom: '1rem', color: 'var(--primary-600)' }}>Evidence Chain <span style={{fontSize:'0.75rem', color: 'var(--text-secondary)'}}>({result.evidenceId})</span></h4>
                  <div className="flex flex-col gap-3 relative">
                    
                    {/* Vertical connecting line */}
                    <div style={{ position: 'absolute', left: '15px', top: '20px', bottom: '20px', width: '2px', backgroundColor: 'var(--border-color)' }}></div>
                    
                    <div className="flex gap-4 items-center" style={{ position: 'relative', zIndex: 1 }}>
                      <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: 'var(--surface-color)', border: '2px solid var(--primary-500)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 'bold' }}>1</div>
                      <div className="flex-1 p-3 card" style={{ padding: '0.75rem' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Raw Observation</span>
                        <p style={{ fontWeight: 500 }}>Load: {result.evidenceData.raw_input.load} {result.evidenceData.raw_input.load_unit}, Ind: {result.evidenceData.raw_input.indication} {result.evidenceData.raw_input.indication_unit}</p>
                      </div>
                    </div>

                    <div className="flex gap-4 items-center" style={{ position: 'relative', zIndex: 1 }}>
                      <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: 'var(--surface-color)', border: '2px solid var(--primary-500)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 'bold' }}>2</div>
                      <div className="flex-1 p-3 card" style={{ padding: '0.75rem' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Calculation & Normalization</span>
                        <p style={{ fontWeight: 500 }}>Error = {result.evidenceData.calculation.formula} = {result.error} {result.evidenceData.calculation.unit}</p>
                      </div>
                    </div>

                    <div className="flex gap-4 items-center" style={{ position: 'relative', zIndex: 1 }}>
                      <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: 'var(--surface-color)', border: '2px solid var(--primary-500)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 'bold' }}>3</div>
                      <div className="flex-1 p-3 card" style={{ padding: '0.75rem' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Applicable R76 Rule</span>
                        <p style={{ fontWeight: 500 }}>{result.evidenceData.rule.code}</p>
                        <p style={{ fontSize: '0.75rem' }}>Calculated MPE threshold: ±{result.evidenceData.rule.threshold} {result.evidenceData.calculation.unit}</p>
                      </div>
                    </div>

                    <div className="flex gap-4 items-center" style={{ position: 'relative', zIndex: 1 }}>
                      <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: 'var(--surface-color)', border: '2px solid var(--primary-500)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 'bold' }}>4</div>
                      <div className="flex-1 p-3 card" style={{ padding: '0.75rem' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Decision</span>
                        <p style={{ fontWeight: 500, color: result.status === 'PASS' ? 'var(--status-pass-text)' : 'var(--status-fail-text)' }}>
                          |{result.error}g| {result.status === 'PASS' ? '≤' : '>'} {result.mpe}g → {result.status}
                        </p>
                      </div>
                    </div>

                  </div>
                </div>
              )}

            </div>
          ) : (
            <div className="flex flex-col items-center justify-center flex-1 text-secondary">
              <Activity size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
              <p>Enter observation data and validate to see results calculated by the backend Engine.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
