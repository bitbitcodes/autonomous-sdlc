#!/usr/bin/env bash
set -euo pipefail

# Autonomous SDLC Framework — Runner Script
# Usage: ./run.sh <command> [args]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Determine project root
# When installed: script is at <project>/.sdlc/framework/run.sh
# When developing: script is at <repo>/run.sh
if [[ "$(basename "$(dirname "$SCRIPT_DIR")" )" == ".sdlc" ]]; then
  PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
else
  PROJECT_ROOT="$SCRIPT_DIR"
fi
SDLC_DIR="${PROJECT_ROOT}/.sdlc"
VERSION="1.1.0"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ─────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────

print_banner() {
  echo -e "${CYAN}"
  echo "  ╔═══════════════════════════════════════════╗"
  echo "  ║     Autonomous SDLC Framework v${VERSION}     ║"
  echo "  ║     Multi-Agent AI Development Cycle      ║"
  echo "  ╚═══════════════════════════════════════════╝"
  echo -e "${NC}"
}

log_info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ─────────────────────────────────────────────
# init — Initialize .sdlc/ directory structure
# ─────────────────────────────────────────────

cmd_init() {
  log_info "Initializing .sdlc/ directory structure..."

  # State
  mkdir -p "${SDLC_DIR}/state"
  mkdir -p "${SDLC_DIR}/queue"

  # Memory
  mkdir -p "${SDLC_DIR}/memory/episodic"
  mkdir -p "${SDLC_DIR}/memory/semantic"
  mkdir -p "${SDLC_DIR}/memory/learnings"

  # Artifacts (per phase)
  mkdir -p "${SDLC_DIR}/artifacts/product"
  mkdir -p "${SDLC_DIR}/artifacts/story-tasks"
  mkdir -p "${SDLC_DIR}/artifacts/architecture"
  mkdir -p "${SDLC_DIR}/artifacts/design"
  mkdir -p "${SDLC_DIR}/artifacts/development"
  mkdir -p "${SDLC_DIR}/artifacts/testing"
  mkdir -p "${SDLC_DIR}/artifacts/security"
  mkdir -p "${SDLC_DIR}/artifacts/review"
  mkdir -p "${SDLC_DIR}/artifacts/devops"
  mkdir -p "${SDLC_DIR}/artifacts/observability"

  # Specs
  mkdir -p "${SDLC_DIR}/specs"

  # Initialize orchestrator state
  cat > "${SDLC_DIR}/state/orchestrator.json" << 'EOF'
{
  "current_phase": 0,
  "status": "initialized",
  "complexity": null,
  "phases": {
    "0-bootstrap": { "status": "pending", "gate": null, "review": null },
    "1-product": { "status": "pending", "gate": null, "review": null },
    "2-story-tasks": { "status": "pending", "gate": null, "review": null },
    "3-architecture": { "status": "pending", "gate": null, "review": null },
    "4-design": { "status": "pending", "gate": null, "review": null },
    "5-development": { "status": "pending", "gate": null, "review": null },
    "6-testing": { "status": "pending", "gate": null, "review": null },
    "7-security": { "status": "pending", "gate": null, "review": null },
    "8-review": { "status": "pending", "gate": null, "review": null },
    "9-devops": { "status": "pending", "gate": null, "review": null },
    "10-observability": { "status": "pending", "gate": null, "review": null }
  },
  "active_agents": [],
  "total_tasks": 0,
  "completed_tasks": 0,
  "failed_tasks": 0,
  "blocked_tasks": 0,
  "start_time": null,
  "last_updated": null
}
EOF

  # Initialize queue files
  echo '[]' > "${SDLC_DIR}/queue/pending.json"
  echo '[]' > "${SDLC_DIR}/queue/active.json"
  echo '[]' > "${SDLC_DIR}/queue/completed.json"

  # Initialize memory index
  echo '[]' > "${SDLC_DIR}/memory/episodic/index.json"
  echo '{"patterns": []}' > "${SDLC_DIR}/memory/semantic/patterns.json"
  echo '{"anti_patterns": []}' > "${SDLC_DIR}/memory/semantic/anti-patterns.json"
  echo '[]' > "${SDLC_DIR}/memory/learnings/index.json"

  # Initialize STATUS.md — overall agent dashboard
  cat > "${SDLC_DIR}/STATUS.md" << 'EOF'
# SDLC Status Dashboard

> Auto-updated by the orchestrator at every phase transition.
> Last updated: not started

## Overall Progress

| Metric       | Value       |
|--------------|-------------|
| Status       | initialized |
| Complexity   | —           |
| Current Phase| 0 (Bootstrap) |
| Tasks Done   | 0 / 0       |
| Gate Passes  | 0 / 11      |

## Phase & Agent Status

| Phase | Name           | Agent                  | Subagents Used | Status  | Gate | Key Outcome |
|-------|----------------|------------------------|----------------|---------|------|-------------|
| 0     | Bootstrap      | orch-sdlc              | —              | pending | —    | —           |
| 1     | Product        | stage-product          | —              | pending | —    | —           |
| 2     | Story-Tasks    | stage-story-tasks      | —              | pending | —    | —           |
| 3     | Architecture   | stage-architecture     | —              | pending | —    | —           |
| 4     | Design         | stage-design           | —              | pending | —    | —           |
| 5     | Development    | stage-development      | —              | pending | —    | —           |
| 6     | Testing        | stage-testing          | —              | pending | —    | —           |
| 7     | Security       | stage-security         | —              | pending | —    | —           |
| 8     | Review         | stage-review           | —              | pending | —    | —           |
| 9     | DevOps         | stage-devops           | —              | pending | —    | —           |
| 10    | Observability  | stage-observability    | —              | pending | —    | —           |

## Subagent Detail

| Phase | Subagent                    | Status  | Outcome |
|-------|-----------------------------|---------|---------|
| 1     | sub-requirement-parser      | pending | —       |
| 1     | sub-acceptance-criteria     | pending | —       |
| 1     | sub-risk-analyzer           | pending | —       |
| 1     | sub-assumption-extractor    | pending | —       |
| 2     | sub-story-writer            | pending | —       |
| 2     | sub-task-decomposer         | pending | —       |
| 2     | sub-dependency-mapper       | pending | —       |
| 3     | sub-tech-stack-advisor      | pending | —       |
| 3     | sub-solution-evaluator      | pending | —       |
| 3     | sub-adr-writer              | pending | —       |
| 4     | sub-interface-designer      | pending | —       |
| 4     | sub-data-model-designer     | pending | —       |
| 4     | sub-integration-planner     | pending | —       |
| 4     | sub-nfr-evaluator           | pending | —       |
| 5     | sub-repo-analyzer           | pending | —       |
| 5     | sub-code-generator          | pending | —       |
| 5     | sub-refactoring-agent       | pending | —       |
| 5     | sub-documentation-agent     | pending | —       |
| 6     | sub-unit-test               | pending | —       |
| 6     | sub-integration-test        | pending | —       |
| 6     | sub-regression-test         | pending | —       |
| 6     | sub-test-data               | pending | —       |
| 7     | sub-secret-scanner          | pending | —       |
| 7     | sub-dependency-scanner      | pending | —       |
| 7     | sub-owasp-reviewer          | pending | —       |
| 7     | sub-policy-validator        | pending | —       |
| 8     | sub-code-review             | pending | —       |
| 8     | sub-maintainability         | pending | —       |
| 8     | sub-performance             | pending | —       |

## Artifacts Produced

| Phase | Artifact | Path |
|-------|----------|------|
| —     | —        | —    |
EOF

  # Initialize agent trace log
  echo '{"traces": []}' > "${SDLC_DIR}/state/agent-trace.json"

  # Initialize activity log
  cat > "${SDLC_DIR}/state/activity-log.md" << 'EOF'
# Activity Log

Records every agent dispatch, action, and artifact produced.

> No agent actions yet. The orchestrator will append entries here as it executes phases.
EOF

  # Initialize CONTINUITY.md
  cat > "${SDLC_DIR}/CONTINUITY.md" << 'EOF'
# CONTINUITY — Working Memory

## Current Phase
Phase 0: Bootstrap — Initialized, awaiting spec input.

## Active Tasks
- None

## Completed Tasks
- None

## Mistakes & Learnings
- None yet

## Decisions Made
- None yet

## Next Steps
1. Receive input spec (PRD, brief, YAML, or issue)
2. Normalize spec to .sdlc/specs/normalized-spec.md
3. Detect complexity and select agent team
4. Begin Phase 1: Product Discovery

## Open Questions
- None

## Blocked Items
- None
EOF

  log_ok "Initialized ${SDLC_DIR}/ directory structure"
  log_info "Directories created:"
  find "${SDLC_DIR}" -type d | sort | sed 's/^/  /'
}

