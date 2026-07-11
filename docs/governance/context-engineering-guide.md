# Context Engineering Guide

Gartner's 2028 forecast flags "bloated context windows" as a primary driver of unsustainable AI coding costs. autonomous-sdlc addresses this with the **Context Optimizer** (`sub-context-optimizer`) and model routing.

## The Problem

`CONTINUITY.md` is read on every single turn to restore working memory across sessions. Left unchecked, it grows unbounded — a single feature can accumulate 50K+ tokens of "Completed Tasks" and "Mistakes & Learnings" detail that's no longer relevant, multiplied by every subsequent turn that re-reads it.

## The Fix: sub-context-optimizer

Dispatched by the orchestrator at phase boundaries or when `CONTINUITY.md` exceeds ~40K tokens. It:

1. **Never touches** Open Questions, Blocked Items, or the current phase/active task state.
2. Collapses "Completed Tasks" older than the current phase into one summary line per phase.
3. Deduplicates "Mistakes & Learnings" into pattern counts (e.g. "JSON overwrite violations: 3 occurrences, all fixed") instead of listing every instance.
4. Trims "Next Steps" to the top 3 priorities.
5. Archives anything removed to `.sdlc/memory/episodic/archive.md` — nothing is destroyed, only compressed.

**Expected savings:** ~60% token reduction per compression pass (per the v4.0 cost model, roughly 4M tokens per feature over a full lifecycle).

## Model Routing

`.sdlc/model-config.json` routes each agent to a cost-appropriate tier (`reasoning`, `coding`, `fast`) — see `sdlc models`. Pair this with context compression and task-based execution models (`execution-policy.yaml`) for the full Gartner-recommended cost stack:

```
Tiered model routing (81% reduction) + Context compression (60% reduction)
+ Task-based execution (71% reduction) = ~90% total cost reduction by 2028
```

See [Cost-Benefit Analysis](../evaluation/cost-benefit-analysis.md) for the full model.
