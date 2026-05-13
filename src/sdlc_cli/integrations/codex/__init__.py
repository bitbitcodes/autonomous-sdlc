"""Codex CLI integration for autonomous-sdlc."""

from .. import register
from ..base import MarkdownIntegration


@register
class CodexIntegration(MarkdownIntegration):
    key = "codex"
    display_name = "Codex CLI"
    config = {
        "name": "Codex CLI",
        "folder": ".codex",
        "commands_subdir": "commands",
    }
    context_file = ".codex/instructions.md"

    def command_filename(self, template_name: str) -> str:
        return f"sdlc-{template_name}.md"

    def _context_template_name(self) -> str:
        return "generic-instructions.md"
