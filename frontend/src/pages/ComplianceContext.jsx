import React, { useState, useEffect } from 'react';
import { 
  Compass, 
  MapPin, 
  Calculator, 
  ArrowRight, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  Layers, 
  HelpCircle,
  RefreshCw,
  Info
} from 'lucide-react';

export default function ComplianceContext() {
  const [locations, setLocations] = useState([]);
  const [loading, setLoading] = useState(false);

  // Somigliana Calculator State
  const [calcLat, setCalcLat] = useState(28.6139);
  const [calcElev, setCalcElev] = useState(216);
  const [calcResult, setCalcResult] = useState(null);

  // Transferability Sandbox State
  const [selectedClass, setSelectedClass] = useState('III');
  const [maxCapacity, setMaxCapacity] = useState(30.0);
  const [intervalE, setIntervalE] = useState(10.0);
  const [hasInternalCal, setHasInternalCal] = useState(false);
  const [isGravitySensitive, setIsGravitySensitive] = useState(true);
  const [originLocation, setOriginLocation] = useState('New Delhi Central Laboratory');
  const [destLocation, setDestLocation] = useState('Leh Ladakh High-Altitude Facility');
  const [originG, setOriginG] = useState(9.7912);
  const [destG, setDestG] = useState(9.7744);
  const [transferResult, setTransferResult] = useState(null);

  useEffect(() => {
    fetch('/api/compliance-context/locations')
      .then(res => res.ok ? res.json() : [])
      .then(data => {
        if (data && data.length > 0) {
          setLocations(data);
          const delhi = data.find(l => l.name.includes('Delhi'));
          const leh = data.find(l => l.name.includes('Leh'));
          if (delhi) {
            setOriginLocation(delhi.name);
            setOriginG(delhi.declared_gravity);
          }
          if (leh) {
            setDestLocation(leh.name);
            setDestG(leh.declared_gravity);
          }
        }
      })
      .catch(console.error);

    // Initial estimate calculation
    runSomiglianaEstimate(28.6139, 216);
  }, []);

  const runSomiglianaEstimate = async (lat, elev) => {
    try {
      const res = await fetch('/api/compliance-context/estimate-gravity', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ latitude_deg: parseFloat(lat), elevation_m: parseFloat(elev) })
      });
      if (res.ok) {
        const data = await res.json();
        setCalcResult(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleOriginChange = (locName) => {
    setOriginLocation(locName);
    const loc = locations.find(l => l.name === locName);
    if (loc) setOriginG(loc.declared_gravity);
  };

  const handleDestChange = (locName) => {
    setDestLocation(locName);
    const loc = locations.find(l => l.name === locName);
    if (loc) setDestG(loc.declared_gravity);
  };

  const evaluateTransfer = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/compliance-context/evaluate-transferability', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          accuracy_class: selectedClass,
          max_capacity_kg: parseFloat(maxCapacity),
          verification_interval_e_g: parseFloat(intervalE),
          has_internal_calibration: hasInternalCal,
          is_gravity_sensitive: isGravitySensitive,
          test_location_name: originLocation,
          test_gravity_ms2: parseFloat(originG),
          intended_location_name: destLocation,
          intended_gravity_ms2: parseFloat(destG)
        })
      });
      if (res.ok) {
        const data = await res.json();
        setTransferResult(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Run transfer evaluation when inputs change
  useEffect(() => {
    evaluateTransfer();
  }, [selectedClass, maxCapacity, intervalE, hasInternalCal, isGravitySensitive, originLocation, destLocation, originG, destG]);

  return (
    <div className="container" style={{ maxWidth: '1280px', margin: '0 auto', padding: '1.5rem' }}>
      {/* Title & Context Banner */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div className="flex items-center gap-2">
          <Compass size={28} style={{ color: 'var(--primary-600)' }} />
          <h1 style={{ margin: 0, fontSize: '1.75rem' }}>Gravity & Location Compliance Engine</h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', margin: '0.25rem 0 0', fontSize: '0.9rem' }}>
          OIML R76-1:2006 Clause 3.9.2: Metrological characteristics depending on acceleration of gravity.
        </p>
      </div>

      {/* Metrological Safety Callout */}
      <div style={{
        backgroundColor: '#eff6ff',
        border: '1px solid #bfdbfe',
        borderRadius: '10px',
        padding: '1rem',
        marginBottom: '1.5rem',
        display: 'flex',
        gap: '0.75rem',
        alignItems: 'flex-start'
      }}>
        <Info size={20} style={{ color: '#2563eb', flexShrink: 0, marginTop: '2px' }} />
        <div style={{ fontSize: '0.85rem', color: '#1e3a8a', lineHeight: '1.5' }}>
          <strong>Core Metrology Principle:</strong> CALIBRA does not physically calibrate or change the scale mechanism.
          Instead, CALIBRA mathematically determines whether a verified legal result remains valid at an intended destination or whether the gravitational shift requires on-site re-testing.
        </div>
      </div>

      {/* Main 2-Column Grid */}
      <div className="grid grid-cols-2 gap-6" style={{ alignItems: 'start' }}>
        
        {/* Left Column: Transferability Sandbox */}
        <div className="card" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.15rem', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem' }}>
            <MapPin size={20} style={{ color: 'var(--primary-600)' }} />
            Clause 3.9.2 Transferability Sandbox
          </h3>

          {/* Instrument Parameters */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem', marginBottom: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Accuracy Class</label>
              <select
                value={selectedClass}
                onChange={(e) => setSelectedClass(e.target.value)}
                style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '0.85rem' }}
              >
                <option value="I">Class I (Special)</option>
                <option value="II">Class II (High)</option>
                <option value="III">Class III (Medium)</option>
                <option value="IIII">Class IIII (Ordinary)</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Max (kg)</label>
              <input
                type="number"
                value={maxCapacity}
                onChange={(e) => setMaxCapacity(e.target.value)}
                style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '0.85rem' }}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Interval e (g)</label>
              <input
                type="number"
                value={intervalE}
                onChange={(e) => setIntervalE(e.target.value)}
                style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '0.85rem' }}
              />
            </div>
          </div>

          {/* Instrument Switches */}
          <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1.25rem', padding: '0.75rem', backgroundColor: '#f8fafc', borderRadius: '8px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.82rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={hasInternalCal}
                onChange={(e) => setHasInternalCal(e.target.checked)}
              />
              Internal Auto-Calibration Weight
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.82rem', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={isGravitySensitive}
                onChange={(e) => setIsGravitySensitive(e.target.checked)}
              />
              Gravity-Sensitive Transducer
            </label>
          </div>

          {/* Location Origin & Destination */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
            {/* Origin Location */}
            <div style={{ padding: '0.85rem', backgroundColor: '#f1f5f9', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#475569' }}>
                1. Test Location (Origin)
              </label>
              <select
                value={originLocation}
                onChange={(e) => handleOriginChange(e.target.value)}
                style={{ width: '100%', padding: '0.45rem', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '0.8rem', marginTop: '0.2rem' }}
              >
                {locations.map(l => (
                  <option key={l.id} value={l.name}>{l.name} ({l.declared_gravity} m/s²)</option>
                ))}
              </select>
              <div style={{ fontSize: '0.8rem', color: '#334155', marginTop: '0.3rem' }}>
                Local g: <strong>{originG} m/s²</strong>
              </div>
            </div>

            {/* Destination Location */}
            <div style={{ padding: '0.85rem', backgroundColor: '#fef2f2', borderRadius: '8px', border: '1px solid #fecaca' }}>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#991b1b' }}>
                2. Intended Location (Destination)
              </label>
              <select
                value={destLocation}
                onChange={(e) => handleDestChange(e.target.value)}
                style={{ width: '100%', padding: '0.45rem', borderRadius: '6px', border: '1px solid #fca5a5', fontSize: '0.8rem', marginTop: '0.2rem' }}
              >
                {locations.map(l => (
                  <option key={l.id} value={l.name}>{l.name} ({l.declared_gravity} m/s²)</option>
                ))}
              </select>
              <div style={{ fontSize: '0.8rem', color: '#991b1b', marginTop: '0.3rem' }}>
                Local g: <strong>{destG} m/s²</strong>
              </div>
            </div>
          </div>

          {/* Transferability Verdict Box */}
          {transferResult && (
            <div style={{
              padding: '1.25rem',
              borderRadius: '10px',
              backgroundColor: transferResult.is_transferable ? '#f0fdf4' : (transferResult.decision === 'CONDITIONAL' ? '#fffbeb' : '#fef2f2'),
              border: `1px solid ${transferResult.is_transferable ? '#86efac' : (transferResult.decision === 'CONDITIONAL' ? '#fde68a' : '#fca5a5')}`,
            }}>
              <div className="flex justify-between items-center" style={{ marginBottom: '0.5rem' }}>
                <span style={{
                  fontWeight: 700,
                  fontSize: '0.95rem',
                  color: transferResult.is_transferable ? '#166534' : (transferResult.decision === 'CONDITIONAL' ? '#92400e' : '#991b1b')
                }}>
                  DECISION: {transferResult.decision}
                </span>
                <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                  {transferResult.r76_clause}
                </span>
              </div>

              <p style={{ fontSize: '0.85rem', color: '#334155', margin: '0 0 1rem', lineHeight: '1.4' }}>
                {transferResult.reason}
              </p>

              {/* Metrics Breakdown */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem', textAlign: 'center', backgroundColor: '#ffffff', padding: '0.75rem', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div>
                  <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Relative Gravity Shift</div>
                  <div style={{ fontSize: '1rem', fontWeight: 700, color: transferResult.is_transferable ? '#166534' : '#dc2626' }}>
                    {transferResult.relative_delta_g_ppm || 0} ppm
                  </div>
                  <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>Δg = {transferResult.delta_g_ms2?.toFixed(4)} m/s²</div>
                </div>

                <div>
                  <div style={{ fontSize: '0.7rem', color: '#64748b' }}>Permissible MPE Limit</div>
                  <div style={{ fontSize: '1rem', fontWeight: 700, color: '#2563eb' }}>
                    {transferResult.relative_mpe_ppm || 'N/A'} ppm
                  </div>
                  <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>±{transferResult.mpe_at_max_g} g at Max</div>
                </div>

                <div>
                  <div style={{ fontSize: '0.7rem', color: '#64748b' }}>1/3 MPE Limit</div>
                  <div style={{ fontSize: '1rem', fontWeight: 700, color: '#059669' }}>
                    {transferResult.one_third_mpe_ppm || 'N/A'} ppm
                  </div>
                  <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>Transfer Threshold</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column: Somigliana Calculator & Reference Locations */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Somigliana Theoretical Calculator Card */}
          <div className="card" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1.15rem', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <Calculator size={20} style={{ color: 'var(--primary-600)' }} />
              Somigliana (WGS84) Gravity Estimator
            </h3>
            <p style={{ fontSize: '0.8rem', color: '#64748b', margin: '0 0 1rem' }}>
              Theoretical normal gravity formula + Free-air elevation reduction (-3.086 µGal/m).
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '0.75rem', marginBottom: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#475569' }}>Latitude (°N)</label>
                <input
                  type="number"
                  step="0.0001"
                  value={calcLat}
                  onChange={(e) => {
                    setCalcLat(e.target.value);
                    runSomiglianaEstimate(e.target.value, calcElev);
                  }}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '0.85rem' }}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#475569' }}>Elevation (meters)</label>
                <input
                  type="number"
                  value={calcElev}
                  onChange={(e) => {
                    setCalcElev(e.target.value);
                    runSomiglianaEstimate(calcLat, e.target.value);
                  }}
                  style={{ width: '100%', padding: '0.5rem', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '0.85rem' }}
                />
              </div>
            </div>

            {calcResult && (
              <div style={{ backgroundColor: '#f8fafc', padding: '1rem', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '0.85rem' }}>
                <div className="flex justify-between items-center" style={{ marginBottom: '0.3rem' }}>
                  <span style={{ color: '#64748b' }}>Sea-Level Normal Gravity γ(φ):</span>
                  <strong>{calcResult.sea_level_gravity_ms2} m/s²</strong>
                </div>
                <div className="flex justify-between items-center" style={{ marginBottom: '0.3rem' }}>
                  <span style={{ color: '#64748b' }}>Free-Air Elevation Reduction Δg:</span>
                  <span style={{ color: '#dc2626' }}>{calcResult.free_air_correction_ms2} m/s²</span>
                </div>
                <div className="flex justify-between items-center" style={{ borderTop: '1px solid #e2e8f0', paddingTop: '0.4rem', marginTop: '0.4rem' }}>
                  <span style={{ fontWeight: 600, color: '#0f172a' }}>Local Estimated Acceleration:</span>
                  <strong style={{ fontSize: '1.1rem', color: '#2563eb' }}>
                    {calcResult.estimated_gravity_ms2} m/s²
                  </strong>
                </div>
              </div>
            )}
          </div>

          {/* Reference Testing Locations Table */}
          <div className="card" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1.15rem', display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <Layers size={20} style={{ color: 'var(--primary-600)' }} />
              National & Reference Locations
            </h3>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', fontSize: '0.8rem', borderCollapse: 'collapse', marginTop: '0.5rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #e2e8f0', textAlign: 'left', color: '#64748b' }}>
                    <th style={{ padding: '0.4rem' }}>Location</th>
                    <th style={{ padding: '0.4rem' }}>Elevation</th>
                    <th style={{ padding: '0.4rem' }}>Declared g</th>
                  </tr>
                </thead>
                <tbody>
                  {locations.map(loc => (
                    <tr key={loc.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                      <td style={{ padding: '0.5rem 0.4rem', fontWeight: 500 }}>{loc.name}</td>
                      <td style={{ padding: '0.5rem 0.4rem', color: '#64748b' }}>{loc.elevation} m</td>
                      <td style={{ padding: '0.5rem 0.4rem', fontFamily: 'monospace', fontWeight: 600, color: '#2563eb' }}>
                        {loc.declared_gravity} m/s²
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
