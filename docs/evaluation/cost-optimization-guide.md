# Cost Optimization Guide

Practical checklist for reducing token/cost spend, mapped to the mechanisms shipped in v4.0.

## 1. Enable Context Compression

Ensure `sub-context-optimizer` runs at phase boundaries (default behavior when `.sdlc/governance/` is present). Verify `CONTINUITY.md` stays under ~40K tokens with `sdlc status`.

## 2. Use Tiered Model Routing

```bash
sdlc models            # Review current agent → tier assignments
```

Route `stage-architecture`, `sub-adr-writer`, `stage-security` to `reasoning`; `stage-product`, `stage-design`, `stage-development`, `stage-testing` to `coding`; and all `sub-*` parsing/generation tasks to `fast`. See `.sdlc/model-config.json`.

## 3. Classify Work by Execution Tier

Apply `execution-policy.yaml`'s classification rules — don't run `fully_agent_led` autonomy on architecture decisions, and don't burn `developer_led` budget on CRUD generation.

## 4. Use Lite Mode for Low-Risk Features

See [Tiered Approach](tiered-approach.md) — skip Problem Discovery/Architecture/Security/Review/DevOps/Observability for prototypes.

## 5. Monitor and React

```bash
sdlc cost-report        # Per-run token/cost breakdown
```

Watch the `retry_stats` and `gate_stats` sections — high retry counts or gate failure rates indicate a prompt or context problem, not just a cost problem. Fixing the root cause (bad prompt, missing context) reduces cost AND improves quality.

## 6. Let Adaptive Mode Do the Work

If `.sdlc/governance/adaptive-policy.yaml` is configured, the framework automatically shifts between `aggressive_cost_saving`, `balanced`, and `quality_focused` modes based on monthly spend — no manual intervention required, though you should review `current_mode` periodically to confirm it matches your risk tolerance.

## 7. Diversify Vendors

Avoid single-vendor lock-in and pricing opacity by configuring multiple model vendors in `.sdlc/model-config.json` (see `vendors` block) and routing by task type/cost sensitivity.
