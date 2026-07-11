# Agent Types Reference

## Overview

The Autonomous SDLC Framework has 52 agents organized in a 3-tier hierarchy: 1 orchestrator, 12 stage agents, and 39 subagents. The orchestrator dispatches only the agents needed — typically all stage agents run sequentially, but subagents are selected based on project complexity. After every phase (except Phase 1 Bootstrap and Phase 9 Review), the orchestrator dispatches the full Review agent (3 blind reviewers) to assess that phase's artifacts.

---

## Orchestrator

| Agent | ID | Capabilities |
|-------|----|-------------|
| SDLC Orchestrator | `orch-sdlc` | Workflow control, phase transitions, task delegation, output validation, memory maintenance, quality gate enforcement, retry coordination, policy enforcement |

---

## Stage Agents

Phase 1 (Bootstrap) is handled directly by the orchestrator and has no dedicated stage agent. Phase 12 (Retirement) is only dispatched when triggered.

| Agent | ID | Phase | Capabilities | Subagent Count |
|-------|----|-------|-------------|----------------|
| Problem Discovery Agent | `stage-problem-discovery` | 0 | Problem validation, user-research synthesis, business case, build-vs-buy, go/no-go decision | 4 |
| Product Agent | `stage-product` | 2 | Requirements analysis, stakeholder synthesis, feature prioritization, scope definition | 4 |
| Story-Tasks Agent | `stage-story-tasks` | 3 | Epic/story/task decomposition, dependency mapping, prioritization, queue population | 3 |
| Architecture Agent | `stage-architecture` | 4 | High-level system design, tech stack selection, solution evaluation, ADR authoring | 3 |
| Design Agent | `stage-design` | 5 | Interface contracts, data/state modeling, integration planning, NFR evaluation | 4 |
| Development Agent | `stage-development` | 6 | Code generation, implementation orchestration, pattern enforcement, test-alongside workflow | 4 |
| Testing Agent | `stage-testing` | 7 | Test strategy, coverage orchestration, test data management, regression planning | 4 |
| Security Agent | `stage-security` | 8 | Threat modeling, vulnerability scanning, OWASP review, policy compliance | 4 |
| Review Agent | `stage-review` | 9 | Blind review orchestration, severity aggregation, anti-sycophancy checks | 3 |
| DevOps Agent | `stage-devops` | 10 | CI/CD pipelines, Docker, IaC, deployment strategies, environment configuration | 0 |
| Observability Agent | `stage-observability` | 11 | SLO/SLI definition, logging, alerting, dashboards, health checks, runbooks | 0 |
| Retirement Agent | `stage-retirement` | 12 | Deprecation planning, user migration, data retention, decommissioning | 4 |

---

## Product Subagents

| Agent | ID | Capabilities |
|-------|----|-------------|
| Requirement Parser | `sub-requirement-parser` | Parse raw input (PRD, brief, YAML, issue) into structured requirements. Identify functional vs non-functional. Categorize by domain. Detect ambiguity. |
| Acceptance Criteria Generator | `sub-acceptance-criteria` | Generate testable Given/When/Then criteria for each requirement. Map criteria to features. Ensure measurability. |
| Risk Analyzer | `sub-risk-analyzer` | Identify technical, business, schedule, and resource risks. Rate likelihood and impact. Propose mitigations. |
| Assumption Extractor | `sub-assumption-extractor` | Surface hidden assumptions in specs. Categorize as validated/unvalidated. Flag assumptions that could invalidate architecture. |

---

## Story-Tasks Subagents

| Agent | ID | Capabilities |
|-------|----|-------------|
| Story Writer | `sub-story-writer` | Decompose requirements into user stories with acceptance criteria. Group by epics. Ensure full requirement traceability. |
| Task Decomposer | `sub-task-decomposer` | Break stories into implementable tasks (< 4 hours). Assign agent types. Estimate effort (S/M/L). Define done criteria. |
| Dependency Mapper | `sub-dependency-mapper` | Build dependency graph. Identify critical path. Detect circular dependencies. Flag parallelizable tasks. |

---

## Architecture Subagents (ADR-Focused)

| Agent | ID | Capabilities |
|-------|----|-------------|
| Tech Stack Advisor | `sub-tech-stack-advisor` | Analyze requirements and recommend technology stack. Evaluate compatibility. Justify each choice against alternatives. |
| Solution Evaluator | `sub-solution-evaluator` | Evaluate alternative architectural solutions. Produce weighted trade-off analysis. Recommend best-fit option per decision. |
| ADR Writer | `sub-adr-writer` | Write Architecture Decision Records. Document context, options, rationale, consequences. Number sequentially. |

---

## Design Subagents

| Agent | ID | Capabilities |
|-------|----|-------------|
| Interface Designer | `sub-interface-designer` | Design interface contracts appropriate to project type: OpenAPI for REST APIs, GraphQL schemas, CLI specs, UI component specs, event catalogs, protocol definitions. Reference ADRs. |
| Data Model Designer | `sub-data-model-designer` | Design data/state models: relational schemas, document stores, file structures, in-memory state, event stores. Define structures, relationships, access patterns. Reference storage ADR. |
| Integration Planner | `sub-integration-planner` | Plan integrations: API calls, message queues, IPC, file I/O, SDK calls, hardware interfaces, plugin systems. Define patterns, error handling, fallbacks. Reference ADRs. |
| NFR Evaluator | `sub-nfr-evaluator` | Evaluate non-functional requirements: performance targets, scalability limits, availability SLAs, security requirements. Reference ADRs. |

---

## Development Subagents