# ─────────────────────────────────────────────
# start — Start SDLC with an input spec
# ─────────────────────────────────────────────

cmd_start() {
  local spec_input="${1:-}"

  if [[ -z "$spec_input" ]]; then
    log_error "No spec provided. Usage: ./run.sh start <spec-file-or-brief>"
    echo ""
    echo "Examples:"
    echo "  ./run.sh start ./prd.md              # Markdown PRD"
    echo "  ./run.sh start ./spec.yaml           # YAML spec"
    echo "  ./run.sh start ./spec.json           # JSON spec"
    echo "  ./run.sh start \"Build a todo app\"    # One-liner brief"
    exit 1
  fi

  # Initialize if not already done
  if [[ ! -d "$SDLC_DIR" ]]; then
    cmd_init
  fi

  # Detect input type and normalize
  if [[ -f "$spec_input" ]]; then
    local ext="${spec_input##*.}"
    log_info "Detected spec file: ${spec_input} (${ext})"
    cp "$spec_input" "${SDLC_DIR}/specs/original-spec.${ext}"
    cp "$spec_input" "${SDLC_DIR}/specs/normalized-spec.md"
    log_ok "Spec copied to ${SDLC_DIR}/specs/"
  else
    # Treat as one-liner brief
    log_info "Detected one-liner brief"
    echo "# Project Brief" > "${SDLC_DIR}/specs/normalized-spec.md"
    echo "" >> "${SDLC_DIR}/specs/normalized-spec.md"
    echo "$spec_input" >> "${SDLC_DIR}/specs/normalized-spec.md"
    log_ok "Brief saved to ${SDLC_DIR}/specs/normalized-spec.md"
  fi

  # Detect complexity (simple heuristic)
  local spec_lines
  spec_lines=$(wc -l < "${SDLC_DIR}/specs/normalized-spec.md" | tr -d ' ')
  local complexity="simple"
  if (( spec_lines > 100 )); then
    complexity="enterprise"
  elif (( spec_lines > 50 )); then
    complexity="complex"
  elif (( spec_lines > 15 )); then
    complexity="medium"
  fi

  log_info "Detected complexity: ${complexity} (${spec_lines} lines)"

  # Update orchestrator state
  local now
  now=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  # Use python for JSON update (cross-platform)
  python3 -c "
import json, sys
with open('${SDLC_DIR}/state/orchestrator.json', 'r') as f:
    state = json.load(f)
state['complexity'] = '${complexity}'
state['status'] = 'in_progress'
state['start_time'] = '${now}'
state['last_updated'] = '${now}'
state['phases']['0-bootstrap']['status'] = 'complete'
state['phases']['0-bootstrap']['gate'] = 'pass'
state['current_phase'] = 1
with open('${SDLC_DIR}/state/orchestrator.json', 'w') as f:
    json.dump(state, f, indent=2)
" 2>/dev/null || log_warn "Could not update orchestrator.json (python3 not available)"

  # Update CONTINUITY.md
  cat > "${SDLC_DIR}/CONTINUITY.md" << EOF
# CONTINUITY — Working Memory

## Current Phase
Phase 1: Product Discovery — Bootstrap complete, spec loaded.

## Complexity
${complexity}

## Active Tasks
- Phase 1: Dispatch Product Agent

## Completed Tasks
- Phase 0: Bootstrap — Initialized .sdlc/, normalized spec, detected complexity: ${complexity}

## Mistakes & Learnings
- None yet

## Decisions Made
- Complexity detected as ${complexity} (${spec_lines} lines in spec)

## Next Steps
1. Read .sdlc/framework/agents/orchestrator.md — adopt orchestrator role
2. Dispatch stage-product agent (.sdlc/framework/agents/stage/product.md)
3. Execute Phase 1: Product Discovery

## Open Questions
- None

## Blocked Items
- None
EOF

  echo ""
  log_ok "Bootstrap complete!"
  echo ""
  echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${CYAN}║                    NEXT STEP                                 ║${NC}"
  echo -e "${CYAN}╠═══════════════════════════════════════════════════════════════╣${NC}"
  echo -e "${CYAN}║                                                              ║${NC}"
  echo -e "${CYAN}║  Open your AI IDE and select the sdlc.orchestrator agent:    ║${NC}"
  echo -e "${CYAN}║                                                              ║${NC}"
  echo -e "${CYAN}║  Copilot:    Select sdlc.orchestrator from agent dropdown    ║${NC}"
  echo -e "${CYAN}║  Windsurf:   Type /sdlc.orchestrator in Cascade chat         ║${NC}"
  echo -e "${CYAN}║  Claude Code: Type /sdlc-orchestrator in chat                ║${NC}"
  echo -e "${CYAN}║  Cursor:     Start chat (context auto-loads)                 ║${NC}"
  echo -e "${CYAN}║                                                              ║${NC}"
  echo -e "${CYAN}║  The orchestrator picks up the pre-loaded spec and begins.   ║${NC}"
  echo -e "${CYAN}║                                                              ║${NC}"
  echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
}

