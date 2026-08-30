"""Tests for `sdlc run new`, including inline (online) spec support.

`run new` accepts a spec three ways: a path to a spec file, an inline spec
string (either as the bare positional argument or via `--text`), or an
interactive prompt when nothing is given. These tests cover the non-file
paths, since the file path was already exercised manually.
"""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from sdlc_cli import app

runner = CliRunner()


def _init(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        ["init", str(tmp_path), "--integration", "devin", "--non-interactive"],
    )
    assert result.exit_code == 0


def test_run_new_from_file(tmp_path: Path) -> None:
    _init(tmp_path)
    spec = tmp_path / "feature.md"
    spec.write_text("# JWT Auth API\n\nBuild a JWT-based auth API.\n", encoding="utf-8")

    result = runner.invoke(app, ["run", "new", str(spec), "--target", str(tmp_path)])
    assert result.exit_code == 0, result.output

    runs_dir = tmp_path / ".sdlc" / "runs"
    slugs = [p.name for p in runs_dir.iterdir() if p.is_dir()]
    assert len(slugs) == 1
    run_dir = runs_dir / slugs[0]
    assert (run_dir / "specs" / "feature.md").is_file()
    normalized = (run_dir / "specs" / "normalized-spec.md").read_text(encoding="utf-8")
    assert "JWT" in normalized


def test_run_new_inline_positional_text(tmp_path: Path) -> None:
    """A positional argument that isn't an existing file is treated as an
    inline/online spec instead of erroring out with 'file not found'."""
    _init(tmp_path)

    result = runner.invoke(
        app,
        ["run", "new", "Build a todo app with JWT auth", "--target", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output

    runs_dir = tmp_path / ".sdlc" / "runs"
    slugs = [p.name for p in runs_dir.iterdir() if p.is_dir()]
    assert len(slugs) == 1
    run_dir = runs_dir / slugs[0]
    normalized = (run_dir / "specs" / "normalized-spec.md").read_text(encoding="utf-8")
    assert normalized.strip() == "Build a todo app with JWT auth"
    # No source file was provided, so nothing besides normalized-spec.md
    # should exist in specs/.
    assert [p.name for p in (run_dir / "specs").iterdir()] == ["normalized-spec.md"]


def test_run_new_text_flag(tmp_path: Path) -> None:
    _init(tmp_path)

    result = runner.invoke(
        app,
        ["run", "new", "--text", "Stripe payment webhook integration", "--target", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output

    runs_dir = tmp_path / ".sdlc" / "runs"
    slugs = [p.name for p in runs_dir.iterdir() if p.is_dir()]
    assert len(slugs) == 1
    assert "stripe" in slugs[0]


def test_run_new_rejects_both_positional_and_text(tmp_path: Path) -> None:
    _init(tmp_path)

    result = runner.invoke(
        app,
        ["run", "new", "some spec text", "--text", "other spec text", "--target", str(tmp_path)],
    )
    assert result.exit_code != 0
    assert "not both" in result.output