| Agent | ID | Capabilities |
|-------|----|-------------|
| Repo Analyzer | `sub-repo-analyzer` | Analyze existing codebase: directory structure, patterns, conventions, dependencies, tech stack. Generate codebase summary. |
| Code Generator | `sub-code-generator` | Implement features from task definitions. Follow existing patterns. Write production-quality code with error handling. |
| Refactoring Agent | `sub-refactoring-agent` | Identify and execute refactoring opportunities. Apply SOLID principles. Reduce complexity. Improve naming and structure. |
| Documentation Agent | `sub-documentation-agent` | Generate code-level docs (JSDoc/docstrings), API documentation, README updates, architecture diagrams. |

---

## Testing Subagents

| Agent | ID | Capabilities |
|-------|----|-------------|
| Unit Test Agent | `sub-unit-test` | Generate unit tests for functions/methods/classes. Achieve ≥80% coverage. Test edge cases, error paths, boundary conditions. |
| Integration Test Agent | `sub-integration-test` | Test component interactions: API endpoints, database queries, service communication. Verify contracts. |
| Regression Test Agent | `sub-regression-test` | Map acceptance criteria to regression tests. Build suite that catches regressions. Verify existing functionality preserved. |
| Test Data Generator | `sub-test-data` | Generate test fixtures, mock data, factory functions. Create realistic but deterministic test data sets. |

---

## Security Subagents

| Agent | ID | Capabilities |
|-------|----|-------------|
| Secret Scanner | `sub-secret-scanner` | Detect hardcoded secrets, API keys, tokens, passwords, connection strings. Check .env files, config, code. |
| Dependency Scanner | `sub-dependency-scanner` | Audit all dependencies for known CVEs. Check for outdated packages. Recommend patches or alternatives. |
| OWASP Reviewer | `sub-owasp-reviewer` | Review code for OWASP Top 10: injection, broken auth, XSS, insecure deserialization, SSRF, etc. |
| Policy Validator | `sub-policy-validator` | Validate security policies: CORS, CSP, rate limiting, input validation, auth/authz, encryption at rest/transit. |

---

## Review Subagents

| Agent | ID | Capabilities |
|-------|----|-------------|
| Code Review Agent | `sub-code-review` | Review for code quality, SOLID principles, DRY, design patterns, error handling, naming, readability. |
| Maintainability Reviewer | `sub-maintainability` | Assess maintainability: cyclomatic complexity, coupling, cohesion, tech debt, test coverage, documentation. |
| Performance Reviewer | `sub-performance` | Identify performance issues: N+1 queries, unnecessary re-renders, missing indexes, inefficient algorithms, memory leaks. |

---

## Problem Discovery Subagents

| Agent | ID | Capabilities |
|-------|----|-------------|
| Problem Statement Extractor | `sub-problem-statement-extractor` | Parse vague input into a clear, testable problem statement. |
| User Research Synthesizer | `sub-user-research-synthesizer` | Validate problem severity via evidence and user research. |
| Opportunity Analyzer | `sub-opportunity-analyzer` | Assess market/business value and build the business case. |
| Solution Space Explorer | `sub-solution-space-explorer` | Evaluate build vs. buy vs. don't-build alternatives. |

---

## Retirement Subagents

| Agent | ID | Capabilities |
|-------|----|-------------|
| Deprecation Planner | `sub-deprecation-planner` | Timeline, communication, and stakeholder management for deprecation. |
| Migration Strategist | `sub-migration-strategist` | Plan user/data migration to replacement systems. |
| Data Retention Auditor | `sub-data-retention-auditor` | GDPR/HIPAA-compliant data retention and deletion. |
| Decommission Executor | `sub-decommission-executor` | Infrastructure removal and dependency cleanup. |

---

## Cross-Cutting Subagents

| Agent | ID | Capabilities |
|-------|----|-------------|
| Compliance Validator | `sub-compliance-validator` | GDPR/HIPAA/SOX/PCI-DSS validation (Phases 5, 8, 12). |
| Context Optimizer | `sub-context-optimizer` | Compress CONTINUITY.md working memory. |

---

## Agent Execution Model

Agents execute via role switching — the AI IDE takes on each agent's persona through its prompt file:

1. **Sequential (default):** Execute stage agents one at a time in phase order
2. **Parallel subagents:** Within a stage, subagents can run in parallel if independent
3. **Role switching:** The AI reads the agent's `.md` prompt and adopts that role

```
# Sequential stage execution (Phase 1 Bootstrap is orchestrator-direct)
for stage in problem-discovery product story-tasks architecture design development testing security review devops observability; do
  # AI reads agents/stage/$stage.md and executes
done
# Retirement (stage-retirement) runs only when triggered

# Parallel subagent execution within a stage
# Product stage dispatches all 4 subagents, then aggregates
```

---

## Agent Lifecycle

```
DISPATCH --> READ_PROMPT --> EXECUTE_RARV --> PRODUCE_ARTIFACTS --> HANDOFF
    |            |               |                  |               |
    |       Load agent.md    Reason-Act-       Write to          Update
    |       + context        Reflect-Verify    .sdlc/artifacts/  CONTINUITY.md
    |                             |                                |
    |                        Pass quality                    Next agent
    |                        gate?                           or phase
    |                             |
    |                     NO: retry (max 3)
    |                             |
    |                     FAIL: escalate
    v
 Orchestrator decides next dispatch
```

---

## Complexity-Based Agent Selection

| Complexity | Detection Criteria | Agents Spawned |
|------------|-------------------|----------------|
| Simple | < 5 requirements, single service, no integrations | All stages, minimal subagents (parser + code-gen + unit-test) |
| Medium | 5-15 requirements, 2-3 services, basic integrations | All stages, core subagents per stage |
| Complex | 15-50 requirements, microservices, multiple integrations | All stages, all subagents |
| Enterprise | 50+ requirements, distributed system, compliance needs | All stages, all subagents + extended review cycles |
