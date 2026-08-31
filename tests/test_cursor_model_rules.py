"""Tests for Cursor per-stage model rules and run-folder priority.

`sdlc init --integration cursor-agent` generates `.cursor/rules/sdlc.model.*.mdc`
files with a `model:` frontmatter hint per stage. The models come from
model-config.json loaded with run-folder priority (run folder first, then
global), and the rules are refreshed whenever the effective config could have
changed: `run new`, `run switch`, `run archive` (when it clears the active
run), and `sdlc models --edit` / `--reset`.
"""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from sdlc_cli import app

runner = CliRunner()


def _init_cursor(tmp_path: Path) -> Path:
    """Init with the Cursor integration and return the rules directory."""
    result = runner.invoke(
        app,
        ["init", str(tmp_path), "--integration", "cursor-agent", "--non-interactive"],
    )
    assert result.exit_code == 0, result.output
    rules_dir = tmp_path / ".cursor" / "rules"
    assert (rules_dir / "sdlc.model.product.mdc").is_file()
    return rules_dir


def _write_run_config(tmp_path: Path, slug: str, reasoning_model: str) -> Path:
    """Drop a per-run model-config.json override into .sdlc/runs/<slug>/."""
    from sdlc_cli.models import load_config

    sdlc_dir = tmp_path / ".sdlc"
    run_dir = sdlc_dir / "runs" / slug
    run_dir.mkdir(parents=True, exist_ok=True)
    cfg = load_config(sdlc_dir)
    assert cfg is not None
    cfg["tiers"]["reasoning"] = reasoning_model
    (run_dir / "model-config.json").write_text(
        json.dumps(cfg, indent=2) + "\n", encoding="utf-8"
    )
    return run_dir


def _rule_model(rules_dir: Path, stage: str) -> str:
    """Extract the `model:` value from a generated rule's frontmatter."""
    text = (rules_dir / f"sdlc.model.{stage}.mdc").read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("model:"):
            return line.split(":", 1)[1].strip()
    raise AssertionError(f"No model: frontmatter in sdlc.model.{stage}.mdc")


def test_init_generates_rules_from_global_config(tmp_path: Path) -> None:
    rules_dir = _init_cursor(tmp_path)
    # Global defaults: product (reasoning tier) = claude-opus-4.7
    assert _rule_model(rules_dir, "product") == "claude-opus-4.7"


def test_run_switch_refreshes_rules_with_run_priority(tmp_path: Path) -> None:
    rules_dir = _init_cursor(tmp_path)

    result = runner.invoke(
        app,
        ["run", "new", "First spec for alpha", "--name", "alpha", "--target", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    assert "Cursor model rule" in result.output  # refresh fired on run new

    # Newly created run has no config yet → rules still reflect global config
    assert _rule_model(rules_dir, "product") == "claude-opus-4.7"

    _write_run_config(tmp_path, "alpha", "run-reasoning-model")

    # Create a second run (active switches to beta → back to global models)…
    result = runner.invoke(
        app,
        ["run", "new", "Second spec for beta", "--name", "beta", "--target", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    assert _rule_model(rules_dir, "product") == "claude-opus-4.7"

    # …then switch back to alpha → its run-folder config takes priority
    result = runner.invoke(app, ["run", "switch", "alpha", "--target", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert "Cursor model rule" in result.output
    assert _rule_model(rules_dir, "product") == "run-reasoning-model"


def test_models_reset_refreshes_rules_from_run_config(tmp_path: Path) -> None:
    rules_dir = _init_cursor(tmp_path)

    result = runner.invoke(
        app,
        ["run", "new", "Spec for reset test", "--name", "alpha", "--target", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    _write_run_config(tmp_path, "alpha", "run-reasoning-model")
    result = runner.invoke(app, ["run", "switch", "alpha", "--target", str(tmp_path)])
    assert result.exit_code == 0, result.output
    assert _rule_model(rules_dir, "product") == "run-reasoning-model"

    # Run-scoped reset restores defaults → rules revert to the default model
    result = runner.invoke(app, ["models", str(tmp_path), "--reset"])
    assert result.exit_code == 0, result.output
    assert _rule_model(rules_dir, "product") == "claude-opus-4.7"


def test_run_commands_without_cursor_integration_skip_refresh(tmp_path: Path) -> None:
    """Projects scaffolded without Cursor must not gain .cursor/ on run ops."""
    result = runner.invoke(
        app,
        ["init", str(tmp_path), "--integration", "devin", "--non-interactive"],
    )
    assert result.exit_code == 0, result.output
    assert not (tmp_path / ".cursor").exists()

    result = runner.invoke(
        app,
        ["run", "new", "Spec without cursor", "--name", "alpha", "--target", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    assert "Cursor model rule" not in result.output
    assert not (tmp_path / ".cursor").exists()
