"""Smoke tests for the `sdlc` CLI.

These cover the basic, non-interactive command surface exercised during
manual review: help/version output, `init --non-interactive`, and the
`models`/`phases` display commands. They are intentionally lightweight —
the goal is regression protection for the CLI wiring, not exhaustive
coverage of every flag combination.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from sdlc_cli import app

runner = CliRunner()


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "init" in result.output
    assert "models" in result.output


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "autonomous-sdlc" in result.output


def test_init_non_interactive(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["init", str(tmp_path), "--integration", "devin", "--non-interactive"],
    )
    assert result.exit_code == 0
    assert (tmp_path / ".sdlc").is_dir()
    assert (tmp_path / ".sdlc" / "framework" / "run.sh").is_file()
    assert (tmp_path / ".devin").is_dir()


def test_init_windsurf_alias_scaffolds_devin(tmp_path: Path) -> None:
    """`--integration windsurf` is a back-compat alias for `devin` (Windsurf
    was rebranded to Devin Desktop) — it should still work and produce the
    same `.devin/` files, not a separate `.windsurf/` tree.
    """
    result = runner.invoke(
        app,
        ["init", str(tmp_path), "--integration", "windsurf", "--non-interactive"],
    )
    assert result.exit_code == 0
    assert (tmp_path / ".devin" / "rules" / "sdlc.md").is_file()


def test_list_integrations_has_no_duplicate_devin_entry() -> None:
    """The `windsurf` alias must not cause Devin Desktop to be listed twice."""
    from sdlc_cli.integrations import list_integrations

    integrations = list_integrations()
    keys = [key for key, _ in integrations]
    assert keys.count("devin") == 1
    assert "windsurf" not in keys


def test_models_requires_init(tmp_path: Path) -> None:
    result = runner.invoke(app, ["models", str(tmp_path)])
    assert result.exit_code != 0
    assert ".sdlc" in result.output


def test_models_after_init(tmp_path: Path) -> None:
    runner.invoke(
        app,
        ["init", str(tmp_path), "--integration", "devin", "--non-interactive"],
    )
    result = runner.invoke(app, ["models", str(tmp_path)])
    assert result.exit_code == 0
    assert "Model Tiers" in result.output


def test_models_reset(tmp_path: Path) -> None:
    runner.invoke(
        app,
        ["init", str(tmp_path), "--integration", "devin", "--non-interactive"],
    )
    result = runner.invoke(app, ["models", str(tmp_path), "--reset"])
    assert result.exit_code == 0
    assert (tmp_path / ".sdlc" / "model-config.json").is_file()


def test_phases_after_init(tmp_path: Path) -> None:
    runner.invoke(
        app,
        ["init", str(tmp_path), "--integration", "devin", "--non-interactive"],
    )
    result = runner.invoke(app, ["phases", str(tmp_path)])
    assert result.exit_code == 0
    assert "Bootstrap" in result.output or "Product" in result.output
