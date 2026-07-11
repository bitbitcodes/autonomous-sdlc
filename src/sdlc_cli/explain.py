"""Decision explainability for autonomous-sdlc.

Reads .sdlc/governance/decision-log.json to answer "why was this decision
made?" — alternatives considered, rationale, approver, and impact.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_decisions(sdlc_dir: Path) -> list[dict[str, Any]]:
    path = sdlc_dir / "governance" / "decision-log.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data.get("decisions", [])


def find_decision(sdlc_dir: Path, decision_id: str) -> dict[str, Any] | None:
    for d in load_decisions(sdlc_dir):
        if d.get("id") == decision_id:
            return d
    return None
