"""HTML template for the SDLC real-time dashboard."""

DASHBOARD_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SDLC Agent Dashboard</title>
<style>
  :root {
    --bg: #0d1117; --bg2: #161b22; --bg3: #21262d;
    --border: #30363d; --text: #e6edf3; --dim: #8b949e;
    --green: #3fb950; --yellow: #d29922; --red: #f85149;
    --blue: #58a6ff; --purple: #bc8cff; --cyan: #39d353;
    --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
    --mono: 'SF Mono', SFMono-Regular, Consolas, 'Liberation Mono', Menlo, monospace;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: var(--font); background: var(--bg); color: var(--text); min-height: 100vh; }

  /* Header */
  .header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 24px; border-bottom: 1px solid var(--border); background: var(--bg2);
  }
  .header h1 { font-size: 18px; font-weight: 600; }
  .header h1 span { color: var(--blue); }
  .conn-status {
    display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--dim);
  }
  .conn-dot {
    width: 8px; height: 8px; border-radius: 50%; background: var(--red);
    transition: background 0.3s;
  }
  .conn-dot.connected { background: var(--green); }

  /* Grid layout */
  .grid {
    display: grid; grid-template-columns: 340px 1fr;
    grid-template-rows: auto auto 1fr; gap: 1px;
    background: var(--border); min-height: calc(100vh - 57px);
  }
  .card {
    background: var(--bg2); padding: 16px; overflow: auto;
  }
  .card-title {
    font-size: 12px; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.5px; color: var(--dim); margin-bottom: 12px;
  }

  /* Phase progress */
  .phases { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 16px; }
  .phase-pill {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 4px 10px; border-radius: 12px; font-size: 12px;
    font-weight: 500; border: 1px solid var(--border); background: var(--bg3);
  }
  .phase-pill.complete { border-color: var(--green); color: var(--green); }
  .phase-pill.in_progress { border-color: var(--yellow); color: var(--yellow); animation: pulse 2s infinite; }
  .phase-pill.failed { border-color: var(--red); color: var(--red); }
  .phase-pill.pending { color: var(--dim); }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.6; } }

  /* Summary stats */
  .stats { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 16px; }
  .stat {
    background: var(--bg3); border-radius: 8px; padding: 12px;
    border: 1px solid var(--border);
  }
  .stat-label { font-size: 11px; color: var(--dim); text-transform: uppercase; letter-spacing: 0.5px; }
  .stat-value { font-size: 20px; font-weight: 700; margin-top: 2px; }
  .stat-value.active { color: var(--yellow); }
  .stat-value.green { color: var(--green); }

  /* Queue */
  .queue-bars { display: flex; flex-direction: column; gap: 6px; }
  .queue-row {
    display: flex; align-items: center; gap: 8px; font-size: 13px;
  }
  .queue-label { width: 80px; color: var(--dim); }
  .queue-bar {
    flex: 1; height: 20px; background: var(--bg3); border-radius: 4px;
    overflow: hidden; position: relative;
  }
  .queue-fill {
    height: 100%; border-radius: 4px; transition: width 0.5s ease;
    min-width: 0;
  }
  .queue-fill.pending { background: var(--dim); }
  .queue-fill.active { background: var(--yellow); }
  .queue-fill.completed { background: var(--green); }
  .queue-count { width: 30px; text-align: right; font-family: var(--mono); font-size: 13px; }

  /* Interaction map (trace tree) */
  .trace-tree { font-family: var(--mono); font-size: 13px; line-height: 1.8; }
  .trace-tree details { margin-left: 16px; }
  .trace-tree summary {
    cursor: pointer; list-style: none; user-select: none;
  }
  .trace-tree summary::-webkit-details-marker { display: none; }
  .trace-tree summary::before {
    content: '\\25B6'; display: inline-block; width: 16px; font-size: 10px;
    transition: transform 0.15s; color: var(--dim);
  }
  .trace-tree details[open] > summary::before { transform: rotate(90deg); }
  .trace-phase { font-weight: 600; color: var(--text); }
  .trace-agent { color: var(--cyan); }
  .trace-sub { color: var(--purple); }
  .trace-action { color: var(--dim); font-size: 12px; margin-left: 4px; }
  .trace-artifact { color: var(--dim); font-size: 12px; padding-left: 32px; }
  .trace-artifact::before { content: ''; }
  .trace-gate { font-size: 11px; padding-left: 16px; }
  .trace-gate.pass { color: var(--green); }
  .trace-gate.fail { color: var(--red); }
  .icon-complete::before { content: '\\2705 '; }
  .icon-in_progress::before { content: '\\1F504 '; }
  .icon-pending::before { content: '\\2B1C '; }
  .icon-failed::before { content: '\\274C '; }
  .icon-skipped::before { content: '\\23ED\\FE0F '; }
  .model-badge {
    display: inline-block; font-size: 10px; padding: 1px 6px; border-radius: 4px;
    background: var(--bg3); border: 1px solid var(--border); color: var(--blue);
    font-family: var(--mono); vertical-align: middle; margin-left: 4px;
  }
  .no-data { color: var(--dim); font-style: italic; font-size: 13px; }

  /* Activity feed */
  .activity-feed {
    font-family: var(--mono); font-size: 12px; line-height: 1.7;
    max-height: 300px; overflow-y: auto;
  }
  .activity-line { color: var(--dim); white-space: pre-wrap; word-break: break-all; }
  .activity-line strong { color: var(--text); font-weight: 600; }

  /* Working memory */
  .memory-content {
    font-family: var(--mono); font-size: 12px; line-height: 1.7;
    color: var(--dim); white-space: pre-wrap; max-height: 200px; overflow-y: auto;
  }

  /* Responsive */
  @media (max-width: 900px) {
    .grid { grid-template-columns: 1fr; }
  }

  /* Last updated */
  .last-updated { font-size: 11px; color: var(--dim); margin-top: 8px; }
