# Memory System Reference

## Core Insight: Memory Over Reasoning

Memory is more valuable than reasoning. An agent that remembers its mistakes and patterns outperforms one with better reasoning but no memory. Every error captured in memory prevents the same error in every future iteration.

---

## Memory Hierarchy Overview

| Layer | Purpose | Location | Persistence |
|-------|---------|----------|-------------|
| Working Memory | Current session state | `.sdlc/CONTINUITY.md` | Per session (overwritten each turn) |
| Episodic Memory | Per-task execution traces | `.sdlc/memory/episodic/` | Per project |
| Semantic Memory | Generalized patterns and facts | `.sdlc/memory/semantic/` | Cross-project (portable) |
| Learnings | Mistakes and corrections | `.sdlc/memory/learnings/` | Permanent |

---

## Directory Structure

```
.sdlc/memory/
├── episodic/
│   ├── {date}/
│   │   ├── task-001.json      # Full trace of task execution
│   │   └── task-002.json
│   └── index.json             # Temporal index for retrieval
│
├── semantic/
│   ├── patterns.json          # Generalized patterns (what works)
│   ├── anti-patterns.json     # What NOT to do
│   └── facts.json             # Domain knowledge
│
└── learnings/
    ├── {date}.json            # Daily learning extractions
    └── index.json             # Searchable learning index
```

---

## Episodic Memory Schema

Each task execution creates an episodic trace:

```json
{
  "id": "ep-2026-01-15-001",
  "task_id": "task-042",
  "timestamp": "2026-01-15T10:30:00Z",
  "duration_seconds": 342,
  "agent": "sub-code-generator",
  "phase": "development",
  "context": {
    "goal": "Implement POST /api/todos endpoint",
    "constraints": ["No third-party deps", "< 200ms response"],
    "files_involved": ["src/routes/todos.ts", "src/db/todos.ts"]
  },
  "action_log": [
    {"t": 0, "action": "read_file", "target": "interface-contracts.yaml"},
    {"t": 5, "action": "write_file", "target": "src/routes/todos.ts"},
    {"t": 120, "action": "run_test", "result": "fail", "error": "missing return type"},
    {"t": 140, "action": "edit_file", "target": "src/routes/todos.ts"},
    {"t": 180, "action": "run_test", "result": "pass"}
  ],
  "outcome": "success",
  "errors_encountered": [
    {
      "type": "TypeScript compilation",
      "message": "Missing return type annotation",
      "resolution": "Added explicit :void to route handler"
    }
  ],
  "artifacts_produced": ["src/routes/todos.ts", "tests/todos.test.ts"],
  "git_commit": "abc123"
}
```

---

## Semantic Memory Schema

Generalized patterns extracted from episodic memory:

```json
{
  "id": "sem-001",
  "pattern": "Express route handlers require explicit return types in strict mode",
  "category": "typescript",
  "conditions": [
    "Using TypeScript strict mode",
    "Writing Express route handlers"
  ],
  "correct_approach": "Add `: void` to handler signature",
  "incorrect_approach": "Omitting return type annotation",
  "confidence": 0.95,
  "source_episodes": ["ep-2026-01-15-001"],
  "usage_count": 1,
  "last_used": "2026-01-15T14:00:00Z"
}
```

### Anti-Pattern Schema

```json
{
  "id": "anti-001",
  "pattern": "Never use string concatenation for SQL queries",
  "category": "security",
  "why": "SQL injection vulnerability",
  "correct_alternative": "Use parameterized queries or ORM",
  "severity": "critical",
  "source_episodes": ["ep-2026-01-15-003"]
}
```

---

## Learnings Schema

Extracted from task failures and corrections:

```json
{
  "id": "learn-001",
  "date": "2026-01-15",
  "agent": "sub-code-generator",
  "task_id": "task-042",
  "what_went_wrong": "Route handler missing return type caused build failure",
  "root_cause": "TypeScript strict mode enforces return type annotations",
  "fix_applied": "Added :void to async handler signature",
  "prevention_rule": "Always add return type annotations to Express handlers",
  "applicable_to": ["typescript", "express", "route-handlers"]
}
```

---

## Memory Retrieval

### Before Task Execution

At the start of every task, the agent should:

1. **Check learnings** — Search `.sdlc/memory/learnings/` for entries matching the task category
2. **Check semantic patterns** — Look for applicable patterns in `.sdlc/memory/semantic/patterns.json`
3. **Check anti-patterns** — Verify no known anti-patterns apply to the planned approach
4. **Check episodic** — Find similar past tasks for reference

### Retrieval Strategy by Task Type

| Task Type | Memory Priority |
|-----------|----------------|
| Code generation | Learnings > Semantic patterns > Episodic traces |
| Bug fixing | Learnings > Anti-patterns > Episodic traces |
| Architecture | Semantic patterns > Anti-patterns > Learnings |
| Testing | Semantic patterns > Learnings > Episodic traces |
| Security review | Anti-patterns > Learnings > Semantic patterns |

---

## Memory Maintenance

### After Task Completion

1. Write episodic trace to `.sdlc/memory/episodic/{date}/`
2. If errors occurred: extract learnings to `.sdlc/memory/learnings/`
3. If new pattern discovered: add to `.sdlc/memory/semantic/patterns.json`
4. If anti-pattern encountered: add to `.sdlc/memory/semantic/anti-patterns.json`

### Consolidation (End of Phase)

At the end of each SDLC phase:
1. Review all episodic traces from the phase
2. Extract recurring patterns → semantic memory
3. Identify repeated mistakes → consolidated learnings
4. Update CONTINUITY.md with phase summary

---

## Integration with CONTINUITY.md

CONTINUITY.md is the **working memory** — fast-access current state. It references deeper memory:

```markdown
# CONTINUITY — Working Memory

## Mistakes & Learnings
- Loaded from .sdlc/memory/learnings/
- Updated after every error

## Applicable Patterns
- Loaded from .sdlc/memory/semantic/patterns.json
- Filtered for current task context
```

### How They Work Together

1. CONTINUITY.md = what you need right now (this session)
2. Episodic memory = what happened (task traces)
3. Semantic memory = what you know (general patterns)
4. Learnings = what you got wrong (mistake prevention)
