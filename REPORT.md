# autoresearch/mar31 — Prompt Evolution Report

## Overview

This experiment used autonomous prompt evolution to maximize `final_funds` on YC-bench's `medium` scenario — a 12-month business simulation where an LLM agent runs a consultancy, accepting tasks, managing 8 employees, and navigating adversarial clients.

**Starting point**: $-19,259 (bankruptcy, per program.md baseline)
**Final best (v5)**: $1,729,452 — a ~$1.75M improvement

Branch: `autoresearch/mar31`
Model: `anthropic/claude-sonnet-4-6`
Seed: 1

## Results Summary

| Version | Commit  | Final Funds   | Tasks Done | Tasks Failed | Outcome     | Kept? |
|---------|---------|--------------|------------|--------------|-------------|-------|
| baseline| 8b4d9fc | $-3,607      | 1          | 12           | bankruptcy  | --    |
| v1      | 2e4e239 | $806,333     | 79         | 4            | horizon_end | Yes   |
| v2      | 0d8444d | $665,427     | 71         | 21           | horizon_end | No    |
| v3      | 93de43d | $1,024,440   | 120        | 20           | horizon_end | Yes   |
| v4      | 387b4b5 | $-4,639      | 4          | 12           | bankruptcy  | No    |
| v5      | 9109c90 | $1,729,452   | 160        | 6            | horizon_end | Yes   |
| v6      | f8dfc90 | $1,355,484   | 158        | 13           | horizon_end | No    |

## Evolution Path

### Baseline → v1: $-3,607 → $806,333 (+$810K)
**The single biggest improvement.** The default prompt gave no guidance on employee allocation, so the agent assigned all 8 employees to every task. This caused:
- Payroll to compound ~2.7x faster than necessary
- Throughput split penalties (8 employees on N tasks = rate/N per employee)
- Rapid bankruptcy from escalating costs and missed deadlines

**v1 added:**
- Hard cap of 3 employees per task
- Turn-by-turn decision framework (check status → check tasks → decide)
- RAT client detection via `client history`
- Runway monitoring (stop accepting if < 4 months runway)

**Key insight**: Employee allocation is the single biggest lever. Controlling payroll growth is more important than maximizing task throughput.

### v1 → v2: $806,333 → $665,427 (-$141K, reverted)
Tried to optimize further with trust specialization (focus on 2-3 clients), stricter revenue thresholds, and defaulting to 2 employees instead of 3.

**Why it failed**: The revenue threshold was too restrictive — the agent became too picky, accepted fewer tasks overall (71 vs 79), and paradoxically had 5x more failures (21 vs 4). The agent would reject good tasks and later be forced into worse ones.

**Lesson**: Don't over-constrain task selection. Volume matters.

### v1 → v3: $806,333 → $1,024,440 (+$218K)
Built on v1 (not v2) with lighter-touch additions:
- Broad prestige climbing across domains
- Structured scratchpad template
- Post-task scratchpad updates

**Key insight**: Prestige climbing unlocked higher-paying tasks. The agent completed 120 tasks (vs 79 for v1), even with 20 failures — the extra volume more than compensated.

### v3 → v4: $1,024,440 → $-4,639 (bankruptcy, reverted)
Tried explicit "employee teams" (Team A, Team B, Reserve) and pushed for 2-3 concurrent tasks.

**Why it failed catastrophically**: Too much concurrency too early. The agent ran 4+ concurrent tasks from the start, spreading employees thin, missing deadlines, and burning through cash. Bankrupt by month 5.

**Lesson**: Explicit team structures can backfire — the agent follows them too literally and loses flexibility to adapt. Concurrency guidance should be soft ("if idle employees available") not hard ("always run 2-3").

### v3 → v5: $1,024,440 → $1,729,452 (+$705K)
The best iteration. Built on v3 with surgical improvements:
- **No-overlap rule**: "Only run 2 concurrent tasks if you can assign DIFFERENT employees to each" — prevents throughput split
- **Reward-per-employee selection**: Explicit metric for task comparison
- **Conditional second task**: "If 1 active task AND 4+ idle employees" — soft concurrency guidance

**Why it worked so well**: The no-overlap rule was the key. By ensuring employees were never shared across tasks, each task ran at full speed. Combined with smart task selection, this achieved 160 completions with only 6 failures — a 96.4% success rate.

### v5 → v6: $1,729,452 → $1,355,484 (-$374K, reverted)
Added: "In the last 2 months before horizon, only accept tasks you can DEFINITELY complete." Hypothesis: avoiding risky late tasks prevents wasted payroll on unfinished work.

