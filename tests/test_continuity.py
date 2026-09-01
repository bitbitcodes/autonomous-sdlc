"""Unit tests for sdlc_cli.continuity — CONTINUITY.md freshness detection."""

from __future__ import annotations

import json
from pathlib import Path

from sdlc_cli.continuity import check_freshness


def _make_run(
    tmp_path: Path,
    *,
    continuity: str | None,
    current_phase: int | None,
    activity_log: str | None = None,
) -> Path:
    run_dir = tmp_path / "run"
    (run_dir / "state").mkdir(parents=True)
    if continuity is not None:
        (run_dir / "CONTINUITY.md").write_text(continuity, encoding="utf-8")
    if current_phase is not None:
        (run_dir / "state" / "orchestrator.json").write_text(
            json.dumps({"current_phase": current_phase}), encoding="utf-8"
        )
    if activity_log is not None:
        (run_dir / "state" / "activity-log.md").write_text(activity_log, encoding="utf-8")
    return run_dir


def test_not_started_when_nothing_exists(tmp_path: Path) -> None:
    run_dir = tmp_path / "empty-run"
    run_dir.mkdir()
    result = check_freshness(run_dir)
    assert result.status == "not_started"
    assert result.fresh is True
    assert result.reasons == []


def test_fresh_when_phase_matches_and_no_log(tmp_path: Path) -> None:
    run_dir = _make_run(
        tmp_path,
        continuity="# CONTINUITY\n\n## Current Phase\nPhase 3: Story-Tasks\n",
        current_phase=3,
    )
    result = check_freshness(run_dir)
    assert result.status == "fresh"
    assert result.fresh is True
    assert result.reasons == []
    assert result.continuity_phase == 3
    assert result.orchestrator_phase == 3


def test_stale_on_phase_mismatch(tmp_path: Path) -> None:
    run_dir = _make_run(
        tmp_path,
        continuity="# CONTINUITY\n\n## Current Phase\nPhase 1: Bootstrap\n",
        current_phase=6,
    )
    result = check_freshness(run_dir)
    assert result.status == "stale"
    assert result.fresh is False
    assert any("Phase 1" in r and "current_phase = 6" in r for r in result.reasons)


def test_stale_on_activity_log_lag(tmp_path: Path) -> None:
    # Same phase (no mismatch), but activity-log.md has a far-future entry —
    # simulates work happening without CONTINUITY.md being touched.
    run_dir = _make_run(
        tmp_path,
        continuity="# CONTINUITY\n\n## Current Phase\nPhase 5: Design\n",
        current_phase=5,
        activity_log="## [2099-01-01T00:00:00Z] Phase 5: Design\n- Agent: stage-design\n",
    )
    result = check_freshness(run_dir)
    assert result.status == "stale"
    assert any("activity-log.md" in r for r in result.reasons)


def test_fresh_when_activity_log_is_older(tmp_path: Path) -> None:
    run_dir = _make_run(
        tmp_path,
        continuity="# CONTINUITY\n\n## Current Phase\nPhase 5: Design\n",
        current_phase=5,
        activity_log="## [2020-01-01T00:00:00Z] Phase 5: Design\n- Agent: stage-design\n",
    )
    result = check_freshness(run_dir)
    assert result.status == "fresh"


def test_unparsable_phase_is_reported_not_crashed(tmp_path: Path) -> None:
    run_dir = _make_run(
        tmp_path,
        continuity="# CONTINUITY\n\n## Current Phase\nSomewhere between phases\n",
        current_phase=2,
    )
    result = check_freshness(run_dir)
    assert result.status == "stale"
    assert result.continuity_phase is None
    assert any("Could not parse" in r for r in result.reasons)


def test_missing_continuity_file_is_unknown_not_a_crash(tmp_path: Path) -> None:
    run_dir = _make_run(tmp_path, continuity=None, current_phase=2)
    result = check_freshness(run_dir)
    assert result.status == "unknown"
    assert result.fresh is True


def test_malformed_orchestrator_json_does_not_crash(tmp_path: Path) -> None:
    run_dir = _make_run(
        tmp_path,
        continuity="# CONTINUITY\n\n## Current Phase\nPhase 2: Product\n",
        current_phase=2,
    )
    (run_dir / "state" / "orchestrator.json").write_text("{not valid json", encoding="utf-8")
    result = check_freshness(run_dir)
    # Can't compare against a phase we couldn't read — falls back to "no mismatch detected".
    assert result.orchestrator_phase is None
    assert result.status == "fresh"


def test_orchestrator_json_missing_entirely_behaves_like_malformed(tmp_path: Path) -> None:
    """CONTINUITY.md exists but state/orchestrator.json was never written (not just
    malformed) — same 'cannot compare, so no mismatch reported' degrade path as the
    malformed case above, not a silent false 'fresh' for a different reason."""
    run_dir = tmp_path / "run"
    (run_dir / "state").mkdir(parents=True)
    (run_dir / "CONTINUITY.md").write_text(
        "# CONTINUITY\n\n## Current Phase\nPhase 2: Product\n", encoding="utf-8"
    )
    # Deliberately no state/orchestrator.json file at all.
    result = check_freshness(run_dir)
    assert result.orchestrator_phase is None
    assert result.status == "fresh"


def test_orchestrator_json_with_trailing_garbage_is_parsed_via_fallback(tmp_path: Path) -> None:
    """Exercises the raw_decode() fallback branch for trailing-data JSON files
    (the same failure mode orchestrator.json can end up in if an agent appends
    instead of overwriting — see JSON File Safety in orchestrator.md)."""
    run_dir = _make_run(
        tmp_path,
        continuity="# CONTINUITY\n\n## Current Phase\nPhase 4: Architecture\n",
        current_phase=None,
    )
    (run_dir / "state" / "orchestrator.json").write_text(
        '{"current_phase": 4}{"extra": "garbage appended, not overwritten"}',
        encoding="utf-8",
    )
    result = check_freshness(run_dir)
    assert result.orchestrator_phase == 4
    assert result.status == "fresh"


