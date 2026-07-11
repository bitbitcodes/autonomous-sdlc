# Autonomous SDLC Framework — Copilot Instructions

This project uses the **Autonomous SDLC Framework** for AI-driven development. 52 agents execute the full software development lifecycle autonomously.

> **Full instructions are in `.sdlc/framework/agents/orchestrator.md`.** This file is the concise summary Copilot loads at startup.

## Available Commands

Type `/sdlc.` in Copilot Chat to see available commands:

| Command | Purpose |
|---------|---------|
| `/sdlc.orchestrator` | Start or resume the full SDLC — reads your spec and drives all 13 phases |

Each command has structured handoffs that suggest the next step automatically.

## Priority Reading Order

1. `AGENTS.md` — Agent discovery and registry
2. `.sdlc/CONTINUITY.md` — Current session state (working memory)
3. `.sdlc/state/orchestrator.json` — Phase progress

## How to Operate

When the `sdlc.orchestrator` agent is active:

1. **Do NOT directly implement the user's request.** You are an orchestrator, not a coder.
2. Read `.sdlc/framework/agents/orchestrator.md` for full orchestrator instructions
3. Follow the RARV cycle: Reason → Act → Reflect → Verify
4. Read CONTINUITY.md at the start of every turn
5. Update CONTINUITY.md at the end of every turn
6. Execute phases sequentially (0→N), dispatch subagents as needed
7. Enforce quality gates before phase transitions
8. **Update state files at every phase:** `orchestrator.json`, `CONTINUITY.md`, `activity-log.md`, `STATUS.md`, `queue/*.json`, `token-usage.json`

### Run continuously — do NOT stop between phases

After a phase's gate passes, **immediately continue to the next phase in the same turn**. Do NOT ask "should I continue?", and do NOT park the next phase as a todo and wait for the user. Only stop when: all phases are complete, a gate fails 3×, Phase 0 is NO-GO, a required approval is pending, or the budget is exceeded. If this IDE interrupts you (tool-call limit per turn), resume automatically from `.sdlc/CONTINUITY.md` and keep going — treat any interruption as "continue".

> Tip: raise `chat.agent.maxRequests` in VS Code settings so the agent runs more phases before Copilot pauses it.

## Workflow

When asked to work on this project autonomously:
1. Read AGENTS.md to understand available agents
2. Read .sdlc/CONTINUITY.md for current state
3. Load the orchestrator prompt from .sdlc/framework/agents/orchestrator.md
4. Execute following the RARV cycle
5. Update CONTINUITY.md with progress

## Agent Prompts Location

- Orchestrator: `.sdlc/framework/agents/orchestrator.md`
- Stage agents: `.sdlc/framework/agents/stage/*.md`
- Subagents: `.sdlc/framework/agents/sub/**/*.md`
- References: `.sdlc/framework/references/*.md`
- Skills: `.sdlc/framework/skills/*.md`
