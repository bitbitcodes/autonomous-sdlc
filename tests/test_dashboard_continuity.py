"""Integration tests for CONTINUITY.md freshness in the dashboard payload.

`artifacts/design/design.md` requires `sdlc dashboard` to surface the same freshness
signal as `sdlc status`; this was previously untested (status has coverage via
test_continuity_cli.py::test_status_shows_stale_warning, dashboard did not).
"""

from __future__ import annotations

import json
from pathlib import Path

from sdlc_cli.dashboard import read_state


def _make_run(tmp_path: Path, *, continuity: str, current_phase: int) -> Path:
    run_dir = tmp_path / "run"
    (run_dir / "state").mkdir(parents=True)
    (run_dir / "CONTINUITY.md").write_text(continuity, encoding="utf-8")
    (run_dir / "state" / "orchestrator.json").write_text(
        json.dumps({"current_phase": current_phase}), encoding="utf-8"
    )
    return run_dir


def test_read_state_includes_fresh_continuity_freshness(tmp_path: Path) -> None:
    run_dir = _make_run(
        tmp_path,
        continuity="# CONTINUITY\n\n## Current Phase\nPhase 2: Product\n",
        current_phase=2,
    )
    state = read_state(run_dir)
    assert state["continuity_freshness"]["status"] == "fresh"
    assert state["continuity_freshness"]["reasons"] == []


def test_read_state_includes_stale_continuity_freshness(tmp_path: Path) -> None:
    run_dir = _make_run(
        tmp_path,
        continuity="# CONTINUITY\n\n## Current Phase\nPhase 1: Bootstrap\n",
        current_phase=6,
    )
    state = read_state(run_dir)
    assert state["continuity_freshness"]["status"] == "stale"
    assert any("Phase 1" in r for r in state["continuity_freshness"]["reasons"])


def test_read_state_never_raises_when_continuity_check_would_fail(tmp_path: Path) -> None:
    """read_state() must degrade gracefully (never propagate an exception) even if
    the freshness checker itself hits something unexpected — the dashboard payload
    is otherwise fully assembled from other files and shouldn't be lost over this."""
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    # No CONTINUITY.md, no state/ dir at all.
    state = read_state(run_dir)
    assert "continuity_freshness" in state
    assert state["continuity_freshness"]["status"] in ("not_started", "unknown")
