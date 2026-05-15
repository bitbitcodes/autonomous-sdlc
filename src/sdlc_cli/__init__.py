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
    console.print("  1. Add your spec: [cyan].sdlc/framework/run.sh start ./your-prd.md[/]")
    console.print("  2. Open your AI IDE and start a new conversation")
    console.print("  3. The orchestrator activates automatically via [cyan]/sdlc.orchestrator[/]")
    console.print("  4. Check status: [cyan]sdlc status[/]")
    console.print()


@app.command()
def status(
    target: str | None = typer.Argument(None, help="Project directory (default: current)"),
) -> None:
    """Show the current SDLC workflow status — phases, agents, and progress."""
    import json as _json

    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found. Run [cyan]sdlc init[/] first.")
        raise typer.Exit(1)

    print_banner(console)

    # ── STATUS.md dashboard ──
    status_file = sdlc_dir / "STATUS.md"
    if status_file.exists():
        from rich.markdown import Markdown

        console.print(Markdown(status_file.read_text()))
        console.print()

    # ── orchestrator.json ──
    orch_file = sdlc_dir / "state" / "orchestrator.json"
    if orch_file.exists():
        state = _json.loads(orch_file.read_text())

        phase_names = {
            "0-bootstrap": "Bootstrap", "1-product": "Product",
            "2-story-tasks": "Story-Tasks", "3-architecture": "Architecture",
            "4-design": "Design", "5-development": "Development",
            "6-testing": "Testing", "7-security": "Security",
            "8-review": "Review", "9-devops": "DevOps",
            "10-observability": "Observability",
        }
        agent_map = {
            "0-bootstrap": "orch-sdlc",
            "1-product": "stage-product (4 sub)",
            "2-story-tasks": "stage-story-tasks (3 sub)",
            "3-architecture": "stage-architecture (3 sub)",
            "4-design": "stage-design (4 sub)",
            "5-development": "stage-development (4 sub)",
            "6-testing": "stage-testing (4 sub)",
            "7-security": "stage-security (4 sub)",
            "8-review": "stage-review (3 sub)",
            "9-devops": "stage-devops",
            "10-observability": "stage-observability",
        }
        status_icons = {
            "complete": "[green]✅ complete[/]",
            "in_progress": "[yellow]🔄 active[/]",
            "pending": "[dim]⬜ pending[/]",
            "failed": "[red]❌ failed[/]",
        }

        # Summary
        console.print("[bold]Current State[/]")
        summary = Table(show_header=False, box=None, padding=(0, 2))
        summary.add_column(style="bold")
        summary.add_column()
        summary.add_row("Status", str(state.get("status", "unknown")))
        summary.add_row("Complexity", str(state.get("complexity") or "—"))
        summary.add_row("Phase", str(state.get("current_phase", 0)))
        summary.add_row(
            "Tasks",
            f"{state.get('completed_tasks', 0)} / {state.get('total_tasks', 0)} complete",
        )
        console.print(summary)
        console.print()

        # Phase table
        phase_table = Table(title="Phase Progress", show_lines=True)
        phase_table.add_column("#", justify="center", width=3)
        phase_table.add_column("Phase", min_width=14)
        phase_table.add_column("Agent", min_width=20)
        phase_table.add_column("Status", min_width=14)
        phase_table.add_column("Gate", justify="center", width=6)

        phases = state.get("phases", {})
        for key in sorted(phases.keys(), key=lambda k: int(k.split("-")[0])):
            phase = phases[key]
            num = key.split("-")[0]
            name = phase_names.get(key, key)
            agent = agent_map.get(key, "")
            st = status_icons.get(phase.get("status", "pending"), phase.get("status", ""))
            gate = phase.get("gate") or "—"
            phase_table.add_row(num, name, agent, st, gate)

        console.print(phase_table)
        console.print()

    # ── Queue ──
    queue_dir = sdlc_dir / "queue"
    if queue_dir.is_dir():
        counts = {}
        for name in ("pending", "active", "completed"):
            f = queue_dir / f"{name}.json"
            if f.exists():
                try:
                    counts[name] = len(_json.loads(f.read_text()))
                except Exception:
                    counts[name] = "?"
            else:
                counts[name] = 0
        console.print(
            f"[bold]Queue:[/]  Pending: {counts.get('pending', 0)}  |  "
            f"Active: {counts.get('active', 0)}  |  "
            f"Completed: {counts.get('completed', 0)}"
        )
        console.print()

    # ── Activity log (last 15 lines) ──
    log_file = sdlc_dir / "state" / "activity-log.md"
    if log_file.exists():
        lines = log_file.read_text().strip().splitlines()
        if len(lines) > 5:
            console.print("[bold]Activity Log (recent):[/]")
            for line in lines[-15:]:
                console.print(f"  {line}")
        else:
            console.print("[dim]Activity Log: No agent actions recorded yet.[/]")
        console.print()

    # ── CONTINUITY.md summary ──
    cont_file = sdlc_dir / "CONTINUITY.md"
    if cont_file.exists():
        lines = cont_file.read_text().strip().splitlines()
        console.print("[bold]Working Memory (CONTINUITY.md):[/]")
        for line in lines[:15]:
            console.print(f"  {line}")
        console.print()


