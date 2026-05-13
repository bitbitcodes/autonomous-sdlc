# Agent Types Reference

## Overview

The Autonomous SDLC Framework has 35 agents organized in a 3-tier hierarchy: 1 orchestrator, 9 stage agents, and 25 subagents. The orchestrator dispatches only the agents needed — typically all 9 stages run sequentially, but subagents are selected based on project complexity.

---

## Orchestrator

| Agent | ID | Capabilities |
|-------|----|-------------|
| SDLC Orchestrator | `orch-sdlc` | Workflow control, phase transitions, task delegation, output validation, memory maintenance, quality gate enforcement, retry coordination, policy enforcement |

---

## Stage Agents

| Agent | ID | Capabilities | Subagent Count |
|-------|----|-------------|----------------|
| Product Agent | `stage-product` | Requirements analysis, stakeholder synthesis, feature prioritization, scope definition | 4 |
| Architecture Agent | `stage-architecture` | System design, technology selection, API contracts, data modeling, NFR evaluation | 4 |
| Backlog Agent | `stage-backlog` | Epic/story/task decomposition, dependency mapping, prioritization (MoSCoW), sprint planning | 0 |
| Development Agent | `stage-development` | Code generation, implementation orchestration, pattern enforcement, test-alongside workflow | 4 |
| Testing Agent | `stage-testing` | Test strategy, coverage orchestration, test data management, regression planning | 4 |
| Security Agent | `stage-security` | Threat modeling, vulnerability scanning, OWASP review, policy compliance | 4 |
| Review Agent | `stage-review` | Blind review orchestration, severity aggregation, anti-sycophancy checks | 3 |
| DevOps Agent | `stage-devops` | CI/CD pipelines, Docker, IaC, deployment strategies, environment configuration | 0 |
| Observability Agent | `stage-observability` | SLO/SLI definition, logging, alerting, dashboards, health checks, runbooks | 0 |

---

## Product Subagents

| Agent | ID | Capabilities |
|-------|----|-------------|
| Requirement Parser | `sub-requirement-parser` | Parse raw input (PRD, brief, YAML, issue) into structured requirements. Identify functional vs non-functional. Categorize by domain. Detect ambiguity. |
| Acceptance Criteria Generator | `sub-acceptance-criteria` | Generate testable Given/When/Then criteria for each requirement. Map criteria to features. Ensure measurability. |
| Risk Analyzer | `sub-risk-analyzer` | Identify technical, business, schedule, and resource risks. Rate likelihood and impact. Propose mitigations. |
| Assumption Extractor | `sub-assumption-extractor` | Surface hidden assumptions in specs. Categorize as validated/unvalidated. Flag assumptions that could invalidate architecture. |

---

## Architecture Subagents

| Agent | ID | Capabilities |
|-------|----|-------------|
| API Designer | `sub-api-designer` | Design RESTful/GraphQL API contracts. Generate OpenAPI 3.x specs. Define request/response schemas, error codes, pagination, auth. |
| Data Model Designer | `sub-data-model-designer` | Design database schemas (relational/NoSQL). Define entities, relationships, constraints, indexes. Generate migration scripts. |
| Integration Planner | `sub-integration-planner` | Plan external system integrations (auth providers, payment gateways, APIs). Define integration patterns, error handling, fallbacks. |
| NFR Evaluator | `sub-nfr-evaluator` | Evaluate non-functional requirements: performance targets, scalability limits, availability SLAs, security requirements, compliance needs. |

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

## Agent Execution Model

Agents execute via role switching — the AI IDE takes on each agent's persona through its prompt file:

1. **Sequential (default):** Execute stage agents one at a time in phase order
2. **Parallel subagents:** Within a stage, subagents can run in parallel if independent
3. **Role switching:** The AI reads the agent's `.md` prompt and adopts that role

```
# Sequential stage execution
for stage in product architecture backlog development testing security review devops observability; do
  # AI reads agents/stage/$stage.md and executes
done

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
