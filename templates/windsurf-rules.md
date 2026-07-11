---
trigger: always
description: "Autonomous SDLC Framework — loaded on every conversation"
---

# Autonomous SDLC Framework — Active

This project uses the **Autonomous SDLC Framework** for AI-driven development. 52 agents execute the full software development lifecycle autonomously.

> **Full instructions are in `.sdlc/framework/agents/orchestrator.md`.** This file is the concise summary Devin Desktop loads at startup.

## Available Workflows

Type `/sdlc.` in Devin Local chat to see available commands:

| Workflow | Purpose |
|----------|---------|
| `/sdlc.orchestrator` | Start or resume the full SDLC — reads your spec and drives all 13 phases |

## Priority Reading Order

1. `AGENTS.md` — Agent discovery and registry
2. `.sdlc/CONTINUITY.md` — Current session state (working memory)
3. `.sdlc/state/orchestrator.json` — Phase progress

## How to Operate

When the `/sdlc.orchestrator` workflow is active:

1. **Do NOT directly implement the user's request.** You are an orchestrator, not a coder.
2. Read `.sdlc/framework/agents/orchestrator.md` for full orchestrator instructions
3. Follow the RARV cycle: Reason → Act → Reflect → Verify
4. Read CONTINUITY.md at the start of every turn
5. Update CONTINUITY.md at the end of every turn
6. Execute phases sequentially (0→9), dispatch subagents as needed
7. Enforce quality gates before phase transitions
8. **Update state files at every phase:** `orchestrator.json`, `CONTINUITY.md`, `activity-log.md`, `STATUS.md`, `queue/*.json`

## Current State

Check `.sdlc/CONTINUITY.md` for the current phase and next steps.

## Agent Prompts Location

- Orchestrator: `.sdlc/framework/agents/orchestrator.md`
- Stage agents: `.sdlc/framework/agents/stage/*.md`
- Subagents: `.sdlc/framework/agents/sub/**/*.md`
- References: `.sdlc/framework/references/*.md`
- Skills: `.sdlc/framework/skills/*.md`
