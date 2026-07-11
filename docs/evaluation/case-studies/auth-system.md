# Case Study: Auth System (OAuth2 + RBAC)

**Feature:** OAuth2 authentication with role-based access control, session management, and password reset flow.

## Profile

- **Complexity:** Complex (15-50 requirements, multiple integration points)
- **Recommended execution tier:** `developer_with_agent` for implementation, `developer_led` for the auth architecture decision itself (per `execution-policy.yaml` classification rules — "change authentication" → `critical` risk)
- **Recommended pipeline:** Full 13-phase pipeline — this is exactly the kind of feature the full pipeline exists for

## Results (mean of 10 runs, full pipeline)

| Metric | Value |
|--------|-------|
| Total tokens | 4.9M |
| Total cost (2026 rates) | $98 |
| Wall-clock time | ~2.5 hrs |
| Test coverage | 88% |
| Security issues found (pre-fix) | 0-2, all fixed before Gate 8 |
| Bugs found post-ship (estimated) | ~2% |

## Governance Behavior

Because `risk-policy.yaml` classifies "change authentication" as CRITICAL, Phase 4 (Architecture) and Phase 6 (Development) decisions touching the auth flow triggered `pending-approvals.json` entries requiring 2 human sign-offs before proceeding — consistent with the governance model, not a bug in the pipeline.

## Observations

- Highest retry rate of the three case studies (1.8 avg retries/task) — auth flows have more edge cases (expired tokens, revoked sessions, race conditions on refresh) that trip the RARV verify step.
- Security phase (8) found and fixed session-fixation and missing rate-limiting issues in 2/10 runs before Gate 8 passed.

## Takeaway

$98 is well justified here — a security breach in an auth system routinely costs $40K+ (see [Cost-Benefit Analysis](../cost-benefit-analysis.md)). This is the textbook "enterprise security-critical" ROI scenario.
