"""Multi-run management for autonomous-sdlc.

Supports running multiple SDLC workflows in the same repo, each with
its own isolated runtime state under .sdlc/runs/<auto-slug>/.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STOPWORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "for", "with", "to", "of", "and", "in", "on", "by", "from", "using",
    "via", "as", "at", "or", "not", "but", "if", "it", "its", "this",
    "that", "we", "our", "you", "your", "i", "my", "me", "do", "does",
    "did", "will", "shall", "should", "would", "could", "can", "may",
    "must", "have", "has", "had", "about", "into", "through", "during",
    "before", "after", "above", "below", "between", "each", "every",
    "all", "any", "both", "few", "more", "most", "other", "some", "such",
    "no", "nor", "only", "own", "same", "so", "than", "too", "very",
    "just", "also", "then", "now", "here", "there", "when", "where",
    "how", "what", "which", "who", "whom", "why", "add", "create",
    "build", "implement", "make", "use", "need", "want",
})

ACTIVE_RUN_FILE = "active-run.json"
RUN_INFO_FILE = "run-info.json"


# ---------------------------------------------------------------------------
# Slug generation
# ---------------------------------------------------------------------------


def generate_run_slug(
    spec_text: str,
    existing_slugs: list[str] | None = None,
    max_words: int = 4,
) -> str:
    """Generate a 3-4 word descriptive slug from spec content.

    Examples:
        "User Authentication with JWT Tokens"  → "user-auth-jwt-tokens"
        "Stripe Payment Webhook Integration"    → "stripe-payment-webhook-integration"
    """
    title = ""
    for line in spec_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip()
            break
        if stripped:
            title = stripped
            break

    # Tokenize and filter
    words = re.findall(r"[a-zA-Z0-9]+", title.lower())
    keywords = [w for w in words if w not in STOPWORDS and len(w) > 1][:max_words]

    slug = "-".join(keywords) if keywords else "unnamed-run"

    # Deduplicate
    if existing_slugs:
        base = slug
        counter = 2
        while slug in existing_slugs:
            slug = f"{base}-{counter}"
            counter += 1

    return slug


# ---------------------------------------------------------------------------
# Run directory resolution
# ---------------------------------------------------------------------------


def resolve_run_dir(sdlc_dir: Path, run_name: str | None = None) -> Path:
    """Resolve the runtime directory for a specific or active run.

    Resolution order:
    1. Explicit run_name → .sdlc/runs/<run_name>
    2. active-run.json  → .sdlc/runs/<active>
    3. Legacy fallback  → .sdlc/ root (single-run mode)
    """
    if run_name:
        run_path = sdlc_dir / "runs" / run_name
        return run_path

    active_file = sdlc_dir / ACTIVE_RUN_FILE
    if active_file.exists():
        try:
            data = json.loads(active_file.read_text(encoding="utf-8"))
            name = data.get("active")
            if name:
                run_path = sdlc_dir / "runs" / name
                if run_path.is_dir():
                    return run_path
        except (json.JSONDecodeError, OSError):
            pass

    # Legacy: state at .sdlc/ root
    return sdlc_dir


# ---------------------------------------------------------------------------
# Run management helpers
# ---------------------------------------------------------------------------


def list_runs(sdlc_dir: Path) -> list[dict[str, Any]]:
    """List all runs with metadata."""
    runs_dir = sdlc_dir / "runs"
    if not runs_dir.is_dir():
        return []

    active = get_active_run(sdlc_dir)
    results = []

    for run_path in sorted(runs_dir.iterdir()):
        if not run_path.is_dir():
            continue
        slug = run_path.name

        # Read run-info.json
        info: dict[str, Any] = {"slug": slug, "active": slug == active}
        info_file = run_path / RUN_INFO_FILE
        if info_file.exists():
            try:
                info.update(json.loads(info_file.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                pass

        # Read orchestrator state for status/phase
        orch_file = run_path / "state" / "orchestrator.json"
        if orch_file.exists():
            try:
                orch = json.loads(orch_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                try:
                    orch, _ = json.JSONDecoder().raw_decode(
                        orch_file.read_text(encoding="utf-8")
                    )
                except (json.JSONDecodeError, OSError):
                    orch = {}
            info["status"] = orch.get("status", "unknown")
            info["current_phase"] = orch.get("current_phase", 0)
            info["last_updated"] = orch.get("last_updated", "")
        else:
            info["status"] = "initialized"

        results.append(info)

    return results


def get_active_run(sdlc_dir: Path) -> str | None:
    """Return the currently active run slug, or None."""
    active_file = sdlc_dir / ACTIVE_RUN_FILE
    if not active_file.exists():
        return None
    try:
        data = json.loads(active_file.read_text(encoding="utf-8"))
        return data.get("active")
    except (json.JSONDecodeError, OSError):
        return None


def set_active_run(sdlc_dir: Path, slug: str) -> None:
    """Set the active run in active-run.json."""
    active_file = sdlc_dir / ACTIVE_RUN_FILE
    data = {"active": slug, "updated": datetime.now(timezone.utc).isoformat()}
    active_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def write_run_info(
    run_dir: Path,
    slug: str,
    title: str,
    spec_file: str | None = None,
) -> None:
    """Write run-info.json inside a run directory."""
    info = {
        "slug": slug,
        "title": title,
        "spec_file": spec_file,
        "created": datetime.now(timezone.utc).isoformat(),
    }
    (run_dir / RUN_INFO_FILE).write_text(
        json.dumps(info, indent=2) + "\n", encoding="utf-8"
    )
