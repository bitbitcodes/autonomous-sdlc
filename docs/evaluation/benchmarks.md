# Benchmarks

Sample benchmark data for 3 representative features, run through the full v4.0 13-phase pipeline. Each feature was modeled across 10 runs to capture retry variance (per the [Realistic Cost Model](realistic-cost-model.md)).

## Feature 1: Simple CRUD API

| Metric | Mean | Range (10 runs) |
|--------|------|-------------------|
| Total tokens | 1.8M | 1.5M - 2.3M |
| Total cost (2026 rates) | $36 | $30 - $46 |
| Wall-clock time | ~45 min | 35 - 60 min |
| Test coverage | 84% | 80% - 90% |
| Security issues (post-scan) | 0 | 0 - 1 |
| Avg retries/task | 1.1 | 0.8 - 1.6 |

See [Case Study: Simple CRUD API](case-studies/simple-crud-api.md).

## Feature 2: Auth System (OAuth2 + RBAC)

| Metric | Mean | Range (10 runs) |
|--------|------|-------------------|
| Total tokens | 4.9M | 3.9M - 6.1M |
| Total cost (2026 rates) | $98 | $78 - $122 |
| Wall-clock time | ~2.5 hrs | 2 - 3.5 hrs |
| Test coverage | 88% | 82% - 93% |
| Security issues (post-scan) | 0 | 0 - 2 (all fixed pre-gate) |
| Avg retries/task | 1.8 | 1.3 - 2.6 |

See [Case Study: Auth System](case-studies/auth-system.md).

## Feature 3: Data Pipeline (ETL + scheduling)

| Metric | Mean | Range (10 runs) |
|--------|------|-------------------|
| Total tokens | 3.3M | 2.7M - 4.2M |
| Total cost (2026 rates) | $66 | $54 - $84 |
| Wall-clock time | ~1.8 hrs | 1.3 - 2.5 hrs |
| Test coverage | 81% | 76% - 87% |
| Security issues (post-scan) | 0 | 0 - 1 |
| Avg retries/task | 1.5 | 1.0 - 2.2 |

See [Case Study: Data Pipeline](case-studies/data-pipeline.md).

## Notes on Methodology

- **10 runs per feature** captures the variance introduced by the RARV retry cycle (agents retry ~30% of tasks) and quality gate failures (~20% of gates fail on first attempt).
- All figures assume the "quality_focused" adaptive mode (see `adaptive-policy.yaml`) — no cost optimizations applied. See [Cost-Benefit Analysis](cost-benefit-analysis.md) for optimized figures.
- These are framework-derived model estimates, not independently audited production data — use them as a starting point and replace with your own `sdlc cost-report` output once you have real runs.
