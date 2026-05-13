"""opencode integration for autonomous-sdlc."""

from .. import register
from ..base import MarkdownIntegration


@register
class OpencodeIntegration(MarkdownIntegration):
    key = "opencode"
    display_name = "opencode"
    config = {
        "name": "opencode",
        "folder": ".opencode",
        "commands_subdir": "commands",
    }
    context_file = ".opencode/instructions.md"

    def command_filename(self, template_name: str) -> str:
        return f"sdlc-{template_name}.md"

    def _context_template_name(self) -> str:
        return "opencode-instructions.md"
