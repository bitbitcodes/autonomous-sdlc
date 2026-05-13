# Changelog

All notable changes to the Autonomous SDLC Framework.

## [1.1.0] - 2026-05-13

### Added
- **LICENSE** — MIT license file
- **CONTRIBUTING.md** — Contribution guidelines, development setup, commit convention
- **Documentation** (`docs/`) — 11 comprehensive docs with Mermaid diagrams:
  - Getting Started, Architecture, Agents, SDLC Phases, Quality Gates, Memory System, CLI Reference, IDE Integrations
  - **Usage Guide** — End-to-end usage: agent dropdown workflow, CLI start, spec formats, monitoring, multi-session, troubleshooting
  - **JIRA Workflow** — 3 approaches: paste in chat, export to file, MCP server auto-fetch
  - **MCP Integrations** — JIRA, GitHub, Database, and other MCP server setup per IDE
- **Example** — `examples/sample-jira-epic.md` — Realistic JIRA epic with 5 stories, acceptance criteria, tech context
- `.sdlc/framework/` subfolder — Isolates installed framework files from runtime state
- **MCP-aware orchestrator** — Orchestrator prompt detects and uses JIRA/GitHub/Linear MCP tools to fetch specs directly
- **Agent dropdown workflow** — Primary usage path: select `sdlc.orchestrator` → paste spec → go

### Changed
- All agent/reference/skill paths now use `.sdlc/framework/` prefix
- README "After Initialization" expanded with Option A (agent dropdown) and Option B (CLI start)
- README updated with Documentation and Contributing sections
- Orchestrator bootstrap now supports 5 spec input methods: chat paste, existing spec, MCP tools, file scan, user prompt

### Removed
- `install.sh` — Replaced by Python CLI (`sdlc init`)
- `__pycache__/` directories cleaned

## [1.0.0] - 2026-05-13

### Added
- Initial release of the Autonomous SDLC Framework
- **Orchestrator Agent** — Parent agent controlling full SDLC workflow
- **9 Stage Agents** — Product, Architecture, Backlog, Development, Testing, Security, Review, DevOps, Observability
- **25 Subagents** — Specialized workers for focused tasks within each stage
- **RARV Cycle** — Reason-Act-Reflect-Verify workflow pattern
- **10 Quality Gates** — Phase transition enforcement
- **3-Tier Memory System** — Episodic, semantic, and learnings memory
- **CONTINUITY.md** — Working memory protocol for session persistence
- **Structured Prompting** — GOAL/CONSTRAINTS/CONTEXT/OUTPUT template standard
- **Blind Review System** — 3 parallel reviewers with anti-sycophancy check
- **Shell Runner** (`run.sh`) — Initialize, start, status, reset commands
- **IDE-Agnostic** — Works with Windsurf, Cursor, Claude Code, Copilot, Aider
- **Example Specs** — Sample PRD, YAML spec, and one-liner brief
- **AGENTS.md** — OpenAI/AAIF agent discovery standard
- **Reference Docs** — Core workflow, SDLC phases, agent types, memory system, quality control
- **Skill Modules** — Structured prompting, agent dispatch, quality gates, testing strategy
- **Templates** — Stage agent, subagent, and handoff templates
