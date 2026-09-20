import React, { useState } from 'react';
import { BookOpen, ShieldCheck, Scale, Compass, CheckCircle2, ChevronRight, Layers } from 'lucide-react';

export default function Rules() {
  const [selectedClass, setSelectedClass] = useState('III');

  const mpeTable = {
    'I': [
      { range: '0 ≤ m ≤ 50,000 e', factorInitial: '±0.5 e', factorInService: '±1.0 e', example: 'For e = 1mg: ±0.5 mg' },
      { range: '50,000 e < m ≤ 200,000 e', factorInitial: '±1.0 e', factorInService: '±2.0 e', example: 'For e = 1mg: ±1.0 mg' },
      { range: '200,000 e < m ≤ Max', factorInitial: '±1.5 e', factorInService: '±3.0 e', example: 'For e = 1mg: ±1.5 mg' }
    ],
    'II': [
      { range: '0 ≤ m ≤ 5,000 e', factorInitial: '±0.5 e', factorInService: '±1.0 e', example: 'For e = 0.01g: ±0.005 g' },
      { range: '5,000 e < m ≤ 20,000 e', factorInitial: '±1.0 e', factorInService: '±2.0 e', example: 'For e = 0.01g: ±0.010 g' },
      { range: '20,000 e < m ≤ 100,000 e', factorInitial: '±1.5 e', factorInService: '±3.0 e', example: 'For e = 0.01g: ±0.015 g' }
    ],
    'III': [
      { range: '0 ≤ m ≤ 500 e', factorInitial: '±0.5 e', factorInService: '±1.0 e', example: 'For e = 10g: ±5.0 g' },
      { range: '500 e < m ≤ 2,000 e', factorInitial: '±1.0 e', factorInService: '±2.0 e', example: 'For e = 10g: ±10.0 g' },
      { range: '2,000 e < m ≤ 10,000 e', factorInitial: '±1.5 e', factorInService: '±3.0 e', example: 'For e = 10g: ±15.0 g' }
    ],
    'IIII': [
      { range: '0 ≤ m ≤ 50 e', factorInitial: '±0.5 e', factorInService: '±1.0 e', example: 'For e = 0.5kg: ±0.25 kg' },
      { range: '50 e < m ≤ 200 e', factorInitial: '±1.0 e', factorInService: '±2.0 e', example: 'For e = 0.5kg: ±0.50 kg' },
      { range: '200 e < m ≤ 1,000 e', factorInitial: '±1.5 e', factorInService: '±3.0 e', example: 'For e = 0.5kg: ±0.75 kg' }
    ]
  };

  return (
    <div className="container" style={{ maxWidth: '1280px', margin: '0 auto', padding: '1.5rem' }}>
      {/* Title Header */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div className="flex items-center gap-2">
          <BookOpen size={28} style={{ color: 'var(--primary-600)' }} />
          <h1 style={{ margin: 0, fontSize: '1.75rem' }}>OIML R76 Versioned Ruleset Registry</h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', margin: '0.25rem 0 0', fontSize: '0.9rem' }}>
          Authoritative legal metrology standards, Table 6 Maximum Permissible Errors, and Clause 3.9.2 gravity requirements.
        </p>
      </div>

      {/* Ruleset Identity Card */}
      <div className="card" style={{ padding: '1.25rem', marginBottom: '1.5rem', backgroundColor: '#f8fafc' }}>
        <div className="flex justify-between items-center">
          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#2563eb' }}>ACTIVE STANDARD</span>
            <h3 style={{ margin: '0.2rem 0', fontSize: '1.15rem' }}>OIML Recommendation R 76-1:2006 (E)</h3>
            <p style={{ margin: 0, fontSize: '0.85rem', color: '#64748b' }}>
              Non-automatic weighing instruments — Part 1: Metrological and technical requirements - Tests
            </p>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span className="badge badge-pass" style={{ fontSize: '0.85rem' }}>PUBLISHED & VALIDATED</span>
            <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.3rem' }}>
              SHA-256: <code>76f9d261e4a1a382c7a9b09f7a5b3a4e</code>
            </div>
          </div>
        </div>
      </div>

      {/* Class Selector & Table 6 Explorer */}
      <div className="card" style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
        <div className="flex justify-between items-center" style={{ marginBottom: '1rem' }}>
          <h3 style={{ fontSize: '1.1rem', margin: 0, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Scale size={18} style={{ color: 'var(--primary-600)' }} />
            Clause 3.5.1 & Table 6: Maximum Permissible Errors on Initial Verification
          </h3>

          <div className="flex gap-2">
            {['I', 'II', 'III', 'IIII'].map(cls => (
              <button
                key={cls}
                className={`btn ${selectedClass === cls ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setSelectedClass(cls)}
                style={{ padding: '0.35rem 0.85rem', fontSize: '0.85rem' }}
              >
                Class {cls}
              </button>
            ))}
          </div>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #e2e8f0', textAlign: 'left', color: '#64748b' }}>
              <th style={{ padding: '0.75rem' }}>Load m (in Verification Intervals e)</th>
              <th style={{ padding: '0.75rem' }}>MPE Initial Verification (Clause 3.5.1)</th>
              <th style={{ padding: '0.75rem' }}>MPE In-Service (Clause 3.5.2)</th>
              <th style={{ padding: '0.75rem' }}>Typical Tolerance Example</th>
            </tr>
          </thead>
          <tbody>
            {mpeTable[selectedClass].map((row, idx) => (
              <tr key={idx} style={{ borderBottom: '1px solid #f1f5f9' }}>
                <td style={{ padding: '0.75rem', fontWeight: 600, fontFamily: 'monospace' }}>
                  {row.range}
                </td>
                <td style={{ padding: '0.75rem', color: '#166534', fontWeight: 600 }}>
                  {row.factorInitial}
                </td>
                <td style={{ padding: '0.75rem', color: '#92400e', fontWeight: 600 }}>
                  {row.factorInService}
                </td>
                <td style={{ padding: '0.75rem', color: '#475569' }}>
                  {row.example}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Metrology Clauses Overview Grid */}
      <div className="grid grid-cols-2 gap-6">
        <div className="card" style={{ padding: '1.25rem' }}>
          <h4 style={{ fontSize: '0.95rem', color: '#0f172a', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Compass size={16} style={{ color: '#2563eb' }} />
            Clause 3.9.2: Gravity Dependency
          </h4>
          <p style={{ fontSize: '0.82rem', color: '#475569', lineHeight: '1.5' }}>
            If an instrument is sensitive to differences of gravity acceleration, it shall be adjusted for the gravity of the place of use, or tested at the place of use, or marked with gravity zones. CALIBRA enforces this by flagging location transfers where Δg exceeds permissible MPE tolerances.
          </p>
        </div>

        <div className="card" style={{ padding: '1.25rem' }}>
          <h4 style={{ fontSize: '0.95rem', color: '#0f172a', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Layers size={16} style={{ color: '#2563eb' }} />
            Clause A.4.4.3: Digital Indication Turning Point
          </h4>
          <p style={{ fontSize: '0.82rem', color: '#475569', lineHeight: '1.5' }}>
            For instruments with digital indication without a continuous reading device, the indication prior to rounding is determined by adding additional weights ΔL until the indication flickers to the next step: <code>P = I + 0.5e - ΔL</code>, eliminating rounding error from observations.
          </p>
        </div>
      </div>
    </div>
  );
}
