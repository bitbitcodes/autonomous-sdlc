# AGENTS.md — Agent Discovery File

This file follows the OpenAI/AAIF agent discovery standard. It describes the agents available in this framework and how to invoke them.

## Framework

**Autonomous SDLC Framework** — A multi-agent system for autonomous software development lifecycle execution.

## Agent Registry

### Orchestrator (Parent Agent)

| Field | Value |
|-------|-------|
| **ID** | `orch-sdlc` |
| **Prompt** | `.sdlc/framework/agents/orchestrator.md` |
| **Role** | Workflow control, task delegation, output validation, memory maintenance |
| **Dispatches** | All stage agents |

### Stage Agents

| ID | Prompt | Role | Subagents |
|----|--------|------|-----------|
| `stage-product` | `.sdlc/framework/agents/stage/product.md` | Requirements analysis & stakeholder synthesis | 4 |
| `stage-story-tasks` | `.sdlc/framework/agents/stage/story-tasks.md` | Epic/story/task decomposition, dependency mapping & queue population | 3 |
| `stage-architecture` | `.sdlc/framework/agents/stage/architecture.md` | High-level system design, tech stack selection & ADR authoring | 3 |
| `stage-design` | `.sdlc/framework/agents/stage/design.md` | Interface contracts, data/state modeling, integration planning & NFR evaluation | 4 |
| `stage-development` | `.sdlc/framework/agents/stage/development.md` | Code generation & implementation orchestration | 4 |
| `stage-testing` | `.sdlc/framework/agents/stage/testing.md` | Test strategy & coverage orchestration | 4 |
| `stage-security` | `.sdlc/framework/agents/stage/security.md` | Threat modeling & vulnerability scanning | 4 |
| `stage-review` | `.sdlc/framework/agents/stage/review.md` | Code review orchestration & quality assessment | 3 |
| `stage-devops` | `.sdlc/framework/agents/stage/devops.md` | CI/CD, infrastructure, deployment | 0 |
| `stage-observability` | `.sdlc/framework/agents/stage/observability.md` | Monitoring, alerting, SLO definition | 0 |

### Subagents

#### Product Subagents
| ID | Prompt | Focus |
|----|--------|-------|
| `sub-requirement-parser` | `.sdlc/framework/agents/sub/product/requirement-parser.md` | Parse & structure raw requirements |
| `sub-acceptance-criteria` | `.sdlc/framework/agents/sub/product/acceptance-criteria-generator.md` | Generate testable acceptance criteria |
| `sub-risk-analyzer` | `.sdlc/framework/agents/sub/product/risk-analyzer.md` | Identify risks & mitigations |
| `sub-assumption-extractor` | `.sdlc/framework/agents/sub/product/assumption-extractor.md` | Surface hidden assumptions |

#### Story-Tasks Subagents
| ID | Prompt | Focus |
|----|--------|-------|
| `sub-story-writer` | `.sdlc/framework/agents/sub/story-tasks/story-writer.md` | Decompose requirements into user stories |
| `sub-task-decomposer` | `.sdlc/framework/agents/sub/story-tasks/task-decomposer.md` | Break stories into implementable tasks |
| `sub-dependency-mapper` | `.sdlc/framework/agents/sub/story-tasks/dependency-mapper.md` | Build dependency graph & critical path |

#### Architecture Subagents (ADR-Focused)
| ID | Prompt | Focus |
|----|--------|-------|
| `sub-tech-stack-advisor` | `.sdlc/framework/agents/sub/architecture/tech-stack-advisor.md` | Technology stack recommendation |
| `sub-solution-evaluator` | `.sdlc/framework/agents/sub/architecture/solution-evaluator.md` | Alternative solution trade-off analysis |
| `sub-adr-writer` | `.sdlc/framework/agents/sub/architecture/adr-writer.md` | Architecture Decision Records |

#### Design Subagents
| ID | Prompt | Focus |
|----|--------|-------|
| `sub-interface-designer` | `.sdlc/framework/agents/sub/design/interface-designer.md` | Interface contract design (APIs, CLIs, UIs, events, protocols) |
| `sub-data-model-designer` | `.sdlc/framework/agents/sub/design/data-model-designer.md` | Data/state model design |
| `sub-integration-planner` | `.sdlc/framework/agents/sub/design/integration-planner.md` | External system integration |
| `sub-nfr-evaluator` | `.sdlc/framework/agents/sub/design/nfr-evaluator.md` | Non-functional requirements |

#### Development Subagents
| ID | Prompt | Focus |
|----|--------|-------|
| `sub-repo-analyzer` | `.sdlc/framework/agents/sub/development/repo-analyzer.md` | Codebase analysis & patterns |
| `sub-code-generator` | `.sdlc/framework/agents/sub/development/code-generator.md` | Code implementation |
| `sub-refactoring-agent` | `.sdlc/framework/agents/sub/development/refactoring-agent.md` | Code refactoring & cleanup |
| `sub-documentation-agent` | `.sdlc/framework/agents/sub/development/documentation-agent.md` | Code & API documentation |

#### Testing Subagents
| ID | Prompt | Focus |
|----|--------|-------|
| `sub-unit-test` | `.sdlc/framework/agents/sub/testing/unit-test-agent.md` | Unit test generation |
| `sub-integration-test` | `.sdlc/framework/agents/sub/testing/integration-test-agent.md` | Integration test generation |
| `sub-regression-test` | `.sdlc/framework/agents/sub/testing/regression-test-agent.md` | Regression test suites |
| `sub-test-data` | `.sdlc/framework/agents/sub/testing/test-data-generator.md` | Test fixture & data generation |

#### Security Subagents
| ID | Prompt | Focus |
|----|--------|-------|
| `sub-secret-scanner` | `.sdlc/framework/agents/sub/security/secret-scanner.md` | Detect hardcoded secrets |
| `sub-dependency-scanner` | `.sdlc/framework/agents/sub/security/dependency-scanner.md` | Dependency vulnerability audit |
| `sub-owasp-reviewer` | `.sdlc/framework/agents/sub/security/owasp-reviewer.md` | OWASP Top 10 review |
| `sub-policy-validator` | `.sdlc/framework/agents/sub/security/policy-validator.md` | Security policy compliance |

#### Review Subagents
| ID | Prompt | Focus |
|----|--------|-------|
| `sub-code-review` | `.sdlc/framework/agents/sub/review/code-review-agent.md` | Code quality & best practices |
| `sub-maintainability` | `.sdlc/framework/agents/sub/review/maintainability-reviewer.md` | Maintainability & tech debt |
| `sub-performance` | `.sdlc/framework/agents/sub/review/performance-reviewer.md` | Performance & optimization |

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
3. `.sdlc/framework/references/` docs (architecture, phases, workflow)
4. `.sdlc/framework/skills/` modules (loaded on demand)
