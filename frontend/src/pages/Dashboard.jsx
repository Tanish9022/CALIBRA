import React from 'react';
import { Activity, AlertCircle, CheckCircle, Clock } from 'lucide-react';

export default function Dashboard() {
  return (
    <div className="animate-fade-in">
      <h1 style={{ marginBottom: '1.5rem' }}>Dashboard</h1>
      
      <div className="grid grid-cols-4 gap-6" style={{ marginBottom: '2rem' }}>
        <div className="card flex flex-col gap-2">
          <div className="flex items-center justify-between text-secondary">
            <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>Active Tests</span>
            <Activity size={18} className="text-blue-500" />
          </div>
          <span style={{ fontSize: '1.5rem', fontWeight: 700 }}>12</span>
        </div>
        
        <div className="card flex flex-col gap-2">
          <div className="flex items-center justify-between text-secondary">
            <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>Pending Review</span>
            <AlertCircle size={18} style={{ color: 'var(--status-review-text)' }} />
          </div>
          <span style={{ fontSize: '1.5rem', fontWeight: 700 }}>3</span>
        </div>
        
        <div className="card flex flex-col gap-2">
          <div className="flex items-center justify-between text-secondary">
            <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>Completed</span>
            <CheckCircle size={18} style={{ color: 'var(--status-pass-text)' }} />
          </div>
          <span style={{ fontSize: '1.5rem', fontWeight: 700 }}>148</span>
        </div>

        <div className="card flex flex-col gap-2">
          <div className="flex items-center justify-between text-secondary">
            <span style={{ fontSize: '0.875rem', fontWeight: 500 }}>Avg. Test Time</span>
            <Clock size={18} />
          </div>
          <span style={{ fontSize: '1.5rem', fontWeight: 700 }}>24m</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="card">
          <h3 style={{ marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>Recent Sessions</h3>
          <div className="flex flex-col gap-4">
            <div className="flex justify-between items-center pb-2" style={{ borderBottom: '1px dashed var(--border-color)'}}>
              <div>
                <p style={{ fontWeight: 500 }}>Session #1024</p>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)'}}>Mettler Toledo - MS205DU</p>
              </div>
              <span className="badge badge-pass">PASS</span>
            </div>
            <div className="flex justify-between items-center pb-2" style={{ borderBottom: '1px dashed var(--border-color)'}}>
              <div>
                <p style={{ fontWeight: 500 }}>Session #1025</p>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)'}}>Ohaus - Adventurer</p>
              </div>
              <span className="badge badge-review">REVIEW</span>
            </div>
            <div className="flex justify-between items-center">
              <div>
                <p style={{ fontWeight: 500 }}>Session #1026</p>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)'}}>Sartorius - Cubis II</p>
              </div>
              <span className="badge badge-fail">FAIL</span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem' }}>Required Actions</h3>
          <div className="flex flex-col gap-2">
            <div className="p-3" style={{ backgroundColor: 'var(--status-review-bg)', border: '1px solid var(--status-review-border)', borderRadius: 'var(--radius-md)' }}>
              <p style={{ fontWeight: 500, color: 'var(--status-review-text)' }}>Review Required: Session #1025</p>
              <p style={{ fontSize: '0.875rem', color: 'var(--status-review-text)' }}>Inconsistent instrument configuration detected during Repeatability test.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
