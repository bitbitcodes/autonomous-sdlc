"""Kilo Code integration for autonomous-sdlc."""

from .. import register
from ..base import MarkdownIntegration


@register
class KilocodeIntegration(MarkdownIntegration):
    key = "kilocode"
    display_name = "Kilo Code"
    config = {
        "name": "Kilo Code",
        "folder": ".kilocode",
        "commands_subdir": "commands",
    }
    context_file = ".kilocode/instructions.md"

    def command_filename(self, template_name: str) -> str:
        return f"sdlc-{template_name}.md"

    def _context_template_name(self) -> str:
        return "generic-instructions.md"
