# Changelog

All notable changes to the Autonomous SDLC Framework.

## [3.0.0] - 2026-05-15

### Added
- **`sdlc trace`** — Agent interaction map CLI. Renders a rich tree showing orchestrator → stage → subagent dispatch hierarchy with input/output artifacts. Options: `--phase N` to filter, `--verify` to cross-check artifacts on disk, `--diagram` to generate Mermaid agent map
- **`sdlc dashboard`** — Real-time web dashboard with live updates via WebSocket. HTTP on port 8420, WebSocket on 8421. Watches orchestrator.json, agent-trace.json, queue files, activity log, and CONTINUITY.md. Dark theme with phase progress pills, agent interaction map, task queue bars, and activity feed
- **`sdlc models`** — Per-agent model routing with 3 capability tiers (reasoning, coding, fast). Default models: claude-opus-4.7, claude-sonnet-4.6, claude-haiku-4.5. Config stored in `.sdlc/model-config.json`. Options: `--edit` to open in $EDITOR, `--reset` to restore defaults
- **`sdlc run`** — Multi-run management for isolating separate specs/use-cases within a single project. Subcommands: `new` (auto-generates slug from spec content), `list`, `switch`, `active`, `archive`. Shared framework at `.sdlc/framework/`; per-run isolated state, queue, memory, artifacts, specs, and CONTINUITY.md
- **`sdlc upgrade`** — Update installed framework files (agents, references, skills, templates, examples, run.sh) to the latest version. Option: `--dry-run` to preview changes
- **Mermaid agent diagram** — Auto-generated flowchart TD with subgraphs per phase for all 40 agents. Status colors (green/yellow/gray) and model badges from model-config.json. Written to `state/agent-map.md` by `sdlc status` and `sdlc trace --diagram`. Rendered in dashboard via mermaid.js CDN
- **`--run <slug>` flag** added to `status`, `trace`, and `dashboard` commands to target a specific run
- **`agent-trace.json`** schema and trace logging added to orchestrator and all 10 stage agents
- **`model-config.json`** committed configuration file for per-agent model routing
- New modules: `runs.py`, `mermaid.py`, `dashboard.py`, `dashboard_html.py`

### Fixed
- JSON corruption recovery via `raw_decode` fallback in state file parsing
- Stale phase numbers in `docs/mcp-integrations.md` and `docs/jira-workflow.md` (not updated during 2.0.0 renumbering)
- Agent count references: "35 agents" → "40 agents" in `pyproject.toml` and `docs/usage-guide.md`
- Model tier defaults in `docs/cli-reference.md` now match actual code in `models.py`
- Version bumped from 1.1.0 to 3.0.0 across `version.py`, `pyproject.toml`, and `run.sh`

## [2.1.0] - 2026-05-13

### Changed
- **API Designer** renamed to **Interface Designer** (`sub-interface-designer`) — now designs interface contracts appropriate to the project type (OpenAPI for APIs, CLI specs, UI component specs, event catalogs, protocol definitions, etc.)
- **Data Model Designer** broadened to handle all storage types: relational databases, NoSQL, file-based storage, in-memory state, event stores, ML feature stores
- **Integration Planner** broadened to cover all integration types: API calls, message queues, IPC, file I/O, SDK calls, hardware interfaces, plugin systems
- **Tech Stack Advisor** example template broadened to show multiple project types (API, CLI, frontend, mobile, ML, library, desktop)
- **Solution Evaluator** example changed from API-style comparison to architecture-style comparison (Monolith vs Microservices vs Serverless)
- **Gate 5 (Design Completeness)** generalized: "valid interface contracts for project type" instead of "valid OpenAPI 3.x"
- All quality gates, references, skills, docs, and registries updated for project-type-aware language
- Artifact path `api-contracts.yaml` replaced with `interface-contracts.*` (extension varies by project type)
- Observability health checks broadened beyond HTTP endpoints to include heartbeats, status commands, etc.

### Removed
- `agents/sub/design/api-designer.md` — Replaced by `agents/sub/design/interface-designer.md`

## [2.0.0] - 2026-05-13

### Added
- **Phase 2: Story-Tasks** — New phase with 3 subagents (Story Writer, Task Decomposer, Dependency Mapper) for epic/story/task decomposition and dependency graph generation
- **Phase 4: Design** — New phase with 4 subagents (Interface Designer, Data Model Designer, Integration Planner, NFR Evaluator) for detailed technical design referencing ADRs
- **Architecture subagents (ADR-focused)** — 3 new subagents: Tech Stack Advisor, Solution Evaluator, ADR Writer
- **Per-phase review** — After every phase (except Phase 0 and Phase 8), 3 blind reviewers assess that phase's artifacts before advancing
- **`review` field in orchestrator.json** — Tracks per-phase review status alongside gate status
- **11 quality gates** — New gates for Story-Task Traceability (Gate 3) and Design Completeness (Gate 5)

### Changed
- **BREAKING:** Phase numbering changed from 0–9 to 0–10 (11 phases total)
- **BREAKING:** `orchestrator.json` phase keys renamed (e.g., `2-architecture` → `3-architecture`, `3-backlog` → removed)
- **Architecture phase** refocused on high-level system design, tech stack selection, and ADR authoring (was: detailed design + API contracts)
- **Backlog phase** renamed to **Story-Tasks** with 3 production-grade subagents (was: no subagents)
- Agent count: 35 → 40 (1 orchestrator + 10 stage agents + 29 subagents)
- Phase 5–10 renumbered: Development (4→5), Testing (5→6), Security (6→7), Review (7→8), DevOps (8→9), Observability (9→10)
- All stage agent prompts updated with correct phase numbers, artifact paths, and gate references
- Orchestrator prompt updated for 11-phase flow and per-phase review protocol
- All IDE templates updated (Windsurf, Copilot, Claude, Cursor, Gemini, opencode, generic)
- All documentation updated (README, agents, phases, quality-gates, architecture, usage-guide, jira-workflow, getting-started, cli-reference)
- CLI scaffold (`scaffold.py`, `__init__.py`) updated with new artifact directories and phase maps
- `run.sh` updated: artifact dirs, orchestrator.json init, STATUS.md dashboard, status display
- AGENTS.md and agents-md-template.md updated with new agent registry
- References (sdlc-phases.md, agent-types.md, quality-control.md) and skills (quality-gates.md) rewritten

### Removed
- `agents/stage/backlog.md` — Replaced by `agents/stage/story-tasks.md`
- `agents/sub/architecture/{api-designer,data-model-designer,integration-planner,nfr-evaluator}.md` — Moved to `agents/sub/design/`
- `artifacts/backlog/` directory — Replaced by `artifacts/story-tasks/`

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
- **`sdlc status` CLI command** — Rich console dashboard showing phases, agents, queue, activity log, and working memory
- **`.sdlc/STATUS.md`** — Tabular agent dashboard with 4 tables: overall progress, phase & agent status, subagent detail, artifacts produced
- **`.sdlc/state/activity-log.md`** — Chronological log of every agent dispatch, action, and artifact produced
- **Framework compliance guardrails** — Command template and IDE rules now enforce "DO NOT skip phases" with explicit state update requirements

### Fixed
- `run.sh init` nested `.sdlc/` directory bug — `SDLC_DIR` now resolves relative to project root, not CWD
- `run.sh` version updated from `1.0.0` to `1.1.0`
- Stale "NEXT STEP" box now shows IDE-specific agent dropdown instructions
- CONTINUITY.md template paths updated to use `.sdlc/framework/agents/`

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
