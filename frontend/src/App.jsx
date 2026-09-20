import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  Scale, 
  FileText, 
  Activity, 
  ListChecks, 
  ShieldCheck, 
  Compass, 
  RotateCcw, 
  BookOpen, 
  History,
  Wrench
} from 'lucide-react';
import './App.css';

// Import Pages
import Dashboard from './pages/Dashboard';
import InstrumentProfile from './pages/InstrumentProfile';
import TestPlan from './pages/TestPlan';
import TestWorkspace from './pages/TestWorkspace';
import Reports from './pages/Reports';
import ComplianceContext from './pages/ComplianceContext';
import ComplianceReplay from './pages/ComplianceReplay';
import Equipment from './pages/Equipment';
import Rules from './pages/Rules';
import Audit from './pages/Audit';

function Sidebar() {
  const location = useLocation();
  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <aside className="sidebar" style={{ width: '250px', flexShrink: 0 }}>
      <div className="navbar-brand" style={{ padding: '1.25rem 1.25rem 1rem', display: 'flex', flexDirection: 'column' }}>
        <div className="flex items-center gap-2">
          <ShieldCheck size={26} style={{ color: 'var(--primary-600)' }} />
          <span style={{ fontWeight: 800, fontSize: '1.25rem', letterSpacing: '-0.02em' }}>CALIBRA</span>
        </div>
        <span style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', fontWeight: 500, marginTop: '0.2rem' }}>
          Explainable Metrology Engine • OIML R76
        </span>
      </div>
      <nav style={{ padding: '0.5rem' }}>
        <Link to="/" className={`sidebar-nav-item flex items-center gap-2 ${isActive('/')}`}>
          <Home size={18} /> Dashboard
        </Link>
        <Link to="/instruments" className={`sidebar-nav-item flex items-center gap-2 ${isActive('/instruments')}`}>
          <Scale size={18} /> Instruments
        </Link>
        <Link to="/compliance-context" className={`sidebar-nav-item flex items-center gap-2 ${isActive('/compliance-context')}`}>
          <Compass size={18} /> Gravity Hub
        </Link>
        <Link to="/test-plan" className={`sidebar-nav-item flex items-center gap-2 ${isActive('/test-plan')}`}>
          <ListChecks size={18} /> Dynamic Test Plan
        </Link>
        <Link to="/workspace" className={`sidebar-nav-item flex items-center gap-2 ${isActive('/workspace')}`}>
          <Activity size={18} /> Test Workspace
        </Link>
        <Link to="/reports" className={`sidebar-nav-item flex items-center gap-2 ${isActive('/reports')}`}>
          <FileText size={18} /> Reports
        </Link>
        <Link to="/replay" className={`sidebar-nav-item flex items-center gap-2 ${isActive('/replay')}`}>
          <RotateCcw size={18} /> Compliance Replay
        </Link>
        <Link to="/equipment" className={`sidebar-nav-item flex items-center gap-2 ${isActive('/equipment')}`}>
          <Wrench size={18} /> Test Standards & Weights
        </Link>
        <Link to="/rules" className={`sidebar-nav-item flex items-center gap-2 ${isActive('/rules')}`}>
          <BookOpen size={18} /> OIML Rules & MPE
        </Link>
        <Link to="/audit" className={`sidebar-nav-item flex items-center gap-2 ${isActive('/audit')}`}>
          <History size={18} /> Audit Trail
        </Link>
      </nav>
    </aside>
  );
}

function App() {
  return (
    <Router>
      <div className="flex flex-col" style={{ minHeight: '100vh' }}>
        <div className="app-container flex" style={{ flexDirection: 'row', flex: 1 }}>
          <Sidebar />
          <main className="main-content" style={{ flex: 1, backgroundColor: 'var(--bg-color)', overflowY: 'auto' }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/instruments" element={<InstrumentProfile />} />
              <Route path="/compliance-context" element={<ComplianceContext />} />
              <Route path="/test-plan" element={<TestPlan />} />
              <Route path="/workspace" element={<TestWorkspace />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/replay" element={<ComplianceReplay />} />
              <Route path="/equipment" element={<Equipment />} />
              <Route path="/rules" element={<Rules />} />
              <Route path="/audit" element={<Audit />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
