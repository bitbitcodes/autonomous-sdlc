"""CLI smoke tests for `sdlc continuity check`."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from sdlc_cli import app

runner = CliRunner()


def _init_project(tmp_path: Path) -> Path:
    result = runner.invoke(
        app,
        ["init", str(tmp_path), "--integration", "devin", "--non-interactive"],
    )
    assert result.exit_code == 0
    return tmp_path


def test_continuity_check_requires_init(tmp_path: Path) -> None:
    result = runner.invoke(app, ["continuity", "check", str(tmp_path)])
    assert result.exit_code == 1
    assert ".sdlc" in result.output


def test_continuity_check_not_started_exits_zero(tmp_path: Path) -> None:
    _init_project(tmp_path)
    result = runner.invoke(app, ["continuity", "check", str(tmp_path)])
    assert result.exit_code == 0


def test_continuity_check_fresh_exits_zero(tmp_path: Path) -> None:
    _init_project(tmp_path)
    sdlc_dir = tmp_path / ".sdlc"
    (sdlc_dir / "state").mkdir(parents=True, exist_ok=True)
    (sdlc_dir / "CONTINUITY.md").write_text(
        "# CONTINUITY\n\n## Current Phase\nPhase 2: Product\n", encoding="utf-8"
    )
    (sdlc_dir / "state" / "orchestrator.json").write_text(
        json.dumps({"current_phase": 2}), encoding="utf-8"
    )
    result = runner.invoke(app, ["continuity", "check", str(tmp_path)])
    assert result.exit_code == 0
    assert "fresh" in result.output.lower()


def test_continuity_check_stale_exits_nonzero(tmp_path: Path) -> None:
    _init_project(tmp_path)
    sdlc_dir = tmp_path / ".sdlc"
    (sdlc_dir / "state").mkdir(parents=True, exist_ok=True)
    (sdlc_dir / "CONTINUITY.md").write_text(
        "# CONTINUITY\n\n## Current Phase\nPhase 1: Bootstrap\n", encoding="utf-8"
    )
    (sdlc_dir / "state" / "orchestrator.json").write_text(
        json.dumps({"current_phase": 6}), encoding="utf-8"
    )
    result = runner.invoke(app, ["continuity", "check", str(tmp_path)])
    assert result.exit_code == 1
    assert "stale" in result.output.lower()


def test_status_shows_stale_warning(tmp_path: Path) -> None:
    _init_project(tmp_path)
    sdlc_dir = tmp_path / ".sdlc"
    (sdlc_dir / "state").mkdir(parents=True, exist_ok=True)
    (sdlc_dir / "CONTINUITY.md").write_text(
        "# CONTINUITY\n\n## Current Phase\nPhase 1: Bootstrap\n", encoding="utf-8"
    )
    (sdlc_dir / "state" / "orchestrator.json").write_text(
        json.dumps(
            {
                "current_phase": 6,
                "status": "in_progress",
                "phases": {},
            }
        ),
        encoding="utf-8",
    )
    result = runner.invoke(app, ["status", str(tmp_path)])
    assert result.exit_code == 0
    assert "may be stale" in result.output.lower()
