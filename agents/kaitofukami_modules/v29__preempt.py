"""Composable debt-accounted SELL preemption wrapper."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from v23.policy_library import reorder_sell_slots
from v23.state_encoder import get
from v28.relay import projected_shed


@dataclass(frozen=True)
class PreemptionConfig:
    horizon: int = 1
    active_start: int = 700
    active_stop: int = 718
    maximum_batch: int = 100
    maximum_orders: int = 10


def _seat(obs: Any) -> int:
    return 1 if int(get(obs, "player", 0) or 0) == 1 else 0


def _future_sells(actions: list[dict], step: int, horizon: int) -> dict[str, int]:
    target = step + horizon
    if target >= len(actions):
        return {}
    result: dict[str, int] = {}
    for order in actions[target].get("market") or []:
        if len(order) >= 3 and order[0] == "SELL":
            item = str(order[1])
            result[item] = result.get(item, 0) + max(0, int(order[2]))
    return result


def wrap_sell_preemption(
    base_policy,
    schedule_actions: list[dict],
    config: PreemptionConfig = PreemptionConfig(),
):
    route = copy.deepcopy(schedule_actions)
    states = {0: {}, 1: {}}
    telemetry = {
        "games": 0,
        "preempt_turns": 0,
        "preempt_units": 0,
        "repaid_units": 0,
    }

    def policy(obs: Any, configuration: Any = None) -> dict:
        seat = _seat(obs)
        step = int(get(obs, "step", 0) or 0)
        state = states[seat]
        if step == 0 or step < int(state.get("last_step", -1)):
            state = {"last_step": step, "due": {}}
            states[seat] = state
            telemetry["games"] += 1
        state["last_step"] = step
        raw = base_policy(obs, configuration)
        result = copy.deepcopy(raw) if isinstance(raw, dict) else {}
        result["farmer"] = list(result.get("farmer") or ["PASS"])
        result["hands"] = [
            list(order or ["PASS"]) for order in (result.get("hands") or [])
        ]
        market = [
            list(order)
            for order in (result.get("market") or [])
            if isinstance(order, (list, tuple))
        ]

        due = dict(state.setdefault("due", {}).pop(step, {}) or {})
        repaid = 0
        adjusted = []
        for order in market:
            if len(order) >= 3 and order[0] == "SELL":
                item = str(order[1])
                debt = max(0, int(due.get(item, 0) or 0))
                if debt:
                    quantity = max(0, int(order[2]))
                    reduction = min(quantity, debt)
                    quantity -= reduction
                    due[item] = debt - reduction
                    repaid += reduction
                    if quantity <= 0:
                        continue
                    order[2] = quantity
            adjusted.append(order)
        for item, quantity in due.items():
            if quantity > 0 and step < 718:
                carry = state.setdefault("due", {}).setdefault(step + 1, {})
                carry[item] = int(carry.get(item, 0) or 0) + int(quantity)
        telemetry["repaid_units"] += repaid
        result["market"] = adjusted

        horizon = max(1, int(config.horizon))
        if not (
            int(config.active_start) <= step < int(config.active_stop)
            and step + horizon < len(route)
            and len(adjusted) < int(config.maximum_orders)
        ):
            return result
        future = _future_sells(route, step, horizon)
        if not future:
            return result
        available = projected_shed(obs, result)
        for order in adjusted:
            if len(order) >= 3 and order[0] == "SELL":
                item = str(order[1])
                available[item] = max(
                    0,
                    int(available.get(item, 0) or 0) - max(0, int(order[2])),
                )
        shifted = 0
        for item, requested in sorted(future.items()):
            if len(result["market"]) >= int(config.maximum_orders):
                break
            quantity = min(
                max(0, int(requested)),
                max(0, int(available.get(item, 0) or 0)),
                max(0, int(config.maximum_batch) - shifted),
            )
            if quantity <= 0:
                continue
            result["market"].append(["SELL", item, quantity])
            available[item] = max(0, int(available.get(item, 0)) - quantity)
            due_step = step + horizon
            due_row = state.setdefault("due", {}).setdefault(due_step, {})
            due_row[item] = int(due_row.get(item, 0) or 0) + quantity
            shifted += quantity
        if shifted:
            telemetry["preempt_turns"] += 1
            telemetry["preempt_units"] += shifted
            return reorder_sell_slots(
                obs,
                result,
                configuration,
                demand_alpha=0.25,
            )
        return result

    policy.states = states
    policy.telemetry = telemetry
    policy.preemption_config = config
    return policy

