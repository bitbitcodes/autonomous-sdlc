#!/usr/bin/env bash
set -euo pipefail

# Autonomous SDLC Framework — Runner Script
# Usage: ./run.sh <command> [args]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SDLC_DIR=".sdlc"
VERSION="1.0.0"

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
  mkdir -p "${SDLC_DIR}/artifacts/architecture"
  mkdir -p "${SDLC_DIR}/artifacts/backlog"
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
    "0-bootstrap": { "status": "pending", "gate": null },
    "1-product": { "status": "pending", "gate": null },
    "2-architecture": { "status": "pending", "gate": null },
    "3-backlog": { "status": "pending", "gate": null },
    "4-development": { "status": "pending", "gate": null },
    "5-testing": { "status": "pending", "gate": null },
    "6-security": { "status": "pending", "gate": null },
    "7-review": { "status": "pending", "gate": null },
    "8-devops": { "status": "pending", "gate": null },
    "9-observability": { "status": "pending", "gate": null }
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
1. Read agents/orchestrator.md — adopt orchestrator role
2. Dispatch stage-product agent (agents/stage/product.md)
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
  echo -e "${CYAN}║  Paste the orchestrator prompt into your AI IDE:             ║${NC}"
  echo -e "${CYAN}║                                                              ║${NC}"
  echo -e "${CYAN}║  1. Open agents/orchestrator.md                              ║${NC}"
  echo -e "${CYAN}║  2. Copy the full content                                    ║${NC}"
  echo -e "${CYAN}║  3. Paste into Windsurf/Cursor/Claude Code chat              ║${NC}"
  echo -e "${CYAN}║  4. The orchestrator will read AGENTS.md and begin           ║${NC}"
  echo -e "${CYAN}║                                                              ║${NC}"
  echo -e "${CYAN}║  Or use with Claude Code:                                    ║${NC}"
  echo -e "${CYAN}║  claude -p \"\$(cat agents/orchestrator.md)\"                    ║${NC}"
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

  echo -e "${BLUE}Current State:${NC}"
  echo ""

  # Show orchestrator state
  if [[ -f "${SDLC_DIR}/state/orchestrator.json" ]]; then
    python3 -c "
import json
with open('${SDLC_DIR}/state/orchestrator.json', 'r') as f:
    state = json.load(f)

phase_names = {
    '0-bootstrap': 'Bootstrap',
    '1-product': 'Product',
    '2-architecture': 'Architecture',
    '3-backlog': 'Backlog',
    '4-development': 'Development',
    '5-testing': 'Testing',
    '6-security': 'Security',
    '7-review': 'Review',
    '8-devops': 'DevOps',
    '9-observability': 'Observability'
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
    gate = f' (gate: {phase[\"gate\"]})' if phase['gate'] else ''
    print(f'    {icon} {name}: {phase[\"status\"]}{gate}')
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
# Main dispatcher
# ─────────────────────────────────────────────

main() {
  local cmd="${1:-help}"
  shift || true

  case "$cmd" in
    init)    cmd_init "$@" ;;
    start)   cmd_start "$@" ;;
    status)  cmd_status "$@" ;;
    reset)   cmd_reset "$@" ;;
    prompt)  cmd_prompt "$@" ;;
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
