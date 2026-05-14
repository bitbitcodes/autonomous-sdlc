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

# Runtime directories to create under .sdlc/
RUNTIME_DIRS = [
    ".sdlc/state",
    ".sdlc/queue",
    ".sdlc/memory/episodic",
    ".sdlc/memory/semantic",
    ".sdlc/memory/learnings",
    ".sdlc/artifacts/product",
    ".sdlc/artifacts/story-tasks",
    ".sdlc/artifacts/architecture",
    ".sdlc/artifacts/design",
    ".sdlc/artifacts/development",
    ".sdlc/artifacts/testing",
    ".sdlc/artifacts/security",
    ".sdlc/artifacts/review",
    ".sdlc/artifacts/devops",
    ".sdlc/artifacts/observability",
    ".sdlc/specs",
]

GITIGNORE_ENTRIES = [
    "# Autonomous SDLC Framework — runtime state (gitignored)",
    ".sdlc/state/",
    ".sdlc/queue/",
    ".sdlc/memory/",
    ".sdlc/artifacts/",
    ".sdlc/specs/",
    ".sdlc/CONTINUITY.md",
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
        ".sdlc/CONTINUITY.md",
    ])

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


def _init_runtime_state(target_dir: Path) -> None:
    """Initialize .sdlc/ runtime state files."""
    sdlc = target_dir / ".sdlc"

    # Orchestrator state
    state = {
        "current_phase": 0,
        "status": "initialized",
        "complexity": None,
        "phases": {
            "0-bootstrap": {"status": "pending", "gate": None, "review": None},
            "1-product": {"status": "pending", "gate": None, "review": None},
            "2-story-tasks": {"status": "pending", "gate": None, "review": None},
            "3-architecture": {"status": "pending", "gate": None, "review": None},
            "4-design": {"status": "pending", "gate": None, "review": None},
            "5-development": {"status": "pending", "gate": None, "review": None},
            "6-testing": {"status": "pending", "gate": None, "review": None},
            "7-security": {"status": "pending", "gate": None, "review": None},
            "8-review": {"status": "pending", "gate": None, "review": None},
            "9-devops": {"status": "pending", "gate": None, "review": None},
            "10-observability": {"status": "pending", "gate": None, "review": None},
        },
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

    # CONTINUITY.md
    continuity = """\
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
"""
    (sdlc / "CONTINUITY.md").write_text(continuity, encoding="utf-8")


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
