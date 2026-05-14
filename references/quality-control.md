# Quality Control Reference

## Quality Gates

Every phase transition requires passing quality gates. Gates are binary: PASS or FAIL. A FAIL blocks the transition until resolved.

---

## The 11 Quality Gates

| # | Gate | Phase | Pass Criteria |
|---|------|-------|---------------|
| 1 | **Input Validation** | 0 (Bootstrap) | Spec is parseable, non-empty, and contains actionable requirements |
| 2 | **Requirements Completeness** | 1 (Product) | All requirements structured, have acceptance criteria, risks identified |
| 3 | **Story-Task Traceability** | 2 (Story-Tasks) | All stories trace to requirements, tasks have done criteria, no circular deps |
| 4 | **Architecture Soundness** | 3 (Architecture) | System design documented, tech stack justified, ADRs for all decisions |
| 5 | **Design Completeness** | 4 (Design) | Interface contracts valid for project type, data/state model defined, NFRs have targets, designs reference ADRs |
| 6 | **Build Green** | 5 (Development) | Zero build errors, zero lint errors, all unit tests pass |
| 7 | **Test Coverage** | 6 (Testing) | Unit ≥ 80%, all acceptance criteria have tests, integration tests pass |
| 8 | **Security Clear** | 7 (Security) | Zero Critical/High findings, no hardcoded secrets, deps patched |
| 9 | **Review Passed** | 8 (Review) | All 3 reviewers PASS, no Critical/High/Medium findings |
| 10 | **Pipeline Green** | 9 (DevOps) | CI/CD runs without errors, Docker builds, deployment runbook complete |
| 11 | **Observability Ready** | 10 (Observability) | SLOs defined, health checks implemented, alerts configured |

---

## Gate Enforcement Protocol

```
Phase N completes
       │
       ▼
 Run quality gate N
       │
   ┌───▼───┐
   │ PASS?  │
   └───┬────┘
   YES │  NO
   ┌───▼───┐  ┌──────────────────┐
   │ Move   │  │ Identify failures │
   │ to     │  │ Log to learnings  │
   │ Phase  │  │ Fix issues        │
   │ N+1    │  │ Re-run gate       │
   └────────┘  │ (max 3 retries)   │
               └──────────────────┘
                      │
                After 3 failures:
                ESCALATE to human
```

---

## Per-Phase Review

After every phase (except Phase 0 Bootstrap and Phase 8 which IS the full review), the orchestrator dispatches the full Review agent (3 blind reviewers) to assess that phase's artifacts. This ensures quality is enforced continuously, not just at Phase 8.

```
Phase N completes → Quality Gate N → PASS → Per-Phase Review (3 blind reviewers) → PASS → Phase N+1
```

Per-phase reviews follow the same blind review protocol as Phase 8, but scoped to the current phase's artifacts only.

---

## Blind Review System

Used in Phase 8 (Review) and per-phase reviews. Three reviewers operate independently:

1. **Code Review Agent** — Quality, SOLID, best practices
2. **Maintainability Reviewer** — Tech debt, readability, complexity
3. **Performance Reviewer** — Bottlenecks, optimization

### Rules:
- All 3 launch simultaneously
- No reviewer sees another's findings
- Each produces: VERDICT (PASS/FAIL) + FINDINGS (severity-tagged)
- Results aggregated by orchestrator

### Anti-Sycophancy Check:
If all 3 reviewers give PASS unanimously, run a 4th "Devil's Advocate" review that specifically looks for issues the others might have overlooked.

---

## Severity Classification

| Severity | Definition | Action |
|----------|-----------|--------|
| **Critical** | Security vulnerability, data loss risk, crash | BLOCK — must fix immediately |
| **High** | Broken functionality, major bug, missing requirement | BLOCK — must fix before proceeding |
| **Medium** | Minor bug, code smell, performance issue | BLOCK — fix before deployment |
| **Low** | Style issue, minor improvement | TODO comment — fix later |
| **Cosmetic** | Formatting, naming suggestion | Informational only — no action required |

---

## Quality Checks Per Task

During Phase 5 (Development), every task must pass these micro-checks:

