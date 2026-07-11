# Changelog

All notable changes to the Autonomous SDLC Framework.

## [Unreleased]

### Added
- **Phase presets** — `sdlc phases --preset <name>` applies a phase-config profile in one command. `lean` enables the common core (Product, Story-Tasks, Architecture, Design, Development, Testing, Review, DevOps + always-on Bootstrap) and disables Problem Discovery, Security, Observability, and Retirement; `full` enables everything (same as `--reset`). Non-breaking and opt-in: `sdlc init` and `--reset` still ship every stage enabled, and applying a preset preserves per-subagent selections so re-enabling a stage restores its subagents. Documented in `docs/cli-reference.md`.

### Fixed
- **Dashboard interaction map no longer shows Phase 12 (Retirement) prematurely.** The map now skips phases with status `'not_triggered'` as well as `'pending'`, so the triggered-only Retirement phase only appears once it's actually running. On a fresh run the map correctly shows "No agent interactions recorded yet."
- **Fixed `SyntaxWarning` in `dashboard_html.py`.** Double-escaped JavaScript regex backslashes (`\s` → `\\s`, `\d` → `\\d`) in the embedded template so Python doesn't interpret them as invalid escape sequences, while preserving Unicode escapes (`\u2B1C`) for JavaScript to render status icons correctly.
- **Orchestrator now runs phases continuously instead of stopping after each one.** Added an explicit "Continuous Execution" directive to the orchestrator prompt (`agents/orchestrator.md`, `templates/commands/orchestrator.md`) and Copilot instructions (`templates/copilot-instructions.md`): after a gate passes, advance to the next phase in the same turn; never end the turn or park the next phase as a todo; in turn-based IDEs (e.g. GitHub Copilot) resume automatically from `CONTINUITY.md` on interruption. Only stop on completion, a 3× gate failure, a Phase 0 NO-GO, a pending approval, or budget exceeded. Also documents raising VS Code's `chat.agent.maxRequests` so Copilot runs more phases before pausing.
- **`token-usage.json` guidance for runtimes without token counts.** The orchestrator now records a reasonable estimate (≈ chars/4, attributed by phase/agent) when exact token counts aren't exposed (e.g. Copilot), so `sdlc cost-report` isn't perpetually zero.
- **`sdlc phases --disable/--enable` now validate stage-ids/subagent-ids.** Previously an invalid id (e.g. `--disable DevOps` instead of `stage-devops`) was silently accepted as a no-op with exit 0. It now errors with exit 1 and lists the valid ids. Added a **Valid stage-ids** table to the `sdlc phases` section of `docs/cli-reference.md`.
- **Dashboard, `sdlc status`, and the agent interaction map now respect `phase-config.json`.** `sdlc dashboard` (phase-progress pills, stats, queue, interaction map panel), the `sdlc status` Phase Progress table, and the Mermaid `agent-map.md` (dashboard diagram + `sdlc status`/`sdlc trace --diagram`) previously rendered every phase from `orchestrator.json`/the full registry, ignoring disabled phases. Disabled phases are now **hidden** everywhere (the `status` table prints an "N phase(s) hidden" hint), so `sdlc phases --preset lean` (or any `--disable`) is reflected consistently. The dashboard payload gained a `phase_enabled` map and now watches `phase-config.json` for live updates.

## [4.0.0] - 2026-07-09

Complete lifecycle (birth-to-death), realistic cost evaluation, AI governance, and Gartner 2028 cost-sustainability adaptations. 40 → 52 agents, 11 → 13 phases.

