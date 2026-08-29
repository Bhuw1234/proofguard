import { useState, useEffect } from 'react';
import { simulate, approve, reject, fetchAudit, fetchExamples } from './api';
import './App.css';

function RiskBadge({ level }) {
  return <span className={`badge badge-${level}`}>{level}</span>;
}

function ImpactTable({ before, after, changed }) {
  if (!before) return null;
  const tables = Object.keys(before);
  return (
    <table className="impact-table">
      <thead>
        <tr>
          <th>Table</th>
          <th>Before</th>
          <th>After</th>
          <th>Change</th>
        </tr>
      </thead>
      <tbody>
        {tables.map((t) => {
          const diff = changed?.[t] ?? 0;
          const cls = diff < 0 ? 'change-negative' : diff > 0 ? 'change-positive' : 'change-zero';
          return (
            <tr key={t}>
              <td className="mono">{t}</td>
              <td>{before[t]}</td>
              <td>{after[t]}</td>
              <td className={cls}>{diff > 0 ? `+${diff}` : diff}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

function Timeline({ result }) {
  const steps = [
    { label: 'SQL received', detail: result.proposed_sql, cls: '' },
    {
      label: 'Risk assessed',
      detail: `Risk level: ${result.risk_level}`,
      cls: result.risk_level === 'high' || result.risk_level === 'critical' ? 'step-danger' : '',
    },
    { label: 'Sandbox created', detail: result.execution_mode, cls: '' },
    {
      label: 'Simulation complete',
      detail: result.simulation_error ? `Error: ${result.simulation_error}` : `${result.changed_tables?.length || 0} table(s) affected`,
      cls: result.simulation_error ? 'step-danger' : 'step-safe',
    },
    { label: 'Awaiting human decision', detail: 'Approve or reject below', cls: '' },
  ];

  return (
    <div className="timeline">
      {steps.map((s, i) => (
        <div key={i} className={`timeline-step ${s.cls}`}>
          <div className="step-label">{s.label}</div>
          <div className="step-detail mono" style={{ fontSize: '0.8rem', wordBreak: 'break-all' }}>
            {s.detail}
          </div>
        </div>
      ))}
    </div>
  );
}

export default function App() {
  const [sql, setSql] = useState('');
  const [examples, setExamples] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [note, setNote] = useState('');
  const [decision, setDecision] = useState(null);
  const [decisionMsg, setDecisionMsg] = useState('');
  const [audit, setAudit] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchExamples()
      .then(setExamples)
      .catch(() => setExamples([]));
    loadAudit();
  }, []);

  function loadAudit() {
    fetchAudit()
      .then(setAudit)
      .catch(() => setAudit([]));
  }

  async function handleSimulate() {
    if (!sql.trim()) return;
    setLoading(true);
    setResult(null);
    setDecision(null);
    setDecisionMsg('');
    setError('');
    setNote('');
    try {
      const res = await simulate(sql);
      setResult(res);
      loadAudit();
    } catch (e) {
      setError('Could not reach the backend. Is uvicorn running on port 8000?');
    } finally {
      setLoading(false);
    }
  }

  async function handleDecision(type) {
    if (!result) return;
    try {
      const fn = type === 'approve' ? approve : reject;
      const res = await fn(result.simulation_id, note);
      setDecision(type === 'approve' ? 'approved' : 'rejected');
      setDecisionMsg(res.message);
      loadAudit();
    } catch (e) {
      setError('Failed to record decision.');
    }
  }

  return (
    <>
      {/* Header */}
      <header className="header">
        <h1><span className="shield">🛡️</span>ProofGuard</h1>
        <p className="tagline">Counterfactual safety for AI agents</p>
        <p className="description">
          Run a risky action in an isolated copy first. See the impact before anything touches the original system.
        </p>
      </header>

      {/* SQL Input */}
      <section className="card" id="sql-input-section">
        <h2>SQL Command</h2>
        <textarea
          id="sql-input"
          className="sql-input"
          placeholder="Enter SQL to simulate, e.g. DELETE FROM users WHERE last_login < '2023-01-01';"
          value={sql}
          onChange={(e) => setSql(e.target.value)}
        />

        {examples.length > 0 && (
          <div style={{ marginTop: '0.75rem' }}>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
              Demo examples:
            </div>
            <div className="examples">
              {examples.map((ex, i) => (
                <button
                  key={i}
                  className="example-btn"
                  onClick={() => setSql(ex.sql)}
                  title={ex.description}
                >
                  {ex.label}
                </button>
              ))}
            </div>
          </div>
        )}

        <button
          id="simulate-btn"
          className="btn-primary"
          onClick={handleSimulate}
          disabled={loading || !sql.trim()}
          style={{ marginTop: '0.75rem' }}
        >
          {loading ? <span className="loading" /> : '▶'}
          Run safe simulation
        </button>
      </section>

      {/* Error */}
      {error && <div className="error-box">{error}</div>}

      {/* Result */}
      {result && (
        <section className="card" id="result-section">
          <div className="result-header">
            <RiskBadge level={result.risk_level} />
            {result.original_database_protected && (
              <span className="protected-badge">✓ Original database protected</span>
            )}
            <span className="mode-badge">{result.execution_mode}</span>
          </div>

          {/* Agent Timeline */}
          <h2>Agent Timeline</h2>
          <Timeline result={result} />

          {/* Impact Table */}
          {result.before_counts && (
            <>
              <h2>Before / After Impact</h2>
              <ImpactTable
                before={result.before_counts}
                after={result.after_counts}
                changed={result.changed}
              />
            </>
          )}

          {/* Dependency Warning */}
          {result.dependency_warning && (
            <div className="warning-box">
              ⚠️ {result.dependency_warning}
            </div>
          )}

          {/* Simulation Error */}
          {result.simulation_error && (
            <div className="error-box">
              ❌ {result.simulation_error}
            </div>
          )}

          {/* Safer Alternative */}
          {result.safer_alternative && (
            <div className="safer-alt">
              <h2>Recommended Non-Destructive Alternative</h2>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                ProofGuard will not recommend deleting users while linked orders or payments still exist.
              </p>
              <pre>{result.safer_alternative}</pre>
              <p className="disclaimer">
                This is an illustrative safer option and must be reviewed before production use.
              </p>
            </div>
          )}

          {/* Approval Panel */}
          <div className="approval-panel" id="approval-panel">
            {decision ? (
              <div className={`decision-msg ${decision}`}>
                {decision === 'approved' ? '✓' : '✗'} {decisionMsg}
              </div>
            ) : (
              <>
                <input
                  className="approval-note"
                  placeholder="Optional note (e.g. 'I reviewed the impact')"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                />
                <button
                  className="btn-primary btn-approve"
                  onClick={() => handleDecision('approve')}
                >
                  ✓ Approve
                </button>
                <button
                  className="btn-primary btn-reject"
                  onClick={() => handleDecision('reject')}
                >
                  ✗ Reject
                </button>
                <p className="approval-disclaimer">
                  Approval records your decision only. This MVP never executes destructive SQL on the original database.
                </p>
              </>
            )}
          </div>
        </section>
      )}

      {/* Audit History */}
      <section className="card" id="audit-section">
        <h2>Recent Audit Events</h2>
        {audit.length === 0 ? (
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            No events yet. Run a simulation to see history here.
          </p>
        ) : (
          <ul className="audit-list">
            {audit.slice(0, 10).map((ev) => (
              <li key={ev.id} className="audit-item">
                <RiskBadge level={ev.risk_level} />
                <span className="audit-sql" title={ev.proposed_sql}>
                  {ev.proposed_sql}
                </span>
                <span className={`audit-decision ${ev.decision}`}>
                  {ev.decision}
                </span>
                <span className="audit-time">
                  {new Date(ev.timestamp).toLocaleString()}
                </span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
  );
}
