import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Instruments() {
  const navigate = useNavigate();
  const [instruments, setInstruments] = useState([]);
  const [loadingList, setLoadingList] = useState(true);
  
  const [showCreate, setShowCreate] = useState(false);
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

  useEffect(() => {
    fetchInstruments();
  }, []);

  const fetchInstruments = async () => {
    try {
      const res = await fetch('/api/instruments/');
      const data = await res.json();
      setInstruments(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingList(false);
    }
  };

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

      navigate(`/workspace?sessionId=${session.id}`);

    } catch (error) {
      console.error(error);
      alert('Error creating instrument or session.');
    } finally {
      setLoading(false);
    }
  };

  const handleStartSession = async (instrumentId) => {
    try {
      const resSess = await fetch('/api/sessions/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          instrument_id: instrumentId,
          ruleset_id: 1, // Defaulting to 1 for MVP
          started_by: "Demo Tech"
        })
      });
      const session = await resSess.json();
      navigate(`/workspace?sessionId=${session.id}`);
    } catch (err) {
      console.error(err);
      alert('Failed to start session.');
    }
  };

  return (
    <div className="animate-fade-in">
      <div className="flex justify-between items-center" style={{ marginBottom: '1.5rem' }}>
        <h1>Instruments</h1>
        <button className="btn btn-primary" onClick={() => setShowCreate(!showCreate)}>
          {showCreate ? 'Cancel' : 'Register New Instrument'}
        </button>
      </div>

      {showCreate && (
        <div className="card animate-slide-down" style={{ marginBottom: '2rem' }}>
          <h3 style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', marginBottom: '1rem' }}>New Instrument Profile</h3>
          <form className="grid grid-cols-2 gap-6" onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label">Manufacturer</label>
              <input type="text" name="manufacturer" className="form-input" value={formData.manufacturer} onChange={handleChange} required />
            </div>

            <div className="form-group">
              <label className="form-label">Model</label>
              <input type="text" name="model" className="form-input" value={formData.model} onChange={handleChange} required />
            </div>

            <div className="form-group">
              <label className="form-label">Instrument Type</label>
              <select name="instrument_type" className="form-select" value={formData.instrument_type} onChange={handleChange}>
                <option value="NAWI">Non-Automatic Weighing Instrument (NAWI)</option>
                <option value="AWI">Automatic Weighing Instrument (AWI)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Accuracy Class</label>
              <select name="accuracy_class" className="form-select" value={formData.accuracy_class} onChange={handleChange}>
                <option value="I">Class I (Special)</option>
                <option value="II">Class II (High)</option>
                <option value="III">Class III (Medium)</option>
                <option value="IIII">Class IIII (Ordinary)</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Max Capacity (kg)</label>
              <input type="number" step="any" name="max_capacity" className="form-input" value={formData.max_capacity} onChange={handleChange} required />
            </div>

            <div className="form-group">
              <label className="form-label">Min Capacity (kg)</label>
              <input type="number" step="any" name="min_capacity" className="form-input" value={formData.min_capacity} onChange={handleChange} required />
            </div>

            <div className="form-group">
              <label className="form-label">Verification Interval, e (kg)</label>
              <input type="number" step="any" name="verification_interval_e" className="form-input" value={formData.verification_interval_e} onChange={handleChange} required />
            </div>

            <div className="form-group">
              <label className="form-label">Number of Intervals (n)</label>
              <input type="number" name="number_of_intervals" className="form-input" value={formData.number_of_intervals} onChange={handleChange} required />
            </div>
            
            <div className="form-group" style={{ gridColumn: 'span 2', display: 'flex', justifyContent: 'flex-end' }}>
              <button className="btn btn-primary" type="submit" disabled={loading}>
                {loading ? 'Processing...' : 'Validate Profile & Generate Test Plan'}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="card">
        <h3 style={{ marginBottom: '1rem' }}>Registered Instruments</h3>
        {loadingList ? (
          <p className="text-secondary">Loading...</p>
        ) : instruments.length === 0 ? (
          <p className="text-secondary">No instruments registered yet.</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)'}}>
                  <th style={{ padding: '0.75rem' }}>ID</th>
                  <th style={{ padding: '0.75rem' }}>Manufacturer</th>
                  <th style={{ padding: '0.75rem' }}>Model</th>
                  <th style={{ padding: '0.75rem' }}>Class</th>
                  <th style={{ padding: '0.75rem' }}>Max (kg)</th>
                  <th style={{ padding: '0.75rem' }}>e (kg)</th>
                  <th style={{ padding: '0.75rem' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {instruments.map(inst => (
                  <tr key={inst.id} style={{ borderBottom: '1px solid rgba(35, 53, 84, 0.5)' }}>
                    <td style={{ padding: '0.75rem' }}>{inst.id}</td>
                    <td style={{ padding: '0.75rem', fontWeight: 500 }}>{inst.manufacturer}</td>
                    <td style={{ padding: '0.75rem' }}>{inst.model}</td>
                    <td style={{ padding: '0.75rem' }}>{inst.accuracy_class}</td>
                    <td style={{ padding: '0.75rem' }}>{inst.max_capacity}</td>
                    <td style={{ padding: '0.75rem' }}>{inst.verification_interval_e}</td>
                    <td style={{ padding: '0.75rem' }}>
                      <button className="btn btn-secondary" onClick={() => handleStartSession(inst.id)} style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}>
                        Start New Test
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
