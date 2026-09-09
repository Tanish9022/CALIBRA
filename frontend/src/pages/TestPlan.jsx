import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { 
  CheckCircle, 
  HelpCircle, 
  ArrowRight, 
  ListChecks 
} from 'lucide-react';

export default function TestPlan() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const sessionId = searchParams.get('sessionId') || '1';

  const [expandedWhy, setExpandedWhy] = useState({});

  const toggleWhy = (testCode) => {
    setExpandedWhy(prev => ({
      ...prev,
      [testCode]: !prev[testCode]
    }));
  };

  const testSuite = [
    {
      code: 'TEST-01',
      number: '01',
      name: 'Administrative Examination',
      applicability: 'REQUIRED',
      status: 'DONE',
      clause: 'OIML R76-1 Section 3.4',
      description: 'Markings, accuracy class inscription, serial numbers, stamping plates, and software version identification.',
      why: 'Mandatory statutory prerequisite under OIML R76-1 Section 3.4. All NAWI instruments must undergo descriptive markings verification prior to metrological load testing.'
    },
    {
      code: 'TEST-02',
      number: '02',
      name: 'Construction & Metrological Security',
      applicability: 'REQUIRED',
      status: 'DONE',
      clause: 'OIML R76-1 Section 3.9',
      description: 'Physical inspection of level indicator, leveling feet stability, tare facilities, and adjustment security seals.',
      why: 'Required to ensure device stability, operational leveling, and tamper-evident sealing of calibration parameters before weights are applied.'
    },
    {
      code: 'TEST-03',
      number: '03',
      name: 'Weighing Performance (Errors of Indication)',
      applicability: 'REQUIRED',
      status: 'READY',
      clause: 'OIML R76-1 Annex A.4.4',
      description: 'Determination of intrinsic indication errors with ascending and descending test loads from Min to Max.',
      why: 'Primary metrological test required for all Class III instruments to establish that errors of indication remain within the Maximum Permissible Error (MPE) step function.'
    },
    {
      code: 'TEST-04',
      number: '04',
      name: 'Repeatability Test',
      applicability: 'REQUIRED',
      status: 'PENDING',
      clause: 'OIML R76-1 Section 3.6.1',
      description: 'Two series of 10 weighings at approximately 0.5 Max and Max to verify repeatability spread.',
      why: 'Mandatory for pattern verification. The difference between results of several weighings with the same load must not exceed the absolute value of the MPE for that load.'
    },
    {
      code: 'TEST-05',
      number: '05',
      name: 'Eccentricity (Eccentric Loading Test)',
      applicability: 'REQUIRED',
      status: 'PENDING',
      clause: 'OIML R76-1 Section 3.6.2',
      description: 'Application of test load (1/3 Max + tare) on 4 platform quadrants and center.',
      why: 'Mandatory for platform weighing instruments to ensure off-center loading does not cause indication errors exceeding the applicable MPE.'
    },
    {
      code: 'TEST-06',
      number: '06',
      name: 'Zero Return & Initial Zero-Setting',
      applicability: 'CONDITIONAL',
      status: 'N/A',
      clause: 'OIML R76-1 Section 4.5',
      description: 'Evaluation of residual zero deviation after maximum capacity load removal.',
      why: 'Applicable conditionally when the instrument features an automatic zero-setting range exceeding 20% of Max or semi-automatic tare devices.'
    }
  ];

  return (
    <div className="animate-fade-in flex flex-col gap-6">
      <div className="flex justify-between items-center">
        <div>
          <div className="flex items-center gap-2" style={{ marginBottom: '0.25rem' }}>
            <span className="badge badge-pass">Session #{sessionId}</span>
            <span className="badge" style={{ backgroundColor: 'var(--primary-50)', color: 'var(--primary-700)', border: '1px solid var(--primary-100)' }}>
              Ruleset: OIML R76:2006 (Class III)
            </span>
          </div>
          <h1>Generated Test Plan</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            CALIBRA Rule Engine evaluated the instrument profile and generated the compliant test suite.
          </p>
        </div>

        <button 
          className="btn btn-primary flex items-center gap-2"
          onClick={() => navigate(`/workspace?sessionId=${sessionId}`)}
        >
          Proceed to Test Workspace <ArrowRight size={16} />
        </button>
      </div>

      {/* Plan Summary Banner */}
      <div className="card" style={{ backgroundColor: 'var(--primary-50)', borderColor: 'var(--primary-100)' }}>
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-4">
            <div style={{
              width: '44px',
              height: '44px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: 'var(--shadow-sm)'
            }}>
              <ListChecks size={24} style={{ color: 'var(--primary-600)' }} />
            </div>
            <div>
              <h4 style={{ margin: 0, color: 'var(--primary-700)' }}>Test Plan Ready for Execution</h4>
              <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                5 Required Procedures • 1 Conditional Procedure • Primary Target: <strong>Weighing Performance (WP-01)</strong>
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            <span className="badge" style={{ backgroundColor: 'white', color: 'var(--text-primary)', border: '1px solid var(--border-color)' }}>
              Estimated Duration: ~45 min
            </span>
          </div>
        </div>
      </div>

      {/* Test List Cards */}
      <div className="flex flex-col gap-4">
        {testSuite.map((test) => (
          <div key={test.code} className="card" style={{ padding: '1.25rem' }}>
            <div className="flex justify-between items-start">
              <div className="flex items-start gap-4">
                <div style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: test.status === 'DONE' ? 'var(--status-pass-bg)' : (test.status === 'READY' ? 'var(--primary-100)' : 'var(--bg-color)'),
                  color: test.status === 'DONE' ? 'var(--status-pass-text)' : (test.status === 'READY' ? 'var(--primary-700)' : 'var(--text-secondary)'),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 700,
                  fontSize: '0.875rem'
                }}>
                  {test.number}
                </div>
                
                <div>
                  <div className="flex items-center gap-2">
                    <h3 style={{ fontSize: '1.05rem', margin: 0 }}>{test.name}</h3>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>({test.clause})</span>
                  </div>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                    {test.description}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3">
                <span className={`badge ${test.applicability === 'REQUIRED' ? 'badge-pass' : ''}`} style={test.applicability === 'CONDITIONAL' ? { backgroundColor: 'var(--bg-color)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' } : {}}>
                  {test.applicability}
                </span>

                {test.status === 'DONE' && (
                  <span className="badge badge-pass flex items-center gap-1">
                    <CheckCircle size={12} /> COMPLETE
                  </span>
                )}
                {test.status === 'READY' && (
                  <span className="badge" style={{ backgroundColor: 'var(--primary-600)', color: 'white' }}>
                    READY TO RUN
                  </span>
                )}
                {test.status === 'PENDING' && (
                  <span className="badge" style={{ backgroundColor: 'var(--bg-color)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' }}>
                    PENDING
                  </span>
                )}
                {test.status === 'N/A' && (
                  <span className="badge" style={{ backgroundColor: 'var(--bg-color)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' }}>
                    NOT APPLICABLE
                  </span>
                )}

                <button 
                  type="button" 
                  className="btn btn-secondary flex items-center gap-1"
                  style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                  onClick={() => toggleWhy(test.code)}
                >
                  <HelpCircle size={14} /> Why required?
                </button>
              </div>
            </div>

            {expandedWhy[test.code] && (
              <div className="animate-fade-in" style={{
                marginTop: '1rem',
                padding: '0.75rem 1rem',
                backgroundColor: 'var(--bg-color)',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--border-color)',
                fontSize: '0.875rem'
              }}>
                <strong style={{ color: 'var(--primary-600)' }}>Regulatory Rationale ({test.clause}):</strong>
                <p style={{ margin: '0.25rem 0 0 0', color: 'var(--text-primary)' }}>
                  {test.why}
                </p>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="flex justify-end" style={{ marginTop: '1rem' }}>
        <button 
          className="btn btn-primary flex items-center gap-2"
          onClick={() => navigate(`/workspace?sessionId=${sessionId}`)}
          style={{ padding: '0.75rem 1.5rem', fontSize: '1rem' }}
        >
          Enter Test Workspace <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );
}
