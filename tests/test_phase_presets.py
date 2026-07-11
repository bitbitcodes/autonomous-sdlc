"""Tests for the `sdlc phases --preset` profiles."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from sdlc_cli import app
from sdlc_cli.phases import (
    LEAN_DISABLED_STAGES,
    default_config,
    preset_config,
    preset_names,
)

runner = CliRunner()


def test_preset_names() -> None:
    assert set(preset_names()) == {"full", "lean"}


def test_full_preset_equals_default() -> None:
    assert preset_config("full") == default_config()


def test_lean_preset_disables_expected_stages() -> None:
    config = preset_config("lean")
    stages = config["stages"]

    for stage_id in LEAN_DISABLED_STAGES:
        assert stages[stage_id]["enabled"] is False

    # Every other stage stays enabled.
    for stage_id, entry in stages.items():
        if stage_id not in LEAN_DISABLED_STAGES:
            assert entry["enabled"] is True


def test_lean_preset_preserves_subagent_flags() -> None:
    # Disabling a stage must not wipe its subagent map (so re-enabling restores it).
    config = preset_config("lean")
    security = config["stages"]["stage-security"]
    assert security["enabled"] is False
    assert security["subagents"]  # non-empty
    assert all(v is True for v in security["subagents"].values())


def test_unknown_preset_raises() -> None:
    with pytest.raises(ValueError):
        preset_config("bogus")


def test_cli_preset_lean(tmp_path: Path) -> None:
    init = runner.invoke(
        app,
        ["init", str(tmp_path), "--integration", "devin", "--non-interactive"],
    )
    assert init.exit_code == 0

    result = runner.invoke(app, ["phases", str(tmp_path), "--preset", "lean"])
    assert result.exit_code == 0

    config = json.loads((tmp_path / ".sdlc" / "phase-config.json").read_text())
    stages = config["stages"]
    for stage_id in LEAN_DISABLED_STAGES:
        assert stages[stage_id]["enabled"] is False
    assert stages["stage-development"]["enabled"] is True


def test_cli_preset_invalid(tmp_path: Path) -> None:
    runner.invoke(
        app,
        ["init", str(tmp_path), "--integration", "devin", "--non-interactive"],
    )
    result = runner.invoke(app, ["phases", str(tmp_path), "--preset", "bogus"])
    assert result.exit_code == 1


def test_cli_preset_full_then_reset(tmp_path: Path) -> None:
    runner.invoke(
        app,
        ["init", str(tmp_path), "--integration", "devin", "--non-interactive"],
    )
    runner.invoke(app, ["phases", str(tmp_path), "--preset", "lean"])
    # Reset restores all-enabled default.
    result = runner.invoke(app, ["phases", str(tmp_path), "--reset"])
    assert result.exit_code == 0
    config = json.loads((tmp_path / ".sdlc" / "phase-config.json").read_text())
    assert all(entry["enabled"] for entry in config["stages"].values())


def _init(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["init", str(tmp_path), "--integration", "devin", "--non-interactive"],
    )
    assert result.exit_code == 0


def test_disable_unknown_stage_errors_and_no_write(tmp_path: Path) -> None:
    _init(tmp_path)
    before = (tmp_path / ".sdlc" / "phase-config.json").read_text()

    # Display name / wrong casing is NOT a valid stage-id.
    result = runner.invoke(app, ["phases", str(tmp_path), "--disable", "DevOps"])
    assert result.exit_code == 1
    assert "Unknown stage-id" in result.output

    # Config must be untouched (no silent no-op write).
    assert (tmp_path / ".sdlc" / "phase-config.json").read_text() == before


def test_disable_valid_stage_id_succeeds(tmp_path: Path) -> None:
    _init(tmp_path)
    result = runner.invoke(app, ["phases", str(tmp_path), "--disable", "stage-devops"])
    assert result.exit_code == 0
    config = json.loads((tmp_path / ".sdlc" / "phase-config.json").read_text())
    assert config["stages"]["stage-devops"]["enabled"] is False


def test_bootstrap_cannot_be_disabled(tmp_path: Path) -> None:
    _init(tmp_path)
    result = runner.invoke(
        app, ["phases", str(tmp_path), "--disable", "stage-bootstrap"]
    )
    assert result.exit_code == 1
    assert "cannot be disabled" in result.output


def test_disable_unknown_subagent_errors(tmp_path: Path) -> None:
    _init(tmp_path)
    result = runner.invoke(
        app,
        ["phases", str(tmp_path), "--disable-sub", "stage-testing:sub-bogus"],
    )
    assert result.exit_code == 1
    assert "Unknown subagent" in result.output


def test_phase_enabled_map_reflects_lean_preset() -> None:
    from sdlc_cli.phases import phase_enabled_map, preset_config

    emap = phase_enabled_map(preset_config("lean"))
    assert emap["8-security"] is False
    assert emap["0-problem-discovery"] is False
    assert emap["11-observability"] is False
    assert emap["12-retirement"] is False
    assert emap["6-development"] is True
    # Bootstrap is always enabled.
    assert emap["1-bootstrap"] is True


def test_mermaid_hides_disabled_phases() -> None:
    from sdlc_cli.mermaid import generate_mermaid
    from sdlc_cli.phases import phase_enabled_map, preset_config

    emap = phase_enabled_map(preset_config("lean"))
    src = generate_mermaid({}, {"traces": []}, {}, emap)

    # Disabled stages + their subagents must be absent entirely.
    assert "stage-security" not in src
    assert "sub-secret-scanner" not in src
    assert "stage-retirement" not in src
    assert "8. Security" not in src

    # Enabled stages remain.
    assert "stage-development" in src
    assert "6. Development" in src


def test_mermaid_shows_all_when_no_map() -> None:
    from sdlc_cli.mermaid import generate_mermaid

    src = generate_mermaid({}, {"traces": []}, {})
    assert "stage-security" in src
    assert "stage-retirement" in src


def test_status_table_hides_disabled_phases(tmp_path: Path) -> None:
    _init(tmp_path)
    runner.invoke(app, ["phases", str(tmp_path), "--preset", "lean"])

    result = runner.invoke(app, ["status", str(tmp_path)])
    assert result.exit_code == 0
    # Enabled phases present; disabled ones hidden with a hint line.
    assert "Development" in result.output
    assert "Security" not in result.output
    assert "Observability" not in result.output
    assert "hidden" in result.output


def test_dashboard_payload_includes_phase_enabled(tmp_path: Path) -> None:
    from sdlc_cli.dashboard import read_state

    _init(tmp_path)
    runner.invoke(app, ["phases", str(tmp_path), "--preset", "lean"])

    state = read_state(tmp_path / ".sdlc")
    emap = state["phase_enabled"]
    assert emap["8-security"] is False
    assert emap["6-development"] is True
    # Disabled phases are hidden from the embedded diagram too.
    assert "stage-security" not in state["mermaid_src"]
    assert "stage-development" in state["mermaid_src"]