### Added
- **Configurable phases/subagents** — new `.sdlc/phase-config.json` and `sdlc phases` CLI (`--disable`, `--enable`, `--disable-sub`, `--enable-sub`, `--edit`, `--reset`) let users disable entire stages (e.g. `stage-security`, `stage-devops`) or individual subagents within a stage (e.g. `stage-testing:sub-regression-test`). The orchestrator checks this config before every stage/subagent dispatch (`agents/orchestrator.md` Stage/Subagent Dispatch Protocol step 0), skipping disabled work entirely — no dispatch, no quality gate, no per-phase review. Disabled phases are marked `"skipped"` (not `"pass"`/`"fail"`) in `orchestrator.json`. Opt-in and additive: absent config = all stages/subagents enabled (v3.0/v4.0-compatible default). Phase 1 (Bootstrap) is never configurable. New module `src/sdlc_cli/phases.py`; written by `scaffold.py` on `sdlc init` alongside `model-config.json`.
- **Phase 0: Problem Discovery** — new `stage-problem-discovery` agent + 4 subagents (`sub-problem-statement-extractor`, `sub-user-research-synthesizer`, `sub-opportunity-analyzer`, `sub-solution-space-explorer`). Validates the problem before any requirements are written; NO-GO decisions stop the pipeline before Bootstrap. New Quality Gate 0.
- **Phase 12: Retirement** — new `stage-retirement` agent + 4 subagents (`sub-deprecation-planner`, `sub-migration-strategist`, `sub-data-retention-auditor`, `sub-decommission-executor`). Triggered (not run by default) for deprecation, migration, compliant data retention, and decommissioning. New Quality Gate 12.
- **Cross-cutting subagents** — `sub-compliance-validator` (GDPR/HIPAA/SOX/PCI-DSS checks in Phases 5, 8, 12) and `sub-context-optimizer` (CONTINUITY.md compression, ~60% token reduction per pass)
- **Opt-in governance layer** under `.sdlc/governance/`: `risk-policy.yaml` (4-tier risk classification), `budget-policy.yaml`, `token-policy.yaml`, `compliance-policy.yaml`, `execution-policy.yaml`, `adaptive-policy.yaml`, `notification-config.yaml`, `pending-approvals.json`, `decision-log.json`. Skipped entirely if absent — fully backward compatible with v3.0
- **`sdlc cost-report`** — token usage, cost breakdown (base/retry/gate-failure/conversation/review overhead), retry/gate stats, and budget utilization
- **`sdlc explain <DEC-ID>`** — decision explainability from `decision-log.json` (alternatives, rationale, approver, impact)
- **`sdlc approvals list/approve/reject/configure`** — governance approval workflow CLI, resolving entries in `pending-approvals.json` and logging to `decision-log.json`
- **`.sdlc/state/token-usage.json`** — realistic per-run cost tracking (base execution, RARV retries, gate failures, conversation overhead, blind review overhead)
- New artifact directories: `artifacts/problem-discovery/`, `artifacts/compliance/`, `artifacts/retirement/`
- New modules: `cost.py`, `approvals.py`, `explain.py`, `phases.py`
- 13-phase renumbering across `orchestrator.md`, `references/sdlc-phases.md`, `references/quality-control.md`, and all `docs/`
- Full documentation: `docs/governance/`, `docs/lifecycle/`, `docs/evaluation/` (methodology, benchmarks, realistic cost model, cost-benefit analysis, tiered approach, cost optimization guide, 3 case studies), `docs/migration/v3-to-v4-migration-guide.md`

### Changed
- All v3.0 phase numbers shift by +1 (old Phase 0 Bootstrap → new Phase 1, ... old Phase 10 Observability → new Phase 11)
- `AGENT_TIERS` in `models.py` extended with `stage-problem-discovery` and `stage-retirement`
- `scaffold.py` initializes `.sdlc/governance/` and `.sdlc/state/token-usage.json` on `sdlc init`
- Agent/phase counts updated throughout: 40 → 52 agents, 10 → 12 stage agents, 29 → 39 subagents, 11 → 13 quality gates

### Breaking Changes
- Phase numbering shift (see Migration Guide) — scripts referencing `orchestrator.json` phase keys (e.g. `"0-bootstrap"`) must update to the new keys (`"1-bootstrap"`, `"0-problem-discovery"`, etc.)
- See `docs/migration/v3-to-v4-migration-guide.md` for full upgrade steps

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
