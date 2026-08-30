"""Smoke tests for the `sdlc` CLI.

These cover the basic, non-interactive command surface exercised during
manual review: help/version output, `init --non-interactive`, and the
`models`/`phases` display commands. They are intentionally lightweight —
the goal is regression protection for the CLI wiring, not exhaustive
coverage of every flag combination.
"""

from __future__ import annotations

import json
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


def test_load_config_prefers_run_folder(tmp_path: Path) -> None:
    """model-config.json in the run folder wins over the global .sdlc copy."""
    from sdlc_cli.models import config_path, load_config, write_config

    sdlc_dir = tmp_path / ".sdlc"
    sdlc_dir.mkdir()
    run_dir = sdlc_dir / "runs" / "alpha"
    run_dir.mkdir(parents=True)

    # No config anywhere → None
    assert load_config(sdlc_dir, run_dir=run_dir) is None

    # Global only → global is the effective file
    assert write_config(sdlc_dir) == sdlc_dir / "model-config.json"
    assert config_path(sdlc_dir, run_dir) == sdlc_dir / "model-config.json"

    # Run-folder config → takes priority over global
    run_cfg = load_config(sdlc_dir)
    run_cfg["tiers"]["fast"] = "run-model"
    (run_dir / "model-config.json").write_text(
        json.dumps(run_cfg, indent=2) + "\n", encoding="utf-8"
    )
    loaded = load_config(sdlc_dir, run_dir=run_dir)
    assert loaded is not None
    assert loaded["tiers"]["fast"] == "run-model"
    assert config_path(sdlc_dir, run_dir) == run_dir / "model-config.json"

    # Writes update the run config in place instead of the global file
    assert write_config(sdlc_dir, run_dir=run_dir) == run_dir / "model-config.json"
    reloaded = load_config(sdlc_dir, run_dir=run_dir)
    assert reloaded is not None
    assert reloaded["tiers"]["fast"] != "run-model"


def test_models_display_uses_active_run_config(tmp_path: Path) -> None:
    """`sdlc models` with an active run shows the run folder's overrides."""
    from sdlc_cli.models import load_config
    from sdlc_cli.runs import set_active_run

    runner.invoke(
        app,
        ["init", str(tmp_path), "--integration", "devin", "--non-interactive"],
    )
    sdlc_dir = tmp_path / ".sdlc"
    run_dir = sdlc_dir / "runs" / "test-run"
    run_dir.mkdir(parents=True)
    set_active_run(sdlc_dir, "test-run")

    run_cfg = load_config(sdlc_dir)
    assert run_cfg is not None
    run_cfg["tiers"]["fast"] = "run-specific-model"
    (run_dir / "model-config.json").write_text(
        json.dumps(run_cfg, indent=2) + "\n", encoding="utf-8"
    )

    result = runner.invoke(app, ["models", str(tmp_path)])
    assert result.exit_code == 0
    assert "Run: test-run" in result.output
    assert "run-specific-model" in result.output
    # Rich may soft-wrap the long absolute path; assert on the stable tail
    assert "runs/test-run/model-config.json" in result.output


def test_models_reset_updates_active_run_config(tmp_path: Path) -> None:
    """`sdlc models --reset` resets the run folder's config when one exists."""
    from sdlc_cli.models import load_config
    from sdlc_cli.runs import set_active_run

    runner.invoke(
        app,
        ["init", str(tmp_path), "--integration", "devin", "--non-interactive"],
    )
    sdlc_dir = tmp_path / ".sdlc"
    run_dir = sdlc_dir / "runs" / "test-run"
    run_dir.mkdir(parents=True)
    set_active_run(sdlc_dir, "test-run")
    (run_dir / "model-config.json").write_text(
        json.dumps({"tiers": {"fast": "custom-model"}}, indent=2) + "\n",
        encoding="utf-8",
    )

    result = runner.invoke(app, ["models", str(tmp_path), "--reset"])
    assert result.exit_code == 0

    reset_cfg = load_config(sdlc_dir, run_dir=run_dir)
    assert reset_cfg is not None
    assert reset_cfg["tiers"]["fast"] != "custom-model"
    # Global config is untouched by a run-scoped reset
    global_cfg = load_config(sdlc_dir)
    assert global_cfg is not None
    assert global_cfg["tiers"]["fast"] == "claude-haiku-4.5"


def test_phases_after_init(tmp_path: Path) -> None:
    runner.invoke(
        app,
        ["init", str(tmp_path), "--integration", "devin", "--non-interactive"],
    )
    result = runner.invoke(app, ["phases", str(tmp_path)])
    assert result.exit_code == 0
    assert "Bootstrap" in result.output or "Product" in result.output
