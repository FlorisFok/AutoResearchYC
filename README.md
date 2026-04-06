# YC-Bench #1 — Autonomous Prompt Evolution

**Score: $1,729,452** — the highest score on [YC-Bench](https://yc-bench.com/) (Medium), beating the previous #1 by over $500K.

| # | Model | Score |
|---|-------|-------|
| **1** | **This repo (Claude Sonnet 4.6)** | **$1,729,452** |
| 2 | zai-org/GLM-5 | $1,208,190 |
| 3 | moonshotai/Kimi-K2.5 | $408,822 |
| 4 | zai-org/GLM-4.7 | $398,410 |
| 5 | MiniMaxAI/MiniMax-M2.5 | $230,465 |
| 6 | deepseek-ai/DeepSeek-V3.2 | $125,263 |
| 7 | Qwen/Qwen3.5-397B-A17B | $90,787 |
| 8 | arcee-ai/Trinity-Large-Thinking | $32,667 |
| 9 | Qwen/Qwen3.5-122B-A10B | $0 |
| - | Claude Sonnet 4.6 (no prompt evolution) | -$3,607 |

See the [full leaderboard on HuggingFace](https://huggingface.co/datasets/collinear-ai/yc-bench) for the most up-to-date rankings.

## What is YC-Bench?

YC-Bench is a 12-month business simulation where an LLM agent runs a consultancy — accepting tasks, managing 8 employees, and navigating adversarial clients. The metric is `final_funds` at the end of the simulation. The agent interacts with the simulation through CLI commands, making decisions about task selection, employee allocation, client management, payroll, and prestige building.

## What we did

We used **autonomous prompt evolution** to iteratively improve the agent's system prompt over 7 versions. An LLM autonomously modifies the prompt, runs the benchmark, evaluates the result, and decides whether to keep or revert the change — in a loop.

Starting from a baseline that went bankrupt (-$3,607), we evolved the prompt to $1,729,452 — a ~$1.75M improvement. The key breakthroughs were:

1. **Employee allocation cap (max 3 per task)** — controlling compounding salary bumps
2. **No-overlap concurrency** — only run parallel tasks with different employees
3. **Broad prestige climbing** — unlocking higher-paying tasks across all domains

The full evolution path, what worked, what didn't, and detailed analysis is in [REPORT.md](REPORT.md).

## Project structure

```
prompt.txt          — the evolved system prompt (this is what we optimize)
program.md          — instructions for the autonomous prompt evolution agent
run_bench.py        — evaluation harness (runs yc-bench with prompt.txt)
run_with_resume.sh  — runner with automatic resume on timeout
custom_config.toml  — yc-bench config with the prompt embedded
REPORT.md           — detailed report of the evolution process
yc-bench-main/      — vendored copy of the YC-Bench benchmark
```

## How it works

The autonomous loop (described in [program.md](program.md)):

1. **Edit** `prompt.txt` — the system prompt sent to the YC-bench agent
2. **Run** the benchmark: `uv run run_bench.py`
3. **Evaluate** the result (final_funds)
4. **Keep** if improved, **revert** if not
5. **Repeat**

The agent can only modify `prompt.txt`. The benchmark, harness, and simulation are read-only.

## Quick start

**Requirements:** Python 3.12+, [uv](https://docs.astral.sh/uv/), an `ANTHROPIC_API_KEY`

```bash
# 1. Clone and enter
git clone https://github.com/FlorisFok/AutoResearchYC.git
cd AutoResearchYC

# 2. Set your API key
export ANTHROPIC_API_KEY="sk-ant-..."

# 3. Install yc-bench dependencies
cd yc-bench-main && uv sync && cd ..

# 4. Run the benchmark with the evolved prompt
uv run run_bench.py
```

Or use the resume wrapper for long runs:

```bash
bash run_with_resume.sh
```

## Run your own prompt evolution

Point your favorite coding agent at this repo and tell it:

```
Read program.md and start evolving the prompt. The goal is to maximize final_funds.
```

The agent will autonomously loop through prompt edits, benchmark runs, and result evaluation.

## Acknowledgments

This project builds on [YC-Bench](https://github.com/collinear-ai/yc-bench) by [Collinear AI](https://collinear.ai/) — a long-horizon deterministic benchmark for LLM agents. The benchmark source is included in `yc-bench-main/` under the MIT license. Thanks to the Collinear AI team for building such a great benchmark!

## License

MIT
