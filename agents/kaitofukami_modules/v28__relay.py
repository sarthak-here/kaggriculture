"""Route-preserving market-timing experts for the v28 metagame study.

The debt-accounted timing idea is derived from two public Kaggriculture
notebooks and extended here into a game-level mixed strategy:

* Andrew Sokolovsky, ``Kaggriculture: Breaking the Tie``
* boatlee, ``V16-RC2 High Score | Near-Mirror Market Relay``

The extension keeps one coherent farm route, shifts only route-existing SELL
quantity, repays every shifted unit at its original step, and can privately
sample the lead horizon once per game.  It never reads opponent identity or
private state.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
import hashlib
import math
import os
from typing import Sequence

from scripts.v22_market_impact import MARKET_PARAMS, market_price
from v23.planner import PlannerConfig, build_sparse_planner
from v23.policy_library import reorder_sell_slots
from v23.state_encoder import get, shop_demand_per_day, regime_from_configuration


DEFAULT_RELAY_ITEMS = (
    "STRAWBERRY",
    "MELON",
    "MILK",
    "WOOL",
    "FERTILIZER",
)


@dataclass(frozen=True)
class RelayConfig:
    horizons: tuple[int, ...] = (0, 1, 2, 3)
    weights: tuple[float, ...] = (0.25, 0.25, 0.25, 0.25)
    items: tuple[str, ...] = DEFAULT_RELAY_ITEMS
    checkpoints: tuple[int, ...] = (24, 48, 72)
    matches_required: int = 3
    distance_max: int = 6
    break_distance: int = 18
    break_checks: int = 2
    active_start: int = 120
    active_stop: int = 678
    minimum_future_quantity: int = 3
    maximum_batch: int = 30
    maximum_orders_per_turn: int = 2
    minimum_edge: float = 1.0
    adaptive_fallback: bool = False
    planner: PlannerConfig = PlannerConfig()


def normalize_weights(weights: Sequence[float]) -> tuple[float, ...]:
    values = tuple(max(0.0, float(value)) for value in weights)
    total = sum(values)
    if not values or total <= 0:
        raise ValueError("relay mixture needs positive weight")
    return tuple(value / total for value in values)


def choose_horizon(
    horizons: Sequence[int],
    weights: Sequence[float],
    *,
    nonce: bytes,
    game_index: int,
    seat: int,
    public_key: str = "",
) -> int:
    """Sample one horizon from process-private entropy and a public game key."""
    choices = tuple(int(value) for value in horizons)
    normalized = normalize_weights(weights)
    if not choices or len(choices) != len(normalized):
        raise ValueError("relay horizons and weights differ")
    if any(value < 0 for value in choices):
        raise ValueError("relay horizons must be non-negative")
    key = f"{int(game_index)}:{int(seat)}:{public_key}".encode("utf-8")
    raw = hashlib.blake2b(key, key=bytes(nonce), digest_size=8).digest()
    draw = int.from_bytes(raw, "big") / float(1 << 64)
    cumulative = 0.0
    for horizon, weight in zip(choices, normalized):
        cumulative += weight
        if draw < cumulative:
            return horizon
    return choices[-1]


def _safe_action(action) -> dict:
    result = copy.deepcopy(action) if isinstance(action, dict) else {}
    result["farmer"] = list(result.get("farmer") or ["PASS"])
    result["hands"] = [
        list(order or ["PASS"]) for order in (result.get("hands") or [])
    ]
    result["market"] = [
        list(order) for order in (result.get("market") or [])
        if isinstance(order, (list, tuple))
    ]
    return result


def _seat(obs) -> int:
    return 1 if int(get(obs, "player", 0) or 0) == 1 else 0


def _farm(obs, seat: int):
    farms = list(get(obs, "farms", []) or [])
    return farms[seat] if seat < len(farms) else {}


def _shed_access(size: int) -> set[tuple[int, int]]:
    half = size // 2
    return {
        (half - 1, half - 1),
        (half, half - 1),
        (half - 1, half),
        (half, half),
    }


def projected_shed(obs, action) -> dict[str, int]:
    """Shed after same-turn DROP/PLACE, before this action's market orders."""
    farm = _farm(obs, _seat(obs))
    private = get(obs, "private", {}) or {}
    projected = {
        str(item): max(0, int(quantity or 0))
        for item, quantity in dict(get(private, "shed", {}) or {}).items()
    }
    inventories = list(get(private, "inventories", []) or [])
    positions = [
        get(farm, "farmer", [0, 0]),
        *list(get(farm, "hands", []) or []),
    ]
    unit_actions = [action.get("farmer", ["PASS"]), *(action.get("hands") or [])]
    tiles = list(get(farm, "tiles", []) or [])
    access = _shed_access(len(tiles) or 10)
    for index, unit_action in enumerate(unit_actions):
        if index >= len(positions) or index >= len(inventories):
            continue
        position = positions[index]
        if not isinstance(position, (list, tuple)) or len(position) < 2:
            continue
        x, y = int(position[0]), int(position[1])
        if (
            (x, y) not in access
            or not (0 <= y < len(tiles))
            or not (0 <= x < len(tiles[y]))
        ):
            continue
        inventory = {
            str(item): max(0, int(quantity or 0))
            for item, quantity in dict(inventories[index] or {}).items()
        }
        if unit_action and unit_action[0] == "DROP":
            deposits = tuple(inventory.items())
        elif unit_action and unit_action[0] == "PLACE" and len(unit_action) >= 2:
            item = str(unit_action[1])
            tile = tiles[y][x]
            structure = {
                "COW": "PASTURE",
                "SHEEP": "PASTURE",
                "GOOSE": "COOP",
            }.get(item)
            if (
                structure
                and isinstance(tile, dict)
                and tile.get("kind") == structure
                and not tile.get("animal")
            ):
                continue
            try:
                requested = int(unit_action[2]) if len(unit_action) >= 3 else 1
            except (TypeError, ValueError):
                continue
            deposits = ((item, min(max(0, requested), inventory.get(item, 0))),)
        else:
            continue
        for item, quantity in deposits:
            room = max(0, 100 - sum(projected.values()))
            amount = min(max(0, int(quantity or 0)), room)
            if amount:
                projected[item] = projected.get(item, 0) + amount
    return projected