</style>
</head>
<body>

<div class="header">
  <h1><span>SDLC</span> Agent Dashboard</h1>
  <div class="conn-status">
    <div class="conn-dot" id="connDot"></div>
    <span id="connText">Connecting...</span>
  </div>
</div>

<div class="grid">
  <!-- Left column: status overview -->
  <div class="card" style="grid-row: 1 / 3;">
    <div class="card-title">Phase Progress</div>
    <div class="phases" id="phases"></div>

    <div class="stats">
      <div class="stat">
        <div class="stat-label">Status</div>
        <div class="stat-value" id="statStatus">--</div>
      </div>
      <div class="stat">
        <div class="stat-label">Complexity</div>
        <div class="stat-value" id="statComplexity">--</div>
      </div>
      <div class="stat">
        <div class="stat-label">Active Agent</div>
        <div class="stat-value active" id="statAgent" style="font-size:14px;">--</div>
      </div>
      <div class="stat">
        <div class="stat-label">Tasks</div>
        <div class="stat-value green" id="statTasks">--</div>
      </div>
    </div>

    <div class="card-title">Task Queue</div>
    <div class="queue-bars" id="queue"></div>

    <div class="last-updated" id="lastUpdated"></div>
  </div>

  <!-- Right column top: interaction map -->
  <div class="card">
    <div class="card-title">Agent Interaction Map</div>
    <div class="trace-tree" id="traceTree">
      <div class="no-data">No agent interactions recorded yet.</div>
    </div>
  </div>

  <!-- Right column bottom split -->
  <div class="card">
    <div class="card-title">Activity Feed</div>
    <div class="activity-feed" id="activityFeed">
      <div class="no-data">No activity yet.</div>
    </div>
  </div>

  <!-- Full width bottom: working memory -->
  <div class="card" style="grid-column: 1 / -1;">
    <div class="card-title">Working Memory (CONTINUITY.md)</div>
    <div class="memory-content" id="memoryContent">
      <span class="no-data">No working memory yet.</span>
    </div>
  </div>
</div>

<script>
const PHASE_NAMES = {
  '0-bootstrap':'Bootstrap','1-product':'Product','2-story-tasks':'Story-Tasks',
  '3-architecture':'Architecture','4-design':'Design','5-development':'Development',
  '6-testing':'Testing','7-security':'Security','8-review':'Review',
  '9-devops':'DevOps','10-observability':'Observability'
};

