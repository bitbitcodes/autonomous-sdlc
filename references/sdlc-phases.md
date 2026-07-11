# SDLC Phases Reference

## Phase Overview

```
Phase 0            Phase 1       Phase 2       Phase 3          Phase 4          Phase 5       Phase 6
Problem Discovery->Bootstrap --> Product ----> Story-Tasks ---> Architecture --> Design -----> Development
  (Validate)         (Setup)    (Discover)    (Decompose)      (Decide)        (Detail)       (Build)
                                                                                                    |
Phase 12         Phase 11        Phase 10      Phase 9        Phase 8         Phase 7             |
Retirement <----Observability < DevOps <--- Review <------- Security <---- Testing <--------------+
  (Retire)         (Monitor)    (Deploy)     (Assess)        (Audit)        (Verify)
```

**Per-Phase Review:** After every phase (except Phase 9 which IS the full review), the orchestrator dispatches 3 blind reviewers to assess that phase's artifacts before advancing.

**Phase 12 (Retirement)** is triggered, not run by default — see its section below.

**Configurability:** Any stage (except Phase 1 Bootstrap) and any individual subagent can be disabled via `.sdlc/phase-config.json` / `sdlc phases`. A disabled phase's status/gate become `"skipped"` in `orchestrator.json` rather than `"pass"`/`"fail"`, and the orchestrator advances directly to the next phase. See `docs/cli-reference.md#sdlc-phases`.

---

## Phase 0: Problem Discovery & Validation

**Purpose:** Validate that the problem is real and severe enough to justify building a solution, and that building (vs. buying or doing nothing) is the right call.

**Stage Agent:** `stage-problem-discovery` (4 subagents)

**Subagents Dispatched:**
| Subagent | Task |
|----------|------|
| `sub-problem-statement-extractor` | Parse vague/raw input into a clear, measurable problem statement |
| `sub-user-research-synthesizer` | Validate problem severity via user pain points and evidence |
| `sub-opportunity-analyzer` | Assess market/business value and build a business case |
| `sub-solution-space-explorer` | Evaluate build vs. buy vs. don't-build alternatives |

**Output:**
- `.sdlc/artifacts/problem-discovery/problem-statement.md`
- `.sdlc/artifacts/problem-discovery/user-research-synthesis.md`
- `.sdlc/artifacts/problem-discovery/business-case.md`
- `.sdlc/artifacts/problem-discovery/solution-alternatives.md`
- `.sdlc/artifacts/problem-discovery/go-no-go-decision.md`

**Quality Gate 0:** Problem is clear and measurable, ≥3 pain points documented, business case shows positive ROI/strategic value, ≥3 alternatives evaluated, go/no-go decision recorded. A NO-GO decision stops the pipeline.

**Per-Phase Review:** 3 blind reviewers assess Phase 0 artifacts.

---

## Phase 1: Bootstrap

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

**Output:** Initialized `.sdlc/` directory, normalized spec, agent team selection.

**Quality Gate 1:** Spec is parseable and non-empty.

---

## Phase 2: Product (Discovery)

**Purpose:** Analyze requirements, identify risks, surface assumptions, generate acceptance criteria.

**Stage Agent:** `stage-product` (4 subagents)

**Subagents Dispatched:**
| Subagent | Task |
|----------|------|
| `sub-requirement-parser` | Parse raw requirements into structured format |
| `sub-acceptance-criteria` | Generate testable acceptance criteria per feature |
| `sub-risk-analyzer` | Identify technical, business, and schedule risks |
| `sub-assumption-extractor` | Surface hidden assumptions in the spec |

**Output:**
- `.sdlc/artifacts/product/requirements.md` — Structured requirements
- `.sdlc/artifacts/product/acceptance-criteria.md` — Testable criteria
- `.sdlc/artifacts/product/risks.md` — Risk register
- `.sdlc/artifacts/product/assumptions.md` — Assumption log

**Quality Gate 2:** All requirements have acceptance criteria. Risks are categorized with mitigations.

