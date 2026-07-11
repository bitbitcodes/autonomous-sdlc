"""Base classes for autonomous-sdlc AI IDE integrations.

Provides:
- ``IntegrationBase`` — abstract base every integration must implement.
- ``MarkdownIntegration`` — concrete base for Markdown-format integrations.
"""

from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class IntegrationBase(ABC):
    """Abstract base class every integration must implement.

    Subclasses must set:
    - ``key`` — unique identifier (e.g. "copilot", "devin")
    - ``display_name`` — human-readable name (e.g. "GitHub Copilot")
    - ``config`` — metadata dict with "name", "folder", "commands_subdir"
    """

    key: str = ""
    display_name: str = ""
    config: dict[str, Any] = {}

    context_file: str | None = None
    """Relative path to the agent context/instructions file."""

    # -- Template discovery ---------------------------------------------------

    @classmethod
    def shared_commands_dir(cls) -> Path | None:
        """Return path to the shared command templates directory."""
        pkg_dir = Path(inspect.getfile(IntegrationBase)).resolve().parent.parent
        for candidate in [
            pkg_dir / "core_pack" / "commands",
            pkg_dir.parent.parent / "templates" / "commands",
        ]:
            if candidate.is_dir():
                return candidate
        return None

    @classmethod
    def shared_templates_dir(cls) -> Path | None:
        """Return path to the shared templates directory."""
        pkg_dir = Path(inspect.getfile(IntegrationBase)).resolve().parent.parent
        for candidate in [
            pkg_dir / "core_pack" / "templates",
            pkg_dir.parent.parent / "templates",
        ]:
            if candidate.is_dir():
                return candidate
        return None

    @classmethod
    def shared_agents_dir(cls) -> Path | None:
        """Return path to the shared agents directory."""
        pkg_dir = Path(inspect.getfile(IntegrationBase)).resolve().parent.parent
        for candidate in [
            pkg_dir / "core_pack" / "agents",
            pkg_dir.parent.parent / "agents",
        ]:
            if candidate.is_dir():
                return candidate
        return None

    @classmethod
    def shared_references_dir(cls) -> Path | None:
        """Return path to the shared references directory."""
        pkg_dir = Path(inspect.getfile(IntegrationBase)).resolve().parent.parent
        for candidate in [
            pkg_dir / "core_pack" / "references",
            pkg_dir.parent.parent / "references",
        ]:
            if candidate.is_dir():
                return candidate
        return None

    @classmethod
    def shared_skills_dir(cls) -> Path | None:
        """Return path to the shared skills directory."""
        pkg_dir = Path(inspect.getfile(IntegrationBase)).resolve().parent.parent
        for candidate in [
            pkg_dir / "core_pack" / "skills",
            pkg_dir.parent.parent / "skills",
        ]:
            if candidate.is_dir():
                return candidate
        return None

    @classmethod
    def shared_examples_dir(cls) -> Path | None:
        """Return path to the shared examples directory."""
        pkg_dir = Path(inspect.getfile(IntegrationBase)).resolve().parent.parent
        for candidate in [
            pkg_dir / "core_pack" / "examples",
            pkg_dir.parent.parent / "examples",
        ]:
            if candidate.is_dir():
                return candidate
        return None

    @classmethod
    def shared_runner_script(cls) -> Path | None:
        """Return path to the shared run.sh script."""
        pkg_dir = Path(inspect.getfile(IntegrationBase)).resolve().parent.parent
        for candidate in [
            pkg_dir / "core_pack" / "run.sh",
            pkg_dir.parent.parent / "run.sh",
        ]:
            if candidate.is_file():
                return candidate
        return None

    def list_command_templates(self) -> list[Path]:
        """Return sorted list of command template files."""
        cmd_dir = self.shared_commands_dir()
        if not cmd_dir or not cmd_dir.is_dir():
            return []
        return sorted(f for f in cmd_dir.iterdir() if f.is_file() and f.suffix == ".md")

    def command_filename(self, template_name: str) -> str:
        """Return the destination filename for a command template."""
        return f"sdlc.{template_name}.md"

    def commands_dest(self, project_root: Path) -> Path:
        """Return the absolute path to the commands output directory."""
        folder = self.config.get("folder", "")
        subdir = self.config.get("commands_subdir", "commands")
        return project_root / folder / subdir

    @abstractmethod
    def setup(self, project_root: Path, project_name: str = "") -> list[Path]:
        """Install this integration's files into the project.

        Returns a list of created file paths.
        """

    def teardown(self, project_root: Path) -> list[Path]:
        """Remove this integration's files from the project.

        Returns a list of removed file paths.
        """
        return []


class MarkdownIntegration(IntegrationBase):
    """Concrete base for standard Markdown-format integrations.

    Subclass, set ``key``, ``display_name``, ``config``, and optionally
    ``context_file``, and you're done.
    """

    def setup(self, project_root: Path, project_name: str = "") -> list[Path]:
        """Copy command templates to the integration's commands directory."""
        created: list[Path] = []
        templates = self.list_command_templates()
        dest_dir = self.commands_dest(project_root)
        dest_dir.mkdir(parents=True, exist_ok=True)

        for template in templates:
            filename = self.command_filename(template.stem)
            dst = dest_dir / filename
            content = template.read_text(encoding="utf-8")
            if project_name:
                content = content.replace("{{PROJECT_NAME}}", project_name)
            dst.write_text(content, encoding="utf-8")
            created.append(dst)

        # Install context file if defined
        ctx_path = self._install_context_file(project_root, project_name)
        if ctx_path:
            created.append(ctx_path)

        return created

    def _install_context_file(self, project_root: Path, project_name: str = "") -> Path | None:
        """Install the agent context/instructions file if defined."""
        if not self.context_file:
            return None

        templates_dir = self.shared_templates_dir()
        if not templates_dir:
            return None

        # Determine the template source filename
        ctx_template_name = self._context_template_name()
        src = templates_dir / ctx_template_name
        if not src.exists():
            return None

        dst = project_root / self.context_file
        dst.parent.mkdir(parents=True, exist_ok=True)
        content = src.read_text(encoding="utf-8")
        if project_name:
            content = content.replace("{{PROJECT_NAME}}", project_name)
        dst.write_text(content, encoding="utf-8")
        return dst

    def _context_template_name(self) -> str:
        """Return the template filename for the context file."""
        return f"{self.key}-instructions.md"
