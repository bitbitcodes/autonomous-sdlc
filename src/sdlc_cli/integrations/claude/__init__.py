"""Claude Code integration for autonomous-sdlc."""

from .. import register
from ..base import MarkdownIntegration


@register
class ClaudeIntegration(MarkdownIntegration):
    key = "claude"
    display_name = "Claude Code"
    config = {
        "name": "Claude Code",
        "folder": ".",
        "commands_subdir": ".claude/commands",
    }
    context_file = "CLAUDE.md"

    def command_filename(self, template_name: str) -> str:
        return f"sdlc-{template_name}.md"

    def _context_template_name(self) -> str:
        return "claude-instructions.md"
