"""Token/cost tracking and reporting for autonomous-sdlc.

Reads .sdlc/state/token-usage.json (per-run) and renders a cost report:
tokens used, cost breakdown, retry stats, and a rough ROI note.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

TOKEN_USAGE_FILENAME = "token-usage.json"


def default_usage() -> dict[str, Any]:
    """Return an empty token-usage.json structure."""
    return {
        "total_tokens": 0,
        "total_cost_usd": 0.0,
        "budget_limit_usd": 100.0,
        "breakdown": {
            "base_execution": 0,
            "retry_overhead": 0,
            "gate_failure_overhead": 0,
            "conversation_overhead": 0,
            "review_overhead": 0,
        },
        "retry_stats": {
            "total_retries": 0,
            "tasks_failed_first_attempt": 0,
            "average_retries_per_task": 0.0,
        },
        "gate_stats": {
            "gates_passed_first_attempt": 0,
            "gates_failed": 0,
            "average_retries_per_gate": 0.0,
        },
        "by_phase": {},
        "by_agent": {},
    }


def load_usage(run_dir: Path) -> dict[str, Any]:
    """Load token-usage.json from a run directory. Returns defaults if missing."""
    path = run_dir / "state" / TOKEN_USAGE_FILENAME
    if not path.exists():
        return default_usage()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default_usage()


def load_budget_limit(sdlc_dir: Path) -> float | None:
    """Read total_limit_usd from .sdlc/governance/budget-policy.yaml, if present."""
    path = sdlc_dir / "governance" / "budget-policy.yaml"
    if not path.exists():
        return None
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return data.get("budget", {}).get("total_limit_usd")
    except Exception:
        # No PyYAML dependency available — do a minimal regex fallback.
        import re

        text = path.read_text(encoding="utf-8")
        match = re.search(r"total_limit_usd:\s*([0-9.]+)", text)
        return float(match.group(1)) if match else None


def build_report(usage: dict[str, Any], budget_limit: float | None = None) -> dict[str, Any]:
    """Compute a display-ready report dict from raw usage data."""
    total_cost = usage.get("total_cost_usd", 0.0)
    limit = budget_limit if budget_limit is not None else usage.get("budget_limit_usd", 100.0)
    pct = (total_cost / limit * 100) if limit else 0.0

    breakdown = usage.get("breakdown", {})
    total_tokens = usage.get("total_tokens", 0) or sum(breakdown.values()) or 1

    breakdown_pct = {
        k: (v / total_tokens * 100 if total_tokens else 0.0) for k, v in breakdown.items()
    }

    return {
        "total_tokens": usage.get("total_tokens", 0),
        "total_cost_usd": total_cost,
        "budget_limit_usd": limit,
        "budget_pct_used": pct,
        "breakdown": breakdown,
        "breakdown_pct": breakdown_pct,
        "retry_stats": usage.get("retry_stats", {}),
        "gate_stats": usage.get("gate_stats", {}),
        "by_phase": usage.get("by_phase", {}),
        "by_agent": usage.get("by_agent", {}),
    }
