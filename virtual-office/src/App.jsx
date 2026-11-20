import React, { useCallback, useEffect, useMemo, useState } from "react";
import OfficeScene from "./OfficeScene.jsx";

const DIVISION_ORDER = ["Executive", "Research & Opportunity", "Content & Audience", "Sales & Monetization", "Operations & Finance", "Technology & Automation"];
const STATUS = {
  working: { label: "Working", className: "working" },
  waiting_input: { label: "Waiting for input", className: "waiting" },
  idle: { label: "Idle", className: "idle" }
};
function timeAgo(value) {
  if (!value) return "—";
  const timestamp = new Date(value).getTime();
  if (!Number.isFinite(timestamp)) return "—";
  const seconds = Math.floor(Math.max(0, Date.now() - timestamp) / 1000);
  if (seconds < 60) return seconds + "s ago";
  if (seconds < 3600) return Math.floor(seconds / 60) + "m ago";
  if (seconds < 86400) return Math.floor(seconds / 3600) + "h ago";
  return new Date(value).toLocaleDateString("id-ID");
}
function formatTimestamp(value) {
  if (!value || !Number.isFinite(new Date(value).getTime())) return "—";
  return new Date(value).toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}
function stateLabel(value) {
  return ({ queued: "Queued", in_progress: "In progress", blocked: "Waiting", completed: "Completed", cancelled: "Cancelled" })[value] || value || "Unknown";
}
function AgentRow({ agent, selected, onClick }) {
  const status = STATUS[agent.status] || STATUS.idle;
  return <button className={"agent-row " + (selected ? "selected" : "")} onClick={onClick}>
    <span className="agent-avatar" style={{ background: agent.color }}>{agent.name.split(" ").map((part) => part[0]).join("").slice(0, 2)}</span>
    <span className="agent-row-copy"><strong>{agent.name}</strong><small>{agent.division || agent.zone}</small>{agent.current_task && <em>{agent.current_task.objective}</em>}</span>
    <span className={"status-pill " + status.className}><i />{status.label}</span>
  </button>;
}
function TaskCard({ task }) {
  return <article className="task-card">
    <div className="task-head"><span className={"task-state " + task.status}>{stateLabel(task.status)}</span><span className={"priority " + (task.priority || "normal")}>{task.priority || "normal"}</span></div>
    <strong>{task.agent}</strong><p>{task.objective}</p>
    <div className="task-foot"><span>{String(task.id || "").slice(0, 10)}</span><span>{task.stale_lease ? "STALE LEASE" : task.lease_active ? "LEASE ACTIVE" : timeAgo(task.updated_at)}</span></div>
  </article>;
}
function LoginScreen({ value, onChange, onSubmit, error, loading }) {
  return <main className="connect-page"><div className="connect-card">
    <div className="brand-mark">A</div><p className="eyebrow">AUTONOMOUS UNIFIED REVENUE AGENT</p><h1>Virtual AI Office</h1>
    <p className="connect-copy">Masuk menggunakan API key AURA yang sama dengan Operations Dashboard. Key disimpan hanya di session browser ini.</p>
    <form onSubmit={onSubmit}><label htmlFor="api-key">AURA API key</label><input id="api-key" type="password" autoComplete="current-password" value={value} onChange={(event) => onChange(event.target.value)} placeholder="Paste AURA_API_KEY" required /><button className="primary-button" type="submit" disabled={loading}>{loading ? "Connecting…" : "Connect to office"}</button></form>
    {error && <div className="error-note">{error}</div>}
    <a href="/dashboard">← Back to operations dashboard</a>
    <p className="fine-print">No credentials are embedded in the app. Never paste passwords, OTPs or recovery codes here.</p>
  </div></main>;
}
export default function App() {
  const [apiKey, setApiKey] = useState(() => sessionStorage.getItem("aura_key") || "");
  const [draftKey, setDraftKey] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState("Agents Orchestrator");
  const [taskFilter, setTaskFilter] = useState("all");
  const [lastUpdated, setLastUpdated] = useState("");

  const loadState = useCallback(async (secret) => {
    const response = await fetch("/office/state", { headers: { "X-AURA-API-Key": secret, "Accept": "application/json" }, cache: "no-store" });
    let payload = {};
    try { payload = await response.json(); } catch (err) { /* parse failure is reported as HTTP error */ }
    if (!response.ok) {
      const failure = new Error(payload.detail || ("Office API returned HTTP " + response.status));
      failure.status = response.status;
      throw failure;
    }
    return payload;
  }, []);

  useEffect(() => {
    if (!apiKey) return undefined;
    let mounted = true;
    let inFlight = false;
    const poll = async () => {
      if (inFlight) return;
      inFlight = true;
      try {
        const payload = await loadState(apiKey);
        if (!mounted) return;
        setData(payload);
        setLastUpdated(payload.generated_at || new Date().toISOString());
        setError("");
      } catch (err) {
        if (!mounted) return;
        if (err.status === 401) {
          sessionStorage.removeItem("aura_key");
          setData(null);
          setApiKey("");
          setError("API key is no longer valid. Connect again with the current AURA API key.");
        } else {
          setError(err.message || "Could not refresh office state");
        }
      } finally {
        inFlight = false;
      }
    };
    poll();
    const timer = window.setInterval(poll, 5000);
    return () => { mounted = false; window.clearInterval(timer); };
  }, [apiKey, loadState]);

  const connect = async (event) => {
    event.preventDefault();
    const secret = draftKey.trim();
    if (!secret) return;
    setLoading(true);
    try {
      const payload = await loadState(secret);
      setData(payload);
      setLastUpdated(payload.generated_at || new Date().toISOString());
      setError("");
      sessionStorage.setItem("aura_key", secret);
      setApiKey(secret);
      setDraftKey("");
    } catch (err) { setError(err.message || "Connection failed"); }
    finally { setLoading(false); }
  };
  const refresh = async () => {
    if (!apiKey) return;
    setLoading(true);
    try {
      const payload = await loadState(apiKey);
      setData(payload);
      setLastUpdated(payload.generated_at || new Date().toISOString());
      setError("");
    } catch (err) {
      if (err.status === 401) {
        sessionStorage.removeItem("aura_key");
        setData(null);
        setApiKey("");
        setError("API key is no longer valid. Connect again with the current AURA API key.");
      } else {
        setError(err.message || "Refresh failed");
      }
    } finally { setLoading(false); }
  };
  const lock = () => { sessionStorage.removeItem("aura_key"); setApiKey(""); setData(null); setDraftKey(""); };
  const agents = data?.agents || [], tasks = data?.active_tasks || [], logs = data?.logs || [], summary = data?.summary || {};
  const selected = agents.find((agent) => agent.name === selectedAgent) || agents[0] || null;
  const visibleTasks = useMemo(() => taskFilter === "all" ? tasks : tasks.filter((task) => task.status === taskFilter), [tasks, taskFilter]);

  if (!apiKey) return <LoginScreen value={draftKey} onChange={setDraftKey} onSubmit={connect} error={error} loading={loading} />;

  return <main className="office-app">
    <header className="topbar">
      <div className="brand-lockup"><div className="brand-mark small">A</div><div><div className="eyebrow">AURA / OPERATIONS FLOOR</div><h1>Virtual AI Office</h1></div></div>
      <div className="topbar-actions"><span className="live-indicator"><i /> CONNECTED</span><span className="last-sync">Updated {formatTimestamp(lastUpdated)}</span><button className="ghost-button" onClick={refresh} disabled={loading}>{loading ? "Refreshing…" : "↻ Refresh"}</button><a className="ghost-button" href="/dashboard">Dashboard</a><button className="ghost-button lock-button" onClick={lock}>Lock</button></div>
    </header>
    {error && <div className="global-error"><strong>Live data unavailable.</strong> {error} <span>Retrying every 5 seconds.</span></div>}
    <section className="metrics-row">
      <div className="metric-card"><span>AGENTS WORKING</span><strong>{summary.agents_working ?? "—"}</strong><small>Valid worker leases</small></div>
      <div className="metric-card"><span>WAITING INPUT</span><strong>{summary.agents_waiting_input ?? "—"}</strong><small>Blocked tasks</small></div>
      <div className="metric-card"><span>ACTIVE TASKS</span><strong>{summary.active_tasks ?? "—"}</strong><small>Queued · running · blocked</small></div>
      <div className="metric-card"><span>STALE LEASES</span><strong className={summary.stale_leases ? "warning-value" : ""}>{summary.stale_leases ?? "—"}</strong><small>Needs worker recovery</small></div>
    </section>
    <section className="office-layout">
      <div className="scene-panel">
        <div className="scene-heading"><div><span className="eyebrow">LIVE FLOOR PLAN</span><h2>Agency floor · 6 divisions</h2></div><span className="scene-hint">Drag to orbit · Scroll to zoom · Select an agent</span></div>
        {data ? <OfficeScene agents={agents} selectedAgent={selected?.name || selectedAgent} onSelectAgent={setSelectedAgent} /> : <div className="scene-loading">Waiting for authenticated office telemetry…</div>}
        <div className="scene-legend"><span><i className="legend-dot working" /> Working</span><span><i className="legend-dot waiting" /> Waiting for input</span><span><i className="legend-dot idle" /> Idle</span></div>
        <div className="runtime-note">{data?.runtime?.model_provider_enabled ? "Model provider enabled" : "Model inference disabled"}<span> · {data?.runtime?.background_scheduler_enabled ? "Scheduler enabled" : "No background scheduler"}</span></div>
      </div>
      <aside className="side-panel">
        <div className="side-header"><div><span className="eyebrow">OPERATIONS FEED</span><h2>Office overview · 6 divisions</h2></div><span className="agent-total">{summary.agents_total || agents.length || 0} AGENTS</span></div>
        {selected && <div className="selected-card">
          <div className="selected-top"><span className="selected-avatar" style={{ background: selected.color }}>{selected.name.split(" ").map((part) => part[0]).join("").slice(0, 2)}</span><div><span className="eyebrow">SELECTED AGENT</span><strong>{selected.name}</strong><small>{selected.title}</small></div><span className={"status-pill " + (STATUS[selected.status] || STATUS.idle).className}><i />{(STATUS[selected.status] || STATUS.idle).label}</span></div>
          <p>{selected.tagline}</p>
          {selected.current_task && <div className="selected-task"><small>CURRENT TASK</small><span>{selected.current_task.objective}</span>{selected.current_task.stale_lease && <em>Lease expired or missing — not counted as working</em>}</div>}
        </div>}
        <section className="side-section"><div className="section-heading"><h3>Agent roster</h3><span>{agents.length} registered</span></div><div className="agent-list">
          {DIVISION_ORDER.map((division) => {
            const members = agents.filter((agent) => agent.division === division);
            return members.length ? <section className="division-group" key={division}><div className="division-heading"><strong>{division}</strong><span>{members.length} agents</span></div>{members.map((agent) => <AgentRow key={agent.name} agent={agent} selected={selected?.name === agent.name} onClick={() => setSelectedAgent(agent.name)} />)}</section> : null;
          })}
          {agents.filter((agent) => !DIVISION_ORDER.includes(agent.division)).map((agent) => <AgentRow key={agent.name} agent={agent} selected={selected?.name === agent.name} onClick={() => setSelectedAgent(agent.name)} />)}
          {!agents.length && <p className="empty-state">Agent profiles will appear when the office API is available.</p>}
        </div></section>
        <section className="side-section"><div className="section-heading"><h3>Active tasks</h3><span>{tasks.length} open</span></div>
          <div className="filter-row">{["all", "queued", "in_progress", "blocked"].map((value) => <button key={value} className={taskFilter === value ? "filter active" : "filter"} onClick={() => setTaskFilter(value)}>{value === "all" ? "All" : stateLabel(value)}</button>)}</div>
          <div className="task-list">{visibleTasks.slice(0, 16).map((task) => <TaskCard task={task} key={task.id} />)}{!visibleTasks.length && <p className="empty-state">No tasks in this view. Queued work is not shown as running.</p>}</div>
        </section>
        <section className="side-section log-section"><div className="section-heading"><h3>Activity log</h3><span>Latest {logs.length}</span></div>
          <div className="log-list">{logs.slice(0, 18).map((log) => <article className="log-row" key={log.id}><span className="log-time">{timeAgo(log.created_at)}</span><div><strong>{String(log.event_type || "event").replaceAll(".", " · ")}</strong><small>{log.details || log.object_id}</small></div></article>)}{!logs.length && <p className="empty-state">No audit events recorded yet.</p>}</div>
        </section>
        <footer className="side-footer"><span>Polling every 5 seconds</span><span>{summary.completed_today || 0} tasks completed today</span></footer>
      </aside>
    </section>
  </main>;
}