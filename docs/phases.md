# SDLC Phases

## Phase Pipeline

The framework executes 10 sequential phases, each with a quality gate:

```mermaid
flowchart TD
    P0["Phase 0: Bootstrap<br/>Initialize, normalize spec"] -->|"Gate 1: Spec Valid"| P1
    P1["Phase 1: Product<br/>Requirements, risks, criteria"] -->|"Gate 2: Requirements Complete"| P2
    P2["Phase 2: Architecture<br/>Design, APIs, data model"] -->|"Gate 3: Architecture Sound"| P3
    P3["Phase 3: Backlog<br/>Epics, stories, tasks"] -->|"Gate 4: Backlog Traceable"| P4
    P4["Phase 4: Development<br/>Implement codebase"] -->|"Gate 5: Build Green"| P5
    P5["Phase 5: Testing<br/>Unit, integration, regression"] -->|"Gate 6: Coverage Met"| P6
    P6["Phase 6: Security<br/>Scan, audit, remediate"] -->|"Gate 7: Security Clear"| P7
    P7["Phase 7: Review<br/>Blind 3-reviewer system"] -->|"Gate 8: Review Passed"| P8
    P8["Phase 8: DevOps<br/>CI/CD, Docker, deploy"] -->|"Gate 9: Pipeline Green"| P9
    P9["Phase 9: Observability<br/>SLOs, alerts, monitoring"] -->|"Gate 10: Observability Ready"| DONE

    DONE["PROJECT COMPLETE"]

    style P0 fill:#6c5ce7,color:#fff
    style P1 fill:#a29bfe,color:#fff
    style P2 fill:#74b9ff,color:#fff
    style P3 fill:#81ecec,color:#000
    style P4 fill:#55efc4,color:#000
    style P5 fill:#ffeaa7,color:#000
    style P6 fill:#fab1a0,color:#000
    style P7 fill:#ff7675,color:#fff
    style P8 fill:#fd79a8,color:#fff
    style P9 fill:#e17055,color:#fff
    style DONE fill:#00b894,color:#fff,font-weight:bold
```

## Phase 0: Bootstrap

**Purpose:** Initialize the framework and normalize the input spec.

**Agent:** Orchestrator (direct — no stage agent)

**Actions:**
1. Create `.sdlc/` directory structure
2. Parse and normalize input spec (PRD, YAML, brief, issue)
3. Store normalized spec in `.sdlc/specs/normalized-spec.md`
4. Detect project complexity (simple / medium / complex / enterprise)
5. Select agent team based on complexity
6. Initialize `CONTINUITY.md` and `orchestrator.json`

**Gate 1 — Spec Valid:** Input spec is parseable, non-empty, contains actionable requirements.

## Phase 1: Product Discovery

**Purpose:** Analyze requirements, identify risks, generate acceptance criteria.

**Agent:** `stage-product` with 4 subagents

```mermaid
flowchart LR
    SPEC[Normalized Spec] --> RP[Requirement Parser]
    RP --> AC[Acceptance Criteria Generator]
    RP --> RA[Risk Analyzer]
    RP --> AE[Assumption Extractor]
    AC & RA & AE --> OUT[Product Artifacts]
```

**Artifacts:**
| File | Content |
|------|---------|
| `artifacts/product/requirements.md` | Structured requirements (functional + NFR) |
| `artifacts/product/acceptance-criteria.md` | Given/When/Then criteria per feature |
| `artifacts/product/risks.md` | Risk register with severity and mitigations |
| `artifacts/product/assumptions.md` | Hidden assumptions flagged for validation |

**Gate 2 — Requirements Complete:** All requirements have IDs, acceptance criteria, and risk assessment.

## Phase 2: Architecture

**Purpose:** Design system architecture, API contracts, data models.

**Agent:** `stage-architecture` with 4 subagents

```mermaid
flowchart LR
    REQ[Requirements] --> AD[API Designer]
    REQ --> DM[Data Model Designer]
    REQ --> IP[Integration Planner]
    REQ --> NE[NFR Evaluator]
    AD & DM & IP & NE --> OUT[Architecture Artifacts]
```

**Artifacts:**
| File | Content |
|------|---------|
| `artifacts/architecture/system-design.md` | Architecture overview, component diagram |
| `artifacts/architecture/api-contracts.yaml` | OpenAPI 3.x specification |
| `artifacts/architecture/data-model.md` | Database schema, ERD, relationships |
| `artifacts/architecture/integrations.md` | External system integration plan |
| `artifacts/architecture/nfr-assessment.md` | NFR evaluation with target metrics |
| `artifacts/architecture/adrs/` | Architecture Decision Records |

**Gate 3 — Architecture Sound:** API contracts are valid OpenAPI, data model is normalized, NFRs have measurable targets.

## Phase 3: Backlog

**Purpose:** Decompose architecture into implementable work items.

**Agent:** `stage-backlog` (no subagents)

```mermaid
flowchart TD
    ARCH[Architecture] --> EPICS[Epics]
    EPICS --> STORIES[User Stories + Acceptance Criteria]
    STORIES --> TASKS["Tasks (< 4h each)"]
    TASKS --> QUEUE[".sdlc/queue/pending.json"]
```

