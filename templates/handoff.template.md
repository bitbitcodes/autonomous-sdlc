# Handoff Template

Use this format when one agent completes work and hands off to the next.

---

## Handoff Record

```json
{
  "from": "<agent-id>",
  "to": "<next-agent-id>",
  "phase": "<phase-name>",
  "timestamp": "<ISO-8601 timestamp>",

  "completed_work": "<1-2 sentence summary of what was accomplished>",

  "artifacts_produced": [
    "<path to artifact 1>",
    "<path to artifact 2>"
  ],

  "decisions_made": [
    "<decision>: <rationale>"
  ],

  "open_questions": [
    "<question that the next agent needs to be aware of>"
  ],

  "mistakes_learned": [
    "<what went wrong> → <how it was fixed>"
  ],

  "quality_gate": {
    "gate_number": 0,
    "status": "PASS",
    "checks_passed": 0,
    "checks_total": 0
  },

  "metrics": {
    "tasks_completed": 0,
    "tasks_failed": 0,
    "retries": 0,
    "duration_seconds": 0
  }
}
```

---

## Usage

### Stage → Stage Handoff
Written by stage agent on phase completion. Read by the next stage agent.

### Subagent → Stage Agent Handoff
Written by subagent on task completion. Read by parent stage agent for aggregation.

---

## Storage

Handoff records are stored in CONTINUITY.md under the "Completed Tasks" section and optionally in `.sdlc/memory/episodic/` for trace purposes.
