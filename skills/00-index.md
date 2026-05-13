# Skill Modules Index

Skill modules are loaded on demand by agents when they need specialized knowledge. The orchestrator and stage agents reference these files for protocol details.

---

## Module Selection Rules

1. **Always load** `AGENTS.md` and `references/core-workflow.md` first
2. **Load by phase:** Each phase loads the relevant skill module(s)
3. **Load on error:** If an agent encounters an unfamiliar problem, check `skills/` for guidance
4. **Never load all:** Only load what's needed to minimize context window usage

---

## Module Descriptions

### structured-prompting.md
**When:** Dispatching any subagent
- GOAL/CONSTRAINTS/CONTEXT/OUTPUT template
- Structured prompt format standard
- Examples for each section
- Anti-patterns in prompting

### agent-dispatch.md
**When:** Orchestrator dispatching stage agents, stage agents dispatching subagents
- Dispatch protocol
- Handoff format
- Confidence-based routing
- Error handling and retry patterns
- Parallel vs sequential execution rules

### quality-gates.md
**When:** Phase transitions, code review, pre-commit checks
- 10 quality gate definitions
- Gate enforcement protocol
- Severity classification
- Blind review system
- Anti-sycophancy checks

### testing.md
**When:** Writing tests, test strategy, verification
- Unit / integration / regression / E2E strategies
- Coverage targets and measurement
- Test data generation patterns
- Deterministic test requirements
- Acceptance criteria mapping

---

## How to Load

Agents reference skill modules by reading the file:

```
READ skills/{module-name}.md
```

The orchestrator decides which modules to load based on the current phase:

| Phase | Skills Loaded |
|-------|--------------|
| 0 (Bootstrap) | structured-prompting, agent-dispatch |
| 1 (Product) | structured-prompting |
| 2 (Architecture) | structured-prompting |
| 3 (Backlog) | — |
| 4 (Development) | structured-prompting, agent-dispatch |
| 5 (Testing) | testing, structured-prompting |
| 6 (Security) | structured-prompting |
| 7 (Review) | quality-gates, agent-dispatch |
| 8 (DevOps) | — |
| 9 (Observability) | — |
