"""Model routing configuration for autonomous-sdlc.

Provides per-agent model assignment via 3 capability tiers
(reasoning, coding, fast) with per-agent overrides.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONFIG_FILENAME = "model-config.json"

# ── Tier definitions ──────────────────────────────────────────────────────

TIERS = {
    "reasoning": "claude-opus-4.7",
    "coding": "claude-sonnet-4.6",
    "fast": "claude-haiku-4.5",
}

# ── Default agent → tier mapping ──────────────────────────────────────────

AGENT_TIERS: dict[str, str] = {
    "orch-sdlc": "reasoning",
    "stage-problem-discovery": "reasoning",
    "stage-product": "reasoning",
    "stage-story-tasks": "reasoning",
    "stage-architecture": "reasoning",
    "stage-design": "reasoning",
    "stage-development": "coding",
    "stage-testing": "coding",
    "stage-security": "reasoning",
    "stage-review": "reasoning",
    "stage-devops": "coding",
    "stage-observability": "coding",
    "stage-retirement": "reasoning",
    "sub-*": "fast",
}

# ── Tier descriptions (used by CLI) ──────────────────────────────────────

TIER_DESCRIPTIONS: dict[str, str] = {
    "reasoning": "Complex analysis, planning, architecture decisions",
    "coding": "Code generation, test writing, infrastructure",
    "fast": "Focused subtasks, parsing, data extraction",
}


def default_config() -> dict[str, Any]:
    """Return the default model routing configuration."""
    return {
        "tiers": dict(TIERS),
        "agent_tiers": dict(AGENT_TIERS),
        "overrides": {},
    }


def write_config(sdlc_dir: Path, config: dict[str, Any] | None = None) -> Path:
    """Write model-config.json into the .sdlc directory.

    Returns the path to the written file.
    """
    if config is None:
        config = default_config()
    path = sdlc_dir / CONFIG_FILENAME
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return path


def load_config(sdlc_dir: Path) -> dict[str, Any] | None:
    """Load model-config.json from the .sdlc directory.

    Returns None if the file doesn't exist.
    """
    path = sdlc_dir / CONFIG_FILENAME
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_model(agent_id: str, config: dict[str, Any]) -> str:
    """Resolve the model for a given agent ID.

    Resolution order:
    1. overrides[agent_id]          → direct model name
    2. agent_tiers[agent_id]        → tier name → tiers[tier]
    3. agent_tiers["sub-*"]         → tier name → tiers[tier]  (for sub-* agents)
    4. tiers["fast"]                → fallback
    """
    tiers = config.get("tiers", TIERS)
    agent_tiers = config.get("agent_tiers", AGENT_TIERS)
    overrides = config.get("overrides", {})

    # 1. Direct override
    if agent_id in overrides:
        return overrides[agent_id]

    # 2. Explicit agent tier
    if agent_id in agent_tiers:
        tier = agent_tiers[agent_id]
        return tiers.get(tier, tier)

    # 3. Glob match for subagents
    if agent_id.startswith("sub-") and "sub-*" in agent_tiers:
        tier = agent_tiers["sub-*"]
        return tiers.get(tier, tier)

    # 4. Fallback
    return tiers.get("fast", "gpt-4.1-mini")


def resolve_all(config: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Resolve model for every known agent.

    Returns dict of {agent_id: {"tier": tier_name, "model": model_name}}.
    """
    agent_tiers = config.get("agent_tiers", AGENT_TIERS)
    overrides = config.get("overrides", {})
    tiers = config.get("tiers", TIERS)

    result: dict[str, dict[str, str]] = {}

    for agent_id in agent_tiers:
        if agent_id == "sub-*":
            continue
        model = resolve_model(agent_id, config)
        tier = agent_tiers.get(agent_id, "fast")
        result[agent_id] = {"tier": tier, "model": model}

    # Add any overrides for agents not in agent_tiers
    for agent_id, model in overrides.items():
        if agent_id not in result:
            result[agent_id] = {"tier": "override", "model": model}
        else:
            result[agent_id]["model"] = model
            result[agent_id]["tier"] = "override"

    # Include the sub-* default entry for display
    if "sub-*" in agent_tiers:
        tier = agent_tiers["sub-*"]
        result["sub-* (default)"] = {"tier": tier, "model": tiers.get(tier, tier)}

    return result
