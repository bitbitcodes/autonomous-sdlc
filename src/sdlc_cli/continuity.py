"""Freshness check for CONTINUITY.md — the framework's working-memory file.

`docs/memory-system.md` specifies that CONTINUITY.md is read at the start and
written at the end of every orchestrator turn, but that protocol is enforced only
by prompt text: nothing checks whether it actually happened, so the file can
silently drift from `state/orchestrator.json` / `state/activity-log.md`. This
module gives that drift a machine-checkable signal instead.

Read-only: never writes to CONTINUITY.md or any other state file.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_PHASE_LINE_RE = re.compile(r"^\**phase\s+(\d+)\s*:", re.IGNORECASE)
_LOG_ENTRY_RE = re.compile(r"^##\s*\[([^\]]+)\]")


@dataclass
class FreshnessResult:
    """Result of comparing CONTINUITY.md against orchestrator.json/activity-log.md."""

    status: str  # "fresh" | "stale" | "not_started" | "unknown"
    reasons: list[str] = field(default_factory=list)
    continuity_phase: int | None = None
    orchestrator_phase: int | None = None
    continuity_mtime: str | None = None
    activity_log_latest: str | None = None

    @property
    def fresh(self) -> bool:
        """True unless status is 'stale'. ('not_started'/'unknown' aren't failures —
        there's nothing to compare yet, or nothing to trust a verdict on.)"""
        return self.status != "stale"


def _read_json(path: Path) -> dict[str, Any] | None:
    """Resilient JSON read matching the pattern used elsewhere in this package
    (dashboard.py, phases.py): tolerate trailing extra data, never raise."""
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            obj, _ = json.JSONDecoder().raw_decode(text)
            return obj if isinstance(obj, dict) else None
        except json.JSONDecodeError:
            return None


def _parse_continuity_phase(text: str) -> int | None:
    """Extract the phase number from CONTINUITY.md's '## Current Phase' section.

    Only matches an anchored "Phase N: ..." at the start of the section's first
    non-blank content line (the documented template format) — never text inside
    the header line itself, and never narrative text further down. Ambiguous
    phrasing like "Transitioning from Phase 3 to Phase 8" is deliberately left
    unparsed (reported as unparsable) rather than guessing the wrong number.
    """
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("## current phase"):
            for candidate in lines[i + 1 :]:
                stripped = candidate.strip()
                if not stripped:
                    continue
                m = _PHASE_LINE_RE.match(stripped)
                return int(m.group(1)) if m else None
            return None
    return None


def _continuity_reports_complete(text: str) -> bool:
    """Whether the '## Current Phase' section's content line marks the run as
    finished (e.g. "PROJECT COMPLETE — all N phases done") rather than naming a
    specific phase. There's no phase *number* to compare once a run is done, so
    this isn't a parse failure — it's a distinct, valid terminal state."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if line.strip().lower().startswith("## current phase"):
            for candidate in lines[i + 1 :]:
                stripped = candidate.strip()
                if not stripped:
                    continue
                return "complete" in stripped.lower()
            return False
    return False


def _parse_iso(ts: str) -> datetime | None:
    """Parse an ISO-8601 timestamp, treating a missing offset as UTC.

    Normalizing naive timestamps to UTC (rather than leaving them naive) keeps
    every datetime this module produces comparable — mixing naive and aware
    datetimes raises TypeError on comparison.
    """
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


def _latest_activity_log_timestamp(text: str) -> str | None:
    """Return the '## [timestamp] ...' entry in activity-log.md with the latest
    parsed timestamp (not simply the last line) — so a corrupted or accidentally
    out-of-order entry can't hide a genuinely later one, and an unparsable
    timestamp is skipped rather than crashing or winning by position.
    """
    latest_raw: str | None = None
    latest_dt: datetime | None = None
    for line in text.splitlines():
        m = _LOG_ENTRY_RE.match(line.strip())
        if not m:
            continue
        raw = m.group(1)
        dt = _parse_iso(raw)
        if dt is None:
            continue
        if latest_dt is None or dt > latest_dt:
            latest_dt = dt
            latest_raw = raw
    return latest_raw


def check_freshness(run_dir: Path) -> FreshnessResult:
    """Determine whether `run_dir`'s CONTINUITY.md is stale.

    Two independent signals, either of which is sufficient to flag staleness:
      1. Phase mismatch: CONTINUITY.md's "Current Phase" vs. orchestrator.json's
         current_phase (primary — robust to mtime/clock issues).
      2. Activity-log lag: activity-log.md has an entry newer than CONTINUITY.md's
         own mtime (secondary — catches "same phase, but work happened since").

    Never raises: missing or malformed files degrade to a reported reason, or to
    status="not_started" / "unknown" when there's nothing meaningful to compare.
    """
    continuity_path = run_dir / "CONTINUITY.md"
    orch_path = run_dir / "state" / "orchestrator.json"
    log_path = run_dir / "state" / "activity-log.md"

    if not continuity_path.exists() and not orch_path.exists():
        return FreshnessResult(status="not_started")

    if not continuity_path.exists():
        return FreshnessResult(status="unknown", reasons=["CONTINUITY.md not found"])

    reasons: list[str] = []

    try:
        continuity_text = continuity_path.read_text(encoding="utf-8")
        continuity_mtime = datetime.fromtimestamp(
            continuity_path.stat().st_mtime, tz=UTC
        ).isoformat()
    except OSError:
        return FreshnessResult(status="unknown", reasons=["CONTINUITY.md could not be read"])

    continuity_phase = _parse_continuity_phase(continuity_text)

    orch = _read_json(orch_path)
    orchestrator_phase = orch.get("current_phase") if orch else None
    orchestrator_status = orch.get("status") if orch else None

    both_report_complete = (
        orchestrator_status == "complete" and _continuity_reports_complete(continuity_text)
    )

    if both_report_complete:
        pass  # both agree the run is finished — no phase number to compare
    elif continuity_phase is None:
        reasons.append(
            "Could not parse a phase number from CONTINUITY.md's '## Current Phase' section"
        )
    elif isinstance(orchestrator_phase, int) and continuity_phase != orchestrator_phase:
        reasons.append(
            f"CONTINUITY.md reports Phase {continuity_phase}, but "
            f"orchestrator.json.current_phase = {orchestrator_phase}"
        )

    activity_log_latest: str | None = None
    if log_path.exists():
        try:
            activity_log_latest = _latest_activity_log_timestamp(
                log_path.read_text(encoding="utf-8")
            )
        except OSError:
            pass

    if activity_log_latest:
        log_dt = _parse_iso(activity_log_latest)
        cont_dt = _parse_iso(continuity_mtime)
        if log_dt and cont_dt and log_dt > cont_dt:
            reasons.append(
                f"activity-log.md's latest entry ({activity_log_latest}) is newer than "
                f"CONTINUITY.md's last edit ({continuity_mtime})"
            )

    status = "stale" if reasons else "fresh"
    return FreshnessResult(
        status=status,
        reasons=reasons,
        continuity_phase=continuity_phase,
        orchestrator_phase=orchestrator_phase,
        continuity_mtime=continuity_mtime,
        activity_log_latest=activity_log_latest,
    )
