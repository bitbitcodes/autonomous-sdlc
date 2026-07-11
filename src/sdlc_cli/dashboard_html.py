"""HTML template for the SDLC real-time dashboard."""

DASHBOARD_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SDLC Agent Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
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

  <!-- Full width: Mermaid agent interaction diagram -->
  <div class="card" style="grid-column: 1 / -1;">
    <div class="card-title">Agent Interaction Diagram</div>
    <div id="mermaidDiagram" style="overflow-x:auto; padding:12px;">
      <span class="no-data">Loading diagram...</span>
    </div>
  </div>
</div>

<script>
const PHASE_NAMES = {
  '0-problem-discovery':'Problem Discovery','1-bootstrap':'Bootstrap','2-product':'Product',
  '3-story-tasks':'Story-Tasks','4-architecture':'Architecture','5-design':'Design',
  '6-development':'Development','7-testing':'Testing','8-security':'Security',
  '9-review':'Review','10-devops':'DevOps','11-observability':'Observability',
  '12-retirement':'Retirement'
};

const STATUS_ICONS = {
  complete: '\\u2705', in_progress: '\\uD83D\\uDD04', pending: '\\u2B1C',
  failed: '\\u274C', skipped: '\\u23ED\\uFE0F'
};

let ws;
let reconnectTimer;
// {phaseKey: bool} from phase-config.json. Disabled phases are hidden.
let PHASE_ENABLED = {};
function phaseDisabled(key) { return PHASE_ENABLED[key] === false; }

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

let lastGoodData = null;

