import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import IncidentDetail from './pages/IncidentDetail';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <nav style={nav}>
        <span style={logo}>🚨 IMS</span>
        <Link to="/" style={link}>Dashboard</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/incident/:id" element={<IncidentDetail />} />
      </Routes>
    </BrowserRouter>
  );
}

const nav: React.CSSProperties = {
  background: '#1a1a2e', padding: '12px 24px',
  display: 'flex', alignItems: 'center', gap: '24px'
};
const logo: React.CSSProperties = { color: 'white', fontWeight: 'bold', fontSize: 20 };
const link: React.CSSProperties = { color: '#a0c4ff', textDecoration: 'none' };

export default App;
