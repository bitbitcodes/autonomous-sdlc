"""Custom agent scaffolding for autonomous-sdlc.

Lets users add their own stage agents (new phases, anchored relative to a
built-in phase) or subagents (attached to an existing stage) when the 52
built-in agents don't cover their need. Prompts are scaffolded from
templates/stage-agent.template.md / templates/subagent.template.md and
registered in .sdlc/custom-agents.json. Enablement is tracked the same way
as built-in agents, in .sdlc/phase-config.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .phases import (
    BOOTSTRAP_ID,
    PHASE_REGISTRY,
    compute_phase_numbers,
    compute_pipeline,
    load_config,
    load_custom_agents,
    set_stage_enabled,
    set_subagent_enabled,
    write_config,
    write_custom_agents,
)

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"


class CustomAgentError(ValueError):
    """Raised for invalid custom-agent registration requests."""


def _known_stage_ids(custom_agents: dict[str, Any]) -> set[str]:
    return {row["stage_id"] for row in compute_pipeline(custom_agents)}


def add_subagent(
    sdlc_dir: Path,
    *,
    sub_id: str,
    stage_id: str,
    name: str,
    description: str,
) -> Path:
    """Scaffold a custom subagent prompt, register it, and enable it.

    Returns the path to the created prompt file.
    """
    if not sub_id.startswith("sub-"):
        raise CustomAgentError("Custom subagent id must start with 'sub-' (e.g. sub-terraform-validator).")

    custom_agents = load_custom_agents(sdlc_dir)
    known_stages = _known_stage_ids(custom_agents)
    if stage_id not in known_stages or stage_id == BOOTSTRAP_ID:
        raise CustomAgentError(
            f"Unknown or non-attachable stage id: '{stage_id}'. Run `sdlc phases` to see valid stage ids."
        )
    if sub_id in PHASE_REGISTRY.get(stage_id, {}).get("subagents", []):
        raise CustomAgentError(f"'{sub_id}' already exists as a built-in subagent of '{stage_id}'.")
    if sub_id in custom_agents.get("custom_subagents", {}):
        raise CustomAgentError(f"Custom subagent '{sub_id}' is already registered.")

    template = (TEMPLATES_DIR / "subagent.template.md").read_text(encoding="utf-8")
    stage_name = PHASE_REGISTRY.get(stage_id, {}).get("name") or _stage_name(custom_agents, stage_id)
    phase_num = compute_phase_numbers(custom_agents).get(stage_id, "?")
    prompt = (
        template.replace("{Subagent Name}", name)
        .replace("{subagent-id}", sub_id)
        .replace("{Stage Name}", stage_name)
        .replace("{N}", str(phase_num))
        .replace("{Phase Name}", stage_name)
        .replace(
            "{What success looks like — specific, measurable outcome for this subagent's focused task.}",
            description,
        )
    )

    stage_slug = stage_id.replace("stage-", "")
    rel_path = Path("agents") / "custom" / "sub" / stage_slug / f"{sub_id.replace('sub-', '')}.md"
    prompt_path = sdlc_dir / "framework" / rel_path
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")

    custom_agents.setdefault("custom_subagents", {})[sub_id] = {
        "name": name,
        "attach_to_stage": stage_id,
        "prompt": str(rel_path),
        "description": description,
    }
    write_custom_agents(sdlc_dir, custom_agents)

    config = load_config(sdlc_dir) or {}
    set_subagent_enabled(config, stage_id, sub_id, True)
    write_config(sdlc_dir, config)

    return prompt_path


def add_stage(
    sdlc_dir: Path,
    *,
    stage_id: str,
    name: str,
    description: str,
    anchor_position: str,
    anchor_stage_id: str,
) -> tuple[Path, dict[str, int]]:
    """Scaffold a custom stage agent, insert it into the pipeline, and
    renumber .sdlc/state/orchestrator.json if a run is already in progress.

    Returns (prompt_path, new_phase_numbers).
    """
    if not stage_id.startswith("stage-"):
        raise CustomAgentError("Custom stage id must start with 'stage-' (e.g. stage-localization).")
    if anchor_position not in ("before", "after"):
        raise CustomAgentError("anchor_position must be 'before' or 'after'.")

    custom_agents = load_custom_agents(sdlc_dir)
    known_stages = _known_stage_ids(custom_agents)
    if stage_id in known_stages:
        raise CustomAgentError(f"Stage id '{stage_id}' already exists.")
    if anchor_stage_id not in known_stages:
        raise CustomAgentError(
            f"Unknown anchor stage id: '{anchor_stage_id}'. Run `sdlc phases` to see valid stage ids."
        )
    if anchor_stage_id == "stage-retirement" and anchor_position == "after":
        raise CustomAgentError("Cannot anchor a stage after Retirement (Phase 12 is always last).")
    if anchor_stage_id == BOOTSTRAP_ID and anchor_position == "before":
        raise CustomAgentError(
            "Cannot anchor a stage before Bootstrap; anchor after 'stage-problem-discovery' instead."
        )

    template = (TEMPLATES_DIR / "stage-agent.template.md").read_text(encoding="utf-8")

    old_numbers = compute_phase_numbers(custom_agents)
    custom_agents.setdefault("custom_stages", {})[stage_id] = {
        "name": name,
        "anchor": {"position": anchor_position, "stage_id": anchor_stage_id},
        "prompt": str(Path("agents") / "custom" / "stage" / f"{stage_id.replace('stage-', '')}.md"),
        "subagents": [],
    }
    new_numbers = compute_phase_numbers(custom_agents)

    phase_num = new_numbers[stage_id]
    prompt = (
        template.replace("{Stage Name}", name)
        .replace("{agent-id}", stage_id)
        .replace("{N}", str(phase_num))
        .replace("{Phase Name}", name)
        .replace("{What success looks like for this phase — measurable outcome.}", description)
    )

    rel_path = Path("agents") / "custom" / "stage" / f"{stage_id.replace('stage-', '')}.md"
    prompt_path = sdlc_dir / "framework" / rel_path
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    prompt_path.write_text(prompt, encoding="utf-8")

    write_custom_agents(sdlc_dir, custom_agents)

    config = load_config(sdlc_dir) or {}
    set_stage_enabled(config, stage_id, True)
    write_config(sdlc_dir, config)

    _renumber_orchestrator_state(sdlc_dir, old_numbers, new_numbers, new_stage_id=stage_id)

    return prompt_path, new_numbers


def _stage_name(custom_agents: dict[str, Any], stage_id: str) -> str:
    for row in compute_pipeline(custom_agents):
        if row["stage_id"] == stage_id:
            return row["name"]
    return stage_id


def _renumber_orchestrator_state(
    sdlc_dir: Path,
    old_numbers: dict[str, int],
    new_numbers: dict[str, int],
    *,
    new_stage_id: str,
) -> None:
    """Rewrite .sdlc/state/orchestrator.json 'phases' keys to reflect the
    newly-computed phase numbers, preserving status/gate/review by stage_id.
    No-op if no run has been started yet (file absent).
    """
    state_path = sdlc_dir / "state" / "orchestrator.json"
    if not state_path.exists():
        return

    data = json.loads(state_path.read_text(encoding="utf-8"))
    old_phases: dict[str, Any] = data.get("phases", {})

    def slug(sid: str) -> str:
        return "bootstrap" if sid == BOOTSTRAP_ID else sid.replace("stage-", "")

    new_phases: dict[str, Any] = {}
    for stage_id, number in sorted(new_numbers.items(), key=lambda kv: kv[1]):
        new_key = f"{number}-{slug(stage_id)}"
        if stage_id == new_stage_id:
            new_phases[new_key] = {"status": "pending", "gate": None, "review": None}
            continue
        old_number = old_numbers.get(stage_id)
        old_key = f"{old_number}-{slug(stage_id)}" if old_number is not None else None
        new_phases[new_key] = old_phases.get(old_key, {"status": "pending", "gate": None, "review": None})

    data["phases"] = new_phases
    state_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def list_custom(sdlc_dir: Path) -> dict[str, Any]:
    return load_custom_agents(sdlc_dir)


def remove_subagent(sdlc_dir: Path, sub_id: str) -> None:
    custom_agents = load_custom_agents(sdlc_dir)
    entry = custom_agents.get("custom_subagents", {}).pop(sub_id, None)
    if entry is None:
        raise CustomAgentError(f"Custom subagent '{sub_id}' is not registered.")
    write_custom_agents(sdlc_dir, custom_agents)

    prompt_path = sdlc_dir / "framework" / entry["prompt"]
    if prompt_path.exists():
        prompt_path.unlink()


def remove_stage(sdlc_dir: Path, stage_id: str) -> None:
    custom_agents = load_custom_agents(sdlc_dir)
    if stage_id not in custom_agents.get("custom_stages", {}):
        raise CustomAgentError(f"Custom stage '{stage_id}' is not registered.")

    old_numbers = compute_phase_numbers(custom_agents)  # full pre-removal state, incl. other custom stages
    entry = custom_agents["custom_stages"].pop(stage_id)
    write_custom_agents(sdlc_dir, custom_agents)
    new_numbers = compute_phase_numbers(custom_agents)

    prompt_path = sdlc_dir / "framework" / entry["prompt"]
    if prompt_path.exists():
        prompt_path.unlink()

    _renumber_orchestrator_state(sdlc_dir, old_numbers, new_numbers, new_stage_id="")
