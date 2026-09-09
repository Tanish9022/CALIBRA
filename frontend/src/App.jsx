import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Home, Scale, FileText, CheckSquare, Activity } from 'lucide-react';
import './App.css';

// Import Pages
import Dashboard from './pages/Dashboard';
import InstrumentProfile from './pages/InstrumentProfile';
import TestWorkspace from './pages/TestWorkspace';

function Sidebar() {
  const location = useLocation();
  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <aside className="sidebar">
      <div className="navbar-brand" style={{ padding: '0 1.5rem 1.5rem' }}>
        CALIBRA
      </div>
      <nav>
        <Link to="/" className={`sidebar-nav-item flex items-center gap-2 ${isActive('/')}`}>
          <Home size={18} /> Dashboard
        </Link>
        <Link to="/instruments" className={`sidebar-nav-item flex items-center gap-2 ${isActive('/instruments')}`}>
          <Scale size={18} /> Instruments
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
            <Route path="/workspace" element={<TestWorkspace />} />
            <Route path="/reports" element={<div className="animate-fade-in"><h2>Reports</h2><p>Coming soon...</p></div>} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
