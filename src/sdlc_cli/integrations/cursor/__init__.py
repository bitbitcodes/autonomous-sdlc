"""Cursor integration for autonomous-sdlc."""

from .. import register
from ..base import MarkdownIntegration


@register
class CursorIntegration(MarkdownIntegration):
    key = "cursor-agent"
    display_name = "Cursor"
    config = {
        "name": "Cursor",
        "folder": ".cursor",
        "commands_subdir": "rules",
    }
    context_file = ".cursor/rules/sdlc.mdc"

    def command_filename(self, template_name: str) -> str:
        return f"sdlc.{template_name}.mdc"

    def _context_template_name(self) -> str:
        return "cursor-rules.mdc"
