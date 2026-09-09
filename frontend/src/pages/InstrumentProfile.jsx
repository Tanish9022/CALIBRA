import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Scale, Sparkles, ArrowRight, CheckCircle } from 'lucide-react';

const DEMO_PRESETS = {
  class3: {
    manufacturer: 'Mettler Toledo',
    model: 'MS205DU',
    instrument_type: 'NAWI',
    accuracy_class: 'III',
    max_capacity: 30.0,
    min_capacity: 0.2,
    verification_interval_e: 10.0, // 10g in grams
    number_of_intervals: 3000
  }
};

export default function InstrumentProfile() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState(DEMO_PRESETS.class3);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleChange = (e) => {
    const value = e.target.type === 'number' ? parseFloat(e.target.value) : e.target.value;
    setFormData({ ...formData, [e.target.name]: value });
  };

  const loadPreset = (presetKey) => {
    setFormData(DEMO_PRESETS[presetKey]);
  };

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setErrorMsg(null);

    try {
      // 1. Create Instrument
      const resInst = await fetch('/api/instruments/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          configuration_json: {
            platform_size: "200x200mm",
            standard: "OIML R76:2006"
          }
        })
      });

      if (!resInst.ok) {
        throw new Error(`Failed to create instrument (${resInst.statusText})`);
      }
      const instrument = await resInst.json();

      // For the demo, ruleset_id=1 exists from seed.py
      const ruleset_id = 1;

      // 2. Create Test Session
      const resSess = await fetch('/api/sessions/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          instrument_id: instrument.id,
          ruleset_id: ruleset_id,
          started_by: "Demo Tech"
        })
      });

      if (!resSess.ok) {
        throw new Error(`Failed to initialize session (${resSess.statusText})`);
      }
      const session = await resSess.json();

      // 3. Navigate to the Generated Test Plan stage
      navigate(`/test-plan?sessionId=${session.id}&instrumentId=${instrument.id}`);

    } catch (error) {
      console.error(error);
      setErrorMsg(error.message || 'Error creating instrument profile or test session.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="flex justify-between items-center" style={{ marginBottom: '1.5rem' }}>
        <div>
          <h1>Instrument Profile</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            Define NAWI metrological characteristics according to OIML R76 requirements.
          </p>
        </div>
        <div className="flex gap-3">
          <button 
            type="button" 
            className="btn btn-secondary flex items-center gap-2"
            onClick={() => loadPreset('class3')}
          >
            <Sparkles size={16} /> Load Demo Preset (Class III)
          </button>
          <button 
            type="button" 
            className="btn btn-primary flex items-center gap-2" 
            onClick={handleSubmit} 
            disabled={loading}
          >
            {loading ? 'Validating Profile...' : (
              <>
                Validate Profile & Generate Test Plan <ArrowRight size={16} />
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
          borderRadius: 'var(--radius-md)',
          marginBottom: '1.5rem'
        }}>
          <strong>Profile Validation Error:</strong> {errorMsg}
        </div>
      )}

      <div className="card">
        <div className="flex items-center justify-between pb-3" style={{ borderBottom: '1px solid var(--border-color)', marginBottom: '1.5rem' }}>
          <div className="flex items-center gap-2">
            <Scale size={20} style={{ color: 'var(--primary-600)' }} />
            <h3 style={{ margin: 0 }}>Metrological Specifications</h3>
          </div>
          <span className="badge badge-pass flex items-center gap-1">
            <CheckCircle size={12} /> Standard: OIML R76:2006
          </span>
        </div>

        <form className="grid grid-cols-2 gap-6" onSubmit={handleSubmit}>
          
          <div className="form-group">
            <label className="form-label">Manufacturer</label>
            <input 
              type="text" 
              name="manufacturer" 
              className="form-input" 
              value={formData.manufacturer} 
              onChange={handleChange} 
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Model Designation</label>
            <input 
              type="text" 
              name="model" 
              className="form-input" 
              value={formData.model} 
              onChange={handleChange} 
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Instrument Type</label>
            <select 
              name="instrument_type" 
              className="form-input" 
              value={formData.instrument_type} 
              onChange={handleChange}
            >
              <option value="NAWI">Non-Automatic Weighing Instrument (NAWI)</option>
              <option value="AWI">Automatic Weighing Instrument (AWI)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Accuracy Class</label>
            <select 
              name="accuracy_class" 
              className="form-input" 
              value={formData.accuracy_class} 
              onChange={handleChange}
            >
              <option value="I">Class I (Special Precision)</option>
              <option value="II">Class II (High Precision)</option>
              <option value="III">Class III (Medium Accuracy — Commercial)</option>
              <option value="IIII">Class IIII (Ordinary Accuracy)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Maximum Capacity, Max (kg)</label>
            <input 
              type="number" 
              step="any" 
              name="max_capacity" 
              className="form-input" 
              value={formData.max_capacity} 
              onChange={handleChange} 
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Minimum Capacity, Min (kg)</label>
            <input 
              type="number" 
              step="any" 
              name="min_capacity" 
              className="form-input" 
              value={formData.min_capacity} 
              onChange={handleChange} 
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Verification Scale Interval, e (g)</label>
            <input 
              type="number" 
              step="any" 
              name="verification_interval_e" 
              className="form-input" 
              value={formData.verification_interval_e} 
              onChange={handleChange} 
              required
            />
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.25rem', display: 'block' }}>
              Specified in grams (e.g. 10 g for 30 kg Class III instrument, n = 3000)
            </span>
          </div>

          <div className="form-group">
            <label className="form-label">Number of Verification Scale Intervals (n)</label>
            <input 
              type="number" 
              name="number_of_intervals" 
              className="form-input" 
              value={formData.number_of_intervals} 
              onChange={handleChange} 
              required
            />
          </div>

        </form>
      </div>
    </div>
  );
}
