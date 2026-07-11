# Cost-Benefit Analysis

## Cost Calculation

True cost per feature (see [Realistic Cost Model](realistic-cost-model.md)):

```
3,314.5K tokens × $0.02/1K (2026 rate) = $66.29 per feature
```

## Value Delivered (Illustrative)

For a typical mid-complexity feature:
- **Bug reduction:** ~16% fewer post-ship defects vs. a 3-phase workflow (see [Methodology](methodology.md))
- **Debugging time saved:** ~4 hours of engineer time (at $75/hr ≈ $300 in avoided cost)
- **Security issue prevention:** varies wildly by context — see ROI scenarios below

## ROI Formula

```
ROI = (Value of defects avoided + time saved + risk avoided) − Cost of pipeline
```

`$66.29` is worth it when the feature is security-sensitive, high-traffic, or where a production incident would cost materially more than $66. It's *not* worth it for throwaway prototypes or internal scripts — use [Tiered Approach](tiered-approach.md) / Lite Mode for those.

## v4.0 Optimizations Change the Math

| Optimization | Mechanism | Cost Reduction |
|---------------|-----------|-----------------|
| Context Compression | `sub-context-optimizer` compresses CONTINUITY.md | ~60% |
| Tiered Model Routing | Route agents to reasoning/coding/fast tiers | ~81% |
| Task-Based Execution | Classify work as developer-led / developer+agent / fully agent-led | ~71% |

Combined (not purely additive — see below): **~71-90% total cost reduction** depending on feature mix and adaptive mode (`adaptive-policy.yaml`).

## Break-Even by Scenario

| Scenario | Optimized Cost | Value Delivered | ROI |
|----------|------------------|-------------------|-----|
| Enterprise security-critical | $33.15 (2028 rates) | $47K+ (breach/compliance/audit avoidance) | +$47K |
| Startup post-PMF | $19.40 (2026, lite mode) | $21K (bug/support/time-to-market) | +$21K |
| Consulting/agency | $33.15 (2028 rates) | $18K (rework/reputation/liability avoidance) | +$18K |
| Internal prototype / throwaway script | $66.29 (full pipeline, unoptimized) | ~$0-$50 | **Negative — use Lite Mode instead** |

## Gartner 2028 Forecast Context

Without optimization, token price increases (3-5x by 2028) push cost per feature to **$331.45**, or **$33,145/year** for 100 features/year — ~28% of an average developer's salary. v4.0's optimizations bring this down to **$33.15/feature** ($3,315/year) — a 90% reduction that keeps the framework sustainable through 2028 and beyond. See the [AI Governance Overview](../governance/ai-governance-overview.md) for the mechanisms.
