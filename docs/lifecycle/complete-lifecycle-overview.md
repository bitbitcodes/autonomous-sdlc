# Complete Lifecycle Overview

v4.0 extends the framework from an 11-phase "requirements to production" pipeline to a full **13-phase birth-to-death lifecycle**:

```
Phase 0            Phase 1     Phase 2-11 (unchanged from v3.0, renumbered +1)      Phase 12
Problem Discovery → Bootstrap → Product → ... → Observability                    → Retirement
   (birth)                                                                          (death, triggered)
```

## Why This Matters

Community feedback on v3.0 repeatedly asked two questions:

1. **"Does the agent understand why?"** — v3.0 started at Bootstrap, assuming the problem was already validated. Phase 0 (Problem Discovery) now forces an explicit go/no-go decision before any requirements are written.
2. **"Where's the death stage?"** — v3.0 had no concept of decommissioning. Phase 12 (Retirement) now handles deprecation timelines, migration, compliant data retention, and infrastructure removal.

## Phase 0: Problem Discovery

See [phase-0-problem-discovery.md](phase-0-problem-discovery.md). Validates the problem is real, severe, and worth solving (vs. buying or not building) before Bootstrap runs. A NO-GO decision stops the pipeline before any cost is incurred on requirements/architecture/development.

## Phase 12: Retirement

See [phase-12-retirement.md](phase-12-retirement.md). Triggered explicitly (not run by default) when a feature/system needs to be deprecated, migrated off, and decommissioned — with compliant data retention and a full audit trail.

## Everything In Between

Phases 1-11 (Bootstrap through Observability) are functionally unchanged from v3.0, just renumbered by +1. See [SDLC Phases Reference](../../references/sdlc-phases.md) for the full phase-by-phase breakdown.
