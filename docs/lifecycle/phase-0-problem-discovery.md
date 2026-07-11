# Phase 0: Problem Discovery & Validation

**Stage Agent:** `stage-problem-discovery` (`agents/stage/problem-discovery.md`)

## Purpose

Validate that a problem is real, severe, and worth solving before a single requirement is written. Evaluate build vs. buy vs. don't-build, and reach an explicit go/no-go decision.

## Subagents

| Subagent | Role |
|----------|------|
| `sub-problem-statement-extractor` | Converts vague/raw input into a clear, measurable problem statement |
| `sub-user-research-synthesizer` | Gathers evidence that the problem is severe/frequent enough (≥3 documented pain points) |
| `sub-opportunity-analyzer` | Builds a business case — ROI or strategic value |
| `sub-solution-space-explorer` | Scores ≥3 alternatives, always including "don't build" |

## Dispatch Order

1. Problem Statement Extractor (first — everything depends on it)
2. User Research Synthesizer + Opportunity Analyzer (parallel)
3. Solution Space Explorer (last — needs the business case)

## Artifacts

- `.sdlc/artifacts/problem-discovery/problem-statement.md`
- `.sdlc/artifacts/problem-discovery/user-research-synthesis.md`
- `.sdlc/artifacts/problem-discovery/business-case.md`
- `.sdlc/artifacts/problem-discovery/solution-alternatives.md`
- `.sdlc/artifacts/problem-discovery/go-no-go-decision.md`

## Quality Gate 0: Problem Validated

- Problem statement is clear and measurable
- ≥3 user pain points documented with evidence
- Business case shows positive ROI or explicit strategic value
- ≥3 solution alternatives evaluated
- Go/No-Go decision documented with rationale

## On NO-GO

The orchestrator **stops the pipeline** and reports the rationale to the user instead of proceeding to Phase 1 (Bootstrap). No architecture, design, or code is produced for a rejected problem.

## Skipping This Phase

Problem Discovery can be skipped only if the user explicitly opts out, or the input spec already includes an approved go/no-go decision (e.g. a JIRA epic with a documented business case).
