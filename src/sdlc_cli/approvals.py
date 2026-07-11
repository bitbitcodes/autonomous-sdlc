"""Governance approval queue management for autonomous-sdlc.

Reads/writes .sdlc/governance/pending-approvals.json — approvals requested
by the orchestrator for HIGH/CRITICAL risk decisions (per risk-policy.yaml)
or budget/token overages.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PENDING_FILENAME = "pending-approvals.json"
DECISION_LOG_FILENAME = "decision-log.json"


def _gov_dir(sdlc_dir: Path) -> Path:
    d = sdlc_dir / "governance"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_pending(sdlc_dir: Path) -> list[dict[str, Any]]:
    path = _gov_dir(sdlc_dir) / PENDING_FILENAME
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data.get("approvals", [])


def _write_pending(sdlc_dir: Path, approvals: list[dict[str, Any]]) -> None:
    path = _gov_dir(sdlc_dir) / PENDING_FILENAME
    path.write_text(json.dumps({"approvals": approvals}, indent=2) + "\n", encoding="utf-8")


def next_approval_id(approvals: list[dict[str, Any]]) -> str:
    max_n = 0
    for a in approvals:
        aid = a.get("id", "")
        if aid.startswith("APPR-"):
            try:
                max_n = max(max_n, int(aid.split("-")[1]))
            except (IndexError, ValueError):
                pass
    return f"APPR-{max_n + 1:03d}"


def request_approval(
    sdlc_dir: Path,
    *,
    phase: str,
    agent: str,
    decision: str,
    risk_level: str,
    context: str = "",
) -> dict[str, Any]:
    """Create a new pending approval entry (called by agents/orchestrator)."""
    approvals = load_pending(sdlc_dir)
    entry = {
        "id": next_approval_id(approvals),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "phase": phase,
        "agent": agent,
        "decision": decision,
        "risk_level": risk_level,
        "context": context,
        "status": "pending",
    }
    approvals.append(entry)
    _write_pending(sdlc_dir, approvals)
    return entry


def resolve_approval(
    sdlc_dir: Path, approval_id: str, *, approve: bool, reason: str = ""
) -> dict[str, Any] | None:
    """Approve or reject a pending approval. Returns the updated entry, or None if not found."""
    approvals = load_pending(sdlc_dir)
    found = None
    for a in approvals:
        if a.get("id") == approval_id:
            a["status"] = "approved" if approve else "rejected"
            a["resolved_at"] = datetime.now(timezone.utc).isoformat()
            if reason:
                a["reason"] = reason
            found = a
            break
    if found is None:
        return None
    _write_pending(sdlc_dir, approvals)
    _append_decision_log(sdlc_dir, found)
    return found


def _append_decision_log(sdlc_dir: Path, approval: dict[str, Any]) -> None:
    path = _gov_dir(sdlc_dir) / DECISION_LOG_FILENAME
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {"decisions": []}
    else:
        data = {"decisions": []}

    decisions = data.get("decisions", [])
    next_n = 0
    for d in decisions:
        did = d.get("id", "")
        if did.startswith("DEC-"):
            try:
                next_n = max(next_n, int(did.split("-")[1]))
            except (IndexError, ValueError):
                pass

    decisions.append({
        "id": f"DEC-{next_n + 1:03d}",
        "timestamp": approval.get("resolved_at", datetime.now(timezone.utc).isoformat()),
        "phase": approval.get("phase"),
        "agent": approval.get("agent"),
        "decision": approval.get("decision"),
        "risk_assessment": approval.get("risk_level"),
        "approval_status": approval.get("status"),
        "approval_ref": approval.get("id"),
        "reason": approval.get("reason", ""),
    })
    data["decisions"] = decisions
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
