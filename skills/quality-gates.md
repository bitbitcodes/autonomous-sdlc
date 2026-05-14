# Quality Gates

Detailed enforcement rules for the 11 quality gates that govern phase transitions.

**Per-Phase Review:** After every phase (except Phase 0 and Phase 8), the orchestrator dispatches 3 blind reviewers on that phase's artifacts. Both the quality gate AND per-phase review must PASS before advancing.

---

## Gate Enforcement Protocol

```
Phase completes → Run gate checks → PASS: advance │ FAIL: fix + retry (max 3) → ESCALATE
```

Every gate check produces a structured result:

```json
{
  "gate": 1,
  "name": "Input Validation",
  "phase": "bootstrap",
  "status": "PASS",
  "checks": [
    { "check": "Spec file exists", "status": "PASS" },
    { "check": "Spec is non-empty", "status": "PASS" },
    { "check": "At least one requirement identified", "status": "PASS" }
  ],
  "blocking_issues": [],
  "timestamp": "2026-01-15T10:00:00Z"
}
```

---

## Gate 1: Input Validation (Phase 0)

| Check | Pass Criteria |
|-------|--------------|
| Spec file exists | `.sdlc/specs/normalized-spec.md` exists |
| Spec is non-empty | File has > 0 actionable content |
| Requirements identifiable | At least 1 requirement can be extracted |
| No contradictions | No directly contradictory statements |

---

## Gate 2: Requirements Completeness (Phase 1)

| Check | Pass Criteria |
|-------|--------------|
| Unique IDs | Every requirement has REQ-xxx ID |
| Acceptance criteria | Every functional requirement has ≥ 1 AC |
| Risk register | `.sdlc/artifacts/product/risks.md` exists with severity ratings |
| Assumptions documented | `.sdlc/artifacts/product/assumptions.md` exists |

---

## Gate 3: Story-Task Traceability (Phase 2)

| Check | Pass Criteria |
|-------|--------------|
| Story traceability | Every user story references ≥ 1 REQ-xxx |
| Done criteria | Every task has clear done criteria |
| No circular deps | Dependency graph has no cycles |
| Estimates present | Every task has S/M/L estimate |
| Queue populated | `.sdlc/queue/pending.json` has tasks |

---

## Gate 4: Architecture Soundness (Phase 3)

| Check | Pass Criteria |
|-------|--------------|
| System design | Component diagram and communication patterns defined |
| Tech stack justified | Each layer has justified technology choice |
| ADRs exist | ADRs for technology stack, API style, and database choice |
| Solution evaluation | ≥ 2 alternatives evaluated per major decision |
| Decisions traceable | All decisions traceable to requirements |

---

## Gate 5: Design Completeness (Phase 4)

| Check | Pass Criteria |
|-------|--------------|
| Valid interface contracts | `interface-contracts.*` exists and is valid for the project type |
| Data/state model | Storage structures and access patterns defined |
| Relationships | All data relationships documented |
| NFR targets | Every NFR has a measurable target metric |
| ADR references | Every design decision references an ADR |

---

## Gate 6: Build Green (Phase 5)

| Check | Pass Criteria |
|-------|--------------|
| Build passes | Zero compilation/build errors |
| Lint clean | Zero lint errors |
| Type check | Zero type errors (if typed language) |
| Unit tests pass | 100% of unit tests pass |
| No regressions | All pre-existing tests still pass |

---

## Gate 7: Test Coverage (Phase 6)

| Check | Pass Criteria |
|-------|--------------|
| Unit coverage | ≥ 80% line coverage |
| Criteria mapped | Every acceptance criterion has ≥ 1 test |
| Integration tests | All integration tests pass |
| Regression tests | All regression tests pass |
| No flaky tests | Zero non-deterministic tests |

---

## Gate 8: Security Clear (Phase 7)

| Check | Pass Criteria |
|-------|--------------|
| Secret scan | Zero hardcoded secrets detected |
| Dependency audit | Zero Critical/High CVEs in dependencies |
| OWASP review | Zero Critical/High OWASP findings |
| Policy compliance | Security policies enforced (CORS, CSP, rate limiting) |

---

## Gate 9: Review Passed (Phase 8)

| Check | Pass Criteria |
|-------|--------------|
| Code review | PASS verdict |
| Maintainability | PASS verdict |
| Performance | PASS verdict |
| No blocking findings | Zero Critical/High/Medium findings remaining |
| Anti-sycophancy | If unanimous PASS, Devil's Advocate check passed |

---

## Gate 10: Pipeline Green (Phase 9)

| Check | Pass Criteria |
|-------|--------------|
| CI config valid | Pipeline YAML is parseable |
| Docker builds | Dockerfile builds without errors (if applicable) |
| Runbook complete | All sections of deployment runbook filled |
| Env configs | Configs exist for dev, staging, production |

---

## Gate 11: Observability Ready (Phase 10)

| Check | Pass Criteria |
|-------|--------------|
| SLOs defined | SLOs exist for all critical user journeys |
| Health checks | Health check endpoint specified/implemented |
| Alerts configured | Alert rules cover error scenarios |
| Structured logging | Logging uses JSON format |

---

## Severity Classification

| Severity | Definition | Gate Action |
|----------|-----------|-------------|
| Critical | Security hole, data loss, crash | BLOCK — fix immediately |
| High | Broken functionality, major bug | BLOCK — fix before proceeding |
| Medium | Minor bug, code smell | BLOCK — fix before deployment |
| Low | Style, minor improvement | TODO — fix later |
| Cosmetic | Formatting, preference | Info only — no action |

---

## Blind Review Protocol

Used in Gate 9 (Review) and per-phase reviews:

1. Dispatch 3 reviewers simultaneously
2. Each reviewer sees only the codebase — NOT other reviewers' findings
3. Each produces independent VERDICT + FINDINGS
4. Orchestrator aggregates after all 3 complete
5. If unanimous PASS → run Devil's Advocate (anti-sycophancy)
6. Devil's Advocate specifically tries to find issues others missed

### Anti-Sycophancy Check
Purpose: Prevent groupthink where all reviewers approve mediocre code.

```
IF all 3 reviewers return PASS:
  Launch 4th reviewer with prompt:
  "The previous 3 reviewers all approved this code.
   Your job is to find what they missed.
   Look for: subtle bugs, edge cases, security issues,
   performance traps, and maintainability concerns.
   Be adversarial but fair."
```

If Devil's Advocate finds Critical/High issues → re-review cycle.
If Devil's Advocate finds only Low/Cosmetic → PASS confirmed.