# ─────────────────────────────────────────────
# status — Show current SDLC status
# ─────────────────────────────────────────────

cmd_status() {
  if [[ ! -d "$SDLC_DIR" ]]; then
    log_error "Not initialized. Run: ./run.sh init"
    exit 1
  fi

  print_banner

  # Show STATUS.md dashboard if available
  if [[ -f "${SDLC_DIR}/STATUS.md" ]]; then
    echo -e "${CYAN}─── Agent Dashboard (STATUS.md) ───${NC}"
    echo ""
    cat "${SDLC_DIR}/STATUS.md" | sed 's/^/  /'
    echo ""
    echo -e "${CYAN}─── Detailed State ───${NC}"
    echo ""
  fi

  echo -e "${BLUE}Current State:${NC}"
  echo ""

  # Show orchestrator state
  if [[ -f "${SDLC_DIR}/state/orchestrator.json" ]]; then
    python3 -c "
import json
with open('${SDLC_DIR}/state/orchestrator.json', 'r') as f:
    content = f.read()
try:
    state = json.loads(content)
except json.JSONDecodeError:
    state, _ = json.JSONDecoder().raw_decode(content)
    print('  ⚠ Warning: orchestrator.json has extra data — using first valid object.')

phase_names = {
    '0-bootstrap': 'Bootstrap',
    '1-product': 'Product',
    '2-story-tasks': 'Story-Tasks',
    '3-architecture': 'Architecture',
    '4-design': 'Design',
    '5-development': 'Development',
    '6-testing': 'Testing',
    '7-security': 'Security',
    '8-review': 'Review',
    '9-devops': 'DevOps',
    '10-observability': 'Observability'
}

agent_map = {
    '0-bootstrap': 'orch-sdlc',
    '1-product': 'stage-product (4 subagents)',
    '2-story-tasks': 'stage-story-tasks (3 subagents)',
    '3-architecture': 'stage-architecture (3 subagents)',
    '4-design': 'stage-design (4 subagents)',
    '5-development': 'stage-development (4 subagents)',
    '6-testing': 'stage-testing (4 subagents)',
    '7-security': 'stage-security (4 subagents)',
    '8-review': 'stage-review (3 subagents)',
    '9-devops': 'stage-devops',
    '10-observability': 'stage-observability'
}

status_icons = {
    'complete': '✅',
    'in_progress': '🔄',
    'pending': '⬜',
    'failed': '❌'
}

print(f'  Status:     {state[\"status\"]}')
print(f'  Complexity: {state.get(\"complexity\", \"unknown\")}')
print(f'  Phase:      {state[\"current_phase\"]}')
print(f'  Tasks:      {state[\"completed_tasks\"]}/{state[\"total_tasks\"]} complete')
print()
print('  Phases:')
for key, phase in state['phases'].items():
    name = phase_names.get(key, key)
    icon = status_icons.get(phase['status'], '❓')
    agent = agent_map.get(key, '')
    gate = f' (gate: {phase[\"gate\"]})' if phase['gate'] else ''
    print(f'    {icon} {name}: {phase[\"status\"]}{gate}')
    print(f'       Agent: {agent}')
" 2>/dev/null || cat "${SDLC_DIR}/state/orchestrator.json"
  fi

  echo ""

  # Show CONTINUITY.md summary
  if [[ -f "${SDLC_DIR}/CONTINUITY.md" ]]; then
    echo -e "${BLUE}Working Memory (CONTINUITY.md):${NC}"
    head -20 "${SDLC_DIR}/CONTINUITY.md" | sed 's/^/  /'
  fi

  echo ""

  # Show queue counts
  if [[ -f "${SDLC_DIR}/queue/pending.json" ]]; then
    local pending active completed
    pending=$(python3 -c "import json; print(len(json.load(open('${SDLC_DIR}/queue/pending.json'))))" 2>/dev/null || echo "?")
    active=$(python3 -c "import json; print(len(json.load(open('${SDLC_DIR}/queue/active.json'))))" 2>/dev/null || echo "?")
    completed=$(python3 -c "import json; print(len(json.load(open('${SDLC_DIR}/queue/completed.json'))))" 2>/dev/null || echo "?")
    echo -e "${BLUE}Queue:${NC}"
    echo "  Pending:   ${pending}"
    echo "  Active:    ${active}"
    echo "  Completed: ${completed}"
  fi

  echo ""

  # Show activity log (last 20 lines)
  if [[ -f "${SDLC_DIR}/state/activity-log.md" ]]; then
    local log_lines
    log_lines=$(wc -l < "${SDLC_DIR}/state/activity-log.md" | tr -d ' ')
    if (( log_lines > 5 )); then
      echo -e "${BLUE}Activity Log (last 20 lines):${NC}"
      tail -20 "${SDLC_DIR}/state/activity-log.md" | sed 's/^/  /'
    else
      echo -e "${BLUE}Activity Log:${NC}"
      echo "  No agent actions recorded yet."
    fi
  fi
}