def test_unparsable_activity_log_timestamp_is_skipped_not_crashed(tmp_path: Path) -> None:
    run_dir = _make_run(
        tmp_path,
        continuity="# CONTINUITY\n\n## Current Phase\nPhase 3: Story-Tasks\n",
        current_phase=3,
        activity_log="## [not-a-real-date] Phase 3: Story-Tasks\n- Agent: stage-story-tasks\n",
    )
    result = check_freshness(run_dir)
    assert result.status == "fresh"
    assert result.activity_log_latest is None


def test_naive_activity_log_timestamp_does_not_crash_comparison(tmp_path: Path) -> None:
    """A timestamp missing a 'Z'/offset (naive) must not raise TypeError when
    compared against CONTINUITY.md's (always timezone-aware) mtime."""
    run_dir = _make_run(
        tmp_path,
        continuity="# CONTINUITY\n\n## Current Phase\nPhase 2: Product\n",
        current_phase=2,
        activity_log="## [2099-01-01T00:00:00] Phase 2: Product\n- Agent: stage-product\n",
    )
    result = check_freshness(run_dir)  # must not raise
    assert result.status == "stale"
    assert any("activity-log.md" in r for r in result.reasons)


def test_out_of_order_activity_log_entries_use_latest_timestamp_not_last_line(
    tmp_path: Path,
) -> None:
    """A far-future entry appearing before an older one (corrupted/out-of-order
    append) must still be detected — picking 'the last line' instead of 'the
    latest timestamp' would silently hide it."""
    run_dir = _make_run(
        tmp_path,
        continuity="# CONTINUITY\n\n## Current Phase\nPhase 2: Product\n",
        current_phase=2,
        activity_log=(
            "## [2099-01-01T00:00:00Z] Phase 2: Product\n- Agent: x\n"
            "## [2001-01-01T00:00:00Z] Phase 2: Product\n- Agent: y\n"
        ),
    )
    result = check_freshness(run_dir)
    assert result.activity_log_latest == "2099-01-01T00:00:00Z"
    assert result.status == "stale"


def test_ambiguous_narrative_phase_text_is_not_parsed(tmp_path: Path) -> None:
    """'Phase N' appearing in a narrative sentence (not the anchored 'Phase N:'
    template format) must not be silently taken as the current phase — reporting
    unparsable is safer than guessing which number was meant."""
    run_dir = _make_run(
        tmp_path,
        continuity=(
            "# CONTINUITY\n\n## Current Phase\n"
            "Transitioning from Phase 3 to Phase 8: Security\n"
        ),
        current_phase=8,
    )
    result = check_freshness(run_dir)
    assert result.continuity_phase is None
    assert result.status == "stale"
    assert any("Could not parse" in r for r in result.reasons)


def test_phase_number_inside_header_line_itself_is_ignored(tmp_path: Path) -> None:
    """A phase number mentioned in the '## Current Phase' header line itself
    (e.g. an editorial aside) must not be mistaken for the actual current phase
    on the following content line."""
    run_dir = _make_run(
        tmp_path,
        continuity="# CONTINUITY\n\n## Current Phase (was Phase 2)\nPhase 8: Security\n",
        current_phase=8,
    )
    result = check_freshness(run_dir)
    assert result.continuity_phase == 8
    assert result.status == "fresh"


def test_completed_run_is_fresh_despite_no_phase_number(tmp_path: Path) -> None:
    """A finished run's CONTINUITY.md legitimately has no phase number to report
    ("PROJECT COMPLETE" instead of "Phase N: ..."). This must not be treated as an
    unparsable/stale CONTINUITY.md when orchestrator.json agrees the run is done —
    otherwise every completed run would show as permanently stale."""
    run_dir = _make_run(
        tmp_path,
        continuity="# CONTINUITY\n\n## Current Phase\nPROJECT COMPLETE — all 13 phases done\n",
        current_phase=None,
    )
    (run_dir / "state" / "orchestrator.json").write_text(
        json.dumps({"current_phase": 11, "status": "complete"}), encoding="utf-8"
    )
    result = check_freshness(run_dir)
    assert result.status == "fresh"
    assert result.reasons == []


def test_completed_continuity_but_orchestrator_still_in_progress_is_stale(
    tmp_path: Path,
) -> None:
    """The 'complete' exemption only applies when BOTH sides agree — CONTINUITY.md
    claiming completion while orchestrator.json is still mid-run is a real mismatch,
    not a terminal state, and must still be flagged."""
    run_dir = _make_run(
        tmp_path,
        continuity="# CONTINUITY\n\n## Current Phase\nPROJECT COMPLETE\n",
        current_phase=None,
    )
    (run_dir / "state" / "orchestrator.json").write_text(
        json.dumps({"current_phase": 5, "status": "in_progress"}), encoding="utf-8"
    )
    result = check_freshness(run_dir)
    assert result.status == "stale"


def test_never_writes_any_file(tmp_path: Path) -> None:
    run_dir = _make_run(
        tmp_path,
        continuity="# CONTINUITY\n\n## Current Phase\nPhase 1: Bootstrap\n",
        current_phase=6,
    )
    before = {
        p: (p.read_text(encoding="utf-8"), p.stat().st_mtime) for p in run_dir.rglob("*") if p.is_file()
    }
    check_freshness(run_dir)
    after = {
        p: (p.read_text(encoding="utf-8"), p.stat().st_mtime) for p in run_dir.rglob("*") if p.is_file()
    }
    assert before == after
