import React, { useState, useEffect } from 'react';
import { ShieldCheck, AlertTriangle, Scale, Plus, CheckCircle, Clock, FileCheck } from 'lucide-react';

export default function Equipment() {
  const [equipment, setEquipment] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  // New Equipment form state
  const [eqId, setEqId] = useState('');
  const [name, setName] = useState('');
  const [eqType, setEqType] = useState('STANDARD_WEIGHTS');
  const [classStd, setClassStd] = useState('M1');
  const [mfg, setMfg] = useState('');
  const [cert, setCert] = useState('');
  const [traceRef, setTraceRef] = useState('');

  const loadEquipment = () => {
    setLoading(true);
    fetch('/api/equipment/')
      .then(res => res.ok ? res.json() : [])
      .then(data => setEquipment(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadEquipment();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/equipment/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          equipment_id: eqId,
          name: name,
          equipment_type: eqType,
          class_standard: classStd,
          manufacturer: mfg,
          certificate_number: cert,
          traceability_reference: traceRef,
          status: 'VALID'
        })
      });
      if (res.ok) {
        setShowAddModal(false);
        loadEquipment();
        // Reset form
        setEqId('');
        setName('');
        setCert('');
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="container" style={{ maxWidth: '1280px', margin: '0 auto', padding: '1.5rem' }}>
      {/* Title Header */}
      <div className="flex justify-between items-center" style={{ marginBottom: '1.5rem' }}>
        <div>
          <div className="flex items-center gap-2">
            <Scale size={28} style={{ color: 'var(--primary-600)' }} />
            <h1 style={{ margin: 0, fontSize: '1.75rem' }}>Test Standards & Equipment Registry</h1>
          </div>
          <p style={{ color: 'var(--text-secondary)', margin: '0.25rem 0 0', fontSize: '0.9rem' }}>
            ISO/IEC 17025 & OIML R76 Standards Traceability. Uncalibrated equipment blocks test report issuance.
          </p>
        </div>

        <button className="btn btn-primary" onClick={() => setShowAddModal(true)} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <Plus size={16} /> Register Standard
        </button>
      </div>

      {/* Equipment Table */}
      <div className="card" style={{ padding: '1rem' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #e2e8f0', textAlign: 'left', color: '#64748b' }}>
              <th style={{ padding: '0.75rem' }}>Equipment ID</th>
              <th style={{ padding: '0.75rem' }}>Name & Standard</th>
              <th style={{ padding: '0.75rem' }}>Class</th>
              <th style={{ padding: '0.75rem' }}>Certificate</th>
              <th style={{ padding: '0.75rem' }}>Traceability Ref</th>
              <th style={{ padding: '0.75rem' }}>Calibration Expiry</th>
              <th style={{ padding: '0.75rem' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {equipment.map(eq => {
              const isExpired = eq.status === 'EXPIRED';
              return (
                <tr key={eq.id} style={{ borderBottom: '1px solid #f1f5f9', backgroundColor: isExpired ? '#fff1f2' : 'transparent' }}>
                  <td style={{ padding: '0.75rem', fontWeight: 600, fontFamily: 'monospace' }}>
                    {eq.equipment_id}
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    <div style={{ fontWeight: 600, color: '#0f172a' }}>{eq.name}</div>
                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{eq.manufacturer || 'Standard Lab'}</div>
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    <span style={{ fontWeight: 600, color: '#2563eb' }}>Class {eq.class_standard || 'N/A'}</span>
                  </td>
                  <td style={{ padding: '0.75rem', fontFamily: 'monospace', color: '#475569' }}>
                    {eq.certificate_number || 'NPL-PENDING'}
                  </td>
                  <td style={{ padding: '0.75rem', color: '#475569' }}>
                    {eq.traceability_reference || 'NPL/SI/MASS'}
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    {eq.calibration_expiry ? String(eq.calibration_expiry).slice(0, 10) : '2027-01-01'}
                  </td>
                  <td style={{ padding: '0.75rem' }}>
                    <span className={`badge ${isExpired ? 'badge-fail' : 'badge-pass'}`}>
                      {eq.status}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(15, 23, 42, 0.6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
        }}>
          <div className="card" style={{ width: '480px', backgroundColor: '#ffffff', padding: '2rem' }}>
            <h3 style={{ marginBottom: '1rem' }}>Register Test Equipment</h3>
            <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600 }}>Equipment ID</label>
                <input required value={eqId} onChange={e => setEqId(e.target.value)} placeholder="e.g. EQ-F1-005" style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #cbd5e1' }} />
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600 }}>Name / Description</label>
                <input required value={name} onChange={e => setName(e.target.value)} placeholder="e.g. 20 kg Stainless Steel Test Standard" style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #cbd5e1' }} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.5rem' }}>
                <div>
                  <label style={{ fontSize: '0.75rem', fontWeight: 600 }}>Standard Class</label>
                  <select value={classStd} onChange={e => setClassStd(e.target.value)} style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #cbd5e1' }}>
                    <option value="E2">Class E2</option>
                    <option value="F1">Class F1</option>
                    <option value="F2">Class F2</option>
                    <option value="M1">Class M1</option>
                  </select>
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', fontWeight: 600 }}>Manufacturer</label>
                  <input value={mfg} onChange={e => setMfg(e.target.value)} placeholder="e.g. Häfner / Troemner" style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #cbd5e1' }} />
                </div>
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600 }}>Certificate Number</label>
                <input value={cert} onChange={e => setCert(e.target.value)} placeholder="e.g. NPL-IND-CAL-2026-99" style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #cbd5e1' }} />
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600 }}>Traceability Reference</label>
                <input value={traceRef} onChange={e => setTraceRef(e.target.value)} placeholder="e.g. NPL/SI/MASS-01" style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #cbd5e1' }} />
              </div>

              <div className="flex justify-between" style={{ marginTop: '1rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowAddModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Save Standard</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
