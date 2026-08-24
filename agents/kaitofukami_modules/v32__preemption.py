"""Observable, latched one-turn SELL preemption for the v32 runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scripts.v19_terminal import clone_distance
from v23.state_encoder import get
from v29.preempt import PreemptionConfig, wrap_sell_preemption


@dataclass(frozen=True)
class LatchedPreemptionConfig:
    """Gate SELL preemption behind an observable near-clone signature.

    Once latched, the expert remains active because the underlying controller
    carries exact per-item debt for sells shifted from future turns.
    """

    horizon: int = 6
    detection_start: int = 48
    active_stop: int = 679
    clone_distance_threshold: float = 2.0
    clone_streak_required: int = 24
    maximum_batch: int = 100
    maximum_orders: int = 10


def wrap_latched_sell_preemption(
    base_policy,
    schedule_actions: list[dict],
    config: LatchedPreemptionConfig = LatchedPreemptionConfig(),
):
    """Preempt future route sells only after a persistent public-state match."""

    inner = wrap_sell_preemption(
        base_policy,
        schedule_actions,
        PreemptionConfig(
            horizon=max(1, int(config.horizon)),
            active_start=max(0, int(config.detection_start)),
            active_stop=max(0, int(config.active_stop)),
            maximum_batch=max(0, int(config.maximum_batch)),
            maximum_orders=max(1, int(config.maximum_orders)),
        ),
    )
    states = {0: {}, 1: {}}
    telemetry = {
        "games": 0,
        "near_turns": 0,
        "latches": 0,
        "latched_turns": 0,
        "preempt_turns": 0,
        "preempt_units": 0,
        "repaid_units": 0,
    }

    def policy(obs: Any, configuration: Any = None) -> dict:
        seat = 1 if int(get(obs, "player", 0) or 0) == 1 else 0
        step = int(get(obs, "step", 0) or 0)
        state = states[seat]
        if step == 0 or step < int(state.get("last_step", -1)):
            state = {"last_step": step, "near_streak": 0, "latched": False}
            states[seat] = state
            telemetry["games"] += 1
        state["last_step"] = step

        if clone_distance(obs) <= float(config.clone_distance_threshold):
            state["near_streak"] = int(state.get("near_streak", 0)) + 1
            telemetry["near_turns"] += 1
        else:
            state["near_streak"] = 0

        if (
            not bool(state.get("latched", False))
            and step >= int(config.detection_start)
            and int(state.get("near_streak", 0))
            >= max(1, int(config.clone_streak_required))
        ):
            state["latched"] = True
            telemetry["latches"] += 1

        if not bool(state.get("latched", False)):
            return base_policy(obs, configuration)

        telemetry["latched_turns"] += 1
        result = inner(obs, configuration)
        for key in ("preempt_turns", "preempt_units", "repaid_units"):
            telemetry[key] = int(inner.telemetry.get(key, 0) or 0)
        return result

    policy.states = states
    policy.telemetry = telemetry
    policy.preemption_config = config
    policy.inner_preemption = inner
    return policy