**Per-Phase Review:** 3 blind reviewers assess Phase 2 artifacts.

---

## Phase 3: Story-Tasks

**Purpose:** Decompose requirements into implementable epics, stories, and tasks. Prioritize work and populate the queue.

**Stage Agent:** `stage-story-tasks` (3 subagents)

**Subagents Dispatched:**
| Subagent | Task |
|----------|------|
| `sub-story-writer` | Decompose requirements into user stories with acceptance criteria |
| `sub-task-decomposer` | Break stories into implementable tasks with estimates |
| `sub-dependency-mapper` | Build dependency graph, identify critical path, detect cycles |

**Output:**
- `.sdlc/artifacts/story-tasks/epics.md` — Epic definitions
- `.sdlc/artifacts/story-tasks/stories.md` — User stories with criteria
- `.sdlc/artifacts/story-tasks/tasks.json` — Task list with dependencies
- `.sdlc/artifacts/story-tasks/dependency-graph.md` — Dependency graph
- `.sdlc/queue/pending.json` — Populated task queue

**Quality Gate 3:** Every story traces to a requirement. Every task has done criteria. No circular dependencies.

**Per-Phase Review:** 3 blind reviewers assess Phase 3 artifacts.

---

## Phase 4: Architecture

**Purpose:** Define high-level system architecture, select technology stack, evaluate alternatives, and document all decisions as ADRs.

**Stage Agent:** `stage-architecture` (3 subagents)

**Subagents Dispatched:**
| Subagent | Task |
|----------|------|
| `sub-tech-stack-advisor` | Analyze requirements and recommend technology stack |
| `sub-solution-evaluator` | Evaluate alternative solutions with trade-off analysis |
| `sub-adr-writer` | Write Architecture Decision Records |

**Output:**
- `.sdlc/artifacts/architecture/system-design.md` — High-level architecture
- `.sdlc/artifacts/architecture/tech-stack.md` — Technology stack with justification
- `.sdlc/artifacts/architecture/solution-evaluation.md` — Trade-off analysis
- `.sdlc/artifacts/architecture/adrs/` — Architecture Decision Records

**Quality Gate 4:** System design has components and patterns. Tech stack justified. ADRs for all major decisions.

**Per-Phase Review:** 3 blind reviewers assess Phase 4 artifacts.

---

## Phase 5: Design

**Purpose:** Create detailed technical design: interface contracts, data/state models, integration plans, NFR evaluation. All design decisions reference ADRs from Phase 4. `sub-compliance-validator` is also dispatched here for data model compliance.

**Stage Agent:** `stage-design` (4 subagents)

**Subagents Dispatched:**
| Subagent | Task |
|----------|------|
| `sub-interface-designer` | Design interface contracts (APIs, CLIs, UIs, events, protocols) |
| `sub-data-model-designer` | Design data/state model (databases, file storage, in-memory state) |
| `sub-integration-planner` | Plan external system integrations |
| `sub-nfr-evaluator` | Evaluate non-functional requirements |

**Output:**
- `.sdlc/artifacts/design/detailed-design.md` — Detailed technical design
- `.sdlc/artifacts/design/interface-contracts.*` — Interface contracts (format varies by project type)
- `.sdlc/artifacts/design/data-model.md` — Data/state model
- `.sdlc/artifacts/design/integrations.md` — Integration plan
- `.sdlc/artifacts/design/nfr-assessment.md` — NFR evaluation

**Quality Gate 5:** Interface contracts valid for the project type. Data/state model defined. NFRs have targets. Designs reference ADRs.

**Per-Phase Review:** 3 blind reviewers assess Phase 5 artifacts.

---

## Phase 6: Development

**Purpose:** Implement the codebase task by task from the story-tasks queue.

**Stage Agent:** `stage-development` (4 subagents)

**Subagents Dispatched:**
| Subagent | Task |
|----------|------|
| `sub-repo-analyzer` | Analyze existing codebase patterns and conventions |
| `sub-code-generator` | Implement features from task definitions |
| `sub-refactoring-agent` | Refactor code for quality and maintainability |
| `sub-documentation-agent` | Generate code-level and API documentation |