@app.command()
def trace(
    target: str | None = typer.Argument(None, help="Project directory (default: current)"),
    phase: int | None = typer.Option(None, "--phase", "-p", help="Filter to a specific phase number"),
    verify: bool = typer.Option(False, "--verify", "-v", help="Cross-check traced artifacts against files on disk"),
) -> None:
    """Show the agent interaction map — which agent did what, dispatched whom, and artifact flow."""
    import json as _json

    from rich.tree import Tree

    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found. Run [cyan]sdlc init[/] first.")
        raise typer.Exit(1)

    trace_file = sdlc_dir / "state" / "agent-trace.json"
    if not trace_file.exists():
        console.print("[red]Error:[/] No trace file found. Run the orchestrator first.")
        raise typer.Exit(1)

    try:
        data = _json.loads(trace_file.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        console.print(f"[red]Error reading trace file:[/] {exc}")
        raise typer.Exit(1)

    traces = data.get("traces", [])
    if not traces:
        console.print("[dim]No agent interactions recorded yet.[/]")
        console.print("Run the orchestrator to generate trace data.")
        raise typer.Exit(0)

    print_banner(console)

    status_icons = {
        "complete": "[green]✅[/]",
        "in_progress": "[yellow]🔄[/]",
        "pending": "[dim]⬜[/]",
        "failed": "[red]❌[/]",
        "skipped": "[dim]⏭️[/]",
    }

    # Group traces by phase
    by_phase: dict[int, list[dict]] = {}
    for t in traces:
        p = t.get("phase", 0)
        by_phase.setdefault(p, [])
        by_phase[p].append(t)

    # Artifact verification counters
    verified_count = 0
    missing_count = 0
    missing_list: list[str] = []

    tree = Tree("[bold cyan]Agent Interaction Map[/]")

    for phase_num in sorted(by_phase.keys()):
        if phase is not None and phase_num != phase:
            continue

        entries = by_phase[phase_num]

        # Find the stage-level or orchestrator entry
        stage_entry = next(
            (e for e in entries if e.get("role") in ("orchestrator", "stage")),
            entries[0],
        )
        icon = status_icons.get(stage_entry.get("status", "pending"), "❓")
        phase_name = stage_entry.get("phase_name", "?").title()
        phase_branch = tree.add(
            f"[bold]Phase {phase_num}: {phase_name}[/] {icon}"
        )

        # Stage agent node
        agent_node = phase_branch.add(f"[cyan]{stage_entry['agent']}[/]")

        # Show stage action
        action = stage_entry.get("action", "")
        if action:
            agent_node.add(f"[dim]{action}[/]")

        # Show stage-level inputs
        for inp in stage_entry.get("input_artifacts", []):
            inp_name = Path(inp).name
            if verify:
                exists = (target_dir / inp).is_file()
                mark = "[green]✅[/]" if exists else "[red]⚠️  MISSING[/]"
                agent_node.add(f"[dim]In:[/]  {inp_name} {mark}")
            else:
                agent_node.add(f"[dim]In:[/]  {inp_name}")

        # Subagent entries
        subs = [e for e in entries if e.get("role") == "subagent"]
        for sub in subs:
            sub_icon = status_icons.get(sub.get("status", "pending"), "❓")
            sub_node = agent_node.add(f"[magenta]{sub['agent']}[/] {sub_icon}")

            sub_action = sub.get("action", "")
            if sub_action:
                sub_node.add(f"[dim]{sub_action}[/]")

            for inp in sub.get("input_artifacts", []):
                inp_name = Path(inp).name
                if verify:
                    exists = (target_dir / inp).is_file()
                    mark = "[green]✅[/]" if exists else "[red]⚠️  MISSING[/]"
                    sub_node.add(f"[dim]In:[/]  {inp_name} {mark}")
                else:
                    sub_node.add(f"[dim]In:[/]  {inp_name}")

            for out in sub.get("output_artifacts", []):
                out_name = Path(out).name
                if verify:
                    exists = (target_dir / out).is_file()
                    if exists:
                        verified_count += 1
                        mark = "[green]✅[/]"
                    else:
                        missing_count += 1
                        missing_list.append(out)
                        mark = "[red]⚠️  MISSING[/]"
                    sub_node.add(f"[bold]Out:[/] {out_name} {mark}")
                else:
                    sub_node.add(f"[bold]Out:[/] {out_name}")

        # Stage-level outputs (if no subs, or stage has its own outputs)
        if not subs:
            for out in stage_entry.get("output_artifacts", []):
                out_name = Path(out).name
                if verify:
                    exists = (target_dir / out).is_file()
                    if exists:
                        verified_count += 1
                        mark = "[green]✅[/]"
                    else:
                        missing_count += 1
                        missing_list.append(out)
                        mark = "[red]⚠️  MISSING[/]"
                    agent_node.add(f"[bold]Out:[/] {out_name} {mark}")
                else:
                    agent_node.add(f"[bold]Out:[/] {out_name}")

        # Gate info
        gate = stage_entry.get("gate")
        if gate:
            gate_str = gate.upper()
            gate_style = "[green]" if gate_str == "PASS" else "[red]"
            phase_branch.add(f"Gate: {gate_style}{gate_str}[/]")

    console.print(tree)
    console.print()

    # Verification summary
    if verify:
        console.print("[bold]─── Artifact Verification ───[/]")
        console.print(f"[green]✅ {verified_count}[/] artifacts traced and verified on disk")
        if missing_count:
            console.print(f"[red]⚠️  {missing_count}[/] artifacts traced but MISSING on disk:")
            for m in missing_list:
                console.print(f"   [red]{m}[/]")
        else:
            console.print("[green]✅ 0[/] artifacts traced but missing on disk")
        console.print()


@app.command()
def dashboard(
    target: str | None = typer.Argument(None, help="Project directory (default: current)"),
    port: int = typer.Option(8420, "--port", "-p", help="HTTP server port (WebSocket = port+1)"),
) -> None:
    """Launch a real-time web dashboard for the SDLC workflow."""
    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found. Run [cyan]sdlc init[/] first.")
        raise typer.Exit(1)

    try:
        import websockets  # noqa: F401
    except ImportError:
        console.print(
            "[red]Error:[/] The [cyan]websockets[/] package is required for the dashboard.\n"
            "Install it with: [cyan]pip install autonomous-sdlc\\[dashboard][/]\n"
            "  or: [cyan]pip install websockets[/]"
        )
        raise typer.Exit(1)

    from .dashboard import serve

    console.print(f"[bold cyan]SDLC Dashboard[/] starting on [link=http://127.0.0.1:{port}]http://127.0.0.1:{port}[/link]")
    console.print(f"WebSocket on port {port + 1}")
    console.print("[dim]Press Ctrl+C to stop.[/]\n")

    serve(sdlc_dir, port=port)


@app.command()
def models(
    target: str | None = typer.Argument(None, help="Project directory (default: current)"),
    edit: bool = typer.Option(False, "--edit", "-e", help="Open model-config.json in $EDITOR"),
    reset: bool = typer.Option(False, "--reset", help="Reset model config to defaults"),
) -> None:
    """Show or manage per-agent model routing configuration."""
    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found. Run [cyan]sdlc init[/] first.")
        raise typer.Exit(1)

    from .models import (
        TIER_DESCRIPTIONS,
        default_config,
        load_config,
        resolve_all,
        write_config,
    )

    # ── Reset ──
    if reset:
        write_config(sdlc_dir)
        console.print("[green]✅ Model config reset to defaults.[/]")
        console.print(f"[dim]  → {sdlc_dir / 'model-config.json'}[/]")
        return

    # ── Edit ──
    if edit:
        import os
        import subprocess

        config_path = sdlc_dir / "model-config.json"
        if not config_path.exists():
            write_config(sdlc_dir)
        editor = os.environ.get("EDITOR", "vi")
        subprocess.run([editor, str(config_path)])
        return

    # ── Display ──
    config = load_config(sdlc_dir)
    if config is None:
        console.print("[yellow]No model-config.json found.[/] Creating defaults...")
        config = default_config()
        write_config(sdlc_dir, config)

    print_banner()

    tiers = config.get("tiers", {})
    overrides = config.get("overrides", {})

    # Tier summary
    tier_table = Table(title="Model Tiers", show_lines=True)
    tier_table.add_column("Tier", style="bold cyan", min_width=12)
    tier_table.add_column("Model", min_width=20)
    tier_table.add_column("Purpose", min_width=40)
    for tier_name, model in tiers.items():
        desc = TIER_DESCRIPTIONS.get(tier_name, "")
        tier_table.add_row(tier_name, model, desc)
    console.print(tier_table)
    console.print()

    # Agent assignments
    resolved = resolve_all(config)
    agent_table = Table(title="Agent → Model Assignments", show_lines=True)
    agent_table.add_column("Agent", style="bold", min_width=22)
    agent_table.add_column("Tier", min_width=10)
    agent_table.add_column("Model", min_width=20)

    tier_colors = {"reasoning": "cyan", "coding": "green", "fast": "yellow", "override": "magenta"}

    for agent_id in sorted(resolved.keys()):
        info = resolved[agent_id]
        tier = info["tier"]
        model = info["model"]
        color = tier_colors.get(tier, "white")
        is_override = agent_id in overrides
        tier_display = f"[{color}]{tier}[/{color}]"
        model_display = f"[bold]{model}[/bold]" if is_override else model
        agent_table.add_row(agent_id, tier_display, model_display)

    console.print(agent_table)

    if overrides:
        console.print(f"\n[dim]({len(overrides)} override(s) active)[/]")
    console.print(f"\n[dim]Config: {sdlc_dir / 'model-config.json'}[/]")
    console.print("[dim]Edit with: sdlc models --edit  |  Reset with: sdlc models --reset[/]")


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
