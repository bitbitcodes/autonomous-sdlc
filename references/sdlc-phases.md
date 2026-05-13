# SDLC Phases Reference

## Phase Overview

```
Phase 0       Phase 1       Phase 2          Phase 3       Phase 4
Bootstrap --> Product ----> Architecture --> Backlog ----> Development
  (Setup)    (Discover)     (Design)       (Decompose)    (Build)
                                                             |
Phase 8       Phase 7       Phase 6         Phase 5         |
Growth <--- Observability < DevOps <------- Testing <-------+
(Iterate)   (Monitor)      (Deploy)        (Verify)
```

---

## Phase 0: Bootstrap

**Purpose:** Initialize framework environment and normalize input spec.

**Stage Agent:** Orchestrator (direct)

**Actions:**
1. Create `.sdlc/` directory structure
2. Parse and normalize input spec (PRD, YAML, brief, issue)
3. Store normalized spec in `.sdlc/specs/`
4. Initialize `CONTINUITY.md`
5. Initialize orchestrator state
6. Detect project complexity (simple / medium / complex / enterprise)
7. Select agent team based on complexity

**Directory Structure Created:**
```
.sdlc/
├── state/orchestrator.json
├── queue/pending.json
├── queue/active.json
├── queue/completed.json
├── memory/episodic/
├── memory/semantic/
├── memory/learnings/
├── artifacts/
├── specs/
└── CONTINUITY.md
```

**Output:** Initialized `.sdlc/` directory, normalized spec, agent team selection.

**Quality Gate:** Spec is parseable and non-empty.

---

## Phase 1: Product (Discovery)

**Purpose:** Analyze requirements, identify risks, surface assumptions, generate acceptance criteria.

**Stage Agent:** `stage-product`

**Subagents Dispatched:**
| Subagent | Task |
|----------|------|
| `sub-requirement-parser` | Parse raw requirements into structured format |
| `sub-acceptance-criteria` | Generate testable acceptance criteria per feature |
| `sub-risk-analyzer` | Identify technical, business, and schedule risks |
| `sub-assumption-extractor` | Surface hidden assumptions in the spec |

**Actions:**
1. Parse raw input into structured requirements
2. Identify functional and non-functional requirements
3. Generate acceptance criteria (Given/When/Then)
4. Analyze risks with severity and mitigations
5. Extract assumptions and flag for validation
6. Produce consolidated Product Discovery Document

**Output:**
- `.sdlc/artifacts/product/requirements.md` — Structured requirements
- `.sdlc/artifacts/product/acceptance-criteria.md` — Testable criteria
- `.sdlc/artifacts/product/risks.md` — Risk register
- `.sdlc/artifacts/product/assumptions.md` — Assumption log

**Quality Gate:** All requirements have acceptance criteria. Risks are categorized with mitigations.

---

## Phase 2: Architecture

**Purpose:** Design system architecture, define API contracts, model data, evaluate NFRs.

**Stage Agent:** `stage-architecture`

**Subagents Dispatched:**
| Subagent | Task |
|----------|------|
| `sub-api-designer` | Design API contracts (OpenAPI/GraphQL) |
| `sub-data-model-designer` | Design database schema and ERDs |
| `sub-integration-planner` | Plan external system integrations |
| `sub-nfr-evaluator` | Evaluate non-functional requirements |

**Actions:**
1. Choose technology stack based on requirements and constraints
2. Design system architecture (components, interactions, boundaries)
3. Define API contracts with request/response schemas
4. Design data models with relationships and constraints
5. Plan external integrations (auth, payments, etc.)
6. Evaluate NFRs (performance, scalability, security, availability)
7. Document architecture decisions (ADRs)

**Output:**
- `.sdlc/artifacts/architecture/system-design.md` — Architecture overview
- `.sdlc/artifacts/architecture/api-contracts.yaml` — OpenAPI spec
- `.sdlc/artifacts/architecture/data-model.md` — Database schema & ERD
- `.sdlc/artifacts/architecture/integrations.md` — Integration plan
- `.sdlc/artifacts/architecture/nfr-assessment.md` — NFR evaluation
- `.sdlc/artifacts/architecture/adrs/` — Architecture Decision Records

**Quality Gate:** API contracts are valid OpenAPI. Data model is normalized. All NFRs have target metrics.

---

## Phase 3: Backlog

**Purpose:** Decompose architecture into implementable epics, stories, and tasks. Prioritize work.

**Stage Agent:** `stage-backlog`

**Subagents Dispatched:** None (backlog agent handles directly)

