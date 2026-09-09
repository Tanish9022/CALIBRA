import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function InstrumentProfile() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    manufacturer: 'Mettler Toledo',
    model: 'MS205DU',
    instrument_type: 'NAWI',
    accuracy_class: 'III',
    max_capacity: 30.0,
    min_capacity: 0.2,
    verification_interval_e: 0.01,
    number_of_intervals: 3000
  });

  const handleChange = (e) => {
    const value = e.target.type === 'number' ? parseFloat(e.target.value) : e.target.value;
    setFormData({ ...formData, [e.target.name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // 1. Create Instrument
      const resInst = await fetch('/api/instruments/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          configuration_json: {}
        })
      });
      const instrument = await resInst.json();

      // For the demo, we assume ruleset_id=1 exists from seed.py
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
      const session = await resSess.json();

      // 3. Navigate to workspace with session ID
      navigate(`/workspace?sessionId=${session.id}`);

    } catch (error) {
      console.error(error);
      alert('Error creating instrument or session.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="flex justify-between items-center" style={{ marginBottom: '1.5rem' }}>
        <h1>Instrument Profile</h1>
        <button className="btn btn-primary" onClick={handleSubmit} disabled={loading}>
          {loading ? 'Processing...' : 'Validate Profile & Generate Test Plan'}
        </button>
      </div>

      <div className="card">
        <form className="grid grid-cols-2 gap-6" onSubmit={handleSubmit}>
          
          <div className="form-group">
            <label className="form-label">Manufacturer</label>
            <input type="text" name="manufacturer" className="form-input" value={formData.manufacturer} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label className="form-label">Model</label>
            <input type="text" name="model" className="form-input" value={formData.model} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label className="form-label">Instrument Type</label>
            <select name="instrument_type" className="form-input" value={formData.instrument_type} onChange={handleChange}>
              <option value="NAWI">Non-Automatic Weighing Instrument (NAWI)</option>
              <option value="AWI">Automatic Weighing Instrument (AWI)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Accuracy Class</label>
            <select name="accuracy_class" className="form-input" value={formData.accuracy_class} onChange={handleChange}>
              <option value="I">Class I (Special)</option>
              <option value="II">Class II (High)</option>
              <option value="III">Class III (Medium)</option>
              <option value="IIII">Class IIII (Ordinary)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Max Capacity (kg)</label>
            <input type="number" step="any" name="max_capacity" className="form-input" value={formData.max_capacity} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label className="form-label">Min Capacity (kg)</label>
            <input type="number" step="any" name="min_capacity" className="form-input" value={formData.min_capacity} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label className="form-label">Verification Interval, e (kg)</label>
            <input type="number" step="any" name="verification_interval_e" className="form-input" value={formData.verification_interval_e} onChange={handleChange} />
          </div>

          <div className="form-group">
            <label className="form-label">Number of Intervals (n)</label>
            <input type="number" name="number_of_intervals" className="form-input" value={formData.number_of_intervals} onChange={handleChange} />
          </div>

        </form>
      </div>
    </div>
  );
}
