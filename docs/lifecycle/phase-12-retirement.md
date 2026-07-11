# Phase 12: Deprecation & Retirement

**Stage Agent:** `stage-retirement` (`agents/stage/retirement.md`)

## Purpose

Safely deprecate and decommission a feature or system: timeline and communication, user migration, compliant data retention, and infrastructure removal — with a post-mortem capturing learnings.

## Triggers

- Explicit "deprecate feature X" request from the user
- A replacement system has been deployed (detected via ADRs referencing this system)
- An end-of-support date has been reached

This phase is **not run by default** — it only executes when triggered.

## Subagents

| Subagent | Role |
|----------|------|
| `sub-deprecation-planner` | Builds a ≥90-day notice timeline and stakeholder communication plan |
| `sub-migration-strategist` | Plans user migration to a replacement system (or graceful removal) |
| `sub-data-retention-auditor` | Validates data deletion against GDPR/HIPAA/compliance-policy.yaml |
| `sub-decommission-executor` | Removes infrastructure and cleans up dependencies — only after approval |

## Dispatch Order

1. Deprecation Planner — sets the timeline
2. Migration Strategist + Data Retention Auditor (parallel)
3. **Approval gate** — decommissioning is classified CRITICAL per `risk-policy.yaml` and requires 2 human sign-offs
4. Decommission Executor — only after approval and notice period elapses

## Artifacts

- `.sdlc/artifacts/retirement/deprecation-plan.md`
- `.sdlc/artifacts/retirement/migration-guide.md`
- `.sdlc/artifacts/retirement/data-retention-policy.md`
- `.sdlc/artifacts/retirement/decommission-checklist.md`
- `.sdlc/artifacts/retirement/post-mortem.md`

## Quality Gate 12: Retirement Complete

- ≥90 days notice published (or emergency approval on record)
- Migration path documented for all affected users
- Data retention complies with active compliance frameworks
- All infrastructure decommissioned or archived
- Post-mortem completed with learnings
- CRITICAL decommission actions have 2 recorded human sign-offs in `decision-log.json`

## Safety Notes

`sub-decommission-executor` will **never** execute irreversible deletion without a recorded governance approval. Archive-then-delete is preferred over direct deletion wherever infrastructure tooling supports it.
