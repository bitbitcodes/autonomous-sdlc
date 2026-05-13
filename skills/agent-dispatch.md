# Agent Dispatch & Handoff

How agents are dispatched, how they communicate, and how work is handed off between them.

---

## Dispatch Protocol

### Orchestrator → Stage Agent

```
1. Read agents/stage/{phase}.md
2. Adopt the stage agent's role and persona
3. Load relevant context (CONTINUITY.md, previous phase artifacts)
4. Execute the stage following RARV cycle
5. On completion: run quality gate, update state, handoff to next stage
```

### Stage Agent → Subagent

```
1. Read agents/sub/{stage}/{subagent}.md
2. Prepare structured prompt (GOAL/CONSTRAINTS/CONTEXT/OUTPUT)
3. Adopt the subagent's role
4. Execute the focused task
5. Validate output against quality criteria
6. Return artifacts to stage agent
7. Resume stage agent role
```

---

## Execution Modes

### Sequential (Default)
Stage agents run one at a time in phase order. Simple, reliable, no coordination needed.

```
Product → Architecture → Backlog → Development → Testing → Security → Review → DevOps → Observability
```

### Parallel Subagents
Within a stage, independent subagents can run in parallel. The stage agent collects all outputs before proceeding.

```
Stage: Security
  ├── Secret Scanner     ─┐
  ├── Dependency Scanner  ├── All run in parallel
  ├── OWASP Reviewer     ─┤
  └── Policy Validator   ─┘
       │
       ▼
  Aggregate findings
```

### When to Parallelize
- Subagents have NO dependencies on each other's output
- Each produces independent artifacts
- Stage agent can aggregate results after all complete

### When NOT to Parallelize
- Subagent B needs Subagent A's output (e.g., Code Generator needs Repo Analyzer results)
- Order matters (e.g., Requirement Parser before Acceptance Criteria Generator)

---

## Handoff Format

When one agent completes and hands off to another:

```json
{
  "from": "<agent-id>",
  "to": "<next-agent-id>",
  "phase": "<phase-name>",
  "timestamp": "<ISO-8601>",
  "completed_work": "<summary of what was accomplished>",
  "artifacts_produced": [
    "<file-path-1>",
    "<file-path-2>"
  ],
  "decisions_made": [
    "<decision-1: rationale>",
    "<decision-2: rationale>"
  ],
  "open_questions": [
    "<question that the next agent should be aware of>"
  ],
  "mistakes_learned": [
    "<error encountered and how it was resolved>"
  ]
}
```

---

## Confidence-Based Routing

When dispatching a subagent, assess confidence in successful execution:

| Confidence | Strategy |
|-----------|----------|
| ≥ 0.90 | Execute directly, skip detailed review |
| 0.70-0.89 | Execute, then verify output |
| 0.40-0.69 | Execute with extra context, mandatory review |
| < 0.40 | Flag for human decision |

### Confidence Factors
- **Requirement clarity** (30%) — Is the task well-defined?
- **Pattern match** (25%) — Have we done this before? (check memory)
- **Complexity** (25%) — How complex is the task?
- **Dependencies** (20%) — Are all dependencies met?

---

## Error Handling

### Subagent Failure Protocol

```
Subagent fails
    │
    ▼
Capture error output
    │
    ▼
Check .sdlc/memory/learnings/ for known fix
    │
  ┌─▼──────┐
  │ Known?  │
  └─┬──────┘
  YES│    NO
    │     │
    ▼     ▼
Apply   Analyze error
fix     Try alternative
    │     │
    ▼     ▼
Retry  Retry (max 3 total)
    │     │
    ▼     ▼
Pass?  Still failing?
    │     │
    ▼     ▼
Done   Log learning
       Mark BLOCKED
       Continue with remaining subagents
       Escalate blocked items to stage agent
```

### Retry Rules
- **Max 3 retries** per subagent per task
- Each retry should use a **different approach** (not identical re-run)
- **Log the error** before retrying (to prevent loops)
- After 3 failures: **skip and mark as blocked**

---

## State Updates

After every dispatch completion, update these files:

1. **`.sdlc/CONTINUITY.md`** — Current phase, active tasks, progress
2. **`.sdlc/state/orchestrator.json`** — Phase status, agent status
3. **`.sdlc/queue/`** — Move tasks between pending/active/completed
4. **`.sdlc/memory/`** — Log episodic trace, extract learnings if errors

---

## Agent Communication Pattern

Agents do NOT communicate directly with each other. All communication flows through:

1. **Artifacts** — Agents read previous agents' output files
2. **CONTINUITY.md** — Shared working memory
3. **Queue files** — Task state coordination
4. **Handoff records** — Explicit context transfer

This design ensures agents are independent, replaceable, and debuggable.
