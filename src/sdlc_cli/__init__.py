"""autonomous-sdlc CLI — Bootstrap multi-agent SDLC workflows into any repo."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .banner import print_banner
from .integrations import list_integrations
from .scaffold import scaffold
from .version import __version__

app = typer.Typer(
    name="sdlc",
    help="Bootstrap multi-agent SDLC workflows into any repository.",
    add_completion=False,
    no_args_is_help=True,
)

console = Console()


@app.command()
def init(
    target: str | None = typer.Argument(None, help="Target directory (default: current)"),
    here: bool = typer.Option(False, "--here", help="Initialize in the current directory"),
    integration: str | None = typer.Option(
        None,
        "--integration", "-i",
        help="AI IDE integration (e.g. copilot, windsurf, cursor-agent, claude)",
    ),
    project_name: str | None = typer.Option(
        None,
        "--project-name", "--name",
        help="Project name (replaces template placeholders)",
    ),
    tech_stack: str | None = typer.Option(
        None,
        "--tech-stack",
        help="Tech stack context for agent prompts",
    ),
    team_size: str | None = typer.Option(
        None,
        "--team-size",
        help="Team size context",
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
    non_interactive: bool = typer.Option(
        False, "--non-interactive", "--yes", "-y",
        help="Skip prompts, use defaults for missing values",
    ),
) -> None:
    """Initialize autonomous-sdlc agent workflows in a repository."""
    print_banner(console)

    # Determine target directory
    if here or target is None:
        target_dir = Path.cwd()
    else:
        target_dir = Path(target).resolve()

    # Warn if target is not empty
    if target_dir.exists() and any(target_dir.iterdir()):
        count = sum(1 for _ in target_dir.iterdir())
        console.print(
            f"[yellow]Warning:[/] Target directory has {count} existing items"
        )
        console.print(
            "Framework files will be merged with existing content"
        )
        if not non_interactive:
            if not typer.confirm("Continue?"):
                console.print("[dim]Cancelled.[/]")
                raise typer.Exit(0)

    # Interactive integration selection if not provided
    if integration is None and not non_interactive:
        try:
            from .selector import select_integration

            choices = list_integrations()
            integration = select_integration(choices, console=console)
            if integration is None:
                console.print("[dim]Cancelled.[/]")
                raise typer.Exit(0)
        except (ImportError, Exception):
            # Fallback to simple prompt if readchar not available
            integration = _fallback_integration_prompt()
    elif integration is None:
        integration = "copilot"

    # Interactive prompts for missing values
    if not non_interactive:
        if project_name is None:
            project_name = typer.prompt(
                "Project name",
                default=target_dir.name,
            )
        if tech_stack is None:
            tech_stack = typer.prompt(
                "Tech stack (optional, press Enter to skip)",
                default="",
            )
        if team_size is None:
            team_size = typer.prompt(
                "Team size (optional, press Enter to skip)",
                default="",
            )

    # Apply defaults for non-interactive mode
    project_name = project_name or target_dir.name
    tech_stack = tech_stack or ""
    team_size = team_size or ""

    # Run scaffold
    console.print()
    with console.status("[bold cyan]Scaffolding autonomous-sdlc...[/]"):
        result = scaffold(
            target_dir,
            integration=integration,
            project_name=project_name,
            tech_stack=tech_stack,
            team_size=team_size,
            force=force,
        )

    # Report results
    console.print()
    console.print("[bold green]autonomous-sdlc initialized successfully![/]\n")

    table = Table(title="Files Created", show_lines=False)
    table.add_column("File", style="cyan")
    for f in sorted(result["files_created"]):
        table.add_row(f)
    console.print(table)

    console.print(f"\n[bold]Integration:[/] {integration}")
    console.print(f"[bold]Project:[/] {project_name}")

    console.print("\n[dim]Next steps:[/]")
    console.print("  1. Add your spec: [cyan].sdlc-framework/run.sh start ./your-prd.md[/]")
    console.print("  2. Open your AI IDE and start a new conversation")
    console.print("  3. The orchestrator activates automatically via [cyan]/sdlc.orchestrator[/]")
    console.print("  4. Check status: [cyan].sdlc-framework/run.sh status[/]")
    console.print()


@app.command()
def version() -> None:
    """Show the autonomous-sdlc version."""
    console.print(f"autonomous-sdlc {__version__}")


def _fallback_integration_prompt() -> str:
    """Simple text-based integration prompt when readchar is not available."""
    choices = list_integrations()
    console.print("\n[bold]Choose your AI IDE:[/]\n")
    for i, (key, name) in enumerate(choices, 1):
        console.print(f"  {i}. {key} ({name})")
    console.print()
    while True:
        raw = typer.prompt("Enter number or name", default="1")
        # Try as number
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(choices):
                return choices[idx][0]
        except ValueError:
            pass
        # Try as name
        for key, _ in choices:
            if raw.lower() == key.lower():
                return key
        console.print("[red]Invalid choice. Try again.[/]")


def main() -> None:
    """Entry point for the CLI."""
    app()