function render(data) {
  // Guard: never overwrite good state with empty orchestrator data
  const orch = data.orchestrator;
  if (!orch || !orch.phases || Object.keys(orch.phases).length === 0) {
    if (lastGoodData) {
      data = lastGoodData;
    }
  } else {
    lastGoodData = data;
  }
  PHASE_ENABLED = data.phase_enabled || {};
  renderPhases(data.orchestrator, data.activity_log);
  renderStats(data.orchestrator, data.queue, data.model_config, data.activity_log);
  renderQueue(data.queue, data.orchestrator, data.activity_log);
  renderTrace(data.trace, data.orchestrator, data.activity_log, data.model_config);
  renderActivity(data.activity_log);
  renderMemory(data.continuity);
  if (data.mermaid_src) renderMermaid(data.mermaid_src);
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

function renderPhases(orch, activityLines) {
  if (!orch || !orch.phases) return;
  const el = document.getElementById('phases');
  const inferred = inferPhasesFromActivity(activityLines);
  const keys = Object.keys(orch.phases)
    .filter(k => !phaseDisabled(k))
    .sort((a,b) => parseInt(a) - parseInt(b));
  el.innerHTML = keys.map(k => {
    const p = orch.phases[k];
    const num = parseInt(k.split('-')[0]);
    const name = PHASE_NAMES[k] || k;
    let st = p.status || 'pending';
    if (st === 'pending' && inferred[num]) st = inferred[num];
    const icon = STATUS_ICONS[st] || '';
    return '<span class="phase-pill ' + st + '">' + icon + ' ' + num + '. ' + name + '</span>';
  }).join('');
}

function renderStats(orch, queue, mc, activityLines) {
  if (!orch) return;
  const inferred = inferPhasesFromActivity(activityLines);
  // Infer status from activity log if orchestrator is stale
  let displayStatus = orch.status || '--';
  const inferredVals = Object.values(inferred);
  if (displayStatus === 'initialized' && inferredVals.length > 0) displayStatus = 'in_progress';
  document.getElementById('statStatus').textContent = displayStatus;
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
  let done = orch.completed_tasks || 0;
  let total = orch.total_tasks || 0;
  if (total === 0 && orch.phases) {
    const keys = Object.keys(orch.phases).filter(k => !phaseDisabled(k));
    total = keys.length;
    done = 0;
    keys.forEach(k => {
      const num = parseInt(k);
      let st = orch.phases[k].status || 'pending';
      if (st === 'pending' && inferred[num]) st = inferred[num];
      if (st === 'complete') done++;
    });
  }
  document.getElementById('statTasks').textContent = done + ' / ' + total;
}

function renderQueue(q, orch, activityLines) {
  const el = document.getElementById('queue');
  let counts = { pending: 0, active: 0, completed: 0 };
  // Use queue files only if tasks are actually moving (active or completed > 0)
  const qMoving = q && (q.active > 0 || q.completed > 0);
  if (qMoving) {
    counts.pending = q.pending || 0;
    counts.active = q.active || 0;
    counts.completed = q.completed || 0;
  } else if (orch && orch.phases) {
    // Derive from orchestrator phases + activity log inference
    const inferred = inferPhasesFromActivity(activityLines);
    Object.entries(orch.phases).forEach(([k, p]) => {
      if (phaseDisabled(k)) return;
      const num = parseInt(k);
      let st = p.status || 'pending';
      if (st === 'pending' && inferred[num]) st = inferred[num];
      if (st === 'complete') counts.completed++;
      else if (st === 'in_progress') counts.active++;
      else counts.pending++;
    });
  }
  const total = Math.max(counts.pending + counts.active + counts.completed, 1);
  el.innerHTML = ['pending','active','completed'].map(k => {
    const v = counts[k] || 0;
    const pct = (v / total * 100).toFixed(1);
    return '<div class="queue-row">' +
      '<span class="queue-label">' + k.charAt(0).toUpperCase() + k.slice(1) + '</span>' +
      '<div class="queue-bar"><div class="queue-fill ' + k + '" style="width:' + pct + '%"></div></div>' +
      '<span class="queue-count">' + v + '</span></div>';
  }).join('');
}

// Map phase key (e.g. '5-development') to stage agent ID
const PHASE_AGENTS = {
  '0-problem-discovery':'stage-problem-discovery','1-bootstrap':'orch-sdlc','2-product':'stage-product',
  '3-story-tasks':'stage-story-tasks','4-architecture':'stage-architecture','5-design':'stage-design',
  '6-development':'stage-development','7-testing':'stage-testing','8-security':'stage-security',
  '9-review':'stage-review','10-devops':'stage-devops','11-observability':'stage-observability',
  '12-retirement':'stage-retirement'
};

const PHASE_SUBAGENTS = {
  0: ['sub-problem-statement-extractor','sub-user-research-synthesizer','sub-opportunity-analyzer','sub-solution-space-explorer'],
  1: [],
  2: ['sub-requirement-parser','sub-acceptance-criteria','sub-risk-analyzer','sub-assumption-extractor'],
  3: ['sub-story-writer','sub-task-decomposer','sub-dependency-mapper'],
  4: ['sub-tech-stack-advisor','sub-solution-evaluator','sub-adr-writer'],
  5: ['sub-interface-designer','sub-data-model-designer','sub-integration-planner','sub-nfr-evaluator'],
  6: ['sub-repo-analyzer','sub-code-generator','sub-refactoring-agent','sub-documentation-agent'],
  7: ['sub-unit-test','sub-integration-test','sub-regression-test','sub-test-data'],
  8: ['sub-secret-scanner','sub-dependency-scanner','sub-owasp-reviewer','sub-policy-validator'],
  9: ['sub-code-review','sub-maintainability','sub-performance'],
  10: [], 11: [],
  12: ['sub-deprecation-planner','sub-migration-strategist','sub-data-retention-auditor','sub-decommission-executor']
};

function inferPhasesFromActivity(lines) {
  if (!lines || !lines.length) return {};
  const result = {};
  let curPhase = null;
  for (const l of lines) {
    const pm = l.match(/Phase\\\\s+(\\\\d+)\\\\s*[:\\\\-]/i);
    if (pm) {
      const n = parseInt(pm[1]);
      if (curPhase !== null && curPhase !== n) result[curPhase] = 'complete';
      curPhase = n;
      result[n] = 'in_progress';
    }
    if (/Gate:\\\\s*PASS/i.test(l) && curPhase !== null) result[curPhase] = 'complete';
  }
  return result;
}

function parseActivityForPhase(lines, phaseName) {
  if (!lines || !lines.length) return { action: null, subs: [] };
  let action = null, subs = [];
  let inPhase = false;
  for (const l of lines) {
    if (l.includes('Phase') && l.toLowerCase().includes(phaseName.toLowerCase())) inPhase = true;
    else if (l.startsWith('[') || (l.startsWith('## ') && inPhase)) inPhase = false;
    if (!inPhase) continue;
    const am = l.match(/Action:\\\\s*(.+)/i);
    if (am) action = am[1];
    const sm = l.match(/Subagents? dispatched:\\\\s*(.+)/i);
    if (sm) subs = sm[1].split(',').map(s => s.trim()).filter(Boolean);
  }
  return { action, subs };
}

function renderTrace(trace, orch, activityLines, mc) {
  const el = document.getElementById('traceTree');

  // Build trace entries from file
  const byPhase = {};
  if (trace && trace.traces) {
    trace.traces.forEach(t => {
      const p = t.phase ?? 0;
      if (!byPhase[p]) byPhase[p] = [];
      byPhase[p].push(t);
    });
  }

  // Synthesize / augment entries using known agent registry + activity log inference
  if (orch && orch.phases) {
    const inferred = inferPhasesFromActivity(activityLines);
    const phaseKeys = Object.keys(orch.phases).sort((a,b) => parseInt(a) - parseInt(b));
    phaseKeys.forEach(k => {
      if (phaseDisabled(k)) return;
      const num = parseInt(k);
      const p = orch.phases[k];
      let st = p.status || 'pending';
      if (st === 'pending' && inferred[num]) st = inferred[num];
      // Skip phases that haven't run: 'pending' and the triggered-only
      // Retirement phase's default 'not_triggered' status. Without this,
      // Phase 12 (Retirement) renders alone at the top on a fresh run.
      if (st === 'pending' || st === 'not_triggered') return;

      const phaseName = PHASE_NAMES[k] || k.replace(/^\\d+-/, '');
      const agentId = PHASE_AGENTS[k] || 'unknown';
      const knownSubs = PHASE_SUBAGENTS[num] || [];

      if (!byPhase[num]) {
        // No trace data — synthesize stage entry
        const parsed = parseActivityForPhase(activityLines, phaseName);
        byPhase[num] = [{
          agent: agentId, role: num === 0 ? 'orchestrator' : 'stage',
          phase: num, phase_name: phaseName, status: st,
          gate: p.gate, model: resolveModel(agentId, mc), action: parsed.action,
          input_artifacts: [], output_artifacts: []
        }];
      } else {
        // Update status of existing stage entry from inferred data
        const stageEntry = byPhase[num].find(e => e.role === 'stage' || e.role === 'orchestrator');
        if (stageEntry && stageEntry.status === 'pending') stageEntry.status = st;
      }

      // Always ensure known subagents are present (even if trace exists but lacks them)
      const existingSubs = new Set(byPhase[num].filter(e => e.role === 'subagent').map(e => e.agent));
      knownSubs.forEach(sub => {
        if (!existingSubs.has(sub)) {
          byPhase[num].push({
            agent: sub, role: 'subagent', phase: num, phase_name: phaseName,
            status: st, model: resolveModel(sub, mc),
            input_artifacts: [], output_artifacts: []
          });
        }
      });
    });
  }

  const phaseNums = Object.keys(byPhase).sort((a,b) => a - b);
  if (phaseNums.length === 0) {
    el.innerHTML = '<div class="no-data">No agent interactions recorded yet.</div>';
    return;
  }

  let html = '';
  phaseNums.forEach(phaseNum => {
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

let mermaidReady = false;
try {
  mermaid.initialize({ startOnLoad: false, theme: 'dark', themeVariables: {
    primaryColor: '#161b22', primaryTextColor: '#e6edf3', primaryBorderColor: '#30363d',
    lineColor: '#58a6ff', secondaryColor: '#21262d', tertiaryColor: '#0d1117'
  }});
  mermaidReady = true;
} catch(e) { console.warn('Mermaid not loaded:', e); }

let lastMermaidSrc = '';
async function renderMermaid(src) {
  const el = document.getElementById('mermaidDiagram');
  if (!src) {
    el.innerHTML = '<span class="no-data">No diagram data.</span>';
    return;
  }
  if (src === lastMermaidSrc) return;
  lastMermaidSrc = src;
  if (!mermaidReady) {
    el.innerHTML = '<span class="no-data">Mermaid library not loaded.</span>';
    return;
  }
  try {
    const { svg } = await mermaid.render('agentDiagram', src);
    el.innerHTML = svg;
  } catch(e) {
    console.error('Mermaid render error:', e);
    el.innerHTML = '<span class="no-data">Diagram render error. Check console.</span>';
  }
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
