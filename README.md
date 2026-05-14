# autonomous-sdlc

Bootstrap multi-agent SDLC workflows into any repository.

```
               _____  __    ______
   _____  ____/ / / _/ ____/ ____/
  / ___/ / __  / / / / ___/ /
 (__  ) / /_/ / / / / /  / /___
/____/  \__,_/ /_/  /_/   \____/
```

**autonomous-sdlc** scaffolds 40 AI agents into your project repo to execute the full software development lifecycle — from a spec to production-ready code with tests, security audit, CI/CD, and monitoring.

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
│   │   ├── agents/               #   40 agent prompts (orchestrator + 10 stage + 29 sub)
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
├── .windsurf/                    # (if Windsurf selected)
│   ├── workflows/sdlc.orchestrator.md
│   └── rules/sdlc.md
└── ...
```

## Supported AI IDEs

| Integration | Key | Context File | Commands Location |
|-------------|-----|--------------|-------------------|
| GitHub Copilot | `copilot` | `.github/copilot-instructions.md` | `.github/agents/` |
| Windsurf | `windsurf` | `.windsurf/rules/sdlc.md` | `.windsurf/workflows/` |
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
  --integration windsurf \
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

Select the `sdlc.orchestrator` agent in your IDE and paste your spec — a JIRA story, PRD, or even a one-liner — directly into the chat. The orchestrator handles everything: bootstraps `.sdlc/`, normalizes your spec, detects complexity, and drives all 11 phases.

| IDE | How |
|-----|-----|
| **Copilot** | Select `sdlc.orchestrator` from the agent dropdown → paste your spec |
| **Windsurf** | Type `/sdlc.orchestrator` in Cascade chat → paste your spec |
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
.sdlc/framework/run.sh status     # Shell alternative (no Python install needed)
cat .sdlc/STATUS.md               # Agent dashboard with subagent-level detail
cat .sdlc/CONTINUITY.md           # Current state in plain English
```

### Multi-Session

IDE sessions have token limits. When one ends, just start a new conversation — the orchestrator reads `CONTINUITY.md` and resumes exactly where it left off.

### What You Get

Each phase produces artifacts in `.sdlc/artifacts/<phase>/` — requirements, interface contracts, data models, implementation, test suites, security reports, CI/CD configs, and more. The actual codebase is written directly into your project directory.

> **Full walkthrough:** [Usage Guide](docs/usage-guide.md) · **JIRA users:** [JIRA Workflow](docs/jira-workflow.md)

## Agents

### Workflow

```
Spec → Orchestrator → Product → Story-Tasks → Architecture → Design → Development → Testing → Security → Review → DevOps → Observability
```

### Agent Hierarchy

| Tier | Count | Agents |
|------|-------|--------|
| Orchestrator | 1 | SDLC Orchestrator — workflow control, delegation, validation |
| Stage Agents | 11 | Product, Story-Tasks, Architecture, Design, Development, Testing, Security, Review, DevOps, Observability |
| Subagents | 31 | Specialized workers dispatched by each stage agent |

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

Each agent pauses at **quality gates** — 11 gates enforce phase transitions. After every phase, 3 blind reviewers assess the artifacts before advancing. Failures trigger self-correction: capture error → analyze root cause → update learnings → retry (max 3).

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
- **11 Quality gates** — Must pass before each phase transition, with per-phase blind review
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
| [Agents](docs/agents.md) | All 40 agents — roles, dispatch, handoff |
| [SDLC Phases](docs/phases.md) | 11 phases from spec to observability |
| [Quality Gates](docs/quality-gates.md) | 11 gates, per-phase blind review, severity model |
| [Memory System](docs/memory-system.md) | 3-tier memory + CONTINUITY.md protocol |
| [CLI Reference](docs/cli-reference.md) | `sdlc init` options, scaffold behavior |
| [IDE Integrations](docs/ide-integrations.md) | 9 supported IDEs, adding your own |
| [MCP Integrations](docs/mcp-integrations.md) | JIRA, GitHub, Database MCP setup |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding conventions, and how to add new IDE integrations or agents.

## License

[MIT](LICENSE)