**Output:**
- Source code implementing all tasks
- Unit tests for all implemented code
- `.sdlc/artifacts/development/implementation-log.md`

**Quality Gate 6:** All unit tests pass. No build errors. Code follows project conventions.

**Per-Phase Review:** 3 blind reviewers assess Phase 6 code.

---

## Phase 7: Testing

**Purpose:** Comprehensive testing beyond unit tests — integration, regression, E2E.

**Stage Agent:** `stage-testing` (4 subagents)

**Subagents Dispatched:**
| Subagent | Task |
|----------|------|
| `sub-unit-test` | Ensure unit test coverage ≥ 80% |
| `sub-integration-test` | Test component interactions |
| `sub-regression-test` | Build regression suite from acceptance criteria |
| `sub-test-data` | Generate test fixtures and mock data |

**Output:**
- Test suites (unit, integration, regression, E2E)
- `.sdlc/artifacts/testing/coverage-report.md`
- `.sdlc/artifacts/testing/test-results.md`
- `.sdlc/artifacts/testing/test-data/` — Fixtures and mocks

**Quality Gate 7:** Unit coverage ≥ 80%. All tests pass. Every acceptance criterion has a test.

**Per-Phase Review:** 3 blind reviewers assess Phase 7 artifacts.

---

## Phase 8: Security

**Purpose:** Security audit — scan for secrets, vulnerabilities, OWASP issues, policy compliance.

**Stage Agent:** `stage-security` (4 subagents)

**Subagents Dispatched:**
| Subagent | Task |
|----------|------|
| `sub-secret-scanner` | Detect hardcoded secrets, API keys, tokens |
| `sub-dependency-scanner` | Audit dependency vulnerabilities |
| `sub-owasp-reviewer` | Review for OWASP Top 10 vulnerabilities |
| `sub-policy-validator` | Check security policy compliance |

**Output:**
- `.sdlc/artifacts/security/secret-scan.md`
- `.sdlc/artifacts/security/dependency-audit.md`
- `.sdlc/artifacts/security/owasp-review.md`
- `.sdlc/artifacts/security/policy-compliance.md`
- `.sdlc/artifacts/security/security-summary.md`

**Quality Gate 8:** Zero Critical/High findings. All secrets removed. Dependencies patched or documented.

**Per-Phase Review:** 3 blind reviewers assess Phase 8 artifacts. `sub-compliance-validator` is also dispatched here for security compliance.

---

## Phase 9: Review (Final Full-Codebase Review)

**Purpose:** Multi-perspective blind code review across the entire codebase — quality, maintainability, performance.

**Stage Agent:** `stage-review` (3 subagents)

**Subagents Dispatched:**
| Subagent | Task |
|----------|------|
| `sub-code-review` | Code quality, SOLID, best practices |
| `sub-maintainability` | Maintainability, tech debt, readability |
| `sub-performance` | Performance bottlenecks, optimization |

