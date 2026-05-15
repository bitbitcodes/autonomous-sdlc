"""Mermaid diagram generator for the SDLC agent interaction map."""

from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Static agent registry — all 40 agents with phase/role/subagent structure
# ---------------------------------------------------------------------------

AGENT_REGISTRY: list[dict[str, Any]] = [
    {
        "phase": 0, "key": "0-bootstrap", "name": "Bootstrap",
        "agent": "orch-sdlc", "role": "orchestrator", "subagents": [],
    },
    {
        "phase": 1, "key": "1-product", "name": "Product",
        "agent": "stage-product", "role": "stage",
        "subagents": [
            "sub-requirement-parser", "sub-acceptance-criteria",
            "sub-risk-analyzer", "sub-assumption-extractor",
        ],
    },
    {
        "phase": 2, "key": "2-story-tasks", "name": "Story-Tasks",
        "agent": "stage-story-tasks", "role": "stage",
        "subagents": [
            "sub-story-writer", "sub-task-decomposer", "sub-dependency-mapper",
        ],
    },
    {
        "phase": 3, "key": "3-architecture", "name": "Architecture",
        "agent": "stage-architecture", "role": "stage",
        "subagents": [
            "sub-tech-stack-advisor", "sub-solution-evaluator", "sub-adr-writer",
        ],
    },
    {
        "phase": 4, "key": "4-design", "name": "Design",
        "agent": "stage-design", "role": "stage",
        "subagents": [
            "sub-interface-designer", "sub-data-model-designer",
            "sub-integration-planner", "sub-nfr-evaluator",
        ],
    },
    {
        "phase": 5, "key": "5-development", "name": "Development",
        "agent": "stage-development", "role": "stage",
        "subagents": [
            "sub-repo-analyzer", "sub-code-generator",
            "sub-refactoring-agent", "sub-documentation-agent",
        ],
    },
    {
        "phase": 6, "key": "6-testing", "name": "Testing",
        "agent": "stage-testing", "role": "stage",
        "subagents": [
            "sub-unit-test", "sub-integration-test",
            "sub-regression-test", "sub-test-data",
        ],
    },
    {
        "phase": 7, "key": "7-security", "name": "Security",
        "agent": "stage-security", "role": "stage",
        "subagents": [
            "sub-secret-scanner", "sub-dependency-scanner",
            "sub-owasp-reviewer", "sub-policy-validator",
        ],
    },
    {
        "phase": 8, "key": "8-review", "name": "Review",
        "agent": "stage-review", "role": "stage",
        "subagents": [
            "sub-code-review", "sub-maintainability", "sub-performance",
        ],
    },
    {
        "phase": 9, "key": "9-devops", "name": "DevOps",
        "agent": "stage-devops", "role": "stage", "subagents": [],
    },
    {
        "phase": 10, "key": "10-observability", "name": "Observability",
        "agent": "stage-observability", "role": "stage", "subagents": [],
    },
]


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
) -> str:
    """Generate a Mermaid flowchart showing per-phase agent interactions.

    Args:
        orch_data: orchestrator.json content (for phase statuses)
        trace_data: agent-trace.json content (for actual dispatch info)
        model_config: model-config.json content (for model labels)

    Returns:
        Mermaid diagram source string
    """
    phases = (orch_data or {}).get("phases", {})
    traces = (trace_data or {}).get("traces", [])

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

        # Determine status
        phase_info = phases.get(key, {})
        status = phase_info.get("status", "pending")
        cls = _status_class(status)

        # Model label
        model_label = model_map.get(agent, "")
        model_suffix = f"<br/><i>{model_label}</i>" if model_label else ""

        lines.append(f"    subgraph P{phase_num}[\"{phase_num}. {name}\"]")

        if phase_num == 0:
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

    # Orchestrator dispatch arrows
    lines.append("    %% Dispatch flow")
    for reg in AGENT_REGISTRY:
        nid = _node_id(reg["agent"])
        lines.append(f"    ORCH -.->|\"Phase {reg['phase']}\"| {nid}")

    # Phase sequence arrows
    lines.append("")
    lines.append("    %% Phase sequence")
    for i in range(len(AGENT_REGISTRY) - 1):
        a = _node_id(AGENT_REGISTRY[i]["agent"])
        b = _node_id(AGENT_REGISTRY[i + 1]["agent"])
        lines.append(f"    {a} ==> {b}")

    # Style definitions
    lines.extend([
        "",
        "    %% Styles",
        "    classDef done fill:#238636,stroke:#3fb950,color:#fff",
        "    classDef active fill:#9e6a03,stroke:#d29922,color:#fff",
        "    classDef pending fill:#21262d,stroke:#30363d,color:#8b949e",
    ])

    # Apply status styles to individual nodes
    for reg in AGENT_REGISTRY:
        phase_info = phases.get(reg["key"], {})
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
) -> str:
    """Generate a full Markdown document with the Mermaid diagram."""
    diagram = generate_mermaid(orch_data, trace_data, model_config)
    return (
        "# Agent Interaction Map\n\n"
        "```mermaid\n"
        f"{diagram}\n"
        "```\n\n"
        "*Auto-generated by `sdlc status` / `sdlc trace --diagram`. "
        "View in any Markdown previewer (VS Code, GitHub, etc.)*\n"
    )