# ─────────────────────────────────────────────
# trace — Show agent interaction map
# ─────────────────────────────────────────────

cmd_trace() {
  if [[ ! -d "$SDLC_DIR" ]]; then
    log_error "Not initialized. Run: ./run.sh init"
    exit 1
  fi

  local trace_file="${SDLC_DIR}/state/agent-trace.json"
  if [[ ! -f "$trace_file" ]]; then
    log_error "No trace file found. Run the orchestrator first."
    exit 1
  fi

  local phase_filter="${1:-}"

  echo -e "${CYAN}"
  echo "  ╔═══════════════════════════════════════════╗"
  echo "  ║        Agent Interaction Map              ║"
  echo "  ╚═══════════════════════════════════════════╝"
  echo -e "${NC}"

  python3 -c "
import json, os, sys

with open('${trace_file}', 'r') as f:
    data = json.load(f)

traces = data.get('traces', [])
if not traces:
    print('  No agent interactions recorded yet.')
    print('  Run the orchestrator to generate trace data.')
    sys.exit(0)

phase_filter = '${phase_filter}' if '${phase_filter}' else None

# Group by phase
phases = {}
for t in traces:
    p = t.get('phase', 0)
    if phase_filter and str(p) != phase_filter:
        continue
    phases.setdefault(p, [])
    phases[p].append(t)

status_icon = {'complete': '✅', 'in_progress': '🔄', 'pending': '⬜', 'failed': '❌', 'skipped': '⏭️'}
verified = 0
missing = 0

for phase_num in sorted(phases.keys()):
    entries = phases[phase_num]
    # Find the stage-level entry
    stage = next((e for e in entries if e.get('role') in ('orchestrator', 'stage')), entries[0])
    icon = status_icon.get(stage.get('status', 'pending'), '❓')
    print(f\"Phase {phase_num}: {stage.get('phase_name', '?').title()} {icon}\")
    print(f\"  {stage['agent']}\")

    # Show subagent dispatches
    subs = [e for e in entries if e.get('role') == 'subagent']
    for i, sub in enumerate(subs):
        is_last = (i == len(subs) - 1)
        prefix = '└──' if is_last else '├──'
        sub_icon = status_icon.get(sub.get('status', 'pending'), '❓')
        print(f\"  {prefix} {sub['agent']} {sub_icon}\")
        child_prefix = '    ' if is_last else '│   '
        # Show inputs
        for inp in sub.get('input_artifacts', []):
            exists = os.path.isfile(os.path.join('${PROJECT_ROOT}', inp))
            mark = '✅' if exists else '⚠️  MISSING'
            print(f\"  {child_prefix}In:  {os.path.basename(inp)} {mark}\")
        # Show outputs
        for out in sub.get('output_artifacts', []):
            exists = os.path.isfile(os.path.join('${PROJECT_ROOT}', out))
            if exists:
                verified += 1
                mark = '✅'
            else:
                missing += 1
                mark = '⚠️  MISSING'
            print(f\"  {child_prefix}Out: {os.path.basename(out)} {mark}\")

    # Show stage-level outputs if no subs
    if not subs:
        for out in stage.get('output_artifacts', []):
            exists = os.path.isfile(os.path.join('${PROJECT_ROOT}', out))
            if exists:
                verified += 1
                mark = '✅'
            else:
                missing += 1
                mark = '⚠️  MISSING'
            print(f\"  └── Out: {os.path.basename(out)} {mark}\")

    gate = stage.get('gate', '')
    if gate:
        print(f\"  Gate: {gate.upper()}\")
    print()

print('─── Artifact Verification ───')
print(f'✅ {verified} artifacts traced and verified on disk')
if missing:
    print(f'⚠️  {missing} artifacts traced but MISSING on disk')
else:
    print(f'✅ 0 artifacts traced but missing on disk')
" 2>/dev/null || log_error "Could not render trace (python3 required)"
}

# ─────────────────────────────────────────────
# run — Multi-run management
# ─────────────────────────────────────────────

cmd_run() {
  if [[ ! -d "$SDLC_DIR" ]]; then
    log_error "Not initialized. Run: ./run.sh init"
    exit 1
  fi

  local subcmd="${1:-help}"
  shift || true

  case "$subcmd" in
    new)
      python3 -c "
import sys, os
sys.path.insert(0, os.path.join('${PROJECT_ROOT}', 'src'))
from sdlc_cli.__init__ import app
sys.argv = ['sdlc', 'run', 'new'] + sys.argv[1:]
app()
" "$@"
      ;;
    list)
      python3 -c "
import sys, os
sys.path.insert(0, os.path.join('${PROJECT_ROOT}', 'src'))
from sdlc_cli.__init__ import app
sys.argv = ['sdlc', 'run', 'list']
app()
"
      ;;
    switch)
      python3 -c "
import sys, os
sys.path.insert(0, os.path.join('${PROJECT_ROOT}', 'src'))
from sdlc_cli.__init__ import app
sys.argv = ['sdlc', 'run', 'switch', '$1']
app()
"
      ;;
    active)
      python3 -c "
import sys, os
sys.path.insert(0, os.path.join('${PROJECT_ROOT}', 'src'))
from sdlc_cli.__init__ import app
sys.argv = ['sdlc', 'run', 'active']
app()
"
      ;;
    archive)
      python3 -c "
import sys, os
sys.path.insert(0, os.path.join('${PROJECT_ROOT}', 'src'))
from sdlc_cli.__init__ import app
sys.argv = ['sdlc', 'run', 'archive', '$1']
app()
"
      ;;
    help|*)
      echo "Usage: ./run.sh run <subcommand>"
      echo ""
      echo "Subcommands:"
      echo "  new [spec-file]     Create a new run (auto-names from spec)"
      echo "  list                List all runs with status"
      echo "  switch <slug>       Set the active run"
      echo "  active              Show current active run"
      echo "  archive <slug>      Archive a completed run"
      ;;
  esac
}

# ─────────────────────────────────────────────
# dashboard — Launch real-time web dashboard
# ─────────────────────────────────────────────

cmd_dashboard() {
  if [[ ! -d "$SDLC_DIR" ]]; then
    log_error "Not initialized. Run: ./run.sh init"
    exit 1
  fi

  local port="${1:-8420}"

  if ! python3 -c 'import websockets' 2>/dev/null; then
    log_error "The 'websockets' package is required for the dashboard."
    echo "  Install it with: pip install websockets"
    echo "  or: pip install autonomous-sdlc[dashboard]"
    exit 1
  fi

  echo -e "${CYAN}SDLC Dashboard${NC} starting on http://127.0.0.1:${port}"
  echo "WebSocket on port $((port + 1))"
  echo "Press Ctrl+C to stop."
  echo ""

  python3 -c "
import sys, os
sys.path.insert(0, os.path.join('${PROJECT_ROOT}', 'src'))
from pathlib import Path
from sdlc_cli.dashboard import serve
serve(Path('${SDLC_DIR}'), port=${port})
"
}

# ─────────────────────────────────────────────
# models — Show/manage per-agent model routing
# ─────────────────────────────────────────────

cmd_models() {
  if [[ ! -d "$SDLC_DIR" ]]; then
    log_error "Not initialized. Run: ./run.sh init"
    exit 1
  fi

  local flag="${1:-}"

  if [[ "$flag" == "--reset" ]]; then
    python3 -c "
import sys, os
sys.path.insert(0, os.path.join('${PROJECT_ROOT}', 'src'))
from pathlib import Path
from sdlc_cli.models import write_config
write_config(Path('${SDLC_DIR}'))
print('Model config reset to defaults.')
"
    return
  fi

  if [[ "$flag" == "--edit" ]]; then
    local config_file="${SDLC_DIR}/model-config.json"
    if [[ ! -f "$config_file" ]]; then
      python3 -c "
import sys, os
sys.path.insert(0, os.path.join('${PROJECT_ROOT}', 'src'))
from pathlib import Path
from sdlc_cli.models import write_config
write_config(Path('${SDLC_DIR}'))
"
    fi
    "${EDITOR:-vi}" "$config_file"
    return
  fi

  # Display current config
  python3 -c "
import sys, os, json
sys.path.insert(0, os.path.join('${PROJECT_ROOT}', 'src'))
from pathlib import Path
from sdlc_cli.models import load_config, resolve_all, default_config, write_config, TIER_DESCRIPTIONS

sdlc_dir = Path('${SDLC_DIR}')
config = load_config(sdlc_dir)
if config is None:
    config = default_config()
    write_config(sdlc_dir, config)

tiers = config.get('tiers', {})
print('Model Tiers:')
print(f'  {"Tier":<12} {"Model":<22} Purpose')
print(f'  {"-"*12} {"-"*22} {"-"*40}')
for t, m in tiers.items():
    desc = TIER_DESCRIPTIONS.get(t, '')
    print(f'  {t:<12} {m:<22} {desc}')

print()
resolved = resolve_all(config)
print('Agent Assignments:')
print(f'  {"Agent":<24} {"Tier":<12} Model')
print(f'  {"-"*24} {"-"*12} {"-"*22}')
for aid in sorted(resolved):
    info = resolved[aid]
    print(f'  {aid:<24} {info["tier"]:<12} {info["model"]}')
"
}

# ─────────────────────────────────────────────
# reset — Reset .sdlc/ state (keep framework)
# ─────────────────────────────────────────────

cmd_reset() {
  if [[ ! -d "$SDLC_DIR" ]]; then
    log_warn "Nothing to reset — ${SDLC_DIR}/ does not exist"
    exit 0
  fi

  log_warn "This will delete all runtime state in ${SDLC_DIR}/"
  echo -n "Continue? [y/N] "
  read -r confirm
  if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    log_info "Aborted"
    exit 0
  fi

  rm -rf "${SDLC_DIR}"
  log_ok "Removed ${SDLC_DIR}/"
  cmd_init
}

# ─────────────────────────────────────────────
# prompt — Output the orchestrator prompt for piping
# ─────────────────────────────────────────────

cmd_prompt() {
  local agent="${1:-orchestrator}"
  local prompt_file

  if [[ "$agent" == "orchestrator" ]]; then
    prompt_file="${SCRIPT_DIR}/agents/orchestrator.md"
  elif [[ -f "${SCRIPT_DIR}/agents/stage/${agent}.md" ]]; then
    prompt_file="${SCRIPT_DIR}/agents/stage/${agent}.md"
  elif [[ -f "${SCRIPT_DIR}/agents/sub/${agent}" ]]; then
    prompt_file="${SCRIPT_DIR}/agents/sub/${agent}"
  else
    log_error "Unknown agent: ${agent}"
    echo "Available agents:"
    echo "  orchestrator"
    ls "${SCRIPT_DIR}/agents/stage/" 2>/dev/null | sed 's/\.md$//' | sed 's/^/  stage: /'
    exit 1
  fi

  cat "$prompt_file"
}

# ─────────────────────────────────────────────
# help
# ─────────────────────────────────────────────

cmd_help() {
  print_banner
  echo "Usage: ./run.sh <command> [args]"
  echo ""
  echo "Commands:"
  echo "  init                Initialize .sdlc/ directory structure"
  echo "  start <spec>        Start SDLC with an input spec"
  echo "  status              Show current SDLC status"
  echo "  trace [phase]       Show agent interaction map"
  echo "  run <subcommand>    Manage multiple runs (new/list/switch/archive)"
  echo "  dashboard [port]    Launch real-time web dashboard (default: 8420)"
  echo "  models [--edit|--reset]  Show/manage per-agent model routing"
  echo "  upgrade [--dry-run]     Update framework files (keeps runtime state)"
  echo "  reset               Reset .sdlc/ state"
  echo "  prompt [agent]      Output an agent's prompt (default: orchestrator)"
  echo "  help                Show this help message"
  echo ""
  echo "Examples:"
  echo "  ./run.sh init"
  echo "  ./run.sh start ./prd.md"
  echo "  ./run.sh start \"Build a REST API for a blog platform\""
  echo "  ./run.sh status"
  echo "  ./run.sh prompt orchestrator"
  echo ""
  echo "Spec formats supported:"
  echo "  .md     Markdown PRD"
  echo "  .yaml   YAML spec"
  echo "  .json   JSON spec"
  echo "  .txt    Plain text brief"
  echo "  string  One-liner brief (in quotes)"
  echo ""
  echo "IDE setup is handled by the CLI: sdlc init --integration <ide>"
}

# ─────────────────────────────────────────────
# upgrade — Update framework files only
# ─────────────────────────────────────────────

cmd_upgrade() {
  if [[ ! -d "$SDLC_DIR" ]]; then
    log_error "Not initialized. Run: ./run.sh init"
    exit 1
  fi

  local dry_flag=""
  if [[ "${1:-}" == "--dry-run" ]]; then
    dry_flag="--dry-run"
  fi

  python3 -c "
import sys, os
sys.path.insert(0, os.path.join('${PROJECT_ROOT}', 'src'))
from sdlc_cli.__init__ import app
sys.argv = ['sdlc', 'upgrade', '${PROJECT_ROOT}']
if '${dry_flag}':
    sys.argv.append('${dry_flag}')
app()
"
}

# ─────────────────────────────────────────────
# Main dispatcher
# ─────────────────────────────────────────────

main() {
  local cmd="${1:-help}"
  shift || true

  case "$cmd" in
    init)       cmd_init "$@" ;;
    start)      cmd_start "$@" ;;
    status)     cmd_status "$@" ;;
    trace)      cmd_trace "$@" ;;
    run)        cmd_run "$@" ;;
    dashboard)  cmd_dashboard "$@" ;;
    models)     cmd_models "$@" ;;
    upgrade)    cmd_upgrade "$@" ;;
    reset)      cmd_reset "$@" ;;
    prompt)     cmd_prompt "$@" ;;
    help|-h|--help) cmd_help ;;
    version|-v|--version) echo "autonomous-sdlc v${VERSION}" ;;
    *)
      log_error "Unknown command: ${cmd}"
      cmd_help
      exit 1
      ;;
  esac
}

main "$@"
