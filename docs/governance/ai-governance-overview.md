# AI Governance Overview

autonomous-sdlc v4.0 adds an **opt-in governance layer** addressing the Gartner 2028 forecast that AI coding costs will exceed developer salaries without oversight. Governance is activated by the presence of `.sdlc/governance/` (created automatically by `sdlc init`, or run once via `sdlc upgrade` on existing projects).

If `.sdlc/governance/` does not exist, the orchestrator skips all governance checks — fully backward compatible with v3.0 behavior.

## Components

| File | Purpose |
|------|---------|
| `risk-policy.yaml` | 4-tier risk classification (low/medium/high/critical) with approval requirements |
| `budget-policy.yaml` | Total and per-phase USD spend limits with alert thresholds |
| `token-policy.yaml` | Per-feature/phase/agent token limits (Gartner token governance layer) |
| `compliance-policy.yaml` | Enabled regulatory frameworks (GDPR, HIPAA, SOX, PCI-DSS) |
| `execution-policy.yaml` | Task-based execution models (developer-led / developer+agent / fully agent-led) |
| `adaptive-policy.yaml` | Automatic mode switching based on monthly spend |
| `notification-config.yaml` | Slack/email/desktop channels for approval requests |
| `pending-approvals.json` | Runtime queue of approval requests awaiting a human decision |
| `decision-log.json` | Append-only audit trail of every significant decision |

## How It Works

1. **Before dispatching any agent**, the orchestrator classifies the upcoming decision against `risk-policy.yaml`.
2. **HIGH/CRITICAL risk decisions** pause execution and write an entry to `pending-approvals.json`. The user is notified (CLI/Slack/email per `notification-config.yaml`) and must run `sdlc approvals approve <ID>` or `sdlc approvals reject <ID> --reason "..."` before the orchestrator resumes.
3. **After every agent execution**, budget and token consumption are checked against `budget-policy.yaml` and `token-policy.yaml`. Warnings are logged at 50-80%; execution pauses at 100%.
4. **Every non-trivial decision** (technology choices, architecture trade-offs, retirement actions) is appended to `decision-log.json` with alternatives considered, rationale, and approval status — queryable via `sdlc explain <DEC-ID>`.
5. **Compliance-sensitive phases** (Design, Security, Retirement) dispatch `sub-compliance-validator` to check work against enabled frameworks in `compliance-policy.yaml`.

## See Also

- [Risk Classification](risk-classification.md)
- [Approval Workflows](approval-workflows.md)
- [Budget Controls](budget-controls.md)
- [Compliance Frameworks](compliance-frameworks.md)
- [Context Engineering Guide](context-engineering-guide.md)
