import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const API = 'http://localhost:8000/api';

const SEVERITY_COLOR: Record<string, string> = {
  P0: '#ff4444', P1: '#ff8800', P2: '#ffcc00', P3: '#44bb44'
};
const STATUS_COLOR: Record<string, string> = {
  OPEN: '#ff4444', INVESTIGATING: '#ff8800', RESOLVED: '#44bb44', CLOSED: '#888'
};

export default function Dashboard() {
  const [items, setItems] = useState<any[]>([]);
  const navigate = useNavigate();

  const fetchData = async () => {
    const res = await axios.get(`${API}/dashboard`);
    setItems(res.data);
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: 24, background: '#0f0f1a', minHeight: '100vh', color: 'white' }}>
      <h1>🔴 Live Incident Feed</h1>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ background: '#1a1a2e', textAlign: 'left' }}>
            <th style={th}>ID</th><th style={th}>Component</th>
            <th style={th}>Severity</th><th style={th}>Status</th><th style={th}>Action</th>
          </tr>
        </thead>
        <tbody>
          {items.map(item => (
            <tr key={item.id} style={{ borderBottom: '1px solid #333' }}>
              <td style={td}>#{item.id}</td>
              <td style={td}>{item.component_id}</td>
              <td style={td}><span style={badge(SEVERITY_COLOR[item.severity])}>{item.severity}</span></td>
              <td style={td}><span style={badge(STATUS_COLOR[item.status])}>{item.status}</span></td>
              <td style={td}>
                <button onClick={() => navigate(`/incident/${item.id}`)} style={btn}>
                  View →
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {items.length === 0 && <p style={{ color: '#888', marginTop: 32 }}>No active incidents. System healthy ✅</p>}
    </div>
  );
}

const th: React.CSSProperties = { padding: '12px 16px', color: '#a0c4ff' };
const td: React.CSSProperties = { padding: '12px 16px' };
const badge = (color: string): React.CSSProperties => ({
  background: color + '33', color, border: `1px solid ${color}`,
  borderRadius: 4, padding: '2px 8px', fontWeight: 'bold', fontSize: 12
});
const btn: React.CSSProperties = {
  background: '#1a1a2e', color: '#a0c4ff', border: '1px solid #a0c4ff',
  borderRadius: 4, padding: '6px 12px', cursor: 'pointer'
};
