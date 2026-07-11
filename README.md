[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/bitbitcodes-autonomous-sdlc-badge.png)](https://mseep.ai/app/bitbitcodes-autonomous-sdlc)

# autonomous-sdlc

Bootstrap multi-agent SDLC workflows into any repository.

```
               ___ ___ ____
   _____  ____/ / / / / __/
  / ___/ / __  / / / / /
 (__  ) / /_/ / / / / /___
/____/  \__,_/ /_/  \____/
```

**autonomous-sdlc** scaffolds 52 AI agents into your project repo to execute the full software development lifecycle — from problem validation through production-ready code with tests, security audit, CI/CD, monitoring, and eventual retirement.

## Quick Start

```bash
# One-time usage (no install required)
uvx --from git+https://github.com/bitbitcodes/autonomous-sdlc.git sdlc init .

# Or install persistently
pip install git+https://github.com/bitbitcodes/autonomous-sdlc.git
sdlc init .
```

## What It Does

Running `sdlc init` scaffolds everything into a single `.sdlc/` directory in your repo:

```
your-project/
├── .sdlc/
│   ├── framework/                # Installed by CLI — don't modify
│   │   ├── agents/               #   52 agent prompts (orchestrator + 12 stage + 39 sub)
│   │   ├── references/           #   Architecture & workflow docs
│   │   ├── skills/               #   Skill modules (loaded on demand)
│   │   ├── templates/            #   Agent prompt templates
│   │   ├── examples/             #   Sample specs (PRD, YAML, brief)
│   │   └── run.sh                #   Utility runner (status, reset, start)
│   ├── init-options.json         # Saved configuration
│   ├── state/                    # Runtime (gitignored)
│   │   ├── orchestrator.json     #   Phase progress
│   │   └── activity-log.md       #   Agent action history
│   ├── queue/                    # Runtime (gitignored)
│   ├── memory/                   # Runtime (gitignored)
│   ├── artifacts/                # Runtime (gitignored)
│   ├── specs/                    # Runtime (gitignored)
│   ├── STATUS.md                 # Agent dashboard (gitignored)
│   └── CONTINUITY.md             # Working memory (gitignored)
├── AGENTS.md                     # Agent discovery (OpenAI/AAIF standard)
├── .github/agents/               # (if Copilot selected)
│   └── sdlc.orchestrator.md
├── .devin/                       # (if Devin Desktop selected)
│   ├── workflows/sdlc.orchestrator.md
│   └── rules/sdlc.md
└── ...
```

## Supported AI IDEs

| Integration | Key | Context File | Commands Location |
|-------------|-----|--------------|-------------------|
| GitHub Copilot | `copilot` | `.github/copilot-instructions.md` | `.github/agents/` |
| Devin Desktop | `devin` | `.devin/rules/sdlc.md` | `.devin/workflows/` |
| Claude Code | `claude` | `CLAUDE.md` | `.claude/commands/` |
| Cursor | `cursor-agent` | `.cursor/rules/sdlc.mdc` | `.cursor/rules/` |
| opencode | `opencode` | `.opencode/instructions.md` | `.opencode/commands/` |
| Gemini CLI | `gemini` | `.gemini/GEMINI.md` | `.gemini/commands/` |
| Codex CLI | `codex` | `.codex/instructions.md` | `.codex/commands/` |
| Kilo Code | `kilocode` | `.kilocode/instructions.md` | `.kilocode/commands/` |
| Amp | `amp` | `.amp/instructions.md` | `.amp/commands/` |

## Usage

### Interactive Mode (default)

```bash
sdlc init .
```

This launches an interactive session with:
1. ASCII art banner
2. Arrow-key IDE selector
3. Prompts for project name, tech stack, team size

### Non-Interactive Mode

```bash
sdlc init . \
  --integration devin \
  --project-name "My API" \
  --tech-stack "Python, FastAPI, PostgreSQL" \
  --team-size "3 developers" \
  --non-interactive
```

### CLI Options

| Flag | Description | Default |
|------|-------------|---------|
| `--integration`, `-i` | AI IDE integration key | (interactive) |
| `--project-name`, `--name` | Project name | directory name |
| `--tech-stack` | Tech stack context | (empty) |
| `--team-size` | Team size context | (empty) |
| `--force`, `-f` | Overwrite existing files | `false` |
| `--non-interactive`, `-y` | Skip prompts, use defaults | `false` |
| `--here` | Init in current directory | `false` |

## After Initialization

### Option A: Agent Dropdown (Easiest)

Select the `sdlc.orchestrator` agent in your IDE and paste your spec — a JIRA story, PRD, or even a one-liner — directly into the chat. The orchestrator handles everything: validates the problem is worth solving, bootstraps `.sdlc/`, normalizes your spec, detects complexity, and drives all 13 phases through to production (and retirement, when triggered).

| IDE | How |
|-----|-----|
| **Copilot** | Select `sdlc.orchestrator` from the agent dropdown → paste your spec |
| **Devin Desktop** | Type `/sdlc.orchestrator` in Devin Local chat → paste your spec |
| **Claude Code** | Use `/sdlc-orchestrator` command → paste your spec |
| **Cursor** | Start chat (context auto-loads) → paste your spec |

**Example:** Select the agent, then paste your JIRA story:

```
PROJ-101 User Registration

As a new user, I want to register with email and password.

Acceptance Criteria:
- Given a valid email and password, when I POST /api/v1/auth/register, then a 201 is returned
- Given a duplicate email, when I POST /api/v1/auth/register, then a 409 is returned

Tech Stack: Python, FastAPI, PostgreSQL
```

The orchestrator takes it from there — no other steps needed.

**With JIRA MCP:** If you have a [JIRA MCP server](docs/mcp-integrations.md) configured, just say `Build the feature in JIRA epic PROJ-100` — the orchestrator fetches stories directly from JIRA.

### Option B: CLI Start (For Larger Specs)

For larger specs stored as files (PRD documents, YAML specs, multi-story JIRA epics), use the CLI to pre-load the spec before opening your IDE:

```bash
.sdlc/framework/run.sh start ./prd.md          # Markdown PRD
.sdlc/framework/run.sh start ./spec.yaml        # YAML spec
.sdlc/framework/run.sh start ./jira-epic.md     # JIRA epic (see examples/)
.sdlc/framework/run.sh start "Build a task API" # One-liner
```

Then open your IDE and select the `sdlc.orchestrator` agent — it picks up the pre-loaded spec automatically.

See [`examples/`](examples/) for sample specs including a [JIRA epic example](examples/sample-jira-epic.md).

### Monitor Progress

```bash
sdlc status                       # Rich dashboard — phases, agents, queue, activity log
sdlc trace                        # Agent interaction map (orchestrator → stage → subagent)
sdlc dashboard                    # Real-time web dashboard (http://localhost:8420)
.sdlc/framework/run.sh status     # Shell alternative (no Python install needed)
cat .sdlc/STATUS.md               # Agent dashboard with subagent-level detail
cat .sdlc/CONTINUITY.md           # Current state in plain English
```

### Multi-Session

IDE sessions have token limits. When one ends, just start a new conversation — the orchestrator reads `CONTINUITY.md` and resumes exactly where it left off.

### What You Get

Each phase produces artifacts in `.sdlc/artifacts/<phase>/` — requirements, interface contracts, data models, implementation, test suites, security reports, CI/CD configs, and more. The actual codebase is written directly into your project directory.

> **Full walkthrough:** [Usage Guide](docs/usage-guide.md) · **JIRA users:** [JIRA Workflow](docs/jira-workflow.md)

## CLI Commands

`[TARGET]` is the **project directory** to act on (the folder containing `.sdlc/`). It's **optional** — omit it to use the current directory, or pass a path to target another project (e.g. `sdlc status ./my-app`). Notation: `[...]` = optional, `<...>` = required.

| Command | Description |
|---------|-------------|
| `sdlc init [TARGET]` | Scaffold `.sdlc/` framework into a project directory |
| `sdlc status [TARGET]` | Rich console dashboard — phases, agents, queue, activity log |
| `sdlc trace [TARGET]` | Agent interaction map — tree view of orchestrator → stage → subagent calls |
| `sdlc dashboard [TARGET]` | Real-time web dashboard with live updates (port 8420) |
| `sdlc models [TARGET]` | View/edit per-agent model routing (3 tiers: reasoning, coding, fast) |
| `sdlc phases [TARGET]` | View/enable/disable stages and subagents; `--preset lean\|full` applies a profile |
| `sdlc cost-report [TARGET]` | Token usage, cost breakdown, retry stats, and budget status |
| `sdlc explain <DEC-ID>` | Explain a logged decision — alternatives, rationale, approver, impact |
| `sdlc approvals list\|approve\|reject\|configure` | Manage governance approval requests (risk-policy.yaml gates) |
| `sdlc run <subcommand>` | Multi-run management — isolate separate specs/use-cases |
| `sdlc upgrade [TARGET]` | Update framework files to the latest version |
| `sdlc version` | Show installed version |

### Multi-Run

Isolate multiple SDLC executions within the same project:

```bash
sdlc run new ./feature-spec.md    # Create a new isolated run
sdlc run list                     # List all runs
sdlc run switch <slug>            # Switch active run
sdlc run active                   # Show current active run
sdlc run archive <slug>           # Archive a completed run
```

Commands that read state (`status`, `trace`, `dashboard`) accept `--run <slug>` to target a specific run.

> **Full reference:** [CLI Reference](docs/cli-reference.md)

## Agents

### Workflow

```
Spec → Problem Discovery → Orchestrator (Bootstrap) → Product → Story-Tasks → Architecture → Design →
Development → Testing → Security → Review → DevOps → Observability → (Retirement, when triggered)
```

### Agent Hierarchy

| Tier | Count | Agents |
|------|-------|--------|
| Orchestrator | 1 | SDLC Orchestrator — workflow control, delegation, validation |
| Stage Agents | 12 | Problem Discovery, Product, Story-Tasks, Architecture, Design, Development, Testing, Security, Review, DevOps, Observability, Retirement |
| Subagents | 39 | Specialized workers dispatched by each stage agent, plus cross-cutting compliance/context-optimizer agents |

### Subagents by Stage

| Stage | Subagents |
|-------|-----------|
| **Product** | Requirement Parser, Acceptance Criteria Generator, Risk Analyzer, Assumption Extractor |
| **Story-Tasks** | Story Writer, Task Decomposer, Dependency Mapper |
| **Architecture** | Tech Stack Advisor, Solution Evaluator, ADR Writer |
| **Design** | Interface Designer, Data Model Designer, Integration Planner, NFR Evaluator |
| **Development** | Repo Analyzer, Code Generator, Refactoring Agent, Documentation Agent |
| **Testing** | Unit Test Agent, Integration Test Agent, Regression Test Agent, Test Data Generator |
| **Security** | Secret Scanner, Dependency Scanner, OWASP Reviewer, Policy Validator |
| **Review** | Code Review Agent, Maintainability Reviewer, Performance Reviewer |

### RARV Cycle

Every agent follows: **Reason → Act → Reflect → Verify**

1. **Reason** — Read CONTINUITY.md, check state, identify next task
2. **Act** — Execute task, write code, generate artifacts
3. **Reflect** — Verify success, update working memory
4. **Verify** — Run tests, check spec compliance, enforce quality gates

Each agent pauses at **quality gates** — 13 gates (0-12) enforce phase transitions. After every phase, 3 blind reviewers assess the artifacts before advancing. Failures trigger self-correction: capture error → analyze root cause → update learnings → retry (max 3). Governance is opt-in: if `.sdlc/governance/` policy files are present, HIGH/CRITICAL risk decisions pause for human approval, and budget/token limits are enforced.

## Development

### Prerequisites

- Python >= 3.11

### Setup

```bash
git clone https://github.com/bitbitcodes/autonomous-sdlc.git
cd autonomous-sdlc
pip install -e ".[test,dev]"
```

### Run Tests

```bash
pytest
```

### Lint

```bash
ruff check src/ tests/
```

## Architecture

autonomous-sdlc follows the integration registry pattern:

- **Integration subpackages** — Each AI IDE is a self-contained package in `src/sdlc_cli/integrations/`
- **Base classes** — `IntegrationBase` and `MarkdownIntegration` provide shared behavior
- **Template system** — Markdown templates with `{{PROJECT_NAME}}` placeholders
- **Registry** — Integrations self-register via `@register` decorator

Adding a new IDE integration is a single file in `src/sdlc_cli/integrations/your_ide/__init__.py`.

## Key Concepts

- **Bootstrap into any repo** — Framework installs alongside your code via `sdlc init .`
- **IDE-native integration** — 9 AI IDEs supported with auto-loading context files
- **Markdown-driven** — Every agent is a `.md` file. No framework dependency.
- **CONTINUITY.md** — Working memory read/written every turn for cross-session persistence
- **Structured prompting** — GOAL / CONSTRAINTS / CONTEXT / OUTPUT format
- **13 Quality gates** — Must pass before each phase transition (0: Problem Validated → 12: Retirement Complete), with per-phase blind review
- **Governance (opt-in)** — Risk classification, budget/token limits, human approval gates, compliance validation, and a decision audit trail
- **3-tier memory** — Episodic (traces), semantic (patterns), learnings (mistakes)
- **Blind review** — 3 parallel reviewers with anti-sycophancy check

## Documentation

Full documentation lives in [`docs/`](docs/):

| Document | Description |
|----------|-------------|
| [Getting Started](docs/getting-started.md) | Installation, first run, walkthrough |
| [Usage Guide](docs/usage-guide.md) | End-to-end: feed spec → phases → artifacts |
| [JIRA Workflow](docs/jira-workflow.md) | Using JIRA epics/stories as input |
| [Architecture](docs/architecture.md) | System design, component model, data flow |
| [Agents](docs/agents.md) | All 52 agents — roles, dispatch, handoff |
| [SDLC Phases](docs/phases.md) | 13 phases from problem discovery to retirement |
| [Quality Gates](docs/quality-gates.md) | 13 gates, per-phase blind review, severity model |
| [Memory System](docs/memory-system.md) | 3-tier memory + CONTINUITY.md protocol |
| [CLI Reference](docs/cli-reference.md) | All commands — init, status, trace, dashboard, models, cost-report, explain, approvals, run, upgrade, version |
| [Governance](docs/governance/ai-governance-overview.md) | Risk classification, approvals, budget controls, compliance |
| [Lifecycle](docs/lifecycle/complete-lifecycle-overview.md) | Problem Discovery and Retirement phases |
| [Migration Guide](docs/migration/v3-to-v4-migration-guide.md) | Upgrading from v3.0 to v4.0 |
| [Agent Graph](docs/agent-graph.md) | Full agent hierarchy Mermaid diagram, dispatch patterns, data flow |
| [IDE Integrations](docs/ide-integrations.md) | 9 supported IDEs, adding your own |
| [MCP Integrations](docs/mcp-integrations.md) | JIRA, GitHub, Database MCP setup |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding conventions, and how to add new IDE integrations or agents.

## License

[MIT](LICENSE)
