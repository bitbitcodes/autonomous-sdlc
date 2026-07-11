"""Phase/subagent enablement configuration for autonomous-sdlc.

Lets users disable entire stage agents (phases) or individual subagents
within a stage. Mirrors the model-config.json / models.py pattern:
a JSON config file in .sdlc/ plus load/write/resolve helpers used by the
`sdlc phases` CLI command and (conceptually) the orchestrator dispatch
protocol.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONFIG_FILENAME = "phase-config.json"
CUSTOM_AGENTS_FILENAME = "custom-agents.json"

# Pseudo stage-id for Phase 1 (Bootstrap), which has no dedicated stage agent
# (handled directly by the orchestrator) and can never be disabled or moved.
BOOTSTRAP_ID = "stage-bootstrap"

# ── Stage registry: stage_id -> {phase, name, subagents} ──────────────────
# Phase 1 (Bootstrap) is handled directly by the orchestrator and has no
# stage agent, so it is intentionally excluded from PHASE_REGISTRY — it can
# never be disabled, but IS present in BUILTIN_ORDER below so custom stages
# can be anchored relative to it.

PHASE_REGISTRY: dict[str, dict[str, Any]] = {
    "stage-problem-discovery": {
        "phase": 0,
        "name": "Problem Discovery",
        "subagents": [
            "sub-problem-statement-extractor",
            "sub-user-research-synthesizer",
            "sub-opportunity-analyzer",
            "sub-solution-space-explorer",
        ],
    },
    "stage-product": {
        "phase": 2,
        "name": "Product",
        "subagents": [
            "sub-requirement-parser",
            "sub-acceptance-criteria",
            "sub-risk-analyzer",
            "sub-assumption-extractor",
        ],
    },
    "stage-story-tasks": {
        "phase": 3,
        "name": "Story-Tasks",
        "subagents": [
            "sub-story-writer",
            "sub-task-decomposer",
            "sub-dependency-mapper",
        ],
    },
    "stage-architecture": {
        "phase": 4,
        "name": "Architecture",
        "subagents": [
            "sub-tech-stack-advisor",
            "sub-solution-evaluator",
            "sub-adr-writer",
        ],
    },
    "stage-design": {
        "phase": 5,
        "name": "Design",
        "subagents": [
            "sub-interface-designer",
            "sub-data-model-designer",
            "sub-integration-planner",
            "sub-nfr-evaluator",
        ],
    },
    "stage-development": {
        "phase": 6,
        "name": "Development",
        "subagents": [
            "sub-repo-analyzer",
            "sub-code-generator",
            "sub-refactoring-agent",
            "sub-documentation-agent",
        ],
    },
    "stage-testing": {
        "phase": 7,
        "name": "Testing",
        "subagents": [
            "sub-unit-test",
            "sub-integration-test",
            "sub-regression-test",
            "sub-test-data",
        ],
    },
    "stage-security": {
        "phase": 8,
        "name": "Security",
        "subagents": [
            "sub-secret-scanner",
            "sub-dependency-scanner",
            "sub-owasp-reviewer",
            "sub-policy-validator",
        ],
    },
    "stage-review": {
        "phase": 9,
        "name": "Review",
        "subagents": [
            "sub-code-review",
            "sub-maintainability",
            "sub-performance",
        ],
    },
    "stage-devops": {
        "phase": 10,
        "name": "DevOps",
        "subagents": [],
    },
    "stage-observability": {
        "phase": 11,
        "name": "Observability",
        "subagents": [],
    },
    "stage-retirement": {
        "phase": 12,
        "name": "Retirement",
        "subagents": [
            "sub-deprecation-planner",
            "sub-migration-strategist",
            "sub-data-retention-auditor",
            "sub-decommission-executor",
        ],
    },
}

# Stages that can never be disabled via phase-config.json.
ALWAYS_ENABLED: set[str] = {BOOTSTRAP_ID}

# Canonical built-in pipeline order (by stage_id), independent of the numeric
# phase labels in PHASE_REGISTRY. Custom stages are spliced into this list at
# registration time (see compute_pipeline) and phase numbers are then derived
# purely from position in the merged list — so inserting a custom stage
# renumbers every built-in stage after it.
BUILTIN_ORDER: list[str] = [
    "stage-problem-discovery",
    BOOTSTRAP_ID,
    "stage-product",
    "stage-story-tasks",
    "stage-architecture",
    "stage-design",
    "stage-development",
    "stage-testing",
    "stage-security",
    "stage-review",
    "stage-devops",
    "stage-observability",
    "stage-retirement",
]


def default_config() -> dict[str, Any]:
    """Return the default phase configuration — everything enabled."""
    stages: dict[str, Any] = {}
    for stage_id, info in PHASE_REGISTRY.items():
        stages[stage_id] = {
            "enabled": True,
            "subagents": {sub_id: True for sub_id in info["subagents"]},
        }
    return {"stages": stages}


# ── Presets ───────────────────────────────────────────────────────────────
# Opt-in profiles applied via `sdlc phases --preset <name>`. They only change
# which stages ship enabled in phase-config.json; the built-in default
# (written by `sdlc init` / `--reset`) remains "full" (everything enabled).

# Stages the "lean" common-core preset disables (everything else stays on).
LEAN_DISABLED_STAGES: set[str] = {
    "stage-problem-discovery",
    "stage-security",
    "stage-observability",
    "stage-retirement",
}

# preset name -> set of stage-ids to disable ("full" disables nothing).
PRESETS: dict[str, set[str]] = {
    "full": set(),
    "lean": set(LEAN_DISABLED_STAGES),
}


def preset_names() -> list[str]:
    """Return the available preset names."""
    return list(PRESETS.keys())


def preset_config(name: str) -> dict[str, Any]:
    """Return a phase configuration for the named preset.

    Starts from ``default_config()`` (all enabled) and disables the stages
    listed for that preset. Subagent flags are left intact so re-enabling a
    stage later restores its original subagent selection.
    """
    if name not in PRESETS:
        raise ValueError(
            f"Unknown preset '{name}'. Valid presets: {', '.join(preset_names())}."
        )
    config = default_config()
    for stage_id in PRESETS[name]:
        set_stage_enabled(config, stage_id, False)
    return config


def write_config(sdlc_dir: Path, config: dict[str, Any] | None = None) -> Path:
    """Write phase-config.json into the .sdlc directory.

    Returns the path to the written file.
    """
    if config is None:
        config = default_config()
    path = sdlc_dir / CONFIG_FILENAME
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return path


def load_config(sdlc_dir: Path) -> dict[str, Any] | None:
    """Load phase-config.json from the .sdlc directory.

    Returns None if the file doesn't exist.
    """
    path = sdlc_dir / CONFIG_FILENAME
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def is_stage_enabled(stage_id: str, config: dict[str, Any]) -> bool:
    """Return whether a stage is enabled. Defaults to True if unknown/absent."""
    if stage_id in ALWAYS_ENABLED:
        return True
    stages = config.get("stages", {})
    entry = stages.get(stage_id)
    if entry is None:
        return True
    return bool(entry.get("enabled", True))


def is_subagent_enabled(stage_id: str, sub_id: str, config: dict[str, Any]) -> bool:
    """Return whether a subagent within a stage is enabled.

    Defaults to True if the stage or subagent is unknown/absent. If the
    parent stage itself is disabled, its subagents are also considered
    disabled regardless of their individual flag.
    """
    if not is_stage_enabled(stage_id, config):
        return False
    stages = config.get("stages", {})
    entry = stages.get(stage_id)
    if entry is None:
        return True
    subagents = entry.get("subagents", {})
    if sub_id not in subagents:
        return True
    return bool(subagents[sub_id])


def set_stage_enabled(config: dict[str, Any], stage_id: str, enabled: bool) -> None:
    """Mutate config in place, enabling/disabling a stage (built-in or custom)."""
    if stage_id in ALWAYS_ENABLED:
        raise ValueError(f"'{stage_id}' cannot be disabled (Bootstrap is orchestrator-direct).")
    default_subs = {s: True for s in PHASE_REGISTRY.get(stage_id, {}).get("subagents", [])}
    stages = config.setdefault("stages", {})
    entry = stages.setdefault(stage_id, {"enabled": True, "subagents": default_subs})
    entry["enabled"] = enabled


def set_subagent_enabled(config: dict[str, Any], stage_id: str, sub_id: str, enabled: bool) -> None:
    """Mutate config in place, enabling/disabling a subagent within a stage
    (built-in or custom stage/subagent)."""
    default_subs = {s: True for s in PHASE_REGISTRY.get(stage_id, {}).get("subagents", [])}
    stages = config.setdefault("stages", {})
    entry = stages.setdefault(stage_id, {"enabled": True, "subagents": default_subs})
    subagents = entry.setdefault("subagents", {})
    subagents[sub_id] = enabled


def known_stage_ids(custom_agents: dict[str, Any] | None = None) -> list[str]:
    """Return all configurable stage-ids (built-in + registered custom).

    Bootstrap is excluded — it has no stage-id and is never configurable.
    """
    ids = list(PHASE_REGISTRY.keys())
    if custom_agents:
        ids.extend(custom_agents.get("custom_stages", {}).keys())
    return ids


def known_subagent_ids(
    stage_id: str, custom_agents: dict[str, Any] | None = None
) -> list[str]:
    """Return all subagent-ids valid for a stage (built-in + custom)."""
    subs = list(PHASE_REGISTRY.get(stage_id, {}).get("subagents", []))
    if custom_agents:
        # Custom stages carry their subagents inline.
        custom_stage = custom_agents.get("custom_stages", {}).get(stage_id)
        if custom_stage:
            subs.extend(custom_stage.get("subagents", []))
        # Custom subagents attached to a built-in/custom stage.
        for sub_id, entry in custom_agents.get("custom_subagents", {}).items():
            if entry.get("attach_to_stage") == stage_id and sub_id not in subs:
                subs.append(sub_id)
    return subs


def default_custom_agents() -> dict[str, Any]:
    """Return the default (empty) custom-agents.json structure."""
    return {"custom_stages": {}, "custom_subagents": {}}


def write_custom_agents(sdlc_dir: Path, data: dict[str, Any] | None = None) -> Path:
    """Write custom-agents.json into the .sdlc directory."""
    if data is None:
        data = default_custom_agents()
    path = sdlc_dir / CUSTOM_AGENTS_FILENAME
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def load_custom_agents(sdlc_dir: Path) -> dict[str, Any]:
    """Load custom-agents.json from the .sdlc directory.

    Returns the default (empty) structure if the file doesn't exist.
    """
    path = sdlc_dir / CUSTOM_AGENTS_FILENAME
    if not path.exists():
        return default_custom_agents()
    return json.loads(path.read_text(encoding="utf-8"))


def compute_pipeline(custom_agents: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Merge registered custom stages into BUILTIN_ORDER at their anchor point
    and return the full run order (built-in + custom), WITHOUT phase numbers.

    Each row: {stage_id, name, is_custom, subagents: [sub_id, ...]}
    """
    if custom_agents is None:
        custom_agents = default_custom_agents()
    custom_stages: dict[str, Any] = custom_agents.get("custom_stages", {})

    order = list(BUILTIN_ORDER)
    for stage_id, entry in custom_stages.items():
        if stage_id in order:
            continue  # already inserted (defensive against duplicate calls)
        anchor = entry.get("anchor", {})
        anchor_stage = anchor.get("stage_id")
        position = anchor.get("position", "after")
        if anchor_stage in order:
            idx = order.index(anchor_stage)
            insert_idx = idx + 1 if position == "after" else idx
        else:
            # Unknown/missing anchor — fall back to just before Retirement.
            insert_idx = order.index("stage-retirement")
        order.insert(insert_idx, stage_id)

    rows = []
    for stage_id in order:
        if stage_id in custom_stages:
            entry = custom_stages[stage_id]
            rows.append(
                {
                    "stage_id": stage_id,
                    "name": entry.get("name", stage_id),
                    "is_custom": True,
                    "subagents": list(entry.get("subagents", [])),
                }
            )
        elif stage_id == BOOTSTRAP_ID:
            rows.append({"stage_id": stage_id, "name": "Bootstrap", "is_custom": False, "subagents": []})
        else:
            info = PHASE_REGISTRY[stage_id]
            rows.append(
                {
                    "stage_id": stage_id,
                    "name": info["name"],
                    "is_custom": False,
                    "subagents": list(info["subagents"]),
                }
            )
    return rows


