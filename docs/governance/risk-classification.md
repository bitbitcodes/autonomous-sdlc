# Risk Classification

Configured in `.sdlc/governance/risk-policy.yaml`. Every decision the orchestrator or a stage agent is about to execute is classified into one of 4 risk levels before execution.

## Risk Levels

| Level | Examples | Approval Required | Auto-Execute |
|-------|----------|--------------------|---------------|
| **Low** | Docs, tests, cosmetic changes | No | Yes |
| **Medium** | Feature additions, refactors, config changes | No (human review after) | Yes |
| **High** | Architecture changes, security policy, data model changes | Yes | No |
| **Critical** | Auth changes, payment logic, PII handling, production deploys, decommissioning | Yes (2 sign-offs) | No |

## Classification Rules

`risk-policy.yaml` contains a `decision_classification` list of regex-like patterns matched against the decision description, e.g.:

```yaml
decision_classification:
  - pattern: "change authentication"
    risk: critical
  - pattern: "modify database schema"
    risk: high
  - pattern: "add api endpoint"
    risk: medium
  - pattern: "update documentation"
    risk: low
```

Add project-specific patterns to tune classification for your domain (e.g. `pattern: "modify pricing"` → `critical` for an e-commerce project).

## Behavior on HIGH/CRITICAL

1. The orchestrator writes an entry to `.sdlc/governance/pending-approvals.json`.
2. Execution of that specific decision pauses (other independent work may continue).
3. The user is notified per `notification-config.yaml`.
4. `sdlc approvals approve APPR-XXX` or `sdlc approvals reject APPR-XXX --reason "..."` resolves it.
5. The resolution is appended to `decision-log.json`, retrievable via `sdlc explain DEC-XXX`.

CRITICAL decisions additionally require `requires_sign_off: 2` — two separate approvals before execution proceeds.
