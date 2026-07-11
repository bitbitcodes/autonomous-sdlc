"""Mermaid diagram generator for the SDLC agent interaction map."""

from __future__ import annotations

from typing import Any

from .phases import agent_registry

# ---------------------------------------------------------------------------
# Agent registry — derived from the single source of truth in phases.py so the
# interaction map always matches the actual 13-phase / 52-agent pipeline.
# ---------------------------------------------------------------------------

AGENT_REGISTRY: list[dict[str, Any]] = agent_registry()


def _node_id(agent: str) -> str:
    """Convert agent ID to a valid Mermaid node ID."""
    return agent.replace("-", "_")


def _status_class(status: str | None) -> str:
    """Map status to a CSS class name for Mermaid styling."""
    if status == "complete":
        return "done"
    if status == "in_progress":
        return "active"
    return "pending"


def generate_mermaid(
    orch_data: dict | None = None,
    trace_data: dict | None = None,
    model_config: dict | None = None,
    enabled_map: dict[str, bool] | None = None,
) -> str:
    """Generate a Mermaid flowchart showing per-phase agent interactions.

    Args:
        orch_data: orchestrator.json content (for phase statuses)
        trace_data: agent-trace.json content (for actual dispatch info)
        model_config: model-config.json content (for model labels)
        enabled_map: {phase_key: enabled} from phase-config.json. Disabled
            phases are greyed out and marked; None means all enabled.

    Returns:
        Mermaid diagram source string
    """
    phases = (orch_data or {}).get("phases", {})
    traces = (trace_data or {}).get("traces", [])
    enabled_map = enabled_map or {}

    def _disabled(key: str) -> bool:
        return enabled_map.get(key, True) is False

    # Build lookup: agent_id -> model name
    model_map: dict[str, str] = {}
    if model_config:
        tiers = model_config.get("tiers", {})
        agent_tiers = model_config.get("agent_tiers", {})
        overrides = model_config.get("overrides", {})
        for reg in AGENT_REGISTRY:
            aid = reg["agent"]
            if aid in overrides:
                model_map[aid] = overrides[aid]
            elif aid in agent_tiers:
                model_map[aid] = tiers.get(agent_tiers[aid], agent_tiers[aid])
            for sub in reg["subagents"]:
                if sub in overrides:
                    model_map[sub] = overrides[sub]
                elif "sub-*" in agent_tiers:
                    model_map[sub] = tiers.get(agent_tiers["sub-*"], agent_tiers["sub-*"])

    # Build trace lookup: agent_id -> trace entry
    trace_map: dict[str, dict] = {}
    for t in traces:
        trace_map[t.get("agent", "")] = t

    lines = [
        "flowchart TD",
        "    ORCH([\"🎯 orch-sdlc<br/>Orchestrator\"])",
        "",
    ]

    # Generate subgraphs for each phase
    for reg in AGENT_REGISTRY:
        phase_num = reg["phase"]
        key = reg["key"]
        name = reg["name"]
        agent = reg["agent"]
        subs = reg["subagents"]
        nid = _node_id(agent)

        # Hide disabled phases entirely.
        if _disabled(key):
            continue

        # Determine status
        phase_info = phases.get(key, {})
        status = phase_info.get("status", "pending")
        cls = _status_class(status)

        # Model label
        model_label = model_map.get(agent, "")
        model_suffix = f"<br/><i>{model_label}</i>" if model_label else ""

        lines.append(f"    subgraph P{phase_num}[\"{phase_num}. {name}\"]")

        if reg.get("role") == "orchestrator":
            lines.append(f"        {nid}[\"🎯 {agent}{model_suffix}\"]")
        else:
            lines.append(f"        {nid}[\"📋 {agent}{model_suffix}\"]")

        for sub in subs:
            sub_nid = _node_id(sub)
            sub_model = model_map.get(sub, "")
            sub_suffix = f"<br/><i>{sub_model}</i>" if sub_model else ""
            sub_status = "pending"
            if status == "complete":
                sub_status = "complete"
            elif sub in trace_map:
                sub_status = trace_map[sub].get("status", "pending")
            sub_cls = _status_class(sub_status)
            lines.append(f"        {sub_nid}[\"⚙️ {sub}{sub_suffix}\"]")
            lines.append(f"        {nid} --> {sub_nid}")

        lines.append("    end")
        lines.append(f"    class P{phase_num} {cls}")
        lines.append("")

    # Only enabled phases participate in arrows/sequence.
    visible = [r for r in AGENT_REGISTRY if not _disabled(r["key"])]

    # Orchestrator dispatch arrows
    lines.append("    %% Dispatch flow")
    for reg in visible:
        nid = _node_id(reg["agent"])
        lines.append(f"    ORCH -.->|\"Phase {reg['phase']}\"| {nid}")

    # Phase sequence arrows
    lines.append("")
    lines.append("    %% Phase sequence")
    for i in range(len(visible) - 1):
        a = _node_id(visible[i]["agent"])
        b = _node_id(visible[i + 1]["agent"])
        lines.append(f"    {a} ==> {b}")

    # Style definitions
    lines.extend([
        "",
        "    %% Styles",
        "    classDef done fill:#238636,stroke:#3fb950,color:#fff",
        "    classDef active fill:#9e6a03,stroke:#d29922,color:#fff",
        "    classDef pending fill:#21262d,stroke:#30363d,color:#8b949e",
    ])

    # Apply status styles to individual nodes (enabled phases only)
    for reg in visible:
        key = reg["key"]
        phase_info = phases.get(key, {})
        status = phase_info.get("status", "pending")
        cls = _status_class(status)
        nid = _node_id(reg["agent"])
        lines.append(f"    class {nid} {cls}")
        for sub in reg["subagents"]:
            sub_nid = _node_id(sub)
            sub_status = status if status == "complete" else "pending"
            if sub in trace_map:
                sub_status = trace_map[sub].get("status", "pending")
            lines.append(f"    class {sub_nid} {_status_class(sub_status)}")

    return "\n".join(lines)


def generate_agent_map_md(
    orch_data: dict | None = None,
    trace_data: dict | None = None,
    model_config: dict | None = None,
    enabled_map: dict[str, bool] | None = None,
) -> str:
    """Generate a full Markdown document with the Mermaid diagram."""
    diagram = generate_mermaid(orch_data, trace_data, model_config, enabled_map)
    return (
        "# Agent Interaction Map\n\n"
        "```mermaid\n"
        f"{diagram}\n"
        "```\n\n"
        "*Auto-generated by `sdlc status` / `sdlc trace --diagram`. "
        "View in any Markdown previewer (VS Code, GitHub, etc.)*\n"
    )
