import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Home, Scale, FileText, Activity, ListChecks, ShieldCheck } from 'lucide-react';
import './App.css';

// Import Pages
import Dashboard from './pages/Dashboard';
import InstrumentProfile from './pages/InstrumentProfile';
import TestPlan from './pages/TestPlan';
import TestWorkspace from './pages/TestWorkspace';
import Reports from './pages/Reports';

function Sidebar() {
  const location = useLocation();
  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <aside className="sidebar">
      <div className="navbar-brand" style={{ padding: '0 1.5rem 1.5rem', display: 'flex', flexDirection: 'column' }}>
        <div className="flex items-center gap-2">
          <ShieldCheck size={24} style={{ color: 'var(--primary-600)' }} />
          <span>CALIBRA</span>
        </div>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', fontWeight: 400, marginTop: '0.2rem' }}>
          OIML R76 Compliance Engine
        </span>
      </div>
      <nav>
        <Link to="/" className={`sidebar-nav-item flex items-center gap-2 ${isActive('/')}`}>
          <Home size={18} /> Dashboard
        </Link>
        <Link to="/instruments" className={`sidebar-nav-item flex items-center gap-2 ${isActive('/instruments')}`}>
          <Scale size={18} /> Instruments
        </Link>
        <Link to="/test-plan" className={`sidebar-nav-item flex items-center gap-2 ${isActive('/test-plan')}`}>
          <ListChecks size={18} /> Test Plan
        </Link>
        <Link to="/workspace" className={`sidebar-nav-item flex items-center gap-2 ${isActive('/workspace')}`}>
          <Activity size={18} /> Test Workspace
        </Link>
        <Link to="/reports" className={`sidebar-nav-item flex items-center gap-2 ${isActive('/reports')}`}>
          <FileText size={18} /> Reports
        </Link>
      </nav>
    </aside>
  );
}

function App() {
  return (
    <Router>
      <div className="app-container flex" style={{ flexDirection: 'row' }}>
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/instruments" element={<InstrumentProfile />} />
            <Route path="/test-plan" element={<TestPlan />} />
            <Route path="/workspace" element={<TestWorkspace />} />
            <Route path="/reports" element={<Reports />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
