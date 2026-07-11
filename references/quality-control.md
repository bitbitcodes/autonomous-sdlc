# Quality Control Reference

## Quality Gates

Every phase transition requires passing quality gates. Gates are binary: PASS or FAIL. A FAIL blocks the transition until resolved.

---

## The 13 Quality Gates

| # | Gate | Phase | Pass Criteria |
|---|------|-------|---------------|
| 0 | **Problem Validated** | 0 (Problem Discovery) | Problem is clear/measurable, ≥3 pain points documented, business case positive, ≥3 alternatives evaluated, go/no-go recorded |
| 1 | **Input Validation** | 1 (Bootstrap) | Spec is parseable, non-empty, and contains actionable requirements |
| 2 | **Requirements Completeness** | 2 (Product) | All requirements structured, have acceptance criteria, risks identified |
| 3 | **Story-Task Traceability** | 3 (Story-Tasks) | All stories trace to requirements, tasks have done criteria, no circular deps |
| 4 | **Architecture Soundness** | 4 (Architecture) | System design documented, tech stack justified, ADRs for all decisions |
| 5 | **Design Completeness** | 5 (Design) | Interface contracts valid for project type, data/state model defined, NFRs have targets, designs reference ADRs, compliance sign-off (if enabled) |
| 6 | **Build Green** | 6 (Development) | Zero build errors, zero lint errors, all unit tests pass |
| 7 | **Test Coverage** | 7 (Testing) | Unit ≥ 80%, all acceptance criteria have tests, integration tests pass |
| 8 | **Security Clear** | 8 (Security) | Zero Critical/High findings, no hardcoded secrets, deps patched, compliance sign-off (if enabled) |
| 9 | **Review Passed** | 9 (Review) | All 3 reviewers PASS, no Critical/High/Medium findings |
| 10 | **Pipeline Green** | 10 (DevOps) | CI/CD runs without errors, Docker builds, deployment runbook complete |
| 11 | **Observability Ready** | 11 (Observability) | SLOs defined, health checks implemented, alerts configured |
| 12 | **Retirement Complete** | 12 (Retirement, triggered) | ≥90 days notice, migration documented, compliant data retention, infra decommissioned, post-mortem complete |

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

After every phase (except Phase 1 Bootstrap and Phase 9 which IS the full review), the orchestrator dispatches the full Review agent (3 blind reviewers) to assess that phase's artifacts. This ensures quality is enforced continuously, not just at Phase 9.

```
Phase N completes → Quality Gate N → PASS → Per-Phase Review (3 blind reviewers) → PASS → Phase N+1
```

Per-phase reviews follow the same blind review protocol as Phase 9, but scoped to the current phase's artifacts only.

---

## Governance Gate (Opt-In)

If `.sdlc/governance/` policy files are present, an additional check runs before AND after every phase gate:

```
CHECK: Decisions classified per risk-policy.yaml; HIGH/CRITICAL decisions have a recorded
       approval in decision-log.json (or a pending entry in pending-approvals.json blocking
       progress)
CHECK: Budget consumed this phase/total <= budget-policy.yaml limits (warn at 80%, pause at 100%)
CHECK: Tokens consumed this phase/feature/agent <= token-policy.yaml limits (pause at 90%,
       hard stop at 100%)
```

This gate is skipped entirely if `.sdlc/governance/` does not exist (v3.0-compatible behavior).

---

## Blind Review System

Used in Phase 9 (Review) and per-phase reviews. Three reviewers operate independently:

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

### Gate 0: Problem Validated
```
CHECK: Problem statement is clear and measurable
CHECK: >=3 user pain points documented with evidence
CHECK: Business case shows positive ROI or explicit strategic value
CHECK: >=3 solution alternatives evaluated (including "don't build")
CHECK: Go/No-Go decision documented with rationale
OUTPUT: .sdlc/artifacts/problem-discovery/ contains all deliverables
```

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

### Gate 12: Retirement Complete
```
CHECK: Deprecation timeline published (>=90 days notice, or emergency approval on record)
CHECK: Migration path documented for all affected user/stakeholder segments
CHECK: Data retention/deletion plan complies with active compliance frameworks
CHECK: All infrastructure decommissioned or archived
CHECK: Post-mortem completed with learnings
CHECK: CRITICAL decommission actions have 2 recorded human sign-offs
OUTPUT: .sdlc/artifacts/retirement/ contains all deliverables
```
