"""Windsurf integration for autonomous-sdlc."""

from .. import register
from ..base import MarkdownIntegration


@register
class WindsurfIntegration(MarkdownIntegration):
    key = "windsurf"
    display_name = "Windsurf"
    config = {
        "name": "Windsurf",
        "folder": ".windsurf",
        "commands_subdir": "workflows",
    }
    context_file = ".windsurf/rules/sdlc.md"

    def _context_template_name(self) -> str:
        return "windsurf-rules.md"
