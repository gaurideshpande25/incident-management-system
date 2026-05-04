import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const API = 'http://localhost:8000/api';

export default function IncidentDetail() {
  const { id } = useParams();
  const [data, setData] = useState<any>(null);
  const [rca, setRca] = useState({
    incident_start: '', incident_end: '',
    root_cause_category: 'DATABASE',
    fix_applied: '', prevention_steps: ''
  });
  const [msg, setMsg] = useState('');

  useEffect(() => {
    axios.get(`${API}/work-items/${id}`).then(r => setData(r.data));
  }, [id]);

  const advanceStatus = async () => {
    const wi = data?.work_item;
    const payload: any = { status: wi.status };
    if (wi.status === 'RESOLVED') payload.rca = {
      ...rca,
      incident_start: new Date(rca.incident_start).toISOString(),
      incident_end: new Date(rca.incident_end).toISOString(),
    };
    try {
      await axios.patch(`${API}/work-items/${id}`, payload);
      setMsg('✅ Updated! Refreshing...');
      setTimeout(() => window.location.reload(), 1000);
    } catch (e: any) {
      setMsg('❌ ' + (e.response?.data?.detail || 'Error'));
    }
  };

  if (!data) return <div style={{ color: 'white', padding: 24 }}>Loading...</div>;

  const wi = data.work_item;
  return (
    <div style={{ padding: 24, background: '#0f0f1a', minHeight: '100vh', color: 'white' }}>
      <h1>🔍 Incident #{id}</h1>
      <p><b>Component:</b> {wi.component_id} | <b>Severity:</b> {wi.severity} | <b>Status:</b> {wi.status}</p>
      {wi.mttr_minutes && <p>⏱ MTTR: <b>{wi.mttr_minutes} minutes</b></p>}

      <h2>Raw Signals ({data.signals.length})</h2>
      <div style={{ maxHeight: 200, overflow: 'auto', background: '#1a1a2e', borderRadius: 8, padding: 12 }}>
        {data.signals.map((s: any, i: number) => (
          <div key={i} style={{ borderBottom: '1px solid #333', padding: '6px 0', fontSize: 13 }}>
            [{s.severity}] {s.error_code} — {s.message}
          </div>
        ))}
      </div>

      {wi.status !== 'CLOSED' && (
        <div style={{ marginTop: 32 }}>
          <h2>Advance Status</h2>
          {wi.status === 'RESOLVED' && (
            <div style={{ background: '#1a1a2e', borderRadius: 8, padding: 16, marginBottom: 16 }}>
              <h3>📝 Root Cause Analysis (Required to Close)</h3>
              <label>Incident Start</label><br />
              <input type="datetime-local" style={inp} value={rca.incident_start}
                onChange={e => setRca({ ...rca, incident_start: e.target.value })} /><br />
              <label>Incident End</label><br />
              <input type="datetime-local" style={inp} value={rca.incident_end}
                onChange={e => setRca({ ...rca, incident_end: e.target.value })} /><br />
              <label>Root Cause Category</label><br />
              <select style={inp} value={rca.root_cause_category}
                onChange={e => setRca({ ...rca, root_cause_category: e.target.value })}>
                {['INFRASTRUCTURE','APPLICATION','DATABASE','NETWORK','HUMAN_ERROR'].map(c =>
                  <option key={c}>{c}</option>)}
              </select><br />
              <label>Fix Applied</label><br />
              <textarea style={{ ...inp, height: 80 }} value={rca.fix_applied}
                onChange={e => setRca({ ...rca, fix_applied: e.target.value })} /><br />
              <label>Prevention Steps</label><br />
              <textarea style={{ ...inp, height: 80 }} value={rca.prevention_steps}
                onChange={e => setRca({ ...rca, prevention_steps: e.target.value })} />
            </div>
          )}
          <button onClick={advanceStatus} style={bigBtn}>
            {wi.status === 'OPEN' ? 'Start Investigating →' :
             wi.status === 'INVESTIGATING' ? 'Mark Resolved →' : 'Close with RCA ✓'}
          </button>
          {msg && <p style={{ marginTop: 12, color: msg.startsWith('✅') ? '#44bb44' : '#ff4444' }}>{msg}</p>}
        </div>
      )}
    </div>
  );
}

const inp: React.CSSProperties = {
  background: '#0f0f1a', color: 'white', border: '1px solid #333',
  borderRadius: 4, padding: '8px 12px', width: '100%', marginBottom: 12, boxSizing: 'border-box'
};
const bigBtn: React.CSSProperties = {
  background: '#4a90e2', color: 'white', border: 'none',
  borderRadius: 6, padding: '12px 24px', fontSize: 16, cursor: 'pointer'
};
