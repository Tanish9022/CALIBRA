import React from 'react';
import { X, HelpCircle, CheckCircle, XCircle, AlertTriangle, Scale, ShieldCheck, ArrowRight } from 'lucide-react';

export default function ExplainabilityModal({ isOpen, onClose, traceData }) {
  if (!isOpen || !traceData) return null;

  const isPass = traceData.status === 'PASS';
  const isFail = traceData.status === 'FAIL';

  const raw = traceData.raw_inputs || {};
  const norm = traceData.normalized_inputs || {};
  const calc = traceData.calculation_trace || {};
  const rule = traceData.rule_evaluated || {};
  const dec = traceData.decision || {};

  return (
    <div className="modal-overlay" style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      backgroundColor: 'rgba(15, 23, 42, 0.65)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 9999,
      padding: '1rem'
    }}>
      <div className="card modal-content" style={{
        width: '100%',
        maxWidth: '720px',
        maxHeight: '90vh',
        overflowY: 'auto',
        backgroundColor: '#ffffff',
        borderRadius: '16px',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
        padding: '2rem',
        border: '1px solid #e2e8f0'
      }}>
        {/* Header */}
        <div className="flex items-center justify-between" style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '1rem', marginBottom: '1.5rem' }}>
          <div className="flex items-center gap-2">
            <div style={{
              width: '36px', height: '36px', borderRadius: '10px',
              backgroundColor: isPass ? '#dcfce7' : (isFail ? '#fee2e2' : '#fef3c7'),
              display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              {isPass && <CheckCircle size={22} style={{ color: '#166534' }} />}
              {isFail && <XCircle size={22} style={{ color: '#991b1b' }} />}
              {!isPass && !isFail && <AlertTriangle size={22} style={{ color: '#92400e' }} />}
            </div>
            <div>
              <h2 style={{ fontSize: '1.25rem', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                Compliance Decision Derivation
                <span className={`badge ${isPass ? 'badge-pass' : (isFail ? 'badge-fail' : 'badge-review')}`} style={{ fontSize: '0.75rem', padding: '0.2rem 0.6rem' }}>
                  {traceData.status || 'EVALUATED'}
                </span>
              </h2>
              <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                Deterministic OIML R76-1:2006 Mathematical Trace • No Probabilistic Bias
              </span>
            </div>
          </div>
          <button onClick={onClose} style={{
            background: 'none', border: 'none', cursor: 'pointer', color: '#64748b', padding: '4px'
          }}>
            <X size={20} />
          </button>
        </div>

        {/* Narrative Reason */}
        <div style={{
          backgroundColor: isPass ? '#f0fdf4' : (isFail ? '#fef2f2' : '#fffbeb'),
          border: `1px solid ${isPass ? '#bbf7d0' : (isFail ? '#fecaca' : '#fde68a')}`,
          borderRadius: '10px',
          padding: '1rem',
          marginBottom: '1.5rem',
          fontSize: '0.9rem',
          lineHeight: '1.5',
          color: isPass ? '#166534' : (isFail ? '#991b1b' : '#92400e')
        }}>
          <strong>Decision Rationale:</strong> {traceData.explanation || dec.explanation || 'Result evaluated under applicable OIML R76 rules.'}
        </div>

        {/* Trace Pipeline Steps */}
        <h3 style={{ fontSize: '1rem', marginBottom: '1rem', color: '#0f172a' }}>
          Step-by-Step Calculation Lineage
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.5rem' }}>
          {/* Step 1: Input & Turning Point */}
          <div style={{ padding: '0.85rem', borderRadius: '8px', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0' }}>
            <div className="flex justify-between items-center" style={{ marginBottom: '0.3rem' }}>
              <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#334155' }}>
                1. Reference Load & Turning Point Correction (Clause A.4.4.3)
              </span>
              <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Turning Point ΔL</span>
            </div>
            <div style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: '#0f172a' }}>
              P = I + 0.5e - ΔL = {norm?.indication?.raw || raw?.indication || '0'} + 0.5({norm?.e?.raw || raw?.e || '10'}) - {norm?.delta_l?.raw || raw?.delta_l || '0'} = <strong>{calc.indication_p || calc.indication_prior_to_rounding_p || norm?.indication?.raw} g</strong>
            </div>
            <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.2rem' }}>
              Applied Reference Load L = {norm?.load?.raw || raw?.load} {norm?.load?.unit || raw?.load_unit} ({norm?.load?.normalized || raw?.load} g)
            </div>
          </div>

          {/* Step 2: Error Calculation */}
          <div style={{ padding: '0.85rem', borderRadius: '8px', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0' }}>
            <div className="flex justify-between items-center" style={{ marginBottom: '0.3rem' }}>
              <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#334155' }}>
                2. Error & Zero Correction (Clause A.4.4.1)
              </span>
              <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Ec = (P - L) - E0</span>
            </div>
            <div style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: '#0f172a' }}>
              Raw Error E = P - L = {calc.raw_error_E !== undefined ? `${calc.raw_error_E > 0 ? '+' : ''}${calc.raw_error_E} g` : 'N/A'}
            </div>
            <div style={{ fontFamily: 'monospace', fontSize: '0.85rem', color: '#0f172a', marginTop: '0.2rem' }}>
              Corrected Error Ec = E - E0 = <strong>{calc.corrected_error_Ec !== undefined ? `${calc.corrected_error_Ec > 0 ? '+' : ''}${calc.corrected_error_Ec} g` : (calc.error !== undefined ? `${calc.error > 0 ? '+' : ''}${calc.error} g` : 'N/A')}</strong>
              {calc.zero_error_E0 ? ` (Zero Error E0 = ${calc.zero_error_E0} g)` : ''}
            </div>
          </div>

          {/* Step 3: Applicable MPE Limit */}
          <div style={{ padding: '0.85rem', borderRadius: '8px', backgroundColor: '#f8fafc', border: '1px solid #e2e8f0' }}>
            <div className="flex justify-between items-center" style={{ marginBottom: '0.3rem' }}>
              <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#334155' }}>
                3. Applicable Maximum Permissible Error (Table 6)
              </span>
              <span style={{ fontSize: '0.75rem', color: '#2563eb', fontWeight: 500 }}>
                {rule.code || 'OIML R76-1:2006 Clause 3.5.1'}
              </span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem', marginTop: '0.3rem', fontSize: '0.8rem' }}>
              <div>
                <span style={{ color: '#64748b' }}>Load in intervals m:</span>
                <div style={{ fontWeight: 600 }}>{rule.load_in_e ? `${rule.load_in_e} e` : 'N/A'}</div>
              </div>
              <div>
                <span style={{ color: '#64748b' }}>MPE Multiplier:</span>
                <div style={{ fontWeight: 600 }}>
                  {rule.threshold_mpe && norm?.e?.normalized ? `±${(rule.threshold_mpe / norm.e.normalized).toFixed(1)} e` : '±1.0 e'}
                </div>
              </div>
              <div>
                <span style={{ color: '#64748b' }}>Permissible MPE Limit:</span>
                <div style={{ fontWeight: 600, color: '#0f172a' }}>
                  ±{rule.threshold_mpe ? Number(rule.threshold_mpe).toFixed(4) : 'N/A'} g
                </div>
              </div>
            </div>
          </div>

          {/* Step 4: Comparison & Final Gate */}
          <div style={{ padding: '0.85rem', borderRadius: '8px', backgroundColor: isPass ? '#f0fdf4' : '#fef2f2', border: `1px solid ${isPass ? '#86efac' : '#fca5a5'}` }}>
            <div className="flex justify-between items-center">
              <span style={{ fontWeight: 600, fontSize: '0.85rem', color: isPass ? '#166534' : '#991b1b' }}>
                4. Deterministic Compliance Comparison
              </span>
              <span style={{ fontWeight: 700, fontSize: '0.9rem', color: isPass ? '#166534' : '#991b1b' }}>
                {isPass ? 'COMPLIANT (PASS)' : 'NON-COMPLIANT (FAIL)'}
              </span>
            </div>
            <div style={{ fontFamily: 'monospace', fontSize: '0.9rem', marginTop: '0.3rem', color: '#0f172a' }}>
              |Ec| = {Math.abs(calc.corrected_error_Ec ?? calc.error ?? 0).toFixed(4)} g {isPass ? '≤' : '>'} MPE = {Number(rule.threshold_mpe ?? 0).toFixed(4)} g
            </div>
          </div>
        </div>

        {/* Metadata Footer */}
        <div style={{ borderTop: '1px solid #e2e8f0', paddingTop: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: '#64748b' }}>
          <div>
            Rule Version: <strong>{rule.edition ? `OIML R76 Edition ${rule.edition}` : 'OIML R76-1:2006'}</strong> • Calculation: <strong>v1.0-decimal34</strong>
          </div>
          <button className="btn btn-primary" onClick={onClose} style={{ padding: '0.4rem 1rem', fontSize: '0.85rem' }}>
            Close Explanation
          </button>
        </div>
      </div>
    </div>
  );
}
