# Realistic Cost Model

## The Problem With Naive Estimates

A naive token estimate for a feature (sum of each agent's expected base output) undercounts true cost by ignoring:

1. **RARV retries** — every agent retries failed verification steps, averaging 1.5 retries/task
2. **Quality gate failures** — ~20% of gates fail on first attempt and require rework
3. **Multi-agent conversation overhead** — context passed between orchestrator, stage agents, and subagents (40+ agents in v3.0, 52 in v4.0)
4. **Blind review overhead** — 3 parallel reviewers + Devil's Advocate anti-sycophancy check, run after every phase

## True Cost Breakdown (Representative Feature, 2026 Rates)

| Component | Tokens | Cost | % of Total |
|-----------|--------|------|------------|
| Base execution | 620K | $12.40 | 23% |
| RARV retries (1.5 avg) | 562.5K | $11.25 | 21% |
| Quality gate failures | 132K | $2.64 | 5% |
| Multi-agent conversations | 600K | $12.00 | 22% |
| Blind review overhead | 1,400K | $28.00 | 52%* |
| **TOTAL** | **3,314.5K** | **$66.29** | — |

*Percentages don't sum to 100% in the source model due to overlapping accounting between conversation and review overhead — treat the breakdown as directional.

## Why This Matters

Developers naturally optimize for speed, not cost, when designing agent pipelines. Left unmanaged, this "true cost" compounds badly against the Gartner 2028 token-price forecast (see [Cost-Benefit Analysis](cost-benefit-analysis.md)).

## Where v4.0 Tracks This

`.sdlc/state/token-usage.json` records every component above per phase and per agent in real time. `sdlc cost-report` renders it as a table with retry/gate statistics, so the true cost is visible during a run, not just estimated after the fact.
