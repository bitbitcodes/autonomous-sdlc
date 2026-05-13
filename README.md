# autonomous-sdlc

Bootstrap multi-agent SDLC workflows into any repository.

```
               _____  __    ______
   _____  ____/ / / _/ ____/ ____/
  / ___/ / __  / / / / ___/ /
 (__  ) / /_/ / / / / /  / /___
/____/  \__,_/ /_/  /_/   \____/
```

**autonomous-sdlc** scaffolds 35 AI agents into your project repo to execute the full software development lifecycle — from a spec to production-ready code with tests, security audit, CI/CD, and monitoring.

## Quick Start

```bash
# One-time usage (no install required)
uvx --from git+https://github.com/yourorg/autonomous-sdlc.git sdlc init .

# Or install persistently
pip install git+https://github.com/yourorg/autonomous-sdlc.git
sdlc init .
```

## What It Does

Running `sdlc init` scaffolds everything you need into your repo:

```
your-project/
├── .sdlc-framework/
│   ├── agents/                   # 35 agent prompts (orchestrator + 9 stage + 25 sub)
│   │   ├── orchestrator.md
│   │   ├── stage/*.md
│   │   └── sub/**/*.md
│   ├── references/               # Architecture & workflow docs
│   ├── skills/                   # Skill modules (loaded on demand)
│   ├── templates/                # Agent prompt templates
│   ├── examples/                 # Sample specs (PRD, YAML, brief)
│   └── run.sh                    # Utility runner (status, reset, start)
├── .sdlc/
│   ├── state/                    # Orchestrator phase tracking
│   ├── queue/                    # Task queue (pending/active/completed)
│   ├── memory/                   # 3-tier memory (episodic/semantic/learnings)
│   ├── artifacts/                # Generated outputs per phase
│   ├── specs/                    # Normalized input spec
│   ├── init-options.json         # Saved configuration
│   └── CONTINUITY.md             # Working memory
├── AGENTS.md                     # Agent discovery (OpenAI/AAIF standard)
├── .github/agents/               # (if Copilot selected)
│   └── sdlc.orchestrator.md
├── .windsurf/                    # (if Windsurf selected)
│   ├── workflows/sdlc.orchestrator.md
│   └── rules/sdlc.md
└── .env.example
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

1. Add your spec:
```bash
.sdlc-framework/run.sh start ./your-prd.md
.sdlc-framework/run.sh start "Build a REST API for task management"
```
2. Open your AI IDE and start a conversation
3. The orchestrator activates automatically via `/sdlc.orchestrator`
4. Check status: `.sdlc-framework/run.sh status`

## Agents

### Workflow

```
Spec → Orchestrator → Product → Architecture → Backlog → Development → Testing → Security → Review → DevOps → Observability
```

### Agent Hierarchy

| Tier | Count | Agents |
|------|-------|--------|
| Orchestrator | 1 | SDLC Orchestrator — workflow control, delegation, validation |
| Stage Agents | 9 | Product, Architecture, Backlog, Development, Testing, Security, Review, DevOps, Observability |
| Subagents | 25 | Specialized workers dispatched by each stage agent |

### Subagents by Stage

| Stage | Subagents |
|-------|-----------|
| **Product** | Requirement Parser, Acceptance Criteria Generator, Risk Analyzer, Assumption Extractor |
| **Architecture** | API Designer, Data Model Designer, Integration Planner, NFR Evaluator |
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

Each agent pauses at **quality gates** — 10 gates enforce phase transitions. Failures trigger self-correction: capture error → analyze root cause → update learnings → retry (max 3).

## Development

### Prerequisites

- Python >= 3.11

### Setup

```bash
git clone https://github.com/yourorg/autonomous-sdlc.git
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
- **10 Quality gates** — Must pass before each phase transition
- **3-tier memory** — Episodic (traces), semantic (patterns), learnings (mistakes)
- **Blind review** — 3 parallel reviewers with anti-sycophancy check

## License

MIT
