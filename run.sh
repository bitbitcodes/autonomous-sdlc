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
# Single source of truth: read the package version; fall back if unavailable.
VERSION="$(python3 -c "import sys, os; sys.path.insert(0, os.path.join('${PROJECT_ROOT}', 'src')); from sdlc_cli.version import __version__; print(__version__)" 2>/dev/null || echo "4.0.0")"

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

  # Initialize orchestrator state — phases derived from the single source of
  # truth (sdlc_cli.phases) so this never drifts from the actual pipeline.
  python3 -c "
import sys, os, json
sys.path.insert(0, os.path.join('${PROJECT_ROOT}', 'src'))
from sdlc_cli.phases import orchestrator_phases_template
state = {
    'current_phase': 0,
    'status': 'initialized',
    'complexity': None,
    'phases': orchestrator_phases_template(),
    'active_agents': [],
    'total_tasks': 0,
    'completed_tasks': 0,
    'failed_tasks': 0,
    'blocked_tasks': 0,
    'start_time': None,
    'last_updated': None,
}
with open('${SDLC_DIR}/state/orchestrator.json', 'w') as f:
    json.dump(state, f, indent=2)
    f.write('\n')
" || log_error "Could not initialize orchestrator.json (python3 with sdlc_cli required)"

  # Initialize queue files
  echo '[]' > "${SDLC_DIR}/queue/pending.json"
  echo '[]' > "${SDLC_DIR}/queue/active.json"
  echo '[]' > "${SDLC_DIR}/queue/completed.json"

  # Initialize memory index
  echo '[]' > "${SDLC_DIR}/memory/episodic/index.json"
  echo '{"patterns": []}' > "${SDLC_DIR}/memory/semantic/patterns.json"
  echo '{"anti_patterns": []}' > "${SDLC_DIR}/memory/semantic/anti-patterns.json"
  echo '[]' > "${SDLC_DIR}/memory/learnings/index.json"

  # Initialize STATUS.md — overall agent dashboard, generated from the single
  # source of truth (sdlc_cli.phases) so the phase/subagent tables always
  # match the actual pipeline.
  python3 -c "
import sys, os
sys.path.insert(0, os.path.join('${PROJECT_ROOT}', 'src'))
from sdlc_cli.phases import agent_registry

reg = agent_registry()
total_gates = len(reg)
lines = []
lines.append('# SDLC Status Dashboard')
lines.append('')
lines.append('> Auto-updated by the orchestrator at every phase transition.')
lines.append('> Last updated: not started')
lines.append('')
lines.append('## Overall Progress')
lines.append('')
lines.append('| Metric        | Value       |')
lines.append('|---------------|-------------|')
lines.append('| Status        | initialized |')
lines.append('| Complexity    | —           |')
lines.append('| Current Phase | 0 (%s) |' % reg[0]['name'])
lines.append('| Tasks Done    | 0 / 0       |')
lines.append('| Gate Passes   | 0 / %d      |' % total_gates)
lines.append('')
lines.append('## Phase & Agent Status')
lines.append('')
lines.append('| Phase | Name | Agent | Subagents Used | Status | Gate | Key Outcome |')
lines.append('|-------|------|-------|----------------|--------|------|-------------|')
for row in reg:
    n = len(row['subagents'])
    subs = str(n) if n else '—'
    lines.append('| %d | %s | %s | %s | pending | — | — |' % (row['phase'], row['name'], row['agent'], subs))
lines.append('')
lines.append('## Subagent Detail')
lines.append('')
lines.append('| Phase | Subagent | Status | Outcome |')
lines.append('|-------|----------|--------|---------|')
for row in reg:
    for sub in row['subagents']:
        lines.append('| %d | %s | pending | — |' % (row['phase'], sub))
lines.append('')
lines.append('## Artifacts Produced')
lines.append('')
lines.append('| Phase | Artifact | Path |')
lines.append('|-------|----------|------|')
lines.append('| — | — | — |')
lines.append('')
with open('${SDLC_DIR}/STATUS.md', 'w') as f:
    f.write('\n'.join(lines))
" || log_warn "Could not generate STATUS.md (python3 with sdlc_cli required)"

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
Phase 0: Problem Discovery — Initialized, awaiting spec input.

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
2. Run Phase 0: Problem Discovery (stage-problem-discovery) and reach a GO decision
3. Normalize spec to .sdlc/specs/normalized-spec.md
4. Detect complexity and select agent team
5. Begin Phase 1: Bootstrap

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

  # Use python for JSON update (cross-platform). The spec is now loaded; the
  # orchestrator drives the pipeline starting at Phase 0 (Problem Discovery).
  python3 -c "
import json, sys
with open('${SDLC_DIR}/state/orchestrator.json', 'r') as f:
    state = json.load(f)
state['complexity'] = '${complexity}'
state['status'] = 'in_progress'
state['start_time'] = '${now}'
state['last_updated'] = '${now}'
state['current_phase'] = 0
with open('${SDLC_DIR}/state/orchestrator.json', 'w') as f:
    json.dump(state, f, indent=2)
    f.write('\n')
" 2>/dev/null || log_warn "Could not update orchestrator.json (python3 not available)"

  # Update CONTINUITY.md
  cat > "${SDLC_DIR}/CONTINUITY.md" << EOF
# CONTINUITY — Working Memory

## Current Phase
Phase 0: Problem Discovery — Spec loaded, ready to run.

## Complexity
${complexity}

## Active Tasks
- Phase 0: Dispatch Problem Discovery Agent (stage-problem-discovery)

## Completed Tasks
- None (spec loaded, complexity detected: ${complexity})

## Mistakes & Learnings
- None yet

## Decisions Made
- Complexity detected as ${complexity} (${spec_lines} lines in spec)

## Next Steps
1. Read .sdlc/framework/agents/orchestrator.md — adopt orchestrator role
2. Dispatch stage-problem-discovery agent (.sdlc/framework/agents/stage/problem-discovery.md)
3. Reach a GO decision, then proceed to Phase 1: Bootstrap

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
  echo -e "${CYAN}║  Devin:      Type /sdlc.orchestrator in Devin Local chat     ║${NC}"
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

  # Delegate to the Python CLI — the single source of truth for phase/agent
  # rendering. This avoids maintaining a second (drift-prone) status renderer.
  python3 -c "
import sys, os
sys.path.insert(0, os.path.join('${PROJECT_ROOT}', 'src'))
from sdlc_cli.__init__ import app
sys.argv = ['sdlc', 'status', '${PROJECT_ROOT}']
app()
"
}

# ─────────────────────────────────────────────
# trace — Show agent interaction map
# ─────────────────────────────────────────────

cmd_trace() {
  if [[ ! -d "$SDLC_DIR" ]]; then
    log_error "Not initialized. Run: ./run.sh init"
    exit 1
  fi

  # Delegate to the Python CLI (single source of truth). An optional numeric
  # argument is passed through as a phase filter.
  local phase_filter="${1:-}"
  python3 -c "
import sys, os
sys.path.insert(0, os.path.join('${PROJECT_ROOT}', 'src'))
from sdlc_cli.__init__ import app
argv = ['sdlc', 'trace', '${PROJECT_ROOT}', '--verify']
if '${phase_filter}':
    argv += ['--phase', '${phase_filter}']
sys.argv = argv
app()
"
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

  python3 -c "
import sys, os
sys.path.insert(0, os.path.join('${PROJECT_ROOT}', 'src'))
from sdlc_cli.__init__ import app
sys.argv = ['sdlc', 'models', '${PROJECT_ROOT}'] + sys.argv[1:]
app()
" "$@"
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
