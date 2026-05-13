#!/usr/bin/env bash
set -euo pipefail

# Autonomous SDLC Framework — Bootstrap Installer
# Run this FROM your project repo to install the SDLC framework into it.
#
# Usage:
#   curl -sL https://raw.githubusercontent.com/bitbitcodes/autonomous-sdlc/main/install.sh | bash
#   OR
#   /path/to/autonomous-sdlc/install.sh [--ide windsurf|copilot|claude|cursor|opencode]

VERSION="1.0.0"
FRAMEWORK_DIR=".sdlc-framework"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC}    $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

print_banner() {
  echo -e "${CYAN}"
  echo "  ╔═══════════════════════════════════════════════╗"
  echo "  ║   Autonomous SDLC Framework Installer v${VERSION}  ║"
  echo "  ║   Bootstrap AI agents into your project       ║"
  echo "  ╚═══════════════════════════════════════════════╝"
  echo -e "${NC}"
}

# ─────────────────────────────────────────────
# Determine source location
# ─────────────────────────────────────────────

resolve_source() {
  # If run from the repo itself, use that path
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

  if [[ -f "${script_dir}/agents/orchestrator.md" ]]; then
    echo "$script_dir"
    return
  fi

  # If run via curl/pipe, clone to temp
  local tmp_dir
  tmp_dir=$(mktemp -d)
  log_info "Downloading framework to ${tmp_dir}..."
  git clone --depth 1 https://github.com/bitbitcodes/autonomous-sdlc.git "$tmp_dir" 2>/dev/null || {
    log_error "Failed to clone. Run install.sh directly from the framework repo instead."
    exit 1
  }
  echo "$tmp_dir"
}

# ─────────────────────────────────────────────
# Copy framework files into target project
# ─────────────────────────────────────────────

install_framework() {
  local source_dir="$1"
  local target_dir="$(pwd)"

  log_info "Installing SDLC framework into: ${target_dir}"

  # Guard: don't install into the framework repo itself
  if [[ -f "${target_dir}/install.sh" && -f "${target_dir}/agents/orchestrator.md" ]]; then
    log_error "You are inside the framework repo. Run this from your PROJECT repo."
    exit 1
  fi

  # Create framework directory
  mkdir -p "${FRAMEWORK_DIR}"

  # Copy agent prompts
  log_info "Copying agent prompts..."
  cp -r "${source_dir}/agents" "${FRAMEWORK_DIR}/agents"

  # Copy reference docs
  log_info "Copying reference docs..."
  cp -r "${source_dir}/references" "${FRAMEWORK_DIR}/references"

  # Copy skills
  log_info "Copying skill modules..."
  cp -r "${source_dir}/skills" "${FRAMEWORK_DIR}/skills"

  # Copy templates
  log_info "Copying templates..."
  cp -r "${source_dir}/templates" "${FRAMEWORK_DIR}/templates"

  # Copy examples
  log_info "Copying examples..."
  cp -r "${source_dir}/examples" "${FRAMEWORK_DIR}/examples"

  # Copy runner script
  cp "${source_dir}/run.sh" "${FRAMEWORK_DIR}/run.sh"
  chmod +x "${FRAMEWORK_DIR}/run.sh"

  # Copy AGENTS.md to project root (agent discovery standard)
  cp "${source_dir}/AGENTS.md" "./AGENTS.md"

  # Create .sdlc/ runtime directory
  "${FRAMEWORK_DIR}/run.sh" init

  log_ok "Framework installed to ${FRAMEWORK_DIR}/"
  log_ok "AGENTS.md created at project root"
  log_ok ".sdlc/ runtime directory initialized"
}

# ─────────────────────────────────────────────
# Append to .gitignore
# ─────────────────────────────────────────────

update_gitignore() {
  local gitignore=".gitignore"
  local marker="# Autonomous SDLC Framework"

  if [[ -f "$gitignore" ]] && grep -q "$marker" "$gitignore"; then
    log_info ".gitignore already has SDLC entries — skipping"
    return
  fi

  cat >> "$gitignore" << 'EOF'

# Autonomous SDLC Framework
.sdlc/state/
.sdlc/queue/
.sdlc/memory/
.sdlc/artifacts/
.sdlc/specs/
.sdlc/CONTINUITY.md
EOF

  log_ok "Updated .gitignore with SDLC runtime exclusions"
}

# ─────────────────────────────────────────────
# IDE Setup — delegates to run.sh setup-ide
# ─────────────────────────────────────────────

setup_ide_via_runner() {
  local ide="$1"
  "${FRAMEWORK_DIR}/run.sh" setup-ide "$ide"
}

select_ide() {
  echo ""
  echo -e "${CYAN}Select your AI IDE:${NC}"
  echo ""
  echo "  1) Windsurf (Cascade)"
  echo "  2) GitHub Copilot"
  echo "  3) Claude Code"
  echo "  4) Cursor"
  echo "  5) OpenCode"
  echo "  6) Skip (manual setup)"
  echo ""
  echo -n "Choice [1-6]: "
  read -r choice

  case "$choice" in
    1) setup_ide_via_runner "windsurf" ;;
    2) setup_ide_via_runner "copilot" ;;
    3) setup_ide_via_runner "claude" ;;
    4) setup_ide_via_runner "cursor" ;;
    5) setup_ide_via_runner "opencode" ;;
    6) log_info "Skipping IDE setup. Run: .sdlc-framework/run.sh setup-ide <ide> later." ;;
    *)
      log_warn "Invalid choice, skipping IDE setup."
      log_info "Run: .sdlc-framework/run.sh setup-ide <ide> later."
      ;;
  esac
}

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

main() {
  print_banner

  local ide_arg=""

  # Parse args
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --ide)
        ide_arg="$2"
        shift 2
        ;;
      *)
        shift
        ;;
    esac
  done

  # Resolve source framework directory
  local source_dir
  source_dir=$(resolve_source)

  # Install framework files
  install_framework "$source_dir"

  # Update .gitignore
  update_gitignore

  # IDE setup
  if [[ -n "$ide_arg" ]]; then
    setup_ide_via_runner "$ide_arg"
  else
    select_ide
  fi

  # Done
  echo ""
  echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${GREEN}║                 INSTALLATION COMPLETE                        ║${NC}"
  echo -e "${GREEN}╠═══════════════════════════════════════════════════════════════╣${NC}"
  echo -e "${GREEN}║                                                              ║${NC}"
  echo -e "${GREEN}║  Next steps:                                                 ║${NC}"
  echo -e "${GREEN}║                                                              ║${NC}"
  echo -e "${GREEN}║  1. Add your spec:                                           ║${NC}"
  echo -e "${GREEN}║     .sdlc-framework/run.sh start ./your-prd.md              ║${NC}"
  echo -e "${GREEN}║     .sdlc-framework/run.sh start \"Build a todo app\"          ║${NC}"
  echo -e "${GREEN}║                                                              ║${NC}"
  echo -e "${GREEN}║  2. Open your AI IDE and start a new conversation.           ║${NC}"
  echo -e "${GREEN}║     The orchestrator will activate automatically.            ║${NC}"
  echo -e "${GREEN}║                                                              ║${NC}"
  echo -e "${GREEN}║  3. Check status anytime:                                    ║${NC}"
  echo -e "${GREEN}║     .sdlc-framework/run.sh status                            ║${NC}"
  echo -e "${GREEN}║                                                              ║${NC}"
  echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
}

main "$@"
