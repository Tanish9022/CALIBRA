import React, { useState, useEffect } from 'react';
import { ShieldCheck, History, User, Calendar, FileText, CheckCircle } from 'lucide-react';

export default function Audit() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/audit')
      .then(res => res.ok ? res.json() : [])
      .then(data => setLogs(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="container" style={{ maxWidth: '1280px', margin: '0 auto', padding: '1.5rem' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <div className="flex items-center gap-2">
          <History size={28} style={{ color: 'var(--primary-600)' }} />
          <h1 style={{ margin: 0, fontSize: '1.75rem' }}>Immutable Metrological Audit Trail</h1>
        </div>
        <p style={{ color: 'var(--text-secondary)', margin: '0.25rem 0 0', fontSize: '0.9rem' }}>
          Tamper-evident record of all regulatory compliance operations, context alterations, and report issuances.
        </p>
      </div>

      <div className="card" style={{ padding: '1rem' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
          <thead>
            <tr style={{ borderBottom: '2px solid #e2e8f0', textAlign: 'left', color: '#64748b' }}>
              <th style={{ padding: '0.75rem' }}>Timestamp</th>
              <th style={{ padding: '0.75rem' }}>Actor</th>
              <th style={{ padding: '0.75rem' }}>Action</th>
              <th style={{ padding: '0.75rem' }}>Entity</th>
              <th style={{ padding: '0.75rem' }}>Entity ID</th>
              <th style={{ padding: '0.75rem' }}>Audit Details</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(item => (
              <tr key={item.id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                <td style={{ padding: '0.75rem', fontFamily: 'monospace', color: '#64748b' }}>
                  {item.timestamp ? String(item.timestamp).replace('T', ' ').slice(0, 19) : 'Just now'}
                </td>
                <td style={{ padding: '0.75rem', fontWeight: 600, color: '#0f172a' }}>
                  {item.actor_id}
                </td>
                <td style={{ padding: '0.75rem' }}>
                  <span className="badge badge-pass" style={{ fontSize: '0.75rem' }}>
                    {item.action}
                  </span>
                </td>
                <td style={{ padding: '0.75rem', color: '#334155' }}>
                  {item.entity_type}
                </td>
                <td style={{ padding: '0.75rem', fontFamily: 'monospace' }}>
                  #{item.entity_id}
                </td>
                <td style={{ padding: '0.75rem', fontSize: '0.8rem', color: '#64748b' }}>
                  {item.after_json?.report_number ? `Report ${item.after_json.report_number}` : JSON.stringify(item.metadata_json || {})}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
