"""Cursor integration for autonomous-sdlc."""

from __future__ import annotations

from pathlib import Path

from .. import register
from ..base import MarkdownIntegration

# Stage agents that get per-stage .mdc files with model hints
_STAGE_AGENTS = [
    ("product", "stage-product"),
    ("story-tasks", "stage-story-tasks"),
    ("architecture", "stage-architecture"),
    ("design", "stage-design"),
    ("development", "stage-development"),
    ("testing", "stage-testing"),
    ("security", "stage-security"),
    ("review", "stage-review"),
    ("devops", "stage-devops"),
    ("observability", "stage-observability"),
]


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

    def setup(self, project_root: Path, project_name: str = "") -> list[Path]:
        """Install Cursor files, including per-stage model hint rules."""
        created = super().setup(project_root, project_name)
        created.extend(self._generate_model_rules(project_root))
        return created

    def _generate_model_rules(self, project_root: Path) -> list[Path]:
        """Generate per-stage .mdc files with model: frontmatter."""
        from ...models import load_config, resolve_model

        sdlc_dir = project_root / ".sdlc"
        config = load_config(sdlc_dir)
        if config is None:
            return []

        rules_dir = project_root / ".cursor" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)

        created: list[Path] = []
        for phase_name, agent_id in _STAGE_AGENTS:
            model = resolve_model(agent_id, config)
            content = (
                f"---\n"
                f"description: \"SDLC {phase_name.title()} phase — use {model}\"\n"
                f"globs:\n"
                f"  - \".sdlc/framework/agents/stage/{phase_name}.md\"\n"
                f"model: {model}\n"
                f"---\n"
                f"\n"
                f"When executing the **{phase_name.title()}** phase of the SDLC framework, "
                f"use the **{model}** model.\n"
                f"\n"
                f"Agent: `{agent_id}`\n"
                f"Prompt: `.sdlc/framework/agents/stage/{phase_name}.md`\n"
            )
            dst = rules_dir / f"sdlc.model.{phase_name}.mdc"
            dst.write_text(content, encoding="utf-8")
            created.append(dst)

        return created
