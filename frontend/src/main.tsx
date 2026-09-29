import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API = "http://localhost:8000";

type Dashboard = {
  experiences: number;
  beliefs: number;
  drifting: number;
  challenged: number;
  supported: number;
  memory_events: number;
  learning_events: number;
};

type Belief = {
  belief_id: string;
  statement: string;
  strength: number;
  status: string;
  support_count: number;
  contradiction_count: number;
  version: number;
};

async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(API + path, {
    headers: { "Content-Type": "application/json" },
    ...options
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

function App() {
  const [dashboard, setDashboard] = React.useState<Dashboard | null>(null);
  const [beliefs, setBeliefs] = React.useState<Belief[]>([]);
  const [validation, setValidation] = React.useState<any>(null);
  const [scenario, setScenario] = React.useState("");
  const [analysis, setAnalysis] = React.useState<any>(null);
  const [running, setRunning] = React.useState(false);
  const [error, setError] = React.useState("");

  const refresh = async () => {
    try {
      setError("");
      const [d, b] = await Promise.all([
        api<Dashboard>("/api/dashboard"),
        api<Belief[]>("/api/beliefs")
      ]);
      setDashboard(d);
      setBeliefs(b);
    } catch {
      setError("Backend is not running. Start FastAPI on port 8000.");
    }
  };

  React.useEffect(() => { refresh(); }, []);

  const runDemo = async () => {
    setRunning(true);
    try {
      const result = await api<any>("/api/demo/run", { method: "POST" });
      setValidation(result.validation);
      setScenario("We are migrating our payment provider next month.");
      setAnalysis(await api("/api/analyze", {
        method: "POST",
        body: JSON.stringify({ scenario: "We are migrating our payment provider next month." })
      }));
      await refresh();
    } catch {
      setError("Demo failed. Check the backend terminal.");
    } finally {
      setRunning(false);
    }
  };

  const validate = async (id: string) => {
    try {
      setValidation(await api(`/api/beliefs/${id}/validate`, { method: "POST" }));
    } catch {
      setError("Could not validate belief.");
    }
  };

  const analyze = async () => {
    if (!scenario.trim()) return;
    try {
      setAnalysis(await api("/api/analyze", {
        method: "POST",
        body: JSON.stringify({ scenario })
      }));
    } catch {
      setError("Could not analyze scenario.");
    }
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="logo">M</div>
          <div>
            <h1>MIRRORLINE</h1>
            <span>Memory evolution agent</span>
          </div>
        </div>
        <nav>
          <a className="active">Dashboard</a>
          <a>Belief Explorer</a>
          <a>Is This Still True?</a>
          <a>Knowledge Drift</a>
          <a>Memory Autopsy</a>
          <a>Evidence Explorer</a>
          <a>Scenario Lab</a>
        </nav>
        <div className="side-note">
          <strong>HINDSIGHT MEMORY</strong>
          <p>Retain → Recall → Reflect → Revise</p>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <div className="eyebrow">LEARNING CONSOLE</div>
            <h2>Knowledge that knows when to change.</h2>
          </div>
          <button className="demo-btn" onClick={runDemo} disabled={running}>
            {running ? "Running…" : "▶ Run Demo"}
          </button>
        </header>

        {error && <div className="error">{error}</div>}

        <section className="hero">
          <div>
            <div className="hero-kicker">THE CORE QUESTION</div>
            <h3>IS THIS STILL TRUE?</h3>
            <p>
              MIRRORLINE tests learned beliefs against new experiences,
              detects knowledge drift, and preserves the evidence behind every revision.
            </p>
          </div>
          <div className="hero-orbit">
            <span>MEMORY</span>
            <span>DRIFT</span>
            <span>REVISION</span>
          </div>
        </section>

        <section className="metrics">
          <Metric label="Experiences" value={dashboard?.experiences ?? 0} />
          <Metric label="Learned beliefs" value={dashboard?.beliefs ?? 0} />
          <Metric label="Drifting" value={dashboard?.drifting ?? 0} />
          <Metric label="Memory events" value={dashboard?.memory_events ?? 0} />
        </section>

        <section className="grid">
          <div className="panel wide">
            <div className="panel-head">
              <div>
                <div className="eyebrow">BELIEF EXPLORER</div>
                <h3>What has MIRRORLINE learned?</h3>
              </div>
            </div>
            {beliefs.length === 0 ? (
              <div className="empty">
                <span>◎</span>
                <p>No beliefs yet.</p>
                <small>Run the deterministic demo to create the first belief.</small>
              </div>
            ) : beliefs.map(b => (
              <div className="belief" key={b.belief_id}>
                <div className="belief-main">
                  <div className="belief-id">{b.belief_id} · VERSION {b.version}</div>
                  <strong>{b.statement}</strong>
                  <div className="chips">
                    <span className="chip">{b.status}</span>
                    <span>{b.support_count} support</span>
                    <span>{b.contradiction_count} contradiction</span>
                  </div>
                </div>
                <button onClick={() => validate(b.belief_id)}>IS THIS STILL TRUE?</button>
              </div>
            ))}
          </div>

          <div className="panel">
            <div className="eyebrow">MEMORY ACTIVITY</div>
            <h3>Hindsight loop</h3>
            <Activity label="RETAIN" text="Experiences persist as memory" />
            <Activity label="RECALL" text="Relevant historical evidence" />
            <Activity label="REFLECT" text="Patterns synthesized across memory" />
            <Activity label="REVISE" text="Beliefs evolve without erasing history" />
          </div>
        </section>

        <section className="grid">
          <div className="panel">
            <div className="eyebrow">BELIEF VALIDATION</div>
            <h3>Is this still true?</h3>
            {!validation ? (
              <div className="muted">Select a belief above to inspect its evidence and drift.</div>
            ) : (
              <div className="validation">
                <div className="status">{validation.status}</div>
                <p className="old-belief">{validation.original_statement}</p>
                <div className="evidence-row">
                  <div><span>{validation.support_count}</span><small>supporting</small></div>
                  <div><span>{validation.contradiction_count}</span><small>contradictory</small></div>
                </div>
                <h4>Context change</h4>
                <p>{validation.context_change}</p>
                <h4>Explanation</h4>
                <p>{validation.explanation}</p>
                {validation.revised_statement && (
                  <div className="revision">
                    <div className="eyebrow">REVISED BELIEF</div>
                    <strong>{validation.revised_statement}</strong>
                  </div>
                )}
              </div>
            )}
          </div>

          <div className="panel">
            <div className="eyebrow">SCENARIO LAB</div>
            <h3>What happens if we do this?</h3>
            <textarea
              value={scenario}
              onChange={e => setScenario(e.target.value)}
              placeholder="e.g. We're migrating our payment provider next month."
            />
            <button className="primary" onClick={analyze}>Analyze scenario</button>
            {analysis && (
              <div className="analysis">
                <div className="status">EVIDENCE: {analysis.evidence_count}</div>
                <p>{analysis.analysis}</p>
                <small>Uncertainty: {analysis.uncertainty}</small>
              </div>
            )}
          </div>
        </section>

        <footer>
          MIRRORLINE · Remember. Question. Revise. Learn.
        </footer>
      </main>
    </div>
  );
}

function Metric({label, value}: {label: string; value: number}) {
  return <div className="metric"><span>{label}</span><strong>{value}</strong></div>;
}

function Activity({label, text}: {label: string; text: string}) {
  return (
    <div className="activity">
      <span>✓</span>
      <div><strong>{label}</strong><small>{text}</small></div>
    </div>
  );
}

createRoot(document.getElementById("root")!).render(
  <React.StrictMode><App /></React.StrictMode>
);
