"""Configuration management for autonomous-sdlc."""

from __future__ import annotations

import json
from pathlib import Path

CONFIG_DIR = ".sdlc"
CONFIG_FILENAME = "init-options.json"


def get_defaults() -> dict:
    """Return default configuration values."""
    return {
        "integration": "copilot",
        "projectName": "",
        "techStack": "",
        "teamSize": "",
        "complexity": "auto",
    }


def create_config(target_dir: Path, user_config: dict) -> dict:
    """Write configuration to .sdlc/init-options.json."""
    defaults = get_defaults()
    merged = {**defaults, **user_config}

    # Remove internal-only options
    merged.pop("force", None)
    merged.pop("here", None)

    config_dir = target_dir / CONFIG_DIR
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / CONFIG_FILENAME
    config_path.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    return merged


def load_config(target_dir: Path) -> dict | None:
    """Load existing configuration from .sdlc/init-options.json."""
    config_path = target_dir / CONFIG_DIR / CONFIG_FILENAME
    if not config_path.exists():
        return None
    content = config_path.read_text(encoding="utf-8")
    return json.loads(content)
