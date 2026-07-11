"""Schema-consistency guards for the phase/agent registry.

The pipeline is defined once in ``sdlc_cli.phases`` and consumed by
``scaffold`` (orchestrator.json), ``mermaid`` (interaction map), and the
CLI ``status`` command. These tests fail if any consumer drifts from the
single source of truth — which is exactly the v3/v4 divergence this
refactor eliminated.
"""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from sdlc_cli import app
from sdlc_cli import mermaid
from sdlc_cli.phases import (
    agent_registry,
    orchestrator_phases_template,
)

runner = CliRunner()

# The canonical v4 pipeline: 13 phases (0-12).
EXPECTED_PHASE_KEYS = [
    "0-problem-discovery",
    "1-bootstrap",
    "2-product",
    "3-story-tasks",
    "4-architecture",
    "5-design",
    "6-development",
    "7-testing",
    "8-security",
    "9-review",
    "10-devops",
    "11-observability",
    "12-retirement",
]


def test_orchestrator_template_has_13_phases_in_order() -> None:
    keys = list(orchestrator_phases_template().keys())
    assert keys == EXPECTED_PHASE_KEYS


def test_retirement_defaults_to_not_triggered() -> None:
    phases = orchestrator_phases_template()
    assert phases["12-retirement"]["status"] == "not_triggered"
    # Every other phase starts pending.
    for key, entry in phases.items():
        if key != "12-retirement":
            assert entry["status"] == "pending"


def test_agent_registry_matches_phase_template() -> None:
    reg_keys = [row["key"] for row in agent_registry()]
    template_keys = list(orchestrator_phases_template().keys())
    assert reg_keys == template_keys


def test_mermaid_registry_is_derived_from_phases() -> None:
    # mermaid.AGENT_REGISTRY must equal phases.agent_registry() so the
    # interaction map never drifts from the real pipeline.
    assert mermaid.AGENT_REGISTRY == agent_registry()


def test_registry_agent_counts() -> None:
    reg = agent_registry()
    stage_agents = [r for r in reg if r["role"] == "stage"]
    orchestrator_rows = [r for r in reg if r["role"] == "orchestrator"]
    pipeline_subagents = sum(len(r["subagents"]) for r in reg)

    assert len(orchestrator_rows) == 1  # bootstrap = orchestrator-direct
    assert len(stage_agents) == 12
    # 37 subagents live in the linear pipeline; 2 cross-cutting subagents
    # (compliance-validator, context-optimizer) are not phase-bound => 39 total.
    assert pipeline_subagents == 37


def test_scaffolded_orchestrator_json_matches_registry(tmp_path: Path) -> None:
    """`sdlc init` must write orchestrator.json phases identical to the registry."""
    result = runner.invoke(
        app,
        ["init", str(tmp_path), "--integration", "devin", "--non-interactive"],
    )
    assert result.exit_code == 0

    orch = json.loads(
        (tmp_path / ".sdlc" / "state" / "orchestrator.json").read_text()
    )
    assert list(orch["phases"].keys()) == EXPECTED_PHASE_KEYS
    assert orch["phases"] == orchestrator_phases_template()
