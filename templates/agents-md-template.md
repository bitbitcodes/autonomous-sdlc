# AGENTS.md — Agent Discovery File

This file follows the OpenAI/AAIF agent discovery standard. It describes the agents available in this framework and how to invoke them.

## Framework

**Autonomous SDLC Framework** — A multi-agent system for autonomous software development lifecycle execution.

## Agent Registry

### Orchestrator (Parent Agent)

| Field | Value |
|-------|-------|
| **ID** | `orch-sdlc` |
| **Prompt** | `.sdlc-framework/agents/orchestrator.md` |
| **Role** | Workflow control, task delegation, output validation, memory maintenance |
| **Dispatches** | All stage agents |

### Stage Agents

| ID | Prompt | Role | Subagents |
|----|--------|------|-----------|
| `stage-product` | `.sdlc-framework/agents/stage/product.md` | Requirements analysis & stakeholder synthesis | 4 |
| `stage-architecture` | `.sdlc-framework/agents/stage/architecture.md` | System design, API contracts, data modeling | 4 |
| `stage-backlog` | `.sdlc-framework/agents/stage/backlog.md` | Epic/story/task decomposition & prioritization | 0 |
| `stage-development` | `.sdlc-framework/agents/stage/development.md` | Code generation & implementation orchestration | 4 |
| `stage-testing` | `.sdlc-framework/agents/stage/testing.md` | Test strategy & coverage orchestration | 4 |
| `stage-security` | `.sdlc-framework/agents/stage/security.md` | Threat modeling & vulnerability scanning | 4 |
| `stage-review` | `.sdlc-framework/agents/stage/review.md` | Code review orchestration & quality assessment | 3 |
| `stage-devops` | `.sdlc-framework/agents/stage/devops.md` | CI/CD, infrastructure, deployment | 0 |
| `stage-observability` | `.sdlc-framework/agents/stage/observability.md` | Monitoring, alerting, SLO definition | 0 |

### Subagents

#### Product Subagents
| ID | Prompt | Focus |
|----|--------|-------|
| `sub-requirement-parser` | `.sdlc-framework/agents/sub/product/requirement-parser.md` | Parse & structure raw requirements |
| `sub-acceptance-criteria` | `.sdlc-framework/agents/sub/product/acceptance-criteria-generator.md` | Generate testable acceptance criteria |
| `sub-risk-analyzer` | `.sdlc-framework/agents/sub/product/risk-analyzer.md` | Identify risks & mitigations |
| `sub-assumption-extractor` | `.sdlc-framework/agents/sub/product/assumption-extractor.md` | Surface hidden assumptions |

#### Architecture Subagents
| ID | Prompt | Focus |
|----|--------|-------|
| `sub-api-designer` | `.sdlc-framework/agents/sub/architecture/api-designer.md` | API contract design (OpenAPI) |
| `sub-data-model-designer` | `.sdlc-framework/agents/sub/architecture/data-model-designer.md` | Database schema & ERD |
| `sub-integration-planner` | `.sdlc-framework/agents/sub/architecture/integration-planner.md` | External system integration |
| `sub-nfr-evaluator` | `.sdlc-framework/agents/sub/architecture/nfr-evaluator.md` | Non-functional requirements |

#### Development Subagents
| ID | Prompt | Focus |
|----|--------|-------|
| `sub-repo-analyzer` | `.sdlc-framework/agents/sub/development/repo-analyzer.md` | Codebase analysis & patterns |
| `sub-code-generator` | `.sdlc-framework/agents/sub/development/code-generator.md` | Code implementation |
| `sub-refactoring-agent` | `.sdlc-framework/agents/sub/development/refactoring-agent.md` | Code refactoring & cleanup |
| `sub-documentation-agent` | `.sdlc-framework/agents/sub/development/documentation-agent.md` | Code & API documentation |

#### Testing Subagents
| ID | Prompt | Focus |
|----|--------|-------|
| `sub-unit-test` | `.sdlc-framework/agents/sub/testing/unit-test-agent.md` | Unit test generation |
| `sub-integration-test` | `.sdlc-framework/agents/sub/testing/integration-test-agent.md` | Integration test generation |
| `sub-regression-test` | `.sdlc-framework/agents/sub/testing/regression-test-agent.md` | Regression test suites |
| `sub-test-data` | `.sdlc-framework/agents/sub/testing/test-data-generator.md` | Test fixture & data generation |

#### Security Subagents
| ID | Prompt | Focus |
|----|--------|-------|
| `sub-secret-scanner` | `.sdlc-framework/agents/sub/security/secret-scanner.md` | Detect hardcoded secrets |
| `sub-dependency-scanner` | `.sdlc-framework/agents/sub/security/dependency-scanner.md` | Dependency vulnerability audit |
| `sub-owasp-reviewer` | `.sdlc-framework/agents/sub/security/owasp-reviewer.md` | OWASP Top 10 review |
| `sub-policy-validator` | `.sdlc-framework/agents/sub/security/policy-validator.md` | Security policy compliance |

#### Review Subagents
| ID | Prompt | Focus |
|----|--------|-------|
| `sub-code-review` | `.sdlc-framework/agents/sub/review/code-review-agent.md` | Code quality & best practices |
| `sub-maintainability` | `.sdlc-framework/agents/sub/review/maintainability-reviewer.md` | Maintainability & tech debt |
| `sub-performance` | `.sdlc-framework/agents/sub/review/performance-reviewer.md` | Performance & optimization |

## Invocation

Agents are invoked by reading their `.md` prompt file and passing it as the system/user prompt to your AI IDE. The orchestrator coordinates the full workflow. Stage agents are dispatched by the orchestrator. Subagents are dispatched by their parent stage agent.

## Structured Prompt Format

All agent prompts follow this structure:

```
## GOAL
[What success looks like — measurable outcome]

## CONSTRAINTS
[Hard limits — what you cannot do]

## CONTEXT
[Files to read, previous attempts, related decisions]

## OUTPUT
[Exact deliverables expected]
```

## Priority Order for Context

1. This `AGENTS.md` file
2. `.sdlc/CONTINUITY.md` (session state)
3. `.sdlc-framework/references/` docs (architecture, phases, workflow)
4. `.sdlc-framework/skills/` modules (loaded on demand)
