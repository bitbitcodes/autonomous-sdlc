"""autonomous-sdlc CLI — Bootstrap multi-agent SDLC workflows into any repo."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .banner import print_banner
from .integrations import list_integrations
from .runs import resolve_run_dir
from .scaffold import scaffold
from .version import __version__

app = typer.Typer(
    name="sdlc",
    help="Bootstrap multi-agent SDLC workflows into any repository.",
    add_completion=False,
    no_args_is_help=True,
)

run_app = typer.Typer(help="Manage multiple SDLC runs (specs/use-cases).")
app.add_typer(run_app, name="run")

approvals_app = typer.Typer(help="Manage governance approval requests (risk-policy.yaml gates).")
app.add_typer(approvals_app, name="approvals")

agents_app = typer.Typer(help="Add custom stage agents/subagents when the built-in 52 don't cover a need.")
app.add_typer(agents_app, name="agents")

console = Console()


def _enabled_map_for(sdlc_dir: Path) -> dict[str, bool]:
    """Return {phase_key: enabled} from phase-config.json, for the Mermaid map.

    Disabled phases are hidden from the generated agent-map.md. Returns an
    empty map (all enabled) if anything goes wrong.
    """
    try:
        from .phases import (
            load_config as _load_phase_config,
            load_custom_agents as _load_custom_agents,
            phase_enabled_map as _phase_enabled_map,
        )

        return _phase_enabled_map(_load_phase_config(sdlc_dir), _load_custom_agents(sdlc_dir))
    except Exception:
        return {}


@app.command()
def init(
    target: str | None = typer.Argument(None, help="Target directory (default: current)"),
    here: bool = typer.Option(False, "--here", help="Initialize in the current directory"),
    integration: str | None = typer.Option(
        None,
        "--integration", "-i",
        help="AI IDE integration (e.g. copilot, devin, cursor-agent, claude)",
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
    run: str | None = typer.Option(None, "--run", "-r", help="Run name/slug (default: active run)"),
) -> None:
    """Show the current SDLC workflow status — phases, agents, and progress."""
    import json as _json

    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found. Run [cyan]sdlc init[/] first.")
        raise typer.Exit(1)

    run_dir = resolve_run_dir(sdlc_dir, run)

    print_banner(console)

    # ── STATUS.md dashboard ──
    status_file = sdlc_dir / "STATUS.md"
    if status_file.exists():
        from rich.markdown import Markdown

        console.print(Markdown(status_file.read_text()))
        console.print()

    # ── orchestrator.json ──
    orch_file = run_dir / "state" / "orchestrator.json"
    if orch_file.exists():
        try:
            state = _json.loads(orch_file.read_text())
        except _json.JSONDecodeError:
            # Handle files with trailing extra data (agent appended instead of overwrote)
            try:
                state, _ = _json.JSONDecoder().raw_decode(orch_file.read_text())
                console.print("[yellow]Warning:[/] orchestrator.json has extra data — using first valid object.\n")
            except _json.JSONDecodeError as exc:
                console.print(f"[red]Error parsing orchestrator.json:[/] {exc}")
                raise typer.Exit(1)

        # Derive phase names + agent labels from the single-source-of-truth
        # registry in phases.py so this display can never drift from the
        # actual pipeline.
        from .phases import agent_registry

        phase_names: dict[str, str] = {}
        agent_map: dict[str, str] = {}
        for _row in agent_registry():
            phase_names[_row["key"]] = _row["name"]
            n_sub = len(_row["subagents"])
            agent_map[_row["key"]] = (
                f"{_row['agent']} ({n_sub} sub)" if n_sub else _row["agent"]
            )
        status_icons = {
            "complete": "[green]✅ complete[/]",
            "in_progress": "[yellow]🔄 active[/]",
            "pending": "[dim]⬜ pending[/]",
            "failed": "[red]❌ failed[/]",
            "not_triggered": "[dim]⏸️  not triggered[/]",
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
        enabled_map = _enabled_map_for(sdlc_dir)
        hidden = 0
        for key in sorted(phases.keys(), key=lambda k: int(k.split("-")[0])):
            # Hide disabled phases (consistent with `sdlc phases`/dashboard).
            if enabled_map.get(key, True) is False:
                hidden += 1
                continue
            phase = phases[key]
            num = key.split("-")[0]
            name = phase_names.get(key, key)
            agent = agent_map.get(key, "")
            st = status_icons.get(phase.get("status", "pending"), phase.get("status", ""))
            gate = phase.get("gate") or "—"
            phase_table.add_row(num, name, agent, st, gate)

        console.print(phase_table)
        if hidden:
            console.print(
                f"[dim]{hidden} phase(s) hidden (disabled in phase-config.json). "
                "Run [cyan]sdlc phases[/] to view/enable them.[/]"
            )
        console.print()

    # ── Queue ──
    queue_dir = run_dir / "queue"
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
    log_file = run_dir / "state" / "activity-log.md"
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
    cont_file = run_dir / "CONTINUITY.md"
    if cont_file.exists():
        lines = cont_file.read_text().strip().splitlines()
        console.print("[bold]Working Memory (CONTINUITY.md):[/]")
        for line in lines[:15]:
            console.print(f"  {line}")
        console.print()

    # ── Generate agent-map.md ──
    try:
        from .mermaid import generate_agent_map_md

        orch_file_2 = run_dir / "state" / "orchestrator.json"
        trace_file_2 = run_dir / "state" / "agent-trace.json"
        mc_file = sdlc_dir / "model-config.json"
        orch_d = _json.loads(orch_file_2.read_text()) if orch_file_2.exists() else {}
        trace_d = _json.loads(trace_file_2.read_text()) if trace_file_2.exists() else {"traces": []}
        mc_d = _json.loads(mc_file.read_text()) if mc_file.exists() else {}
        md = generate_agent_map_md(orch_d, trace_d, mc_d, _enabled_map_for(sdlc_dir))
        map_path = run_dir / "state" / "agent-map.md"
        map_path.write_text(md, encoding="utf-8")
        console.print(f"[dim]Agent diagram written to {map_path.relative_to(sdlc_dir.parent)}[/]")
    except Exception:
        pass


@app.command()
def trace(
    target: str | None = typer.Argument(None, help="Project directory (default: current)"),
    phase: int | None = typer.Option(None, "--phase", "-p", help="Filter to a specific phase number"),
    verify: bool = typer.Option(False, "--verify", "-v", help="Cross-check traced artifacts against files on disk"),
    run: str | None = typer.Option(None, "--run", "-r", help="Run name/slug (default: active run)"),
    diagram: bool = typer.Option(False, "--diagram", "-d", help="Write Mermaid agent-map.md alongside trace output"),
) -> None:
    """Show the agent interaction map — which agent did what, dispatched whom, and artifact flow."""
    import json as _json

    from rich.tree import Tree

    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found. Run [cyan]sdlc init[/] first.")
        raise typer.Exit(1)

    run_dir = resolve_run_dir(sdlc_dir, run)
    trace_file = run_dir / "state" / "agent-trace.json"
    if not trace_file.exists():
        console.print("[red]Error:[/] No trace file found. Run the orchestrator first.")
        raise typer.Exit(1)

    try:
        data = _json.loads(trace_file.read_text(encoding="utf-8"))
    except _json.JSONDecodeError:
        try:
            data, _ = _json.JSONDecoder().raw_decode(trace_file.read_text(encoding="utf-8"))
            console.print("[yellow]Warning:[/] agent-trace.json has extra data — using first valid object.\n")
        except (ValueError, OSError) as exc:
            console.print(f"[red]Error reading trace file:[/] {exc}")
            raise typer.Exit(1)
    except OSError as exc:
        console.print(f"[red]Error reading trace file:[/] {exc}")
        raise typer.Exit(1)

    traces = data.get("traces", [])
    if not traces:
        console.print("[dim]No agent interactions recorded yet.[/]")
        console.print("Run the orchestrator to generate trace data.")
        # Still generate diagram if requested (shows static agent registry)
        if diagram:
            try:
                from .mermaid import generate_agent_map_md

                orch_file_d = run_dir / "state" / "orchestrator.json"
                mc_file_d = sdlc_dir / "model-config.json"
                orch_d = _json.loads(orch_file_d.read_text()) if orch_file_d.exists() else {}
                mc_d = _json.loads(mc_file_d.read_text()) if mc_file_d.exists() else {}
                md_content = generate_agent_map_md(orch_d, data, mc_d, _enabled_map_for(sdlc_dir))
                map_path = run_dir / "state" / "agent-map.md"
                map_path.write_text(md_content, encoding="utf-8")
                console.print(f"[green]✅ Agent diagram written to {map_path}[/]")
            except Exception as exc:
                console.print(f"[yellow]Warning:[/] Could not generate diagram: {exc}")
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

    # Write Mermaid diagram if requested
    if diagram:
        try:
            from .mermaid import generate_agent_map_md

            orch_file_d = run_dir / "state" / "orchestrator.json"
            mc_file_d = sdlc_dir / "model-config.json"
            orch_d = _json.loads(orch_file_d.read_text()) if orch_file_d.exists() else {}
            mc_d = _json.loads(mc_file_d.read_text()) if mc_file_d.exists() else {}
            md_content = generate_agent_map_md(orch_d, data, mc_d, _enabled_map_for(sdlc_dir))
            map_path = run_dir / "state" / "agent-map.md"
            map_path.write_text(md_content, encoding="utf-8")
            console.print(f"[green]✅ Agent diagram written to {map_path}[/]")
        except Exception as exc:
            console.print(f"[yellow]Warning:[/] Could not generate diagram: {exc}")


@app.command()
def dashboard(
    target: str | None = typer.Argument(None, help="Project directory (default: current)"),
    port: int = typer.Option(8420, "--port", "-p", help="HTTP server port (WebSocket = port+1)"),
    run: str | None = typer.Option(None, "--run", "-r", help="Run name/slug (default: active run)"),
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

    run_dir = resolve_run_dir(sdlc_dir, run)
    console.print(f"[bold cyan]SDLC Dashboard[/] starting on [link=http://127.0.0.1:{port}]http://127.0.0.1:{port}[/link]")
    console.print(f"WebSocket on port {port + 1}")
    if run_dir != sdlc_dir:
        console.print(f"[dim]Run: {run_dir.name}[/]")
    console.print("[dim]Press Ctrl+C to stop.[/]\n")

    serve(run_dir, sdlc_dir, port=port)


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
def phases(
    target: str | None = typer.Argument(None, help="Project directory (default: current)"),
    disable: str | None = typer.Option(None, "--disable", help="Disable a stage, e.g. stage-security"),
    enable: str | None = typer.Option(None, "--enable", help="Enable a stage, e.g. stage-security"),
    disable_sub: str | None = typer.Option(
        None, "--disable-sub", help="Disable a subagent, format stage-id:sub-id"
    ),
    enable_sub: str | None = typer.Option(
        None, "--enable-sub", help="Enable a subagent, format stage-id:sub-id"
    ),
    preset: str | None = typer.Option(
        None, "--preset", help="Apply a preset profile: full | lean"
    ),
    edit: bool = typer.Option(False, "--edit", "-e", help="Open phase-config.json in $EDITOR"),
    reset: bool = typer.Option(False, "--reset", help="Reset phase config to defaults (all enabled)"),
) -> None:
    """Show or manage which stages/subagents are enabled for this project."""
    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found. Run [cyan]sdlc init[/] first.")
        raise typer.Exit(1)

    from .phases import (
        BOOTSTRAP_ID,
        PHASE_REGISTRY,
        default_config,
        known_stage_ids,
        known_subagent_ids,
        load_config,
        load_custom_agents,
        preset_config,
        set_stage_enabled,
        set_subagent_enabled,
        summary,
        write_config,
    )

    # ── Reset ──
    if reset:
        write_config(sdlc_dir)
        console.print("[green]✅ Phase config reset to defaults (all enabled).[/]")
        console.print(f"[dim]  → {sdlc_dir / 'phase-config.json'}[/]")
        return

    # ── Preset ──
    if preset:
        try:
            new_config = preset_config(preset)
        except ValueError as exc:
            console.print(f"[red]Error:[/] {exc}")
            raise typer.Exit(1)
        write_config(sdlc_dir, new_config)
        disabled = [
            f"{PHASE_REGISTRY[s]['name']} ({PHASE_REGISTRY[s]['phase']})"
            for s in PHASE_REGISTRY
            if not new_config["stages"][s]["enabled"]
        ]
        console.print(f"[green]✅ Applied '[bold]{preset}[/]' preset.[/]")
        if disabled:
            console.print(f"[dim]  Disabled: {', '.join(disabled)}[/]")
        else:
            console.print("[dim]  All stages enabled.[/]")
        console.print(f"[dim]  → {sdlc_dir / 'phase-config.json'}[/]\n")
        # Fall through to render the resulting table so the user sees the effect.
        config = new_config

    # ── Edit ──
    if edit:
        import os
        import subprocess

        config_path = sdlc_dir / "phase-config.json"
        if not config_path.exists():
            write_config(sdlc_dir)
        editor = os.environ.get("EDITOR", "vi")
        subprocess.run([editor, str(config_path)])
        return

    if not preset:
        config = load_config(sdlc_dir)
        if config is None:
            config = default_config()
            write_config(sdlc_dir, config)

    # ── Mutations ──
    valid_stages = known_stage_ids(load_custom_agents(sdlc_dir))

    def _check_stage(stage_id: str) -> None:
        # Bootstrap is a known id but not disableable; let set_stage_enabled
        # raise its specific "cannot be disabled" message rather than "unknown".
        if stage_id == BOOTSTRAP_ID:
            return
        if stage_id not in valid_stages:
            console.print(
                f"[red]Error:[/] Unknown stage-id '[bold]{stage_id}[/]'. "
                "Use the stage-id (e.g. [cyan]stage-devops[/]), not the phase number or name."
            )
            console.print(f"[dim]Valid stage-ids: {', '.join(valid_stages)}[/]")
            raise typer.Exit(1)

    def _check_sub(stage_id: str, sub_id: str) -> None:
        _check_stage(stage_id)
        valid_subs = known_subagent_ids(stage_id, load_custom_agents(sdlc_dir))
        if sub_id not in valid_subs:
            console.print(
                f"[red]Error:[/] Unknown subagent '[bold]{sub_id}[/]' for stage '{stage_id}'."
            )
            console.print(
                f"[dim]Valid subagents: {', '.join(valid_subs) if valid_subs else '(none)'}[/]"
            )
            raise typer.Exit(1)

    mutated = False
    try:
        if disable:
            _check_stage(disable)
            set_stage_enabled(config, disable, False)
            mutated = True
        if enable:
            _check_stage(enable)
            set_stage_enabled(config, enable, True)
            mutated = True
        if disable_sub:
            stage_id, _, sub_id = disable_sub.partition(":")
            _check_sub(stage_id, sub_id)
            set_subagent_enabled(config, stage_id, sub_id, False)
            mutated = True
        if enable_sub:
            stage_id, _, sub_id = enable_sub.partition(":")
            _check_sub(stage_id, sub_id)
            set_subagent_enabled(config, stage_id, sub_id, True)
            mutated = True
    except ValueError as exc:
        console.print(f"[red]Error:[/] {exc}")
        raise typer.Exit(1)

    if mutated:
        write_config(sdlc_dir, config)
        console.print("[green]✅ Phase config updated.[/]")
        console.print(f"[dim]  → {sdlc_dir / 'phase-config.json'}[/]\n")

    # ── Display ──
    print_banner()

    custom_agents = load_custom_agents(sdlc_dir)

    table = Table(title="Phase / Stage / Subagent Configuration", show_lines=True)
    table.add_column("Phase", justify="right", min_width=5)
    table.add_column("Stage", style="bold", min_width=26)
    table.add_column("Status", min_width=10)
    table.add_column("Subagents", min_width=40)

    for row in summary(config, custom_agents):
        status = "[green]✓ enabled[/]" if row["enabled"] else "[red]✗ disabled[/]"
        stage_name = f"{row['name']} [magenta](custom)[/]" if row["is_custom"] else row["name"]
        if row["subagents"]:
            sub_parts = []
            for sub in row["subagents"]:
                mark = "[green]✓[/]" if sub["enabled"] else "[red]✗[/]"
                tag = " [magenta](custom)[/]" if sub["is_custom"] else ""
                sub_parts.append(f"{mark} {sub['id']}{tag}")
            subs_display = "\n".join(sub_parts)
        else:
            subs_display = "[dim]—[/]"
        table.add_row(str(row["phase"]), stage_name, status, subs_display)

    console.print(table)
    console.print(
        "\n[dim]Phase 1 (Bootstrap) is orchestrator-direct and always runs — not configurable.[/]"
    )
    console.print(f"[dim]Config: {sdlc_dir / 'phase-config.json'}[/]")
    console.print(
        "[dim]Disable: sdlc phases --disable stage-security  |  "
        "Disable subagent: sdlc phases --disable-sub stage-testing:sub-regression-test[/]"
    )
    console.print(
        "[dim]Presets: sdlc phases --preset lean (common core) | --preset full (all enabled)[/]"
    )
    console.print("[dim]Edit with: sdlc phases --edit  |  Reset with: sdlc phases --reset[/]")


@app.command()
def version() -> None:
    """Show the autonomous-sdlc version."""
    console.print(f"autonomous-sdlc {__version__}")


@app.command()
def upgrade(
    target: str | None = typer.Argument(None, help="Project directory (default: current)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would change without writing"),
) -> None:
    """Upgrade .sdlc/framework/ files from the installed package — keeps runtime state intact."""
    from .scaffold import upgrade_framework

    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found. Run [cyan]sdlc init[/] first.")
        raise typer.Exit(1)

    mode = "[yellow]DRY RUN[/] — " if dry_run else ""
    console.print(f"\n{mode}[bold cyan]Upgrading framework[/] from autonomous-sdlc {__version__}\n")

    updated = upgrade_framework(target_dir, dry_run=dry_run)

    if not updated:
        console.print("[yellow]No framework sources found in the installed package.[/]")
        raise typer.Exit(1)

    for component, count in updated.items():
        label = f"{count} file{'s' if count != 1 else ''}"
        console.print(f"  [green]✅[/] {component} — {label} updated")

    console.print()
    if dry_run:
        console.print("[yellow]No files were modified (dry run).[/]")
    else:
        console.print("[green]Framework upgraded.[/] Runtime state untouched.")
    console.print()


@app.command("cost-report")
def cost_report(
    target: str | None = typer.Argument(None, help="Project directory (default: current)"),
    run: str | None = typer.Option(None, "--run", "-r", help="Run name/slug (default: active run)"),
) -> None:
    """Show token usage, cost breakdown, retry stats, and budget status."""
    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found. Run [cyan]sdlc init[/] first.")
        raise typer.Exit(1)

    from .cost import build_report, load_budget_limit, load_usage

    run_dir = resolve_run_dir(sdlc_dir, run)
    usage = load_usage(run_dir)
    budget_limit = load_budget_limit(sdlc_dir)
    report = build_report(usage, budget_limit)

    print_banner(console)

    summary = Table(title="Token & Cost Summary", show_lines=False, box=None, padding=(0, 2))
    summary.add_column(style="bold")
    summary.add_column()
    summary.add_row("Total Tokens", f"{report['total_tokens']:,}")
    summary.add_row("Total Cost", f"${report['total_cost_usd']:.2f}")
    summary.add_row(
        "Budget",
        f"${report['budget_limit_usd']:.2f} ({report['budget_pct_used']:.0f}% utilized)",
    )
    console.print(summary)
    console.print()

    breakdown_table = Table(title="Cost Breakdown", show_lines=True)
    breakdown_table.add_column("Component", min_width=22)
    breakdown_table.add_column("Tokens", justify="right", min_width=12)
    breakdown_table.add_column("% of Total", justify="right", min_width=10)
    for component, tokens in report["breakdown"].items():
        pct = report["breakdown_pct"].get(component, 0.0)
        breakdown_table.add_row(component.replace("_", " ").title(), f"{tokens:,}", f"{pct:.1f}%")
    console.print(breakdown_table)
    console.print()

    retry_stats = report["retry_stats"]
    gate_stats = report["gate_stats"]
    stats_table = Table(title="Retry & Gate Stats", show_lines=False, box=None, padding=(0, 2))
    stats_table.add_column(style="bold")
    stats_table.add_column()
    stats_table.add_row("Total Retries", str(retry_stats.get("total_retries", 0)))
    stats_table.add_row("Tasks Failed First Attempt", str(retry_stats.get("tasks_failed_first_attempt", 0)))
    stats_table.add_row("Avg Retries / Task", f"{retry_stats.get('average_retries_per_task', 0.0):.2f}")
    stats_table.add_row("Gates Passed First Attempt", str(gate_stats.get("gates_passed_first_attempt", 0)))
    stats_table.add_row("Gates Failed", str(gate_stats.get("gates_failed", 0)))
    console.print(stats_table)

    if report["budget_pct_used"] >= 100:
        console.print("\n[red]⚠️  Budget exceeded.[/] Review .sdlc/governance/budget-policy.yaml")
    elif report["budget_pct_used"] >= 80:
        console.print("\n[yellow]⚠️  Budget >80% utilized.[/]")


@app.command()
def explain(
    decision_id: str = typer.Argument(..., help="Decision ID, e.g. DEC-001"),
    target: str | None = typer.Option(None, "--target", "-t", help="Project directory (default: current)"),
) -> None:
    """Explain a logged decision — alternatives considered, rationale, approver, impact."""
    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found. Run [cyan]sdlc init[/] first.")
        raise typer.Exit(1)

    from .explain import find_decision

    decision = find_decision(sdlc_dir, decision_id)
    if decision is None:
        console.print(f"[red]Error:[/] Decision '{decision_id}' not found in decision-log.json.")
        raise typer.Exit(1)

    print_banner(console)
    console.print(f"[bold cyan]{decision.get('id')}[/] — {decision.get('decision', '')}")
    console.print(f"[dim]Phase:[/] {decision.get('phase', '—')}   [dim]Agent:[/] {decision.get('agent', '—')}")
    console.print(f"[dim]Timestamp:[/] {decision.get('timestamp', '—')}\n")

    if decision.get("rationale"):
        console.print(f"[bold]Rationale:[/] {decision['rationale']}\n")

    alternatives = decision.get("alternatives_considered", [])
    if alternatives:
        alt_table = Table(title="Alternatives Considered", show_lines=True)
        alt_table.add_column("Option", min_width=16)
        alt_table.add_column("Pros", min_width=25)
        alt_table.add_column("Cons", min_width=25)
        alt_table.add_column("Score", justify="right", width=8)
        for alt in alternatives:
            alt_table.add_row(
                str(alt.get("option", "")),
                ", ".join(alt.get("pros", [])),
                ", ".join(alt.get("cons", [])),
                str(alt.get("score", "—")),
            )
        console.print(alt_table)
        console.print()

    console.print(f"[bold]Risk assessment:[/] {decision.get('risk_assessment', '—')}")
    console.print(f"[bold]Approval status:[/] {decision.get('approval_status', '—')}")
    if decision.get("approved_by"):
        console.print(f"[bold]Approved by:[/] {decision['approved_by']}")

    impact = decision.get("impact_analysis")
    if impact:
        console.print("\n[bold]Impact analysis:[/]")
        for k, v in impact.items():
            console.print(f"  {k.replace('_', ' ').title()}: {v}")


# ---------------------------------------------------------------------------
# Governance approval subcommands
# ---------------------------------------------------------------------------


@approvals_app.command("list")
def approvals_list(
    target: str | None = typer.Option(None, "--target", "-t", help="Project directory (default: current)"),
    all_: bool = typer.Option(False, "--all", help="Show resolved approvals too (default: pending only)"),
) -> None:
    """Show pending (and optionally resolved) approval requests."""
    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found. Run [cyan]sdlc init[/] first.")
        raise typer.Exit(1)

    from .approvals import load_pending

    approvals = load_pending(sdlc_dir)
    if not all_:
        approvals = [a for a in approvals if a.get("status") == "pending"]

    if not approvals:
        console.print("[dim]No approval requests found.[/]")
        return

    table = Table(title="Governance Approvals", show_lines=True)
    table.add_column("ID", style="cyan", min_width=10)
    table.add_column("Phase", min_width=14)
    table.add_column("Agent", min_width=16)
    table.add_column("Decision", min_width=30)
    table.add_column("Risk", min_width=10)
    table.add_column("Status", min_width=10)

    for a in approvals:
        status = a.get("status", "pending")
        style = {"pending": "yellow", "approved": "green", "rejected": "red"}.get(status, "white")
        table.add_row(
            a.get("id", "—"),
            a.get("phase", "—"),
            a.get("agent", "—"),
            a.get("decision", "—"),
            a.get("risk_level", "—"),
            f"[{style}]{status}[/{style}]",
        )
    console.print(table)


@approvals_app.command("approve")
def approvals_approve(
    approval_id: str = typer.Argument(..., help="Approval ID, e.g. APPR-001"),
    target: str | None = typer.Option(None, "--target", "-t", help="Project directory (default: current)"),
) -> None:
    """Approve a pending governance decision."""
    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found.")
        raise typer.Exit(1)

    from .approvals import resolve_approval

    result = resolve_approval(sdlc_dir, approval_id, approve=True)
    if result is None:
        console.print(f"[red]Error:[/] Approval '{approval_id}' not found.")
        raise typer.Exit(1)

    console.print(f"[green]✅ Approved:[/] {approval_id} — {result.get('decision', '')}")
    console.print("[dim]Logged to .sdlc/governance/decision-log.json[/]")


@approvals_app.command("reject")
def approvals_reject(
    approval_id: str = typer.Argument(..., help="Approval ID, e.g. APPR-001"),
    reason: str = typer.Option(..., "--reason", help="Reason for rejection"),
    target: str | None = typer.Option(None, "--target", "-t", help="Project directory (default: current)"),
) -> None:
    """Reject a pending governance decision with a reason."""
    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found.")
        raise typer.Exit(1)

    from .approvals import resolve_approval

    result = resolve_approval(sdlc_dir, approval_id, approve=False, reason=reason)
    if result is None:
        console.print(f"[red]Error:[/] Approval '{approval_id}' not found.")
        raise typer.Exit(1)

    console.print(f"[red]❌ Rejected:[/] {approval_id} — {reason}")
    console.print("[dim]Logged to .sdlc/governance/decision-log.json[/]")


@approvals_app.command("configure")
def approvals_configure(
    target: str | None = typer.Option(None, "--target", "-t", help="Project directory (default: current)"),
) -> None:
    """Configure notification channels for approval requests (Slack, email)."""
    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"
    gov_dir = sdlc_dir / "governance"
    gov_dir.mkdir(parents=True, exist_ok=True)
    config_path = gov_dir / "notification-config.yaml"

    console.print("[bold cyan]Configure approval notifications[/]\n")
    slack_enabled = typer.confirm("Enable Slack notifications?", default=False)
    slack_webhook = typer.prompt("Slack webhook URL", default="") if slack_enabled else ""
    email_enabled = typer.confirm("Enable email notifications?", default=False)
    email_to = typer.prompt("Notify email address(es), comma-separated", default="") if email_enabled else ""

    config = {
        "channels": {
            "slack": {"enabled": slack_enabled, "webhook_url": slack_webhook},
            "email": {
                "enabled": email_enabled,
                "smtp_host": "",
                "smtp_port": 587,
                "from_address": "",
                "to_addresses": [e.strip() for e in email_to.split(",") if e.strip()],
            },
            "desktop": {"enabled": False},
        },
        "default_channel": "slack" if slack_enabled else ("email" if email_enabled else "cli"),
    }
    try:
        import yaml  # type: ignore

        config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    except ImportError:
        import json as _json

        config_path.write_text(_json.dumps(config, indent=2), encoding="utf-8")

    console.print(f"\n[green]✅ Notification config saved:[/] {config_path}")


# ---------------------------------------------------------------------------
# Custom agent subcommands (sdlc agents ...)
# ---------------------------------------------------------------------------


def _require_sdlc_dir(target: str | None) -> Path:
    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"
    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found. Run [cyan]sdlc init[/] first.")
        raise typer.Exit(1)
    return sdlc_dir


@agents_app.command("list")
def agents_list(
    target: str | None = typer.Option(None, "--target", "-t", help="Project directory (default: current)"),
) -> None:
    """List registered custom stage agents and subagents."""
    sdlc_dir = _require_sdlc_dir(target)

    from .phases import load_custom_agents

    custom = load_custom_agents(sdlc_dir)
    stages = custom.get("custom_stages", {})
    subs = custom.get("custom_subagents", {})

    if not stages and not subs:
        console.print("[dim]No custom agents registered. Add one with `sdlc agents add-stage` or `sdlc agents add-subagent`.[/]")
        return

    if stages:
        table = Table(title="Custom Stage Agents")
        table.add_column("Stage ID", style="bold")
        table.add_column("Name")
        table.add_column("Anchor")
        table.add_column("Prompt")
        for sid, entry in stages.items():
            anchor = entry.get("anchor", {})
            table.add_row(sid, entry.get("name", ""), f"{anchor.get('position')} {anchor.get('stage_id')}", entry.get("prompt", ""))
        console.print(table)

    if subs:
        table = Table(title="Custom Subagents")
        table.add_column("Subagent ID", style="bold")
        table.add_column("Name")
        table.add_column("Attached To Stage")
        table.add_column("Prompt")
        for sid, entry in subs.items():
            table.add_row(sid, entry.get("name", ""), entry.get("attach_to_stage", ""), entry.get("prompt", ""))
        console.print(table)

    console.print("\n[dim]Run `sdlc phases` to see them in the full pipeline order alongside built-ins.[/]")


@agents_app.command("add-subagent")
def agents_add_subagent(
    sub_id: str = typer.Argument(..., help="New subagent id, e.g. sub-terraform-validator"),
    stage: str = typer.Option(..., "--stage", help="Stage id to attach to, e.g. stage-devops"),
    name: str = typer.Option(..., "--name", help="Human-readable name, e.g. 'Terraform Validator'"),
    description: str = typer.Option(..., "--description", help="What this subagent's focused task/goal is"),
    target: str | None = typer.Option(None, "--target", "-t", help="Project directory (default: current)"),
) -> None:
    """Scaffold and register a custom subagent attached to an existing stage."""
    sdlc_dir = _require_sdlc_dir(target)

    from .custom_agents import CustomAgentError, add_subagent

    try:
        prompt_path = add_subagent(sdlc_dir, sub_id=sub_id, stage_id=stage, name=name, description=description)
    except CustomAgentError as exc:
        console.print(f"[red]Error:[/] {exc}")
        raise typer.Exit(1)

    console.print(f"[green]✅ Custom subagent '{sub_id}' created and enabled on '{stage}'.[/]")
    console.print(f"[dim]  → Prompt:  {prompt_path}[/]")
    console.print(f"[dim]  → Registry: {sdlc_dir / 'custom-agents.json'}[/]")
    console.print(f"[dim]  → Fill in the {{...}} placeholders in the prompt file, then edit it further as needed.[/]")
    console.print("[dim]Disable/enable later with: sdlc phases --disable-sub / --enable-sub[/]")


@agents_app.command("add-stage")
def agents_add_stage(
    stage_id: str = typer.Argument(..., help="New stage id, e.g. stage-localization"),
    name: str = typer.Option(..., "--name", help="Human-readable name, e.g. 'Localization'"),
    description: str = typer.Option(..., "--description", help="What success looks like for this new phase"),
    after: str | None = typer.Option(None, "--after", help="Anchor stage id to insert this stage after"),
    before: str | None = typer.Option(None, "--before", help="Anchor stage id to insert this stage before"),
    target: str | None = typer.Option(None, "--target", "-t", help="Project directory (default: current)"),
) -> None:
    """Scaffold and register a custom stage agent (new phase) at a specific point in the pipeline.

    Renumbers built-in phase numbers after the insertion point, including any
    in-progress .sdlc/state/orchestrator.json.
    """
    sdlc_dir = _require_sdlc_dir(target)

    if bool(after) == bool(before):
        console.print("[red]Error:[/] Specify exactly one of --after or --before.")
        raise typer.Exit(1)
    anchor_position = "after" if after else "before"
    anchor_stage_id = after or before

    from .custom_agents import CustomAgentError, add_stage

    try:
        prompt_path, new_numbers = add_stage(
            sdlc_dir,
            stage_id=stage_id,
            name=name,
            description=description,
            anchor_position=anchor_position,
            anchor_stage_id=anchor_stage_id,
        )
    except CustomAgentError as exc:
        console.print(f"[red]Error:[/] {exc}")
        raise typer.Exit(1)

    console.print(f"[green]✅ Custom stage '{stage_id}' created as Phase {new_numbers[stage_id]}.[/]")
    console.print(f"[dim]  → Prompt:   {prompt_path}[/]")
    console.print(f"[dim]  → Registry: {sdlc_dir / 'custom-agents.json'}[/]")
    console.print("[dim]  → Built-in phase numbers after the insertion point have shifted — run `sdlc phases` to see the new order.[/]")
    if (sdlc_dir / "state" / "orchestrator.json").exists():
        console.print("[dim]  → .sdlc/state/orchestrator.json was renumbered to match (existing phase status/gate/review preserved).[/]")
    console.print(f"[dim]  → Fill in the {{...}} placeholders in the prompt file, then add subagents with `sdlc agents add-subagent --stage {stage_id}`.[/]")


@agents_app.command("remove")
def agents_remove(
    agent_id: str = typer.Argument(..., help="Custom stage id (stage-*) or subagent id (sub-*) to remove"),
    target: str | None = typer.Option(None, "--target", "-t", help="Project directory (default: current)"),
) -> None:
    """Remove a registered custom stage agent or subagent (and its prompt file)."""
    sdlc_dir = _require_sdlc_dir(target)

    from .custom_agents import CustomAgentError, remove_stage, remove_subagent

    try:
        if agent_id.startswith("sub-"):
            remove_subagent(sdlc_dir, agent_id)
        elif agent_id.startswith("stage-"):
            remove_stage(sdlc_dir, agent_id)
        else:
            console.print("[red]Error:[/] agent_id must start with 'stage-' or 'sub-'.")
            raise typer.Exit(1)
    except CustomAgentError as exc:
        console.print(f"[red]Error:[/] {exc}")
        raise typer.Exit(1)

    console.print(f"[green]✅ Removed custom agent '{agent_id}'.[/]")


# ---------------------------------------------------------------------------
# Run management subcommands
# ---------------------------------------------------------------------------


@run_app.command("new")
def run_new(
    spec_file: str | None = typer.Argument(None, help="Path to a spec/requirements file"),
    name: str | None = typer.Option(None, "--name", "-n", help="Override auto-generated folder name"),
    target: str | None = typer.Option(None, "--target", "-t", help="Project directory (default: current)"),
) -> None:
    """Create a new SDLC run from a spec — auto-names the folder from content."""
    import json as _json

    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found. Run [cyan]sdlc init[/] first.")
        raise typer.Exit(1)

    from .runs import generate_run_slug, list_runs, set_active_run
    from .scaffold import create_run

    # Read spec content for slug generation
    spec_text = ""
    spec_path = None
    if spec_file:
        spec_path = Path(spec_file).resolve()
        if not spec_path.exists():
            console.print(f"[red]Error:[/] Spec file not found: {spec_file}")
            raise typer.Exit(1)
        spec_text = spec_path.read_text(encoding="utf-8")
    else:
        console.print("[dim]No spec file provided. Enter a title/description for this run:[/]")
        spec_text = typer.prompt("Title")

    # Generate or use provided name
    existing_slugs = [r["slug"] for r in list_runs(sdlc_dir)]
    if name:
        slug = name
        if slug in existing_slugs:
            console.print(f"[red]Error:[/] Run '{slug}' already exists.")
            raise typer.Exit(1)
    else:
        slug = generate_run_slug(spec_text, existing_slugs)

    # Extract title for run-info
    title = ""
    for line in spec_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            title = stripped.lstrip("#").strip()
            break
        if stripped:
            title = stripped
            break
    title = title or slug

    # Create the run
    run_dir = create_run(sdlc_dir, slug, title, str(spec_path) if spec_path else None)

    # Copy spec into the run
    if spec_path:
        import shutil

        dst = run_dir / "specs" / spec_path.name
        shutil.copy2(spec_path, dst)
        # Also write normalized-spec.md
        (run_dir / "specs" / "normalized-spec.md").write_text(spec_text, encoding="utf-8")

    console.print(f"\n[bold green]✅ Run created:[/] [cyan]{slug}[/]")
    console.print(f"   [dim]Title:[/] {title}")
    console.print(f"   [dim]Path:[/]  .sdlc/runs/{slug}/")
    console.print(f"   [dim]Set as active run.[/]")
    console.print(f"\n[dim]Next: Start the orchestrator in your AI IDE.[/]")


@run_app.command("list")
def run_list(
    target: str | None = typer.Option(None, "--target", "-t", help="Project directory (default: current)"),
) -> None:
    """List all SDLC runs with status."""
    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found. Run [cyan]sdlc init[/] first.")
        raise typer.Exit(1)

    from .runs import list_runs

    runs = list_runs(sdlc_dir)
    if not runs:
        console.print("[dim]No runs found. Create one with:[/] sdlc run new <spec-file>")
        return

    table = Table(title="SDLC Runs", show_lines=True)
    table.add_column("", width=2)
    table.add_column("Slug", style="cyan", min_width=25)
    table.add_column("Status", min_width=12)
    table.add_column("Phase", min_width=6)
    table.add_column("Last Updated", min_width=20)

    status_icons = {
        "initialized": "⬜", "in_progress": "🔄", "complete": "✅", "failed": "❌",
    }

    for r in runs:
        marker = "[bold green]▸[/]" if r.get("active") else " "
        st = r.get("status", "unknown")
        icon = status_icons.get(st, "❓")
        phase = str(r.get("current_phase", "—"))
        updated = r.get("last_updated", "—")
        if updated and len(updated) > 19:
            updated = updated[:19]
        table.add_row(marker, r["slug"], f"{icon} {st}", phase, updated)

    console.print(table)
    console.print("[dim]▸ = active run[/]")


@run_app.command("switch")
def run_switch(
    slug: str = typer.Argument(..., help="Run slug to switch to"),
    target: str | None = typer.Option(None, "--target", "-t", help="Project directory (default: current)"),
) -> None:
    """Set the active SDLC run."""
    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found.")
        raise typer.Exit(1)

    run_path = sdlc_dir / "runs" / slug
    if not run_path.is_dir():
        console.print(f"[red]Error:[/] Run '{slug}' not found.")
        raise typer.Exit(1)

    from .runs import set_active_run

    set_active_run(sdlc_dir, slug)
    console.print(f"[green]✅ Active run set to:[/] [cyan]{slug}[/]")


@run_app.command("active")
def run_active(
    target: str | None = typer.Option(None, "--target", "-t", help="Project directory (default: current)"),
) -> None:
    """Show the currently active run."""
    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found.")
        raise typer.Exit(1)

    from .runs import get_active_run

    active = get_active_run(sdlc_dir)
    if active:
        console.print(f"Active run: [cyan]{active}[/]")
    else:
        console.print("[dim]No active run. Using legacy single-run mode.[/]")


@run_app.command("archive")
def run_archive(
    slug: str = typer.Argument(..., help="Run slug to archive"),
    target: str | None = typer.Option(None, "--target", "-t", help="Project directory (default: current)"),
) -> None:
    """Archive a completed run to .sdlc/archive/."""
    import shutil

    target_dir = Path(target).resolve() if target else Path.cwd()
    sdlc_dir = target_dir / ".sdlc"

    if not sdlc_dir.is_dir():
        console.print("[red]Error:[/] .sdlc/ directory not found.")
        raise typer.Exit(1)

    run_path = sdlc_dir / "runs" / slug
    if not run_path.is_dir():
        console.print(f"[red]Error:[/] Run '{slug}' not found.")
        raise typer.Exit(1)

    archive_dir = sdlc_dir / "archive"
    archive_dir.mkdir(exist_ok=True)
    dest = archive_dir / slug

    if dest.exists():
        console.print(f"[red]Error:[/] Archive '{slug}' already exists.")
        raise typer.Exit(1)

    shutil.move(str(run_path), str(dest))

    from .runs import get_active_run

    if get_active_run(sdlc_dir) == slug:
        # Clear active run
        (sdlc_dir / "active-run.json").unlink(missing_ok=True)
        console.print("[dim]Cleared active run (archived was active).[/]")

    console.print(f"[green]✅ Run archived:[/] .sdlc/archive/{slug}/")


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
