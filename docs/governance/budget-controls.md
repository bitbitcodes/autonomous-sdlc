# Budget Controls

Configured in `.sdlc/governance/budget-policy.yaml`. The orchestrator checks cumulative spend after every agent execution.

```yaml
budget:
  total_limit_usd: 100.00
  phase_limits:
    problem-discovery: 5.00
    development: 40.00
    # ... one entry per phase
  alerts:
    - threshold: 0.5
      action: log
    - threshold: 0.8
      action: warn
    - threshold: 1.0
      action: pause_and_escalate
  overage_policy: "pause"  # or "continue_with_approval"
```

## Enforcement

| Utilization | Action |
|---|---|
| >50% | Logged to `.sdlc/state/token-usage.json` |
| >80% | Warning surfaced in CONTINUITY.md and `sdlc status` |
| >100% | Execution pauses; a HIGH-risk approval request is written to `pending-approvals.json` asking to raise the budget or stop |

Run `sdlc cost-report` anytime to see current spend, breakdown by component (base execution, retries, gate failures, conversation overhead, review overhead), and budget utilization.

## Relationship to Token Policy

Budget (USD) and token limits (`token-policy.yaml`) are checked independently — a feature can hit a token hard-stop before exhausting its USD budget if token prices rise (see the [Gartner 2028 forecast context](../evaluation/cost-benefit-analysis.md)).
