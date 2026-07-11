# Case Study: Data Pipeline (ETL + Scheduling)

**Feature:** Scheduled ETL pipeline ingesting from an external API, transforming records, and loading into a data warehouse, with retry/backoff and monitoring.

## Profile

- **Complexity:** Medium-Complex (5-15 requirements, 2-3 services — source API, transform worker, warehouse)
- **Recommended execution tier:** `developer_with_agent`
- **Recommended pipeline:** Full pipeline, with emphasis on Phase 11 (Observability) given the scheduled/unattended nature of the workload

## Results (mean of 10 runs, full pipeline)

| Metric | Value |
|--------|-------|
| Total tokens | 3.3M |
| Total cost (2026 rates) | $66 |
| Wall-clock time | ~1.8 hrs |
| Test coverage | 81% |
| Security issues found | 0-1 |
| Bugs found post-ship (estimated) | ~4% |

## Observations

- Phase 5 (Design) required more NFR evaluation cycles than average — throughput and idempotency targets took 2 iterations to converge on realistic numbers.
- Phase 11 (Observability) artifacts (SLOs, alert rules) were unusually detailed for this feature type since pipeline failures are silent by nature (no user-facing error surface) — this drove above-average token spend in that phase specifically.
- Retry rate (1.5 avg) was mid-pack — mostly from Testing (Phase 7) fixture generation for external API mocking.

## Takeaway

Data pipelines benefit disproportionately from the Observability phase given their unattended operation — don't skip Phase 11 in Lite Mode for this feature type even if other phases are trimmed.
