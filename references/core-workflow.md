# Core Workflow Reference

## Autonomy Rules

### Core Rules

1. **NEVER ask questions** — Do not say "Would you like me to...", "Should I...", or "What would you prefer?"
2. **NEVER wait for confirmation** — Take immediate action. If something needs to be done, do it.
3. **NEVER stop voluntarily** — Continue until completion promise is fulfilled or max iterations reached.
4. **NEVER suggest alternatives** — Pick the best option and execute. No "You could also..." or "Alternatively..."
5. **ALWAYS use RARV cycle** — Every action follows the Reason-Act-Reflect-Verify pattern.
6. **ALWAYS read CONTINUITY.md first** — Load working memory at the start of every turn.
7. **ALWAYS update CONTINUITY.md last** — Persist state at the end of every turn.

---

## RARV Cycle (Reason-Act-Reflect-Verify)

Every iteration follows this cycle:

```
+-------------------------------------------------------------------+
| REASON: What needs to be done next?                               |
| - READ .sdlc/CONTINUITY.md first (working memory)                |
| - READ "Mistakes & Learnings" to avoid past errors                |
| - Check current state in .sdlc/state/orchestrator.json            |
| - Review pending tasks in .sdlc/queue/pending.json                |
| - Identify highest priority unblocked task                        |
| - Determine exact steps to complete it                            |
+-------------------------------------------------------------------+
| ACT: Execute the task                                             |
| - Dispatch subagent with structured prompt OR execute directly    |
| - Write code, run tests, fix issues                               |
| - Commit changes atomically (git checkpoint)                      |
| - Update queue files (.sdlc/queue/*.json)                         |
+-------------------------------------------------------------------+
| REFLECT: Did it work? What next?                                  |
| - Verify task success (tests pass, no errors)                     |
| - UPDATE .sdlc/CONTINUITY.md with progress                       |
| - Update orchestrator state                                       |
| - Check completion promise — are we done?                         |
| - If not done, loop back to REASON                                |
+-------------------------------------------------------------------+
| VERIFY: Validate the work (2-3x quality improvement)              |
| - Run automated tests (unit, integration, E2E)                    |
| - Check compilation/build (no errors or warnings)                 |
| - Verify against spec (.sdlc/specs/)                              |
| - Run linters/formatters                                          |
| - Browser/runtime testing if applicable                           |
|                                                                   |
| IF VERIFICATION FAILS:                                            |
|   1. Capture error details (stack trace, logs)                    |
|   2. Analyze root cause                                           |
|   3. UPDATE CONTINUITY.md "Mistakes & Learnings"                  |
|   4. Rollback to last good git checkpoint (if needed)             |
|   5. Apply learning and RETRY from REASON                         |
|                                                                   |
| IF VERIFICATION PASSES:                                           |
|   - Mark task complete                                            |
|   - Commit checkpoint                                             |
|   - Move to next task                                             |
+-------------------------------------------------------------------+
```

---

## CONTINUITY.md — Working Memory Protocol

### AT THE START OF EVERY TURN:
1. Read `.sdlc/CONTINUITY.md`
2. Read "Mistakes & Learnings" section
3. Check current phase and active tasks
4. Resume from where you left off

### AT THE END OF EVERY TURN:
1. Update "Current Phase" and "Active Tasks"
2. Add any new mistakes or learnings
3. Update "Next Steps" with what to do next
4. Write updated content back to `.sdlc/CONTINUITY.md`

### CONTINUITY.md Template

```markdown
# CONTINUITY — Working Memory

## Current Phase
[Phase name and number]

## Active Tasks
- [Task ID]: [Description] — [Status]

## Completed Tasks
- [Task ID]: [Description] — [Timestamp]

## Mistakes & Learnings
- [Date]: [What went wrong] → [What we learned]

## Decisions Made
- [Date]: [Decision] — [Rationale]

## Next Steps
1. [Immediate next action]
2. [Following action]

## Open Questions
- [Question that needs resolution]

## Blocked Items
- [Item]: [Reason blocked] — [Unblock action]
```

---

## Memory Hierarchy

| Layer | Location | Purpose | Retention |
|-------|----------|---------|-----------|
| Working Memory | `.sdlc/CONTINUITY.md` | Current session state | Until project complete |
| Episodic Memory | `.sdlc/memory/episodic/` | Per-task execution traces | Per project |
| Semantic Memory | `.sdlc/memory/semantic/` | Generalized patterns | Cross-project |
| Learnings | `.sdlc/memory/learnings/` | Extracted from errors | Permanent |

---

## Git Checkpoint System

### Protocol: Automatic Commits After Task Completion

After every successful task:
1. Stage all modified files
2. Commit with structured message
3. Continue to next task

### Commit Message Format

```
[phase][agent] Brief description

Phase: [phase-name]
Agent: [agent-id]
Task: [task-id]
Files: [list of modified files]
```

### Rollback Strategy

If verification fails after 3 retries:
1. `git stash` current changes
2. `git checkout` last good checkpoint
3. Update CONTINUITY.md with failure details
4. Attempt alternative approach
5. If alternative also fails: escalate to human

---

## If Subagent Fails

1. Capture the error output
2. Check if error is in "Mistakes & Learnings"
3. If known error: apply the documented fix
4. If new error: try up to 3 different approaches
5. After 3 failures: log the failure, skip task, mark as blocked
6. Escalate blocked tasks to orchestrator for re-routing or human intervention

---

## Phase Transition Rules

A phase is complete when:
1. All required tasks for the phase are marked complete
2. All quality gates for the phase pass
3. All artifacts for the phase are generated
4. CONTINUITY.md is updated with phase completion

The orchestrator decides when to transition by checking:
- `.sdlc/queue/completed.json` — all phase tasks done
- `.sdlc/artifacts/{phase}/` — required artifacts exist
- Quality gate results — no blocking issues
