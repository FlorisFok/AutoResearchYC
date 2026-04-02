from __future__ import annotations

from dataclasses import dataclass
import os

from .agent.runtime.schemas import RuntimeSettings

@dataclass(frozen=True)
class RuntimeConfig:
    model: str
    temperature: float
    top_p: float
    history_keep_rounds: int = 20

def load_runtime_config():
    model = os.getenv("YC_BENCH_MODEL", "gpt-5.2")

    temperature = float(os.getenv("YC_BENCH_TEMPERATURE", "0"))
    top_p = float(os.getenv("YC_BENCH_TOP_P", "1"))
    history_keep_rounds = int(os.getenv("YC_BENCH_HISTORY_KEEP_ROUNDS", "20"))

    if temperature < 0:
        raise ValueError("YC_BENCH_TEMPERATURE must be >= 0")
    if top_p <= 0 or top_p > 1:
        raise ValueError("YC_BENCH_TOP_P must be in (0, 1]")
    if history_keep_rounds < 1:
        raise ValueError("YC_BENCH_HISTORY_KEEP_ROUNDS must be >= 1")

    return RuntimeConfig(
        model=model,
        temperature=temperature,
        top_p=top_p,
        history_keep_rounds=history_keep_rounds,
    )

def to_runtime_settings(cfg):
    return RuntimeSettings(
        model=cfg.model,
        temperature=cfg.temperature,
        top_p=cfg.top_p,
        history_keep_rounds=cfg.history_keep_rounds,
    )

__all__ = ["RuntimeConfig", "load_runtime_config", "to_runtime_settings"]