def _public_signature(farm) -> tuple[int, int, tuple[int, ...]]:
    keys = (
        "WHEAT",
        "CARROT",
        "TOMATO",
        "STRAWBERRY",
        "MELON",
        "COW",
        "SHEEP",
        "GOOSE",
        "PASTURE",
        "COOP",
        "WEED",
    )
    counts = {key: 0 for key in keys}
    for row in (get(farm, "tiles", []) or []):
        for tile in row if isinstance(row, list) else [row]:
            if not isinstance(tile, dict):
                continue
            for field in ("crop", "animal", "kind"):
                value = str(tile.get(field, "") or "").upper()
                if value in counts:
                    counts[value] += 1
                    break
    return (
        len(get(farm, "hands", []) or []),
        len(get(farm, "unlocked_quadrants", []) or []),
        tuple(counts[key] for key in sorted(counts)),
    )


def public_route_distance(obs) -> int:
    farms = list(get(obs, "farms", []) or [])
    if len(farms) < 2:
        return 10**9
    left = _public_signature(farms[0])
    right = _public_signature(farms[1])
    return (
        abs(left[0] - right[0])
        + 3 * abs(left[1] - right[1])
        + sum(abs(a - b) for a, b in zip(left[2], right[2]))
    )


def _future_sells(actions, step: int, horizon: int, config: RelayConfig):
    future_step = step + horizon
    if horizon <= 0 or future_step >= len(actions):
        return {}
    result: dict[str, int] = {}
    for raw in (actions[future_step].get("market") or []):
        if (
            isinstance(raw, (list, tuple))
            and len(raw) >= 3
            and raw[0] == "SELL"
            and str(raw[1]) in config.items
        ):
            item = str(raw[1])
            result[item] = result.get(item, 0) + max(0, int(raw[2]))
    return result


def _has_intervening_sell(actions, step: int, due_step: int, item: str) -> bool:
    """Protect inventory reserved by a nearer scheduled sale of the same item."""
    for future_step in range(step + 1, due_step):
        for raw in (actions[future_step].get("market") or []):
            if (
                isinstance(raw, (list, tuple))
                and len(raw) >= 3
                and raw[0] == "SELL"
                and str(raw[1]) == item
                and max(0, int(raw[2])) > 0
            ):
                return True
    return False


def _sell_revenue(item: str, inventory: int, quantity: int) -> tuple[float, int]:
    revenue = 0.0
    level = int(inventory)
    for _ in range(max(0, int(quantity))):
        price = market_price(item, level)
        revenue += float(price)
        if price > 1:
            level += 1
    return revenue, level


