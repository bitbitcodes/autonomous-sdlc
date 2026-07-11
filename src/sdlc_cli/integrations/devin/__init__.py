"""Devin Desktop integration for autonomous-sdlc.

Devin Desktop is Cognition's rebrand of Windsurf (announced June 2, 2026).
Legacy ``.windsurf/`` config is still read by the app, but ``.devin/``
takes precedence per Cognition's FAQ, so that's what we scaffold now.

``--integration windsurf`` is kept as a backward-compatible alias — it
resolves to this same integration and still scaffolds into ``.devin/``.
"""

from .. import INTEGRATION_REGISTRY, register
from ..base import MarkdownIntegration


@register
class DevinDesktopIntegration(MarkdownIntegration):
    key = "devin"
    display_name = "Devin Desktop"
    config = {
        "name": "Devin Desktop",
        "folder": ".devin",
        "commands_subdir": "workflows",
    }
    context_file = ".devin/rules/sdlc.md"

    def _context_template_name(self) -> str:
        return "windsurf-rules.md"


# Backward-compatible alias for the pre-rebrand key. `sdlc init --integration
# windsurf` continues to work and scaffolds the same `.devin/` files.
INTEGRATION_REGISTRY["windsurf"] = DevinDesktopIntegration