**Actions:**
1. Decompose system design into epics (major features/components)
2. Break epics into user stories with acceptance criteria
3. Break stories into implementable tasks (< 4 hours each)
4. Establish dependencies between tasks
5. Prioritize using MoSCoW or weighted scoring
6. Populate `.sdlc/queue/pending.json` with all tasks

**Output:**
- `.sdlc/artifacts/backlog/epics.md` — Epic definitions
- `.sdlc/artifacts/backlog/stories.md` — User stories with criteria
- `.sdlc/artifacts/backlog/tasks.json` — Task list with dependencies
- `.sdlc/queue/pending.json` — Populated task queue

**Quality Gate:** Every story traces back to a requirement. Every task has clear done criteria. No circular dependencies.

---

## Phase 4: Development

**Purpose:** Implement the codebase task by task following the backlog.

**Stage Agent:** `stage-development`

**Subagents Dispatched:**
| Subagent | Task |
|----------|------|
| `sub-repo-analyzer` | Analyze existing codebase patterns and conventions |
| `sub-code-generator` | Implement features from task definitions |
| `sub-refactoring-agent` | Refactor code for quality and maintainability |
| `sub-documentation-agent` | Generate code-level and API documentation |

**Workflow Per Task:**
1. Claim task from `.sdlc/queue/pending.json`
2. Move to `.sdlc/queue/active.json`
3. Read task definition, acceptance criteria, and relevant architecture docs
4. Implement code following existing patterns
5. Write unit tests alongside implementation
6. Run tests — fix until passing
7. Commit checkpoint
8. Move task to `.sdlc/queue/completed.json`

**Implementation Rules:**
- Spec-first: read the API contract/data model before writing code
- Test alongside: write tests as you implement, not after
- Small commits: one logical change per commit
- No dead code: remove unused imports, variables, functions
- Follow existing patterns: check repo-analyzer output first

**Output:**
- Source code implementing all backlog tasks
- Unit tests for all implemented code
- `.sdlc/artifacts/development/implementation-log.md`

**Quality Gate:** All unit tests pass. No build errors. Code follows project conventions.

---

## Phase 5: Testing

**Purpose:** Comprehensive testing beyond unit tests — integration, regression, E2E.

**Stage Agent:** `stage-testing`

**Subagents Dispatched:**
| Subagent | Task |
|----------|------|
| `sub-unit-test` | Ensure unit test coverage ≥ 80% |
| `sub-integration-test` | Test component interactions |
| `sub-regression-test` | Build regression suite from acceptance criteria |
| `sub-test-data` | Generate test fixtures and mock data |

**Testing Phases:**
1. **Unit Tests** — Verify individual functions/methods (≥ 80% coverage)
2. **Integration Tests** — Verify component interactions (API endpoints, DB queries)
3. **Regression Tests** — Map acceptance criteria to test cases
4. **E2E Tests** — Full user flow testing (if applicable)

**Output:**
- Test suites (unit, integration, regression, E2E)
- `.sdlc/artifacts/testing/coverage-report.md`
- `.sdlc/artifacts/testing/test-results.md`
- `.sdlc/artifacts/testing/test-data/` — Fixtures and mocks

**Quality Gate:** Unit coverage ≥ 80%. All tests pass. Every acceptance criterion has a test.

---

## Phase 6: Security

**Purpose:** Security audit — scan for secrets, vulnerabilities, OWASP issues, policy compliance.

**Stage Agent:** `stage-security`

**Subagents Dispatched:**
| Subagent | Task |
|----------|------|
| `sub-secret-scanner` | Detect hardcoded secrets, API keys, tokens |
| `sub-dependency-scanner` | Audit dependency vulnerabilities |
| `sub-owasp-reviewer` | Review for OWASP Top 10 vulnerabilities |
| `sub-policy-validator` | Check security policy compliance |

**Actions:**
1. Scan codebase for hardcoded secrets and credentials
2. Audit all dependencies for known vulnerabilities
3. Review code for OWASP Top 10 issues (injection, XSS, auth bypass, etc.)
4. Validate against security policies (CORS, CSP, rate limiting, etc.)
5. Generate security findings with severity ratings
6. Fix Critical and High severity findings automatically

**Output:**
- `.sdlc/artifacts/security/secret-scan.md`
- `.sdlc/artifacts/security/dependency-audit.md`
- `.sdlc/artifacts/security/owasp-review.md`
- `.sdlc/artifacts/security/policy-compliance.md`
- `.sdlc/artifacts/security/security-summary.md`

**Quality Gate:** Zero Critical/High findings. All secrets removed. Dependencies patched or documented.

---

