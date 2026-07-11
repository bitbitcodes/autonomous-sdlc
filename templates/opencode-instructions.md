# Autonomous SDLC Framework

This project uses the **Autonomous SDLC Framework** for AI-driven development. 52 agents execute the full software development lifecycle autonomously.

> **Full instructions are in `.sdlc/framework/agents/orchestrator.md`.** This file is the concise summary opencode loads at startup.

## Priority Reading Order

1. `AGENTS.md` — Agent discovery and registry
2. `.sdlc/CONTINUITY.md` — Current session state (working memory)
3. `.sdlc/state/orchestrator.json` — Phase progress

## How to Operate

- Read `.sdlc/framework/agents/orchestrator.md` for full orchestrator instructions
- Follow the RARV cycle: Reason → Act → Reflect → Verify
- Read CONTINUITY.md at the start of every turn
- Update CONTINUITY.md at the end of every turn
- Execute phases sequentially, dispatch subagents as needed
- Enforce quality gates before phase transitions

## Current State

Check `.sdlc/CONTINUITY.md` for the current phase and next steps.

## Available Commands

Use `/sdlc-orchestrator` to start or resume the SDLC workflow.

## Agent Prompts Location

- Orchestrator: `.sdlc/framework/agents/orchestrator.md`
- Stage agents: `.sdlc/framework/agents/stage/*.md`
- Subagents: `.sdlc/framework/agents/sub/**/*.md`
- References: `.sdlc/framework/references/*.md`
- Skills: `.sdlc/framework/skills/*.md`
