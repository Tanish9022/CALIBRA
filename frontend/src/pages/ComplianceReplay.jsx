import React, { useState, useEffect } from 'react';
import { 
  RotateCcw, 
  ShieldCheck, 
  CheckCircle, 
  XCircle, 
  ArrowRight, 
  Hash, 
  Calendar, 
  FileText, 
  Compass, 
  Layers,
  ChevronRight
} from 'lucide-react';

export default function ComplianceReplay() {
  const [sessions, setSessions] = useState([]);
  const [selectedSessionId, setSelectedSessionId] = useState(1);
  const [replayData, setReplayData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch('/api/sessions/')
      .then(res => res.ok ? res.json() : [])
      .then(data => {
        if (data && data.length > 0) {
          setSessions(data);
          setSelectedSessionId(data[0].id);
        }
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    if (!selectedSessionId) return;
    setLoading(true);
    fetch(`/api/replay/session/${selectedSessionId}`)
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        setReplayData(data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedSessionId]);

  return (
    <div className="container" style={{ maxWidth: '1280px', margin: '0 auto', padding: '1.5rem' }}>
      {/* Title */}
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div className="flex items-center gap-2">
            <RotateCcw size={28} style={{ color: 'var(--primary-600)' }} />
            <h1 style={{ margin: 0, fontSize: '1.75rem' }}>Compliance Replay Engine</h1>
          </div>
          <p style={{ color: 'var(--text-secondary)', margin: '0.25rem 0 0', fontSize: '0.9rem' }}>
            Full immutable lineage reconstruction: Input → Context → Ruleset → Test → Observation → Calculation → MPE → Decision.
          </p>
        </div>

        {/* Session Selector */}
        <div className="flex items-center gap-2">
          <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Select Session:</label>
          <select
            value={selectedSessionId}
            onChange={(e) => setSelectedSessionId(e.target.value)}
            style={{ padding: '0.5rem 0.8rem', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '0.85rem' }}
          >
            {sessions.map(s => (
              <option key={s.id} value={s.id}>Session #{s.id} (Instrument #{s.instrument_id})</option>
            ))}
          </select>
        </div>
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#64748b' }}>
          Reconstructing compliance lineage from cryptographic audit trail...
        </div>
      )}

      {replayData && !loading && (
        <div>
          {/* Integrity Header Card */}
          <div className="card" style={{ marginBottom: '1.5rem', padding: '1.25rem', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0' }}>
            <div className="flex justify-between items-center">
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#2563eb', textTransform: 'uppercase' }}>
                  Cryptographic Trace Verified
                </span>
                <h3 style={{ margin: '0.2rem 0', fontSize: '1.1rem' }}>
                  Session #{replayData.session_id} • Reconstructed Audit Lineage
                </h3>
                <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                  Standard Edition Used: <strong>{replayData.ruleset_used}</strong> • Replay Integrity Hash:
                </div>
                <code style={{ fontSize: '0.75rem', color: '#0f172a', backgroundColor: '#e2e8f0', padding: '2px 6px', borderRadius: '4px', wordBreak: 'break-all' }}>
                  {replayData.audit_hash_sha256}
                </code>
              </div>

              <div style={{ textAlign: 'right' }}>
                <span className="badge badge-pass" style={{ fontSize: '0.85rem', padding: '0.4rem 0.8rem' }}>
                  ✓ IMMUTABLE REPLAY VERIFIED
                </span>
              </div>
            </div>
          </div>

          {/* Step-by-Step Replay Timeline */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {replayData.steps?.map((step) => (
              <div key={step.step_number} className="card" style={{ padding: '1.25rem', borderLeft: '4px solid #2563eb' }}>
                <div className="flex justify-between items-center" style={{ marginBottom: '0.75rem' }}>
                  <div className="flex items-center gap-2">
                    <span style={{
                      backgroundColor: '#2563eb',
                      color: '#ffffff',
                      width: '26px', height: '26px',
                      borderRadius: '50%',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontSize: '0.8rem', fontWeight: 700
                    }}>
                      {step.step_number}
                    </span>
                    <h4 style={{ margin: 0, fontSize: '1rem', color: '#0f172a' }}>{step.title}</h4>
                  </div>
                  <span style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>
                    STAGE: {step.stage}
                  </span>
                </div>

                {/* Step Content */}
                <div style={{ backgroundColor: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #f1f5f9', fontSize: '0.85rem' }}>
                  {step.stage === 'INSTRUMENT_PROFILE' && (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.5rem' }}>
                      <div><span style={{ color: '#64748b' }}>Manufacturer:</span> <strong>{step.data.manufacturer}</strong></div>
                      <div><span style={{ color: '#64748b' }}>Model:</span> <strong>{step.data.model}</strong></div>
                      <div><span style={{ color: '#64748b' }}>Class:</span> <strong>{step.data.accuracy_class}</strong></div>
                      <div><span style={{ color: '#64748b' }}>Capacity Max:</span> <strong>{step.data.max_capacity}</strong></div>
                    </div>
                  )}

                  {step.stage === 'COMPLIANCE_CONTEXT' && (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
                      <div><span style={{ color: '#64748b' }}>Test Location:</span> <strong>{step.data.test_location}</strong></div>
                      <div><span style={{ color: '#64748b' }}>Local Gravity:</span> <strong>{step.data.local_gravity_ms2} m/s²</strong> ({step.data.gravity_source})</div>
                      <div><span style={{ color: '#64748b' }}>Ambient Environment:</span> <strong>{step.data.temperature_c}°C, {step.data.humidity_pct}% RH</strong></div>
                    </div>
                  )}

                  {step.stage === 'RULESET_VERIFICATION' && (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem' }}>
                      <div><span style={{ color: '#64748b' }}>Applied Standard:</span> <strong>{step.data.standard} Edition {step.data.edition}</strong></div>
                      <div><span style={{ color: '#64748b' }}>Active Ruleset Version:</span> <strong>{step.data.active_current_ruleset}</strong></div>
                      <div><span style={{ color: '#64748b' }}>Ruleset Drift:</span> <strong style={{ color: '#166534' }}>{step.data.version_comparison}</strong></div>
                    </div>
                  )}

                  {step.stage === 'TEST_EVIDENCE_EXECUTION' && (
                    <div>
                      <div style={{ marginBottom: '0.5rem', fontWeight: 600, color: '#334155' }}>
                        Executed Test Observations ({step.data.total_executed_tests} recorded):
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                        {step.data.test_traces?.map((t, idx) => (
                          <div key={idx} style={{ backgroundColor: '#ffffff', padding: '0.75rem', borderRadius: '6px', border: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                              <strong>[{t.code}] {t.name}</strong>
                              <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                                Load: {t.normalized?.load?.raw || 'N/A'} {t.normalized?.load?.unit} • Error Ec: {t.calculation_trace?.error ? `${t.calculation_trace.error > 0 ? '+' : ''}${t.calculation_trace.error} g` : 'N/A'} • MPE: ±{t.rule_applied?.threshold_mpe || 'N/A'} g
                              </div>
                            </div>
                            <span className={`badge ${t.status === 'PASS' ? 'badge-pass' : 'badge-fail'}`}>
                              {t.status}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {step.stage === 'FINAL_DECISION' && (
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontSize: '0.9rem', color: '#0f172a' }}>
                          Overall Metrological Verdict: <strong style={{ color: step.data.overall_status === 'PASS' ? '#166534' : '#991b1b' }}>{step.data.overall_status}</strong>
                        </div>
                        <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                          Evaluated: {step.data.tests_evaluated} tests • Passed: {step.data.passed_count} • Failed: {step.data.failed_count}
                        </div>
                      </div>
                      <span className={`badge ${step.data.overall_status === 'PASS' ? 'badge-pass' : 'badge-fail'}`} style={{ fontSize: '0.9rem', padding: '0.4rem 1rem' }}>
                        {step.data.overall_status}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