def compute_phase_numbers(custom_agents: dict[str, Any] | None = None) -> dict[str, int]:
    """Return {stage_id: phase_number} derived from compute_pipeline()."""
    return {row["stage_id"]: i for i, row in enumerate(compute_pipeline(custom_agents))}


# ── Canonical registry derivation (single source of truth) ────────────────
# scaffold.py (orchestrator.json), mermaid.py (AGENT_REGISTRY), and the CLI
# status command all derive their phase/agent structure from these helpers so
# the pipeline is defined in exactly one place.


def phase_slug(stage_id: str) -> str:
    """Return the phase slug for a stage id (e.g. 'stage-product' -> 'product')."""
    if stage_id.startswith("stage-"):
        return stage_id[len("stage-"):]
    return stage_id


def phase_key(stage_id: str, phase_num: int) -> str:
    """Return the orchestrator.json phase key (e.g. '2-product')."""
    return f"{phase_num}-{phase_slug(stage_id)}"


def orchestrator_phases_template(
    custom_agents: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    """Return the 'phases' dict for a fresh orchestrator.json (v4 ordering).

    Retirement defaults to 'not_triggered'; every other phase to 'pending'.
    """
    phases: dict[str, dict[str, Any]] = {}
    for num, row in enumerate(compute_pipeline(custom_agents)):
        stage_id = row["stage_id"]
        status = "not_triggered" if stage_id == "stage-retirement" else "pending"
        phases[phase_key(stage_id, num)] = {"status": status, "gate": None, "review": None}
    return phases


def agent_registry(custom_agents: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Return the ordered agent registry used to render the interaction map.

    Each row: {phase, key, name, agent, role, subagents}. Bootstrap is the
    orchestrator-direct phase (agent 'orch-sdlc', role 'orchestrator').
    """
    registry: list[dict[str, Any]] = []
    for num, row in enumerate(compute_pipeline(custom_agents)):
        stage_id = row["stage_id"]
        if stage_id == BOOTSTRAP_ID:
            registry.append({
                "phase": num,
                "key": phase_key(stage_id, num),
                "name": "Bootstrap",
                "agent": "orch-sdlc",
                "role": "orchestrator",
                "subagents": [],
            })
        else:
            registry.append({
                "phase": num,
                "key": phase_key(stage_id, num),
                "name": row["name"],
                "agent": stage_id,
                "role": "stage",
                "subagents": list(row["subagents"]),
            })
    return registry


def phase_display_names(custom_agents: dict[str, Any] | None = None) -> dict[str, str]:
    """Return {phase_key: display_name} for status rendering."""
    return {row["key"]: row["name"] for row in agent_registry(custom_agents)}


def phase_enabled_map(
    config: dict[str, Any] | None,
    custom_agents: dict[str, Any] | None = None,
) -> dict[str, bool]:
    """Return {phase_key: enabled} for every phase in the pipeline.

    Bootstrap (orchestrator-direct) is always enabled. If ``config`` is None
    (no phase-config.json), every phase is treated as enabled.
    """
    cfg = config or {}
    result: dict[str, bool] = {}
    for row in agent_registry(custom_agents):
        if row["role"] == "orchestrator":
            result[row["key"]] = True
        else:
            result[row["key"]] = is_stage_enabled(row["agent"], cfg)
    return result


def summary(
    config: dict[str, Any], custom_agents: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    """Return a list of rows (ordered by phase number) for display.

    Each row: {phase, stage_id, name, enabled, is_custom, subagents: [{id, enabled, is_custom}]}
    """
    if custom_agents is None:
        custom_agents = default_custom_agents()
    custom_subagents: dict[str, Any] = custom_agents.get("custom_subagents", {})

    rows = []
    for phase_num, row in enumerate(compute_pipeline(custom_agents)):
        stage_id = row["stage_id"]
        if stage_id == BOOTSTRAP_ID:
            continue  # orchestrator-direct, not configurable — omit from display

        sub_ids = list(row["subagents"])
        for sub_id, sub_entry in custom_subagents.items():
            if sub_entry.get("attach_to_stage") == stage_id and sub_id not in sub_ids:
                sub_ids.append(sub_id)

        stage_enabled = is_stage_enabled(stage_id, config)
        sub_rows = [
            {
                "id": sub_id,
                "enabled": is_subagent_enabled(stage_id, sub_id, config),
                "is_custom": sub_id in custom_subagents,
            }
            for sub_id in sub_ids
        ]
        rows.append(
            {
                "phase": phase_num,
                "stage_id": stage_id,
                "name": row["name"],
                "enabled": stage_enabled,
                "is_custom": row["is_custom"],
                "subagents": sub_rows,
            }
        )
    return rows
