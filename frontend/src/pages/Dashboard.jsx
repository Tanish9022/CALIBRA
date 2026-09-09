import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Activity, 
  AlertCircle, 
  CheckCircle, 
  XCircle, 
  ArrowRight, 
  PlusCircle, 
  Zap
} from 'lucide-react';

export default function Dashboard() {
  const navigate = useNavigate();

  const [activeCount, setActiveCount] = useState(1);
  const [sessions] = useState([
    {
      id: 1,
      name: 'Session #1',
      instrument: 'Mettler Toledo - MS205DU (Class III, Max 30kg)',
      status: 'IN_PROGRESS',
      badge: 'ACTIVE',
      badgeClass: 'badge'
    },
    {
      id: 1024,
      name: 'Session #1024',
      instrument: 'Mettler Toledo - MS205DU (Class III)',
      status: 'COMPLETED',
      badge: 'PASS',
      badgeClass: 'badge-pass'
    },
    {
      id: 1025,
      name: 'Session #1025',
      instrument: 'Ohaus - Adventurer AX224',
      status: 'REVIEW',
      badge: 'REVIEW',
      badgeClass: 'badge-review'
    },
    {
      id: 1026,
      name: 'Session #1026',
      instrument: 'Sartorius - Cubis II',
      status: 'FAILED',
      badge: 'FAIL',
      badgeClass: 'badge-fail'
    }
  ]);

  useEffect(() => {
    fetch('/api/instruments/')
      .then(res => res.ok ? res.json() : [])
      .then(data => {
        if (data && data.length > 0) {
          setActiveCount(data.length);
        }
      })
      .catch(() => {});
  }, []);

  return (
    <div className="animate-fade-in flex flex-col gap-6">
      
      {/* Header Banner */}
      <div className="flex justify-between items-center">
        <div>
          <h1>Legal Metrology Dashboard</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            Automated OIML R76 Compliance & Verification Management System
          </p>
        </div>

        <div className="flex gap-3">
          <button 
            type="button" 
            className="btn btn-secondary flex items-center gap-2"
            onClick={() => navigate('/workspace?sessionId=1')}
          >
            <Activity size={16} /> Resume Active Session #1
          </button>
          <button 
            type="button" 
            className="btn btn-primary flex items-center gap-2"
            onClick={() => navigate('/instruments')}
          >
            <PlusCircle size={16} /> Start New Inspection <ArrowRight size={16} />
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-6">
        <div className="card flex flex-col gap-2">
          <div className="flex items-center justify-between text-secondary">
            <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>Active Tests</span>
            <Activity size={18} style={{ color: 'var(--primary-600)' }} />
          </div>
          <span style={{ fontSize: '1.75rem', fontWeight: 700 }}>{activeCount}</span>
        </div>
        
        <div className="card flex flex-col gap-2">
          <div className="flex items-center justify-between text-secondary">
            <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>Pending Review</span>
            <AlertCircle size={18} style={{ color: 'var(--status-review-text)' }} />
          </div>
          <span style={{ fontSize: '1.75rem', fontWeight: 700 }}>1</span>
        </div>
        
        <div className="card flex flex-col gap-2">
          <div className="flex items-center justify-between text-secondary">
            <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>Completed Tests</span>
            <CheckCircle size={18} style={{ color: 'var(--status-pass-text)' }} />
          </div>
          <span style={{ fontSize: '1.75rem', fontWeight: 700 }}>148</span>
        </div>

        <div className="card flex flex-col gap-2">
          <div className="flex items-center justify-between text-secondary">
            <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>Failed Tests</span>
            <XCircle size={18} style={{ color: 'var(--status-fail-text)' }} />
          </div>
          <span style={{ fontSize: '1.75rem', fontWeight: 700 }}>1</span>
        </div>
      </div>

      {/* Core Workflow Callout */}
      <div className="card" style={{ backgroundColor: 'var(--primary-50)', borderColor: 'var(--primary-100)' }}>
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div style={{
              width: '40px',
              height: '40px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: 'var(--shadow-sm)'
            }}>
              <Zap size={22} style={{ color: 'var(--primary-600)' }} />
            </div>
            <div>
              <h4 style={{ margin: 0, color: 'var(--primary-700)' }}>Standard OIML R76 Compliance Workflow</h4>
              <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                Instrument Profile → Auto Test Plan → Observation Entry → Deterministic Validation → Evidence → Report
              </p>
            </div>
          </div>

          <button 
            type="button" 
            className="btn btn-primary"
            onClick={() => navigate('/instruments')}
          >
            Launch Workflow
          </button>
        </div>
      </div>

      {/* Main Panels */}
      <div className="grid grid-cols-2 gap-6">
        
        {/* Recent Sessions */}
        <div className="card">
          <div className="flex justify-between items-center pb-2" style={{ borderBottom: '1px solid var(--border-color)', marginBottom: '1rem' }}>
            <h3 style={{ margin: 0 }}>Recent Inspection Sessions</h3>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Click row to open</span>
          </div>

          <div className="flex flex-col gap-3">
            {sessions.map((sess) => (
              <div 
                key={sess.id}
                className="flex justify-between items-center p-2"
                style={{ 
                  borderRadius: 'var(--radius-md)', 
                  border: '1px solid var(--border-color)', 
                  cursor: 'pointer',
                  transition: 'var(--transition)'
                }}
                onClick={() => navigate(sess.status === 'COMPLETED' ? `/reports?sessionId=${sess.id}` : `/workspace?sessionId=${sess.id}`)}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--bg-color)'}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
              >
                <div>
                  <p style={{ fontWeight: 600, fontSize: '0.9rem', margin: 0 }}>{sess.name}</p>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', margin: '0.1rem 0 0 0' }}>{sess.instrument}</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`badge ${sess.badgeClass}`}>{sess.badge}</span>
                  <ArrowRight size={14} style={{ color: 'var(--text-secondary)' }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Required Actions / Review Items */}
        <div className="card">
          <div className="flex justify-between items-center pb-2" style={{ borderBottom: '1px solid var(--border-color)', marginBottom: '1rem' }}>
            <h3 style={{ margin: 0 }}>Attention & Review Queue</h3>
            <span className="badge badge-review">1 Item</span>
          </div>

          <div className="flex flex-col gap-3">
            <div 
              className="p-3" 
              style={{ 
                backgroundColor: 'var(--status-review-bg)', 
                border: '1px solid var(--status-review-border)', 
                borderRadius: 'var(--radius-md)',
                cursor: 'pointer'
              }}
              onClick={() => navigate('/workspace?sessionId=1025')}
            >
              <div className="flex justify-between items-center">
                <p style={{ fontWeight: 600, color: 'var(--status-review-text)', margin: 0 }}>Review Required: Session #1025</p>
                <span className="badge badge-review">OIML R76 Warning</span>
              </div>
              <p style={{ fontSize: '0.85rem', color: 'var(--status-review-text)', marginTop: '0.4rem', margin: '0.4rem 0 0 0' }}>
                Load region exceeded declared range in Repeatability test. Technical reviewer sign-off required prior to report publication.
              </p>
            </div>

            <div 
              className="p-3" 
              style={{ 
                backgroundColor: 'var(--bg-color)', 
                border: '1px solid var(--border-color)', 
                borderRadius: 'var(--radius-md)'
              }}
            >
              <p style={{ fontWeight: 600, fontSize: '0.875rem', margin: 0 }}>Active Ruleset Status</p>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '0.2rem', margin: '0.2rem 0 0 0' }}>
                OIML R76:2006 Edition 1.0 (Published & Validated) • 14 Metrological Rules Loaded
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
