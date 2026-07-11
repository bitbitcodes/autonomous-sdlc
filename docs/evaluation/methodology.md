# Evaluation Methodology

## Baseline Comparison

To answer "is the multi-agent overhead worth it?", we compare four approaches for the same representative feature (a CRUD API endpoint with auth):

| Approach | Tokens | Time | Test Coverage | Security Issues Found | Bug Rate (post-ship) |
|----------|--------|------|----------------|------------------------|----------------------|
| Single prompt ("write me an API") | ~15K | 2 min | ~20% (if any) | 0 (not scanned) | ~18% |
| 3-phase (requirements → code → test) | ~120K | 12 min | ~55% | 0 (not scanned) | ~10% |
| 10-agent (v3.0, no security/review) | ~450K | 35 min | ~75% | 1-2 (partial scan) | ~6% |
| 40-agent (v3.0 full pipeline) | 3,314.5K (true cost) | 90 min | ≥80% | 0 (full scan) | ~3% |

*(Figures are illustrative estimates derived from the framework's own cost model — see [Realistic Cost Model](realistic-cost-model.md) — not a controlled empirical study. Treat as directional, not precise.)*

## Diminishing Returns

Quality gains plateau after Phase 7 (Testing) / Phase 8 (Security) in the v4.0 numbering — additional review passes (Phase 9) and DevOps/Observability (Phase 10-11) primarily reduce *operational* risk (deployment failures, blind spots in production) rather than *code-level* defect rate.

```
Bug rate reduction by phase completed:
Phase 6 (Development) only:        ~18% → ~10%
+ Phase 7 (Testing):                ~10% → ~6%
+ Phase 8 (Security):                ~6% → ~4%
+ Phase 9 (Review):                  ~4% → ~3%
+ Phase 10-11 (DevOps/Observability): ~3% → ~3% (unchanged defect rate, but faster incident detection)
```

## Recommendation: Lite Mode

For simple, low-risk features (CRUD generation, internal tooling, prototypes), running the full 13-phase pipeline is often not worth the cost. Use `execution-policy.yaml`'s `fully_agent_led` classification with a reduced agent set (Bootstrap → Product → Development → Testing) and skip Security/Review/DevOps/Observability for non-production-critical work. See [Tiered Approach](tiered-approach.md).

## Sample Data & Case Studies

See [Benchmarks](benchmarks.md) for representative per-feature runs and [Case Studies](case-studies/) for three worked examples (simple CRUD, auth system, data pipeline).
