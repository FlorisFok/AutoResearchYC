#!/usr/bin/env bash
set -e

# ── If stdin is not a terminal (piped via curl), re-download & re-exec ──
if [ ! -t 0 ]; then
  rm -f /tmp/yc_bench_start.*.sh 2>/dev/null || true
  SELF=$(mktemp /tmp/yc_bench_start.XXXXXX.sh)
  curl -sSL https://raw.githubusercontent.com/collinear-ai/yc-bench/main/start.sh -o "$SELF"
  exec bash "$SELF" </dev/tty
fi

# ── Install uv if missing ───────────────────────────────────────────────
if ! command -v uv &>/dev/null; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

# ── Clone repo (skip if already inside it) ───────────────────────────────
if [ ! -f "pyproject.toml" ] || ! grep -q "yc.bench" pyproject.toml 2>/dev/null; then
  DIR="$HOME/Downloads/yc-bench"
  if [ -d "$DIR/.git" ]; then
    echo "Updating existing yc-bench in $DIR..."
    git -C "$DIR" pull --ff-only 2>/dev/null || true
  else
    echo "Cloning yc-bench into $DIR..."
    git clone --depth 1 https://github.com/collinear-ai/yc-bench.git "$DIR"
  fi
  cd "$DIR"
fi

# ── Install deps & launch ───────────────────────────────────────────────
uv sync --quiet
exec uv run yc-bench start