**Review Protocol:**
1. All 3 reviewers run in parallel (blind — no shared findings)
2. Each produces VERDICT (PASS/FAIL) + FINDINGS with severity
3. If unanimous PASS: run anti-sycophancy check (Devil's Advocate)
4. Fix Critical/High/Medium issues, re-run until all PASS

**Output:**
- `.sdlc/artifacts/review/code-review.md`
- `.sdlc/artifacts/review/maintainability-review.md`
- `.sdlc/artifacts/review/performance-review.md`
- `.sdlc/artifacts/review/review-summary.md`

**Quality Gate 9:** All reviewers PASS. No Critical/High/Medium findings remaining.

---

## Phase 10: DevOps

**Purpose:** Set up CI/CD, infrastructure configuration, deployment pipeline.

**Stage Agent:** `stage-devops` (no subagents)

**Output:**
- `.github/workflows/ci.yml` — CI/CD pipeline
- `Dockerfile`, `docker-compose.yml` — Containerization
- `.sdlc/artifacts/devops/env-configs/` — Environment configs
- `.sdlc/artifacts/devops/deployment-runbook.md` — Deployment runbook

**Quality Gate 10:** CI pipeline valid. Docker builds. Deployment runbook complete.

**Per-Phase Review:** 3 blind reviewers assess Phase 10 artifacts.

---

## Phase 11: Observability

**Purpose:** Define monitoring, alerting, SLOs, and operational readiness.

**Stage Agent:** `stage-observability` (no subagents)

**Output:**
- `.sdlc/artifacts/observability/slo-definitions.md`
- `.sdlc/artifacts/observability/logging-config.md`
- `.sdlc/artifacts/observability/alert-rules.md`
- `.sdlc/artifacts/observability/dashboard-specs.md`
- `.sdlc/artifacts/observability/runbook.md`

**Quality Gate 11:** SLOs defined for all critical paths. Health checks implemented. Alert rules cover error scenarios.

**Per-Phase Review:** 3 blind reviewers assess Phase 11 artifacts.

---

## Phase 12: Retirement (Triggered)

**Purpose:** Safely deprecate and decommission a feature or system — migration path, compliant data retention, and infrastructure removal.

**Stage Agent:** `stage-retirement` (4 subagents)

**Subagents Dispatched:**
| Subagent | Task |
|----------|------|
| `sub-deprecation-planner` | Build timeline, communication plan, stakeholder management |
| `sub-migration-strategist` | Plan user migration to replacement systems |
| `sub-data-retention-auditor` | Validate GDPR/HIPAA compliance for data deletion |
| `sub-decommission-executor` | Remove infrastructure, clean up dependencies |

**Triggers:** Explicit deprecation request, replacement system deployed, end-of-support date reached.

**Output:**
- `.sdlc/artifacts/retirement/deprecation-plan.md`
- `.sdlc/artifacts/retirement/migration-guide.md`
- `.sdlc/artifacts/retirement/data-retention-policy.md`
- `.sdlc/artifacts/retirement/decommission-checklist.md`
- `.sdlc/artifacts/retirement/post-mortem.md`

**Quality Gate 12:** ≥90 days notice published, migration path documented for all users, data retention complies with regulations, all infrastructure decommissioned/archived, post-mortem completed. `sub-compliance-validator` is dispatched here for data retention compliance. CRITICAL decommission actions require 2 recorded human sign-offs.

**Per-Phase Review:** 3 blind reviewers assess Phase 12 artifacts.

---

## Quality Gates Summary

| Gate | Phase | Pass Criteria |
|------|-------|---------------|
| 0 — Problem Validated | 0 (Problem Discovery) | Problem is clear, business case positive, alternatives evaluated, go/no-go recorded |
| 1 — Spec Valid | 1 (Bootstrap) | Input spec parseable and non-empty |
| 2 — Requirements Complete | 2 (Product) | All requirements have acceptance criteria |
| 3 — Story-Task Traceable | 3 (Story-Tasks) | All stories trace to requirements, no cycles |
| 4 — Architecture Sound | 4 (Architecture) | System design + ADRs for all decisions |
| 5 — Design Complete | 5 (Design) | Interface contracts valid, data/state model defined, NFRs targeted |
| 6 — Build Green | 6 (Development) | Zero build errors, all unit tests pass |
| 7 — Coverage Met | 7 (Testing) | Unit ≥ 80%, all acceptance criteria tested |
| 8 — Security Clear | 8 (Security) | Zero Critical/High findings |
| 9 — Review Passed | 9 (Review) | All 3 reviewers PASS |
| 10 — Pipeline Green | 10 (DevOps) | CI/CD runs without errors |
| 11 — Observability Ready | 11 (Observability) | SLOs defined, health checks implemented |
| 12 — Retirement Complete | 12 (Retirement) | Deprecation notice given, migration documented, compliant data retention, infra decommissioned |
