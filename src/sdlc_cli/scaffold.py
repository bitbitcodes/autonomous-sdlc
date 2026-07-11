"""Scaffold/init logic for autonomous-sdlc.

Creates the directory structure, copies agent prompts, references, skills,
and sets up the selected IDE integration in the target project.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from .config import create_config
from .integrations import get_integration
from .integrations.base import IntegrationBase

# Framework directories to copy into .sdlc/
FRAMEWORK_COPY_DIRS = ["agents", "references", "skills"]

# Runtime sub-directories (relative to a run root — .sdlc/ or .sdlc/runs/<slug>/)
RUNTIME_SUBDIRS = [
    "state",
    "queue",
    "memory/episodic",
    "memory/semantic",
    "memory/learnings",
    "artifacts/problem-discovery",
    "artifacts/product",
    "artifacts/story-tasks",
    "artifacts/architecture",
    "artifacts/design",
    "artifacts/development",
    "artifacts/testing",
    "artifacts/security",
    "artifacts/review",
    "artifacts/devops",
    "artifacts/observability",
    "artifacts/retirement",
    "artifacts/compliance",
    "specs",
]

# Governance policy templates copied once into .sdlc/governance/ (never
# overwritten by upgrade — these are user-editable policy files).
GOVERNANCE_TEMPLATES = [
    "risk-policy.yaml",
    "budget-policy.yaml",
    "token-policy.yaml",
    "compliance-policy.yaml",
    "execution-policy.yaml",
    "adaptive-policy.yaml",
    "notification-config.yaml",
]

# Legacy full-path list (used by scaffold for single-run init)
RUNTIME_DIRS = [".sdlc/" + d for d in RUNTIME_SUBDIRS]

GITIGNORE_ENTRIES = [
    "# Autonomous SDLC Framework — runtime state (gitignored)",
    ".sdlc/state/",
    ".sdlc/queue/",
    ".sdlc/memory/",
    ".sdlc/artifacts/",
    ".sdlc/specs/",
    ".sdlc/CONTINUITY.md",
    ".sdlc/runs/",
    ".sdlc/archive/",
]


def scaffold(
    target_dir: Path,
    *,
    integration: str = "copilot",
    project_name: str = "",
    tech_stack: str = "",
    team_size: str = "",
    complexity: str = "auto",
    force: bool = False,
) -> dict:
    """Scaffold autonomous-sdlc into the target directory.

    Returns a dict with keys: "dirs_created", "files_created", "integration".
    """
    target_dir = Path(target_dir).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    dirs_created: list[str] = []
    files_created: list[str] = []

    # 1. Copy framework directories into .sdlc/framework/
    fw_dir = target_dir / ".sdlc" / "framework"
    for dirname in FRAMEWORK_COPY_DIRS:
        src_dir = _find_source_dir(dirname)
        if src_dir and src_dir.is_dir():
            dst_dir = fw_dir / dirname
            if dst_dir.exists() and force:
                shutil.rmtree(dst_dir)
            if not dst_dir.exists():
                shutil.copytree(src_dir, dst_dir)
                dirs_created.append(f".sdlc/framework/{dirname}/")
                for f in dst_dir.rglob("*"):
                    if f.is_file():
                        files_created.append(str(f.relative_to(target_dir)))

    # Copy examples
    examples_dir = IntegrationBase.shared_examples_dir()
    if examples_dir and examples_dir.is_dir():
        dst = fw_dir / "examples"
        if not dst.exists() or force:
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(examples_dir, dst)
            dirs_created.append(".sdlc/framework/examples/")

    # Copy existing templates (agent/subagent/handoff templates)
    templates_src = _find_source_dir("templates")
    if templates_src and templates_src.is_dir():
        dst = fw_dir / "templates"
        dst.mkdir(parents=True, exist_ok=True)
        for f in templates_src.iterdir():
            if f.is_file() and f.suffix in (".md", ".mdc"):
                # Only copy agent-related templates, not IDE templates
                if "template" in f.name:
                    dst_file = dst / f.name
                    if not dst_file.exists() or force:
                        shutil.copy2(f, dst_file)
                        files_created.append(str(dst_file.relative_to(target_dir)))

    # Copy run.sh utility
    runner_src = IntegrationBase.shared_runner_script()
    if runner_src:
        dst = fw_dir / "run.sh"
        if not dst.exists() or force:
            shutil.copy2(runner_src, dst)
            dst.chmod(0o755)
            files_created.append(".sdlc/framework/run.sh")

    # 2. Create runtime directories under .sdlc/
    for d in RUNTIME_DIRS:
        dir_path = target_dir / d
        dir_path.mkdir(parents=True, exist_ok=True)
        dirs_created.append(d + "/")

    # 3. Initialize runtime state files
    _init_runtime_state(target_dir)
    files_created.extend([
        ".sdlc/state/orchestrator.json",
        ".sdlc/queue/pending.json",
        ".sdlc/queue/active.json",
        ".sdlc/queue/completed.json",
        ".sdlc/memory/episodic/index.json",
        ".sdlc/memory/semantic/patterns.json",
        ".sdlc/memory/semantic/anti-patterns.json",
        ".sdlc/memory/learnings/index.json",
        ".sdlc/state/agent-trace.json",
        ".sdlc/state/token-usage.json",
        ".sdlc/CONTINUITY.md",
    ])

    # 3b. Governance: copy policy templates + init decision-log/pending-approvals
    gov_files = _init_governance(target_dir, force=force)
    dirs_created.append(".sdlc/governance/")
    files_created.extend(gov_files)

    # 4. Install AGENTS.md at project root
    templates_dir = IntegrationBase.shared_templates_dir()
    if templates_dir:
        agents_src = templates_dir / "agents-md-template.md"
        if agents_src.exists():
            agents_dst = target_dir / "AGENTS.md"
            if not agents_dst.exists() or force:
                content = agents_src.read_text(encoding="utf-8")
                if project_name:
                    content = content.replace("{{PROJECT_NAME}}", project_name)
                agents_dst.write_text(content, encoding="utf-8")
                files_created.append("AGENTS.md")

    # 5. Set up the selected IDE integration
    integration_cls = get_integration(integration)
    integration_instance = integration_cls()
    integration_files = integration_instance.setup(target_dir, project_name=project_name)
    for f in integration_files:
        try:
            rel = f.relative_to(target_dir)
            files_created.append(str(rel))
        except ValueError:
            files_created.append(str(f))

    # 6. Update .gitignore
    _update_gitignore(target_dir)
    files_created.append(".gitignore")

    # 7. Save config
    create_config(target_dir, {
        "projectName": project_name,
        "integration": integration,
        "techStack": tech_stack,
        "teamSize": team_size,
        "complexity": complexity,
    })
    files_created.append(".sdlc/init-options.json")

    return {
        "dirs_created": dirs_created,
        "files_created": files_created,
        "integration": integration,
    }


def upgrade_framework(target_dir: Path, *, dry_run: bool = False) -> dict[str, int]:
    """Upgrade .sdlc/framework/ files from the installed package.

    Only touches framework files (agents, references, skills, templates,
    examples, run.sh) and AGENTS.md.  Never touches runtime state, runs,
    model-config, or IDE configs.

    Returns a dict of {component: file_count} for items updated.
    """
    fw_dir = target_dir / ".sdlc" / "framework"
    updated: dict[str, int] = {}

    # Core framework dirs
    for dirname in FRAMEWORK_COPY_DIRS:
        src_dir = _find_source_dir(dirname)
        if src_dir and src_dir.is_dir():
            dst_dir = fw_dir / dirname
            count = sum(1 for f in src_dir.rglob("*") if f.is_file())
            if not dry_run:
                if dst_dir.exists():
                    shutil.rmtree(dst_dir)
                shutil.copytree(src_dir, dst_dir)
            updated[dirname] = count

    # Examples
    examples_dir = IntegrationBase.shared_examples_dir()
    if examples_dir and examples_dir.is_dir():
        dst = fw_dir / "examples"
        count = sum(1 for f in examples_dir.rglob("*") if f.is_file())
        if not dry_run:
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(examples_dir, dst)
        updated["examples"] = count

    # Templates (agent-related only)
    templates_src = _find_source_dir("templates")
    if templates_src and templates_src.is_dir():
        dst = fw_dir / "templates"
        count = 0
        for f in templates_src.iterdir():
            if f.is_file() and f.suffix in (".md", ".mdc") and "template" in f.name:
                count += 1
                if not dry_run:
                    dst.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(f, dst / f.name)
        if count:
            updated["templates"] = count

    # run.sh
    runner_src = IntegrationBase.shared_runner_script()
    if runner_src:
        dst = fw_dir / "run.sh"
        if not dry_run:
            shutil.copy2(runner_src, dst)
            dst.chmod(0o755)
        updated["run.sh"] = 1

    # AGENTS.md at project root
    templates_dir = IntegrationBase.shared_templates_dir()
    if templates_dir:
        agents_src = templates_dir / "agents-md-template.md"
        if agents_src.exists():
            if not dry_run:
                agents_dst = target_dir / "AGENTS.md"
                agents_dst.write_text(
                    agents_src.read_text(encoding="utf-8"), encoding="utf-8"
                )
            updated["AGENTS.md"] = 1

    return updated


def _find_source_dir(dirname: str) -> Path | None:
    """Find a source directory by checking core_pack then repo root."""
    base_cls = IntegrationBase
    lookup = {
        "agents": base_cls.shared_agents_dir,
        "references": base_cls.shared_references_dir,
        "skills": base_cls.shared_skills_dir,
        "examples": base_cls.shared_examples_dir,
    }
    if dirname in lookup:
        return lookup[dirname]()

    # Fallback: check relative to package
    import inspect
    pkg_dir = Path(inspect.getfile(base_cls)).resolve().parent.parent
    for candidate in [
        pkg_dir / "core_pack" / dirname,
        pkg_dir.parent.parent / dirname,
    ]:
        if candidate.is_dir():
            return candidate
    return None


def create_run(sdlc_dir: Path, slug: str, title: str, spec_file: str | None = None) -> Path:
    """Create a new named run under .sdlc/runs/<slug>/ with fresh state."""
    run_dir = sdlc_dir / "runs" / slug
    run_dir.mkdir(parents=True, exist_ok=True)

    for d in RUNTIME_SUBDIRS:
        (run_dir / d).mkdir(parents=True, exist_ok=True)

    _init_runtime_state_in(run_dir)

    from .runs import write_run_info, set_active_run

    write_run_info(run_dir, slug, title, spec_file)
    set_active_run(sdlc_dir, slug)
    return run_dir


def _init_runtime_state(target_dir: Path) -> None:
    """Initialize .sdlc/ runtime state files (legacy single-run)."""
    sdlc = target_dir / ".sdlc"
    _init_runtime_state_in(sdlc)


def _init_runtime_state_in(sdlc: Path) -> None:
    """Initialize runtime state files inside a given directory."""

    # Orchestrator state
    from .phases import orchestrator_phases_template

    state = {
        "current_phase": 0,
        "status": "initialized",
        "complexity": None,
        "phases": orchestrator_phases_template(),
        "active_agents": [],
        "total_tasks": 0,
        "completed_tasks": 0,
        "failed_tasks": 0,
        "blocked_tasks": 0,
        "start_time": None,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }
    (sdlc / "state" / "orchestrator.json").write_text(
        json.dumps(state, indent=2) + "\n", encoding="utf-8"
    )

    # Queue files
    for name in ("pending", "active", "completed"):
        (sdlc / "queue" / f"{name}.json").write_text("[]\n", encoding="utf-8")

    # Memory indexes
    (sdlc / "memory" / "episodic" / "index.json").write_text("[]\n", encoding="utf-8")
    (sdlc / "memory" / "semantic" / "patterns.json").write_text(
        '{"patterns": []}\n', encoding="utf-8"
    )
    (sdlc / "memory" / "semantic" / "anti-patterns.json").write_text(
        '{"anti_patterns": []}\n', encoding="utf-8"
    )
    (sdlc / "memory" / "learnings" / "index.json").write_text("[]\n", encoding="utf-8")

    # Agent trace log
    (sdlc / "state" / "agent-trace.json").write_text(
        json.dumps({"traces": []}, indent=2) + "\n", encoding="utf-8"
    )

    # Token usage tracking (realistic cost evaluation)
    token_usage = {
        "total_tokens": 0,
        "total_cost_usd": 0.0,
        "budget_limit_usd": 100.0,
        "breakdown": {
            "base_execution": 0,
            "retry_overhead": 0,
            "gate_failure_overhead": 0,
            "conversation_overhead": 0,
            "review_overhead": 0,
        },
        "retry_stats": {
            "total_retries": 0,
            "tasks_failed_first_attempt": 0,
            "average_retries_per_task": 0.0,
        },
        "gate_stats": {
            "gates_passed_first_attempt": 0,
            "gates_failed": 0,
            "average_retries_per_gate": 0.0,
        },
        "by_phase": {},
        "by_agent": {},
    }
    (sdlc / "state" / "token-usage.json").write_text(
        json.dumps(token_usage, indent=2) + "\n", encoding="utf-8"
    )

    # CONTINUITY.md
    continuity = """\
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
"""
    (sdlc / "CONTINUITY.md").write_text(continuity, encoding="utf-8")

    # Model routing config — only at .sdlc/ root level (shared, not per-run)
    model_cfg = sdlc / "model-config.json"
    if not model_cfg.exists():
        from .models import write_config as write_model_config

        write_model_config(sdlc)

    # Phase/subagent enablement config — only at .sdlc/ root level (shared,
    # not per-run). Defaults to everything enabled (v3.0-compatible).
    phase_cfg = sdlc / "phase-config.json"
    if not phase_cfg.exists():
        from .phases import write_config as write_phase_config

        write_phase_config(sdlc)

    # Custom agent registry — user-added stage agents/subagents beyond the
    # 52 built-in agents. Defaults to empty (no custom agents).
    custom_agents_cfg = sdlc / "custom-agents.json"
    if not custom_agents_cfg.exists():
        from .phases import write_custom_agents

        write_custom_agents(sdlc)
    (sdlc / "framework" / "agents" / "custom" / "stage").mkdir(parents=True, exist_ok=True)
    (sdlc / "framework" / "agents" / "custom" / "sub").mkdir(parents=True, exist_ok=True)


def _init_governance(target_dir: Path, *, force: bool = False) -> list[str]:
    """Copy governance policy templates into .sdlc/governance/ and
    initialize decision-log.json / pending-approvals.json.

    Policy YAML files are copied ONCE and never overwritten by `sdlc upgrade`
    (they are user-editable config, like model-config.json). Returns the list
    of files created, relative to target_dir.
    """
    gov_dir = target_dir / ".sdlc" / "governance"
    gov_dir.mkdir(parents=True, exist_ok=True)
    created: list[str] = []

    templates_src = _find_source_dir("templates")
    gov_templates_src = (templates_src / "governance") if templates_src else None
    if gov_templates_src and gov_templates_src.is_dir():
        for name in GOVERNANCE_TEMPLATES:
            src_file = gov_templates_src / name
            dst_file = gov_dir / name
            if src_file.exists() and (not dst_file.exists() or force):
                shutil.copy2(src_file, dst_file)
                created.append(f".sdlc/governance/{name}")

    decision_log = gov_dir / "decision-log.json"
    if not decision_log.exists() or force:
        decision_log.write_text(
            json.dumps({"decisions": []}, indent=2) + "\n", encoding="utf-8"
        )
        created.append(".sdlc/governance/decision-log.json")

    pending_approvals = gov_dir / "pending-approvals.json"
    if not pending_approvals.exists() or force:
        pending_approvals.write_text(
            json.dumps({"approvals": []}, indent=2) + "\n", encoding="utf-8"
        )
        created.append(".sdlc/governance/pending-approvals.json")

    return created


def _update_gitignore(target_dir: Path) -> None:
    """Append autonomous-sdlc entries to .gitignore without duplicating."""
    gitignore_path = target_dir / ".gitignore"
    existing_lines: set[str] = set()

    if gitignore_path.exists():
        existing_content = gitignore_path.read_text(encoding="utf-8")
        existing_lines = {line.strip() for line in existing_content.splitlines()}
    else:
        existing_content = ""

    new_entries = []
    for entry in GITIGNORE_ENTRIES:
        if entry.strip() not in existing_lines:
            new_entries.append(entry)

    if new_entries:
        with open(gitignore_path, "a", encoding="utf-8") as f:
            if existing_content and not existing_content.endswith("\n"):
                f.write("\n")
            f.write("\n".join(new_entries) + "\n")
