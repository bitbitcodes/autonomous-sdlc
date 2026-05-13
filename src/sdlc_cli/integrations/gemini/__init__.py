"""Gemini CLI integration for autonomous-sdlc."""

from .. import register
from ..base import MarkdownIntegration


@register
class GeminiIntegration(MarkdownIntegration):
    key = "gemini"
    display_name = "Gemini CLI"
    config = {
        "name": "Gemini CLI",
        "folder": ".gemini",
        "commands_subdir": "commands",
    }
    context_file = ".gemini/GEMINI.md"

    def command_filename(self, template_name: str) -> str:
        return f"sdlc-{template_name}.md"

    def _context_template_name(self) -> str:
        return "gemini-instructions.md"
