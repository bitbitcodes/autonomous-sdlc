# Tiered Approach Guide

Not every feature justifies the full 13-phase pipeline. `execution-policy.yaml` defines 3 execution models — pick the right one per feature based on risk and complexity.

## The Three Tiers

| Tier | Token Budget | Autonomy | Use When |
|------|---------------|----------|----------|
| `developer_led` | 50K | Advisory — human drives, AI suggests | Architecture decisions, novel problems, strategic choices |
| `developer_with_agent` | 500K | Collaborative | Standard feature development, API implementation, schema design |
| `fully_agent_led` | 5M | Autonomous | CRUD generation, test suites, documentation |

## Classification Rules

`execution-policy.yaml` matches decision descriptions against patterns:

```yaml
classification_rules:
  - pattern: "architecture|design pattern|technology choice"
    model: developer_led
  - pattern: "implement|build|create api"
    model: developer_with_agent
  - pattern: "generate crud|add tests|write docs"
    model: fully_agent_led
```

## Lite Mode (Simplified Pipeline)

For low-risk, low-complexity features, skip phases that add the least marginal quality per the [diminishing returns analysis](methodology.md):

```
Full pipeline:  0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 (→ 12 if triggered)
Lite mode:      1 (Bootstrap) → 2 (Product) → 6 (Development) → 7 (Testing)
```

Skip Problem Discovery (0) for well-understood internal tooling, and skip Architecture/Design/Security/Review/DevOps/Observability (3-5, 8-11) for prototypes and throwaway scripts. Re-run the full pipeline before anything reaches production.

## Expected Cost by Tier (2026 Rates)

| Approach | Cost/Feature | When |
|----------|---------------|------|
| Developer-led (20% of features) | ~$1 | Architecture/strategic decisions |
| Developer+agent (60% of features) | ~$10 | Standard feature dev |
| Fully agent-led (20% of features) | ~$66 | CRUD/tests/docs generation |
| **Blended average** | **~$19.40** | 71% reduction vs. always running the full pipeline |