const STATUS_ICONS = {
  complete: '\\u2705', in_progress: '\\uD83D\\uDD04', pending: '\\u2B1C',
  failed: '\\u274C', skipped: '\\u23ED\\uFE0F'
};

let ws;
let reconnectTimer;

function connect() {
  const wsPort = /*WS_PORT*/8421;
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(proto + '://' + location.hostname + ':' + wsPort + '/ws');

  ws.onopen = () => {
    document.getElementById('connDot').classList.add('connected');
    document.getElementById('connText').textContent = 'Connected';
    clearTimeout(reconnectTimer);
  };

  ws.onclose = () => {
    document.getElementById('connDot').classList.remove('connected');
    document.getElementById('connText').textContent = 'Reconnecting...';
    reconnectTimer = setTimeout(connect, 2000);
  };

  ws.onerror = () => ws.close();

  ws.onmessage = (e) => {
    try {
      const data = JSON.parse(e.data);
      render(data);
    } catch (err) {
      console.error('Parse error:', err);
    }
  };
}

function render(data) {
  renderPhases(data.orchestrator);
  renderStats(data.orchestrator, data.queue, data.model_config);
  renderQueue(data.queue);
  renderTrace(data.trace);
  renderActivity(data.activity_log);
  renderMemory(data.continuity);
  document.getElementById('lastUpdated').textContent = 'Updated: ' + new Date().toLocaleTimeString();
}

function resolveModel(agentId, mc) {
  if (!mc) return null;
  const ov = mc.overrides || {};
  if (ov[agentId]) return ov[agentId];
  const at = mc.agent_tiers || {};
  const tiers = mc.tiers || {};
  if (at[agentId]) return tiers[at[agentId]] || at[agentId];
  if (agentId.startsWith('sub-') && at['sub-*']) return tiers[at['sub-*']] || at['sub-*'];
  return null;
}

function renderPhases(orch) {
  if (!orch || !orch.phases) return;
  const el = document.getElementById('phases');
  const keys = Object.keys(orch.phases).sort();
  el.innerHTML = keys.map(k => {
    const p = orch.phases[k];
    const num = k.split('-')[0];
    const name = PHASE_NAMES[k] || k;
    const st = p.status || 'pending';
    const icon = STATUS_ICONS[st] || '';
    return '<span class="phase-pill ' + st + '">' + icon + ' ' + num + '. ' + name + '</span>';
  }).join('');
}

function renderStats(orch, queue, mc) {
  if (!orch) return;
  document.getElementById('statStatus').textContent = orch.status || '--';
  document.getElementById('statComplexity').textContent = orch.complexity || '--';
  const agents = orch.active_agents || [];
  let agentHtml = agents.length ? '' : 'none';
  agents.forEach(a => {
    const m = resolveModel(a, mc);
    agentHtml += '<span>' + escHtml(a);
    if (m) agentHtml += ' <span class="model-badge">' + escHtml(m) + '</span>';
    agentHtml += '</span> ';
  });
  document.getElementById('statAgent').innerHTML = agentHtml;
  document.getElementById('statTasks').textContent =
    (orch.completed_tasks || 0) + ' / ' + (orch.total_tasks || 0);
}

function renderQueue(q) {
  if (!q) return;
  const total = Math.max((q.pending||0) + (q.active||0) + (q.completed||0), 1);
  const el = document.getElementById('queue');
  el.innerHTML = ['pending','active','completed'].map(k => {
    const v = q[k] || 0;
    const pct = (v / total * 100).toFixed(1);
    return '<div class="queue-row">' +
      '<span class="queue-label">' + k.charAt(0).toUpperCase() + k.slice(1) + '</span>' +
      '<div class="queue-bar"><div class="queue-fill ' + k + '" style="width:' + pct + '%"></div></div>' +
      '<span class="queue-count">' + v + '</span></div>';
  }).join('');
}

