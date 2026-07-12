const PHASE_NAMES = {
  '0-problem-discovery':'Problem Discovery','1-bootstrap':'Bootstrap','2-product':'Product',
  '3-story-tasks':'Story-Tasks','4-architecture':'Architecture','5-design':'Design',
  '6-development':'Development','7-testing':'Testing','8-security':'Security',
  '9-review':'Review','10-devops':'DevOps','11-observability':'Observability',
  '12-retirement':'Retirement'
};

const STATUS_ICONS = {
  complete: '\u2705', in_progress: '\uD83D\uDD04', pending: '\u2B1C',
  failed: '\u274C', skipped: '\u23ED\uFE0F'
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
      // If new data is partial, merge it with last good state
      data.orchestrator = lastGoodData.orchestrator;
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
  let currentPhase = -1;

  lines.forEach(line => {
    const phaseMatch = line.match(/Phase (\d+):/i) || line.match(/Next: Phase (\d+)/i);
    if (phaseMatch) {
      const phaseNum = parseInt(phaseMatch[1], 10);
      if (phaseNum > currentPhase) {
        if (currentPhase !== -1) {
          result[currentPhase] = 'complete';
        }
        for (let i = 0; i < phaseNum; i++) {
          if (!result[i]) {
            result[i] = 'complete';
          }
        }
        currentPhase = phaseNum;
        result[currentPhase] = 'in_progress';
      }
    }

    if (/Gate:\s*PASS/i.test(line) && currentPhase !== -1) {
      result[currentPhase] = 'complete';
    }
  });

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
    const am = l.match(/Action:\s*(.+)/i);
    if (am) action = am[1];
    const sm = l.match(/Subagents? dispatched:\s*(.+)/i);
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

      const phaseName = PHASE_NAMES[k] || k.replace(/^\d+-/, '');
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
  el.textContent = lines.join('\n');
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