**Why it underperformed**: Despite a strong early pace ($487K at month 3 vs v5's $289K), v6 finished $374K below v5. The late-game caution rule likely caused the agent to become too conservative in the final months, leaving revenue on the table. Additionally, v6 had 13 failures vs v5's 6 — suggesting the caution rule didn't prevent failures, it just reduced total attempts. The best strategy appears to be maintaining aggressive task acceptance right up to the horizon.

**Lesson**: Late-game conservatism is counterproductive. The compounding value of continued task completion outweighs the risk of a few late failures.

## What Worked (Ranked by Impact)

1. **Employee allocation cap (max 3)**: Transformed bankruptcy into profitability. The compounding salary bump mechanic means every extra employee assigned is a permanent cost increase. Keeping assignments lean is the foundation of everything else.

2. **No-overlap concurrency**: Allowing concurrent tasks ONLY when employees don't overlap gave the best of both worlds — parallel revenue without throughput penalties. This was the difference between $1M and $1.7M.

3. **Broad prestige climbing**: Accepting tasks across domains unlocked higher-prestige, higher-paying opportunities. This increased task volume from 79 to 120+.

4. **Structured decision framework**: The turn-by-turn checklist (check status → check tasks → decide) kept the agent focused and prevented common mistakes like calling `sim resume` with no active tasks.

5. **Scratchpad usage**: The persistent scratchpad survived context truncation (20-turn window). Storing RAT client blacklists and employee skill mappings gave the agent memory across the full 12-month simulation.

## What Didn't Work

1. **Strict revenue thresholds**: Making the agent too picky about task rewards reduced volume and paradoxically increased failures.

2. **Explicit employee teams**: Hard team assignments (Team A, Team B) removed flexibility. The agent needs to dynamically assign based on domain match, not follow a rigid structure.

3. **2-employee default**: Reducing from 3 to 2 employees made tasks take longer, increasing deadline risk. 2-3 with domain-matched skills is the sweet spot.

4. **Trust specialization**: Focusing exclusively on 2-3 clients limited the task pool. Broad prestige climbing was more valuable than deep trust building in this scenario.

5. **Late-game conservatism** (v6): Telling the agent to play it safe in the last 2 months reduced total revenue without reducing failures. The agent should stay aggressive until the horizon.

## Architecture of the Best Prompt (v5)

The winning prompt has four key sections:

1. **CRITICAL RULES** (8 rules): Hard constraints on employee allocation, concurrency, client vetting, deadlines, runway, prestige, and task selection.

2. **Turn-by-Turn Decision Framework**: Step-by-step procedure the agent follows every turn. This is crucial — without it, the agent makes ad-hoc decisions that often skip important checks.

3. **First Turn Setup**: Explicit initialization sequence that gathers intelligence (employee skills, client history) and writes it to the scratchpad before accepting any tasks.

4. **Key Mechanics**: Condensed reference of game mechanics the agent can consult. Reinforces the rules with explanations of why they matter.

## Infrastructure Notes

Two bugs in `yc-bench-main` required fixes to make the harness work:

1. **Chained `extends` in config loader** (`config/loader.py`): The loader only resolved one level of `extends`. Our config extends `medium` which extends `default`, but fields from `default.toml` were missing. Fixed by changing `if "extends"` to `while "extends"`.

2. **Absolute path in filenames** (`runner/main.py`): When `--config` is an absolute path, the DB, transcript, and results filenames included the full path (e.g., `results/yc_bench_result_/Users/.../custom_config.toml_...json`), causing `FileNotFoundError`. Fixed by extracting just the stem from the config path.

## Metrics

- **Total experiments**: 7 completed
- **Total wall-clock time**: ~8 hours (each run takes 30-60 min across multiple 15-min timeout/resume cycles)
- **API cost per run**: $7-13 (claude-sonnet-4-6)
- **Best result**: $1,729,452 (v5) — from $-3,607 baseline

## Next Steps

Promising directions for future iterations:

1. **Complete v6** — early data suggests the late-game caution rule may push past v5. Resume the run to get final numbers.
2. **Payroll-aware task acceptance** — explicitly compute whether a task's reward exceeds the salary bump cost it will create. Only accept tasks with positive net margin after accounting for the permanent payroll increase.
3. **Dynamic employee count** — use 2 employees for easy/low-prestige tasks and 3 for harder ones, rather than a fixed rule. This would slow payroll growth on simple tasks.
4. **Scratchpad as a ledger** — track per-client trust levels and per-domain prestige in the scratchpad so the agent can make informed decisions even after context truncation.
5. **Task pipelining** — instead of waiting for tasks to complete before browsing, pre-select the next task while current ones are in progress to minimize idle time between dispatches.