**Artifacts:**
| File | Content |
|------|---------|
| `artifacts/backlog/epics.md` | Epic definitions |
| `artifacts/backlog/stories.md` | User stories with criteria |
| `artifacts/backlog/tasks.json` | Task list with dependencies |
| `queue/pending.json` | Populated task queue |

**Gate 4 — Backlog Traceable:** Every story traces to a requirement. No circular dependencies.

## Phase 4: Development

**Purpose:** Implement the codebase task by task.

**Agent:** `stage-development` with 4 subagents

```mermaid
flowchart TD
    QUEUE[Task Queue] --> CLAIM[Claim Task]
    CLAIM --> ANALYZE[Repo Analyzer]
    ANALYZE --> CODE[Code Generator]
    CODE --> TEST[Write Unit Tests]
    TEST --> VERIFY{Tests Pass?}
    VERIFY -->|Yes| COMMIT[Commit + Complete]
    VERIFY -->|No| FIX[Fix Issues]
    FIX --> TEST
    COMMIT --> QUEUE
```

**Per-task workflow:**
1. Claim from `queue/pending.json` → move to `queue/active.json`
2. Read task definition + architecture docs
3. Implement following existing patterns (repo analyzer)
4. Write unit tests alongside implementation
5. Run tests until passing
6. Commit checkpoint
7. Move to `queue/completed.json`

**Gate 5 — Build Green:** Zero build errors, zero lint errors, all unit tests pass.

## Phase 5: Testing

**Purpose:** Comprehensive testing beyond unit tests.

**Agent:** `stage-testing` with 4 subagents

**Testing layers:**
1. **Unit Tests** — ≥80% coverage (sub-unit-test)
2. **Integration Tests** — Component interactions (sub-integration-test)
3. **Regression Tests** — From acceptance criteria (sub-regression-test)
4. **Test Data** — Fixtures, mocks, factories (sub-test-data)

**Gate 6 — Coverage Met:** Unit ≥80%, all acceptance criteria have tests, integration tests pass.

## Phase 6: Security

**Purpose:** Security audit — scan, review, remediate.

**Agent:** `stage-security` with 4 subagents

```mermaid
flowchart LR
    CODE[Codebase] --> SS[Secret Scanner]
    CODE --> DS[Dependency Scanner]
    CODE --> OR[OWASP Reviewer]
    CODE --> PV[Policy Validator]
    SS & DS & OR & PV --> FINDINGS[Security Findings]
    FINDINGS --> FIX[Auto-Fix Critical/High]
    FIX --> REPORT[Security Summary]
```

**Gate 7 — Security Clear:** Zero Critical/High findings, no hardcoded secrets, dependencies patched.

## Phase 7: Review

**Purpose:** Multi-perspective code review with anti-sycophancy.

**Agent:** `stage-review` with 3 subagents (blind parallel)

```mermaid
flowchart TD
    CODE[Codebase] --> R1[Code Review Agent]
    CODE --> R2[Maintainability Reviewer]
    CODE --> R3[Performance Reviewer]

    R1 -->|VERDICT + FINDINGS| AGG[Aggregate]
    R2 -->|VERDICT + FINDINGS| AGG
    R3 -->|VERDICT + FINDINGS| AGG

    AGG --> CHECK{All PASS?}
    CHECK -->|"Yes (unanimous)"| DEVIL[Devil's Advocate Check]
    CHECK -->|No| FIX[Fix Issues + Re-review]
    DEVIL --> FINAL[Review Complete]
    FIX --> R1 & R2 & R3

    style R1 fill:#74b9ff,color:#000
    style R2 fill:#a29bfe,color:#fff
    style R3 fill:#fd79a8,color:#fff
```

**Key rules:**
- All 3 reviewers run **blind** — no visibility of each other's findings
- Unanimous PASS triggers an **anti-sycophancy check** (Devil's Advocate)
- Severity: Critical/High/Medium block; Low → TODO; Cosmetic → info only

**Gate 8 — Review Passed:** All reviewers PASS, no Critical/High/Medium findings.

## Phase 8: DevOps

**Purpose:** CI/CD pipeline, containerization, deployment.

**Agent:** `stage-devops` (no subagents)

**Outputs:** CI/CD config (GitHub Actions / GitLab CI), Dockerfile, docker-compose, deployment runbook, environment configs.

**Gate 9 — Pipeline Green:** CI runs without errors, Docker builds, runbook complete.

## Phase 9: Observability

**Purpose:** Monitoring, alerting, operational readiness.

**Agent:** `stage-observability` (no subagents)

**Outputs:** SLO/SLI definitions, logging config, alert rules, dashboard specs, operational runbook, health check endpoints.

**Gate 10 — Observability Ready:** SLOs defined, health checks implemented, alerts configured.

## Final Review

After all phases, a final cross-codebase review runs:

```mermaid
flowchart TD
    ALL[All Phases Complete] --> FR[Final Review: 3 Blind Reviewers]
    FR --> FIX[Fix Remaining Issues]
    FIX --> RE[Re-Review Until All PASS]
    RE --> REPORT[".sdlc/artifacts/final-review.md"]
    REPORT --> DONE["PROJECT COMPLETE"]

    style DONE fill:#00b894,color:#fff,font-weight:bold
```