1. **Compilation** — Code compiles without errors
2. **Lint** — Zero lint errors (warnings acceptable)
3. **Type check** — Zero type errors (if typed language)
4. **Unit tests** — All existing + new tests pass
5. **No regressions** — Previous tests still pass

---

## Velocity-Quality Feedback Loop

### The Trap to Avoid
Agents naturally optimize for velocity (completing tasks fast) at the expense of quality. This creates a debt spiral where later phases spend more time fixing issues than building features.

### Prevention:
- Every task completion includes a verification step (RARV cycle)
- Errors caught during verification are logged as learnings
- The same error type occurring 3+ times triggers a pattern extraction
- Pattern is added to semantic memory and checked before future tasks

### Metrics to Track
| Metric | Target | Red Flag |
|--------|--------|----------|
| First-attempt success rate | ≥ 70% | < 50% |
| Average retries per task | ≤ 1.5 | > 3 |
| Regression rate | ≤ 5% | > 15% |
| Quality gate pass rate | ≥ 80% first attempt | < 60% |

---

## Quality Gate Details

### Gate 1: Input Validation
```
CHECK: Spec file exists and is non-empty
CHECK: At least one actionable requirement identified
CHECK: No contradictory requirements
OUTPUT: .sdlc/specs/ contains normalized spec
```

### Gate 2: Requirements Completeness
```
CHECK: Every requirement has a unique ID
CHECK: Every requirement has acceptance criteria
CHECK: Risk register exists with severity ratings
CHECK: Assumptions are documented
OUTPUT: .sdlc/artifacts/product/ contains all deliverables
```

### Gate 3: Story-Task Traceability
```
CHECK: Every user story references a requirement ID
CHECK: Every task has clear done criteria
CHECK: Dependency graph has no cycles
CHECK: All tasks estimated (S/M/L or hours)
OUTPUT: .sdlc/queue/pending.json populated
```

### Gate 4: Architecture Soundness
```
CHECK: System design has component diagram and communication patterns
CHECK: Tech stack selected with justification for each layer
CHECK: ADRs exist for technology stack choice and API style
CHECK: Solution evaluation covers ≥ 2 alternatives per decision
OUTPUT: .sdlc/artifacts/architecture/ contains all deliverables
```

### Gate 5: Design Completeness
```
CHECK: Interface contracts exist and are valid for the project type
CHECK: Data/state model defines storage structures and access patterns
CHECK: Every NFR has a measurable target
CHECK: Every design decision references an ADR
OUTPUT: .sdlc/artifacts/design/ contains all deliverables
```

### Gate 6: Build Green
```
CHECK: Build completes without errors
CHECK: Linter reports zero errors
CHECK: Type checker reports zero errors
CHECK: All unit tests pass
OUTPUT: Clean build + passing test suite
```

### Gate 7: Test Coverage
```
CHECK: Unit test coverage ≥ 80%
CHECK: Every acceptance criterion has at least one test
CHECK: Integration tests pass
CHECK: Test data fixtures exist
OUTPUT: .sdlc/artifacts/testing/ contains reports
```

### Gate 8: Security Clear
```
CHECK: Secret scanner finds zero secrets in code
CHECK: Dependency scanner finds zero Critical/High CVEs
CHECK: OWASP review finds zero Critical/High issues
CHECK: Security policies enforced (CORS, CSP, rate limiting)
OUTPUT: .sdlc/artifacts/security/ contains reports
```

### Gate 9: Review Passed
```
CHECK: All 3 reviewers return PASS verdict
CHECK: No Critical/High/Medium findings remain
CHECK: Anti-sycophancy check passed (if unanimous)
OUTPUT: .sdlc/artifacts/review/ contains reports
```

### Gate 10: Pipeline Green
```
CHECK: CI pipeline configuration is valid
CHECK: Docker build succeeds (if applicable)
CHECK: Deployment runbook is complete
CHECK: Environment configs exist for all targets
OUTPUT: .sdlc/artifacts/devops/ contains configs
```

### Gate 11: Observability Ready
```
CHECK: SLOs defined for critical user journeys
CHECK: Health check endpoint implemented
CHECK: Alert rules defined for error scenarios
CHECK: Logging configuration is structured (JSON)
OUTPUT: .sdlc/artifacts/observability/ contains specs
```
