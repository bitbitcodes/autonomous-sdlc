# Contributing to autonomous-sdlc

Thanks for your interest in contributing! This guide will help you get started.

## Code of Conduct

Be respectful, constructive, and inclusive. We follow the [Contributor Covenant](https://www.contributor-covenant.org/version/2/1/code_of_conduct/).

## How to Contribute

### Reporting Bugs

1. Search [existing issues](https://github.com/bitbitcodes/autonomous-sdlc/issues) first
2. Open a new issue with:
   - Steps to reproduce
   - Expected vs actual behavior
   - OS, Python version, IDE used
   - Output of `sdlc version`

### Suggesting Features

Open an issue with the `enhancement` label. Include:
- Problem you're solving
- Proposed solution
- Alternatives considered

### Pull Requests

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Make your changes
4. Run checks:
   ```bash
   pip install -e ".[test,dev]"
   pytest
   ruff check src/ tests/
   ```
5. Commit with clear messages (see [Commit Convention](#commit-convention))
6. Open a PR against `main`

## Development Setup

```bash
git clone https://github.com/bitbitcodes/autonomous-sdlc.git
cd autonomous-sdlc
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test,dev]"
```

### Running Tests

```bash
pytest                    # all tests
pytest -x                 # stop on first failure
pytest --cov=sdlc_cli     # with coverage
```

### Linting

```bash
ruff check src/ tests/
ruff format src/ tests/
```

## Project Structure

```
autonomous-sdlc/
├── src/sdlc_cli/               # Python CLI package
│   ├── __init__.py             # Typer app + init command
│   ├── scaffold.py             # Core scaffold/init logic
│   ├── banner.py               # ASCII art banner
│   ├── config.py               # Config persistence
│   ├── version.py              # Version string
│   ├── selector.py             # Interactive arrow-key IDE picker
│   └── integrations/           # IDE integration registry
│       ├── __init__.py         # @register decorator + registry
│       ├── base.py             # IntegrationBase, MarkdownIntegration
│       ├── devin/              # Devin Desktop integration (formerly Windsurf; "windsurf" key kept as alias)
│       ├── copilot/            # GitHub Copilot integration
│       ├── claude/             # Claude Code integration
│       ├── cursor/             # Cursor integration
│       ├── opencode/           # opencode integration
│       ├── gemini/             # Gemini CLI integration
│       ├── codex/              # Codex CLI integration
│       ├── amp/                # Amp integration
│       └── kilocode/           # Kilo Code integration
├── agents/                     # 40 agent prompt files (bundled into package)
├── references/                 # Framework reference docs
├── skills/                     # Skill modules
├── templates/                  # IDE context templates + command templates
├── examples/                   # Sample specs (PRD, YAML, brief)
├── docs/                       # Documentation
├── tests/                      # Test suite
└── pyproject.toml              # Build config + dependencies
```

## Contribution Areas

### Adding a New IDE Integration

This is the easiest way to contribute. Create a new subpackage:

```
src/sdlc_cli/integrations/your_ide/__init__.py
```

Subclass `MarkdownIntegration` and register it:

```python
from ..base import MarkdownIntegration
from .. import register

@register
class YourIdeIntegration(MarkdownIntegration):
    key = "your-ide"
    display_name = "Your IDE Name"
    config = {
        "name": "Your IDE Name",
        "folder": ".your-ide",
        "commands_subdir": "commands",
    }
    context_file = ".your-ide/instructions.md"
```

Then add a context template in `templates/your-ide-instructions.md` if needed.

### Adding a New Agent

1. Create a `.md` file in `agents/stage/` or `agents/sub/<stage>/`
2. Follow the GOAL / CONSTRAINTS / CONTEXT / OUTPUT structure
3. Update `AGENTS.md` and `templates/agents-md-template.md`
4. Update the docs in `docs/`

### Improving Agent Prompts

Agent prompts live in `agents/`. Improvements to prompt quality, error handling, or output format are welcome. Test changes by running `sdlc init` in a scratch directory and verifying the scaffolded prompts.

### Improving Reference Docs

Reference docs in `references/` guide agent behavior. They should be precise, actionable, and avoid ambiguity.

## Commit Convention

```
<type>(<scope>): <short description>

Types: feat, fix, docs, refactor, test, chore
Scopes: cli, agents, integrations, docs, templates
```

Examples:
```
feat(integrations): add JetBrains AI integration
fix(cli): handle missing readchar gracefully
docs(agents): clarify RARV cycle in orchestrator prompt
refactor(scaffold): extract gitignore logic to helper
```

## Release Process

1. Update version in `src/sdlc_cli/version.py` and `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create a git tag: `git tag v1.x.x`
4. Push: `git push origin main --tags`

## Questions?

Open a [discussion](https://github.com/bitbitcodes/autonomous-sdlc/discussions) or reach out in issues.
