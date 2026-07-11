# Case Study: Simple CRUD API

**Feature:** `POST/GET/PUT/DELETE /api/v1/tasks` — a task management CRUD API with PostgreSQL persistence.

## Profile

- **Complexity:** Simple (< 5 requirements, single service)
- **Recommended execution tier:** `fully_agent_led` (per `execution-policy.yaml`)
- **Recommended pipeline:** Lite mode — Bootstrap → Product → Development → Testing (skip Architecture/Design/Security/Review/DevOps/Observability for an internal tool; run the full pipeline before production exposure)

## Results (mean of 10 runs, full pipeline)

| Metric | Value |
|--------|-------|
| Total tokens | 1.8M |
| Total cost (2026 rates) | $36 |
| Wall-clock time | ~45 min |
| Test coverage | 84% |
| Security issues found | 0 |
| Bugs found post-ship (estimated) | ~3% |

## Observations

- Requirements and acceptance criteria were straightforward — Phase 2 (Product) completed in a single pass with zero retries in 8/10 runs.
- Most retry overhead came from Phase 6 (Development) — code generator retried ~1.3x on average due to minor lint/type errors.
- Security scan (Phase 8) found zero issues — expected for a simple internal CRUD API with no auth surface.

## Takeaway

For a feature this simple, the full pipeline's marginal quality gain over Lite Mode is small relative to its cost (~$36 full vs. an estimated ~$10-15 in Lite Mode). Recommend Lite Mode unless the API is customer-facing or handles sensitive data.