def _demand_per_turn(obs, configuration, item: str) -> float:
    town = get(obs, "town", {}) or {}
    shops = list(get(town, "unlocked_shops", []) or [])
    step = int(get(obs, "step", 0) or 0)
    turns = int(get(configuration, "turnsPerDay", 24) or 24)
    shop_interval = int(get(configuration, "townShopSellInterval", 4) or 4)
    regime = regime_from_configuration(configuration)
    center_default = 24 if regime == "rebalance" else 12
    center_interval = int(
        get(configuration, "townCenterSellInterval", center_default) or center_default
    )
    demand = shop_demand_per_day(
        shops,
        day=step // max(1, turns),
        regime=regime,
        turns_per_day=turns,
        shop_interval=shop_interval,
        center_interval=center_interval,
    )
    return float(demand.get(item, 0.0)) / max(1, turns)


def expected_preemption_edge(
    obs,
    configuration,
    item: str,
    quantity: int,
    horizon: int,
) -> float:
    """Value of selling before one same-sized collision instead of behind it."""
    market = get(obs, "market", {}) or {}
    inventory = get(market, "inventory", {}) or {}
    level = int(get(inventory, item, MARKET_PARAMS[item][1]) or 0)
    now, _ = _sell_revenue(item, level, quantity)
    _, after_opponent = _sell_revenue(item, level, quantity)
    recovery = int(round(_demand_per_turn(obs, configuration, item) * horizon))
    later, _ = _sell_revenue(item, max(0, after_opponent - recovery), quantity)
    return now - later


def _repay(action: dict, state: dict, step: int) -> dict:
    due_map = dict((state.get("due") or {}).pop(step, {}) or {})
    if not due_map:
        return action
    result = _safe_action(action)
    remaining = {
        str(item): max(0, int(quantity or 0))
        for item, quantity in due_map.items()
    }
    market = []
    for raw in result["market"]:
        order = list(raw)
        if len(order) >= 3 and order[0] == "SELL":
            item = str(order[1])
            debt = remaining.get(item, 0)
            if debt:
                requested = max(0, int(order[2]))
                reduction = min(requested, debt)
                requested -= reduction
                remaining[item] = debt - reduction
                if requested <= 0:
                    continue
                order[2] = requested
        market.append(order)
    result["market"] = market
    leftovers = {item: quantity for item, quantity in remaining.items() if quantity > 0}
    if leftovers:
        carry = state.setdefault("due", {}).setdefault(step + 1, {})
        for item, quantity in leftovers.items():
            carry[item] = int(carry.get(item, 0) or 0) + int(quantity)
    return result