## Phase 7: Review

**Purpose:** Multi-perspective code review — quality, maintainability, performance.

**Stage Agent:** `stage-review`

**Subagents Dispatched:**
| Subagent | Task |
|----------|------|
| `sub-code-review` | Code quality, SOLID, best practices |
| `sub-maintainability` | Maintainability, tech debt, readability |
| `sub-performance` | Performance bottlenecks, optimization |

**Review Protocol:**
1. All 3 reviewers run in parallel (blind — no visibility of each other's findings)
2. Each produces VERDICT (PASS/FAIL) + FINDINGS with severity
3. Aggregate findings
4. If unanimous PASS: run anti-sycophancy check (Devil's Advocate reviewer)
5. Fix Critical/High/Medium issues
6. Re-run reviewers until all PASS

**Severity Handling:**
| Severity | Action |
|----------|--------|
| Critical | BLOCK — must fix before proceeding |
| High | BLOCK — must fix before proceeding |
| Medium | BLOCK — fix before deployment |
| Low | TODO comment — fix later |
| Cosmetic | Informational only |

**Output:**
- `.sdlc/artifacts/review/code-review.md`
- `.sdlc/artifacts/review/maintainability-review.md`
- `.sdlc/artifacts/review/performance-review.md`
- `.sdlc/artifacts/review/review-summary.md`

**Quality Gate:** All reviewers PASS. No Critical/High/Medium findings remaining.

---

## Phase 8: DevOps

**Purpose:** Set up CI/CD, infrastructure configuration, deployment pipeline.

**Stage Agent:** `stage-devops`

**Subagents Dispatched:** None (DevOps agent handles directly)

**Actions:**
1. Generate CI/CD pipeline configuration (GitHub Actions / GitLab CI)
2. Create Dockerfile and docker-compose.yml (if applicable)
3. Set up environment configurations (dev, staging, production)
4. Configure deployment strategy (blue-green, canary, rolling)
5. Set up infrastructure as code (if applicable)
6. Create deployment runbook

**Output:**
- `.sdlc/artifacts/devops/ci-cd.yml`
- `.sdlc/artifacts/devops/Dockerfile`
- `.sdlc/artifacts/devops/docker-compose.yml`
- `.sdlc/artifacts/devops/deployment-runbook.md`
- `.sdlc/artifacts/devops/env-configs/`

**Quality Gate:** CI pipeline runs without errors. Docker builds successfully. Deployment runbook is complete.

---

## Phase 9: Observability

**Purpose:** Define monitoring, alerting, SLOs, and operational readiness.

**Stage Agent:** `stage-observability`

**Subagents Dispatched:** None (Observability agent handles directly)

**Actions:**
1. Define SLOs/SLIs for the application
2. Set up structured logging configuration
3. Define alert rules and escalation paths
4. Create dashboard specifications
5. Write operational runbook
6. Define health check endpoints

**Output:**
- `.sdlc/artifacts/observability/slo-definitions.md`
- `.sdlc/artifacts/observability/logging-config.md`
- `.sdlc/artifacts/observability/alert-rules.md`
- `.sdlc/artifacts/observability/dashboard-specs.md`
- `.sdlc/artifacts/observability/runbook.md`

**Quality Gate:** SLOs defined for all critical paths. Health checks implemented. Alert rules cover error scenarios.

---

## Final Review (Before Delivery)

```
1. Dispatch 3 reviewers across ENTIRE implementation:
   - Code Review Agent: Full codebase quality
   - Maintainability Reviewer: All requirements met
   - Performance Reviewer: Full performance audit

2. Aggregate findings across all files
3. Fix Critical/High/Medium issues
4. Re-run all 3 reviewers until all PASS
5. Generate final report in .sdlc/artifacts/final-review.md
6. Mark project as COMPLETE only after all PASS
```

---

## Quality Gates Summary

| Gate | Phase | Pass Criteria |
|------|-------|---------------|
| Spec Valid | 0 | Input spec parseable and non-empty |
| Requirements Complete | 1 | All requirements have acceptance criteria |
| Architecture Valid | 2 | API contracts valid, data model normalized |
| Backlog Traceable | 3 | All stories trace to requirements |
| Build Passes | 4 | Zero build errors, all unit tests pass |
| Coverage Met | 5 | Unit ≥ 80%, all acceptance criteria tested |
| Security Clear | 6 | Zero Critical/High findings |
| Review Passed | 7 | All 3 reviewers PASS |
| Pipeline Green | 8 | CI/CD runs without errors |
| Observability Ready | 9 | SLOs defined, health checks implemented |
