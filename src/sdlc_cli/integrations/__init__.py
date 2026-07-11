"""Integration registry for autonomous-sdlc AI IDE integrations.

Each IDE integration is a self-contained subpackage that registers
itself into the INTEGRATION_REGISTRY dict.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import IntegrationBase

INTEGRATION_REGISTRY: dict[str, type[IntegrationBase]] = {}


def register(cls: type[IntegrationBase]) -> type[IntegrationBase]:
    """Class decorator that registers an integration into the global registry."""
    INTEGRATION_REGISTRY[cls.key] = cls
    return cls


def get_integration(key: str) -> type[IntegrationBase]:
    """Look up an integration by key. Raises KeyError if not found."""
    _register_builtins()
    if key not in INTEGRATION_REGISTRY:
        raise KeyError(
            f"Unknown integration {key!r}. "
            f"Available: {', '.join(sorted(INTEGRATION_REGISTRY))}"
        )
    return INTEGRATION_REGISTRY[key]


def list_integrations() -> list[tuple[str, str]]:
    """Return sorted list of (key, display_name) tuples for all registered integrations.

    Integrations may be registered under more than one dict key (e.g. legacy
    aliases like "windsurf" -> DevinDesktopIntegration). Each distinct
    integration class is only listed once, under its canonical ``key``.
    """
    _register_builtins()
    seen: set[type] = set()
    result: list[tuple[str, str]] = []
    for cls in INTEGRATION_REGISTRY.values():
        if cls in seen:
            continue
        seen.add(cls)
        result.append((cls.key, cls.display_name))
    return sorted(result)


_builtins_registered = False


def _register_builtins() -> None:
    """Import all built-in integration subpackages to trigger registration."""
    global _builtins_registered
    if _builtins_registered:
        return
    _builtins_registered = True

    from . import (  # noqa: F401
        amp,
        claude,
        codex,
        copilot,
        cursor,
        devin,
        gemini,
        kilocode,
        opencode,
    )