def build_relay_planner(
    actions,
    config: RelayConfig = RelayConfig(),
    *,
    nonce: bytes | None = None,
):
    """Build a coherent route plus a guarded game-level timing expert."""
    route = copy.deepcopy(actions)
    if len(route) != 719:
        raise ValueError("relay route must contain 719 actions")
    if len(config.horizons) != len(config.weights):
        raise ValueError("relay horizons and weights differ")
    normalized = normalize_weights(config.weights)
    private_nonce = bytes(nonce) if nonce is not None else os.urandom(32)
    if not private_nonce:
        raise ValueError("relay nonce must not be empty")
    base = build_sparse_planner(route, config.planner)
    states = {0: {}, 1: {}}
    telemetry = {
        "games": 0,
        "horizons": {int(value): 0 for value in config.horizons},
        "locks": 0,
        "breaks": 0,
        "relay_turns": 0,
        "relay_orders": 0,
        "relay_quantity": 0,
        "repay_quantity": 0,
    }

    def game_state(obs, step: int):
        seat = _seat(obs)
        state = states[seat]
        if step == 0 or step < int(state.get("last_step", -1)):
            game_index = int(state.get("game_index", -1)) + 1
            public_key = repr(_public_signature(_farm(obs, seat)))
            horizon = choose_horizon(
                config.horizons,
                normalized,
                nonce=private_nonce,
                game_index=game_index,
                seat=seat,
                public_key=public_key,
            )
            state = {
                "last_step": step,
                "game_index": game_index,
                "horizon": horizon,
                "checks": {},
                "locked": False,
                "disabled": False,
                "break_streak": 0,
                "due": {},
            }
            states[seat] = state
            telemetry["games"] += 1
            telemetry["horizons"][horizon] = telemetry["horizons"].get(horizon, 0) + 1
        state["last_step"] = step
        return state

    def update_lock(obs, state: dict, step: int) -> None:
        distance = public_route_distance(obs)
        if step in config.checkpoints and step not in state["checks"]:
            matched = distance <= config.distance_max
            state["checks"][step] = matched
            if (
                not state["locked"]
                and sum(bool(value) for value in state["checks"].values())
                >= config.matches_required
            ):
                state["locked"] = True
                telemetry["locks"] += 1
        if (
            state["locked"]
            and not state["disabled"]
            and step > max(config.checkpoints, default=-1)
            and step % 24 == 0
        ):
            if distance > config.break_distance:
                state["break_streak"] += 1
            else:
                state["break_streak"] = 0
            if state["break_streak"] >= config.break_checks:
                state["disabled"] = True
                telemetry["breaks"] += 1

    def policy(obs, configuration=None):
        step = min(max(0, int(get(obs, "step", 0) or 0)), len(route) - 1)
        state = game_state(obs, step)
        update_lock(obs, state, step)
        action = _safe_action(base(obs, configuration))
        before = sum(
            max(0, int(order[2]))
            for order in action["market"]
            if len(order) >= 3 and order[0] == "SELL"
        )
        action = _repay(action, state, step)
        after = sum(
            max(0, int(order[2]))
            for order in action["market"]
            if len(order) >= 3 and order[0] == "SELL"
        )
        telemetry["repay_quantity"] += max(0, before - after)

        horizon = int(state["horizon"])
        if (
            horizon <= 0
            or not state["locked"]
            or state["disabled"]
            or not (config.active_start <= step < config.active_stop)
        ):
            return action
        if len(action["market"]) >= 10:
            return action

        remaining = projected_shed(obs, action)
        for order in action["market"]:
            if len(order) >= 3 and order[0] == "SELL":
                item = str(order[1])
                remaining[item] = max(
                    0,
                    int(remaining.get(item, 0)) - max(0, int(order[2])),
                )
        horizons = (
            tuple(range(horizon, 0, -1))
            if config.adaptive_fallback
            else (horizon,)
        )
        candidates = []
        due_rows = state.get("due", {}) or {}
        for candidate_horizon in horizons:
            due_step = step + candidate_horizon
            future = _future_sells(route, step, candidate_horizon, config)
            for item, future_quantity in future.items():
                if (
                    future_quantity < config.minimum_future_quantity
                    or int((due_rows.get(due_step, {}) or {}).get(item, 0) or 0) > 0
                    or _has_intervening_sell(route, step, due_step, item)
                ):
                    continue
                quantity = min(
                    int(remaining.get(item, 0)),
                    int(future_quantity),
                    config.maximum_batch,
                )
                if quantity <= 0:
                    continue
                edge = expected_preemption_edge(
                    obs, configuration, item, quantity, candidate_horizon
                )
                if edge >= config.minimum_edge:
                    candidates.append(
                        (edge, candidate_horizon, item, quantity, due_step)
                    )
        candidates.sort(reverse=True)
        shifted = []
        shifted_items = set()
        for _edge, candidate_horizon, item, quantity, due_step in candidates:
            del candidate_horizon
            if len(shifted) >= config.maximum_orders_per_turn:
                break
            if len(action["market"]) >= 10:
                break
            if item in shifted_items:
                continue
            quantity = min(quantity, int(remaining.get(item, 0)))
            if quantity <= 0:
                continue
            action["market"].append(["SELL", item, quantity])
            remaining[item] = max(0, int(remaining.get(item, 0)) - quantity)
            shifted.append((due_step, item, quantity))
            shifted_items.add(item)
        if not shifted:
            return action
        for due_step, item, quantity in shifted:
            due = state.setdefault("due", {}).setdefault(due_step, {})
            due[item] = int(due.get(item, 0) or 0) + int(quantity)
        telemetry["relay_turns"] += 1
        telemetry["relay_orders"] += len(shifted)
        telemetry["relay_quantity"] += sum(row[2] for row in shifted)
        return reorder_sell_slots(obs, action, configuration, demand_alpha=0.25)

    policy.telemetry = telemetry
    policy.relay_config = config
    policy.private_nonce = private_nonce
    policy.states = states
    return policy
