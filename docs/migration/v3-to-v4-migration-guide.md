# Migration Guide: v3.0 → v4.0

## Breaking Changes

1. **Phase numbering shift** — every v3.0 phase number increases by 1 (old Phase 0 Bootstrap → new Phase 1, old Phase 1 Product → new Phase 2, etc). New Phase 0 (Problem Discovery) and Phase 12 (Retirement) are added at the bookends.
2. **New optional governance files** — `.sdlc/governance/` with policy YAMLs. Fully opt-in; absence = v3.0-compatible behavior.
3. **Token tracking** — `.sdlc/state/token-usage.json` is now initialized for every run; agents are expected to log usage, but tracking gracefully degrades to zeros if unavailable.
4. **Model routing additions** — new agent IDs (`stage-problem-discovery`, `stage-retirement`) added to `model-config.json`'s `agent_tiers`. Existing entries are untouched.

## Migration Steps

### 1. Backup existing runs

```bash
cp -r .sdlc/runs .sdlc/runs.backup   # if using multi-run
cp -r .sdlc .sdlc.backup             # single-run
```

### 2. Upgrade the framework

```bash
sdlc upgrade
```

This refreshes `agents/`, `references/`, `skills/` in `.sdlc/framework/` to the v4.0 versions (12 stage agents, 39 subagents). Runtime state (`state/`, `queue/`, `memory/`, `artifacts/`) is left untouched.

### 3. Opt into governance (optional)

Governance files are only created by `sdlc init` on a fresh project. To add governance to an existing v3.0 project:

```bash
sdlc init --here --force   # re-run init; existing runtime state is preserved,
                            # only missing files (like .sdlc/governance/) are added
```

Then review and edit:
- `.sdlc/governance/risk-policy.yaml`
- `.sdlc/governance/budget-policy.yaml`
- `.sdlc/governance/compliance-policy.yaml`

### 4. Update custom scripts

If you have scripts or CI checks referencing phase numbers (e.g. `orchestrator.json` phase keys like `"0-bootstrap"`), update them to the new keys (`"1-bootstrap"`, `"0-problem-discovery"`, etc — see `references/sdlc-phases.md`).

### 5. Test with a sample feature

Run a simple feature through the new pipeline end to end. Verify:
- Phase 0 produces a GO decision before Bootstrap runs
- `sdlc status` shows all 13 phases correctly
- `sdlc cost-report` (if governance enabled) shows non-zero tracking

## Backward Compatibility

- **Governance is opt-in** — existing v3.0 projects without `.sdlc/governance/` behave exactly as before.
- **Runs in progress** continue with their existing phase numbering; new runs use the v4.0 13-phase scheme.
- **Model routing is configurable** — new agent tiers can be reverted to a single model via `sdlc models`.