function renderTrace(trace) {
  const el = document.getElementById('traceTree');
  if (!trace || !trace.traces || trace.traces.length === 0) {
    el.innerHTML = '<div class="no-data">No agent interactions recorded yet.</div>';
    return;
  }

  // Group by phase
  const byPhase = {};
  trace.traces.forEach(t => {
    const p = t.phase ?? 0;
    if (!byPhase[p]) byPhase[p] = [];
    byPhase[p].push(t);
  });

  let html = '';
  Object.keys(byPhase).sort((a,b) => a-b).forEach(phaseNum => {
    const entries = byPhase[phaseNum];
    const stage = entries.find(e => e.role === 'orchestrator' || e.role === 'stage') || entries[0];
    const subs = entries.filter(e => e.role === 'subagent');
    const icon = STATUS_ICONS[stage.status] || '';
    const phaseName = (stage.phase_name || '?');
    const capName = phaseName.charAt(0).toUpperCase() + phaseName.slice(1);

    html += '<details open>';
    html += '<summary><span class="trace-phase">' + icon + ' Phase ' + phaseNum + ': ' + capName + '</span></summary>';
    html += '<div style="padding-left:16px">';
    html += '<div><span class="trace-agent">' + stage.agent + '</span>';
    if (stage.model) html += ' <span class="model-badge">' + escHtml(stage.model) + '</span>';
    if (stage.action) html += '<span class="trace-action"> \u2014 ' + escHtml(stage.action) + '</span>';
    html += '</div>';

    // Inputs
    (stage.input_artifacts || []).forEach(a => {
      html += '<div class="trace-artifact">In: ' + basename(a) + '</div>';
    });

    // Subagents
    subs.forEach(sub => {
      const si = STATUS_ICONS[sub.status] || '';
      html += '<details open style="margin-top:2px">';
      html += '<summary><span class="trace-sub">' + si + ' ' + sub.agent + '</span>';
      if (sub.model) html += ' <span class="model-badge">' + escHtml(sub.model) + '</span>';
      if (sub.action) html += '<span class="trace-action"> \u2014 ' + escHtml(sub.action) + '</span>';
      html += '</summary>';
      (sub.input_artifacts || []).forEach(a => {
        html += '<div class="trace-artifact">In: ' + basename(a) + '</div>';
      });
      (sub.output_artifacts || []).forEach(a => {
        html += '<div class="trace-artifact"><strong>Out:</strong> ' + basename(a) + '</div>';
      });
      html += '</details>';
    });

    // Stage outputs (if no subs)
    if (subs.length === 0) {
      (stage.output_artifacts || []).forEach(a => {
        html += '<div class="trace-artifact"><strong>Out:</strong> ' + basename(a) + '</div>';
      });
    }

    // Gate
    if (stage.gate) {
      const gc = stage.gate.toLowerCase() === 'pass' ? 'pass' : 'fail';
      html += '<div class="trace-gate ' + gc + '">Gate: ' + stage.gate.toUpperCase() + '</div>';
    }

    html += '</div></details>';
  });

  el.innerHTML = html;
}

function renderActivity(lines) {
  const el = document.getElementById('activityFeed');
  if (!lines || lines.length === 0) {
    el.innerHTML = '<div class="no-data">No activity yet.</div>';
    return;
  }
  el.innerHTML = lines.map(l => {
    const esc = escHtml(l);
    // Bold markdown headers
    if (l.startsWith('## ')) return '<div class="activity-line"><strong>' + esc.slice(3) + '</strong></div>';
    if (l.startsWith('- **')) return '<div class="activity-line">' + esc.replace(/\\*\\*/g, '') + '</div>';
    return '<div class="activity-line">' + esc + '</div>';
  }).join('');
  el.scrollTop = el.scrollHeight;
}

function renderMemory(lines) {
  const el = document.getElementById('memoryContent');
  if (!lines || lines.length === 0) {
    el.innerHTML = '<span class="no-data">No working memory yet.</span>';
    return;
  }
  el.textContent = lines.join('\\n');
}

function basename(path) { return path.split('/').pop(); }
function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

connect();
</script>
</body>
</html>
"""
