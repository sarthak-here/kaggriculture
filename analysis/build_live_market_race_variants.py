"""Build bounded market-race variants on the frozen demand-timing controller."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "public_candidates/current_20260924/demand_timing/main.py"
OUT = ROOT / "variants/demand_timing_market_race_20260925"


WRAPPER = r'''

# EXP123: bounded public-state market-race search.  Unit actions, requested
# quantities and products are immutable.  Only existing market slots may move.
import itertools as _MR_IT
import time as _MR_TIME
_MR_PARENT = agent
_MR_MODE = "__MODE__"
_MR_EVAL_LIMIT = 160
_MR_SECONDS = 0.055
_MR_FIXED = frozenset(("HIRE", "BUY_SEED", "BUY_ANIMAL", "BUY_LAND"))
_MR_REPORT = {"changed": 0, "evaluations": 0, "budget_hits": 0,
              "time_hits": 0, "errors": 0}

def _mr_models(orders, slots, sells, fixed):
    def build(positions, sale_orders):
        out = list(orders)
        remaining = [index for index in slots if index not in positions]
        for index, order in zip(positions, sale_orders):
            out[index] = order
        for index, order in zip(remaining, fixed):
            out[index] = order
        return out
    models = [list(orders)]
    if sells and slots:
        models.extend((
            build(slots[:len(sells)], sells),
            build(slots[-len(sells):], sells),
            build(slots[:len(sells)], list(reversed(sells))),
        ))
    unique = []
    seen = set()
    for model in models:
        key = repr(model)
        if key not in seen:
            seen.add(key)
            unique.append(model)
    return unique

def _mr_candidates(orders, slots, sell_slots, sells, fixed):
    target_slots = sell_slots if _MR_MODE == "sell_slots_robust" else slots
    for positions in _MR_IT.permutations(target_slots, len(sells)):
        out = list(orders)
        if _MR_MODE == "sell_slots_robust":
            for index, order in zip(positions, sells):
                out[index] = order
        else:
            remaining = [index for index in slots if index not in positions]
            for index, order in zip(positions, sells):
                out[index] = order
            for index, order in zip(remaining, fixed):
                out[index] = order
        yield out

def _mr_reorder(observation, action):
    orders = [list(order) if isinstance(order, (list, tuple)) else order
              for order in (action.get("market") or [])]
    if len(orders) < 2:
        return action
    bought = {order[1] for order in orders
              if order and len(order) > 1 and order[0] == "BUY_PRODUCT"}
    slots, sell_slots, sells, fixed = [], [], [], []
    for index, order in enumerate(orders):
        if not order:
            continue
        if order[0] in _MR_FIXED:
            slots.append(index)
            fixed.append(order)
        elif order[0] == "SELL" and len(order) > 1 and order[1] not in bought:
            slots.append(index)
            sell_slots.append(index)
            sells.append(order)
    if not sells or len(slots) < 2:
        return action
    if _MR_MODE == "sell_slots_robust" and len(sell_slots) < 2:
        return action

    params = _v44y_params(observation)
    stock = {key:max(0, int(value)) for key, value in
             projected_shed(action, FarmView(observation)).items()}
    inventory = {key:int(value) for key, value in
                 observation["market"]["inventory"].items()}
    opponent_models = _mr_models(orders, slots, sells, fixed)
    scorers = [_v44y_factor_margin(model, inventory, stock, params)
               for model in opponent_models]
    if _MR_MODE == "cross_slot_nominal":
        scorers = scorers[:1]
    def score(candidate):
        return min(scorer(candidate) for scorer in scorers)

    baseline = best = score(orders)
    selected = None
    started = _MR_TIME.perf_counter()
    for evaluations, candidate in enumerate(
            _mr_candidates(orders, slots, sell_slots, sells, fixed), 1):
        if evaluations > _MR_EVAL_LIMIT:
            _MR_REPORT["budget_hits"] += 1
            break
        if _MR_TIME.perf_counter() - started > _MR_SECONDS:
            _MR_REPORT["time_hits"] += 1
            break
        if candidate == orders:
            continue
        value = score(candidate)
        if value > best + .5:
            best, selected = value, candidate
    _MR_REPORT["evaluations"] += min(evaluations, _MR_EVAL_LIMIT)
    if selected is None or best <= baseline + .5:
        return action
    _MR_REPORT["changed"] += 1
    return dict(action, market=selected)

def _market_race_entrypoint(observation, configuration=None):
    if int(observation.get("step", 0)) == 0:
        _MR_REPORT.update(changed=0, evaluations=0, budget_hits=0,
                          time_hits=0, errors=0)
    action = _MR_PARENT(observation, configuration)
    try:
        if _ig_standard(configuration):
            action = _mr_reorder(observation, action)
    except Exception:
        _MR_REPORT["errors"] += 1
    return action

_market_race_entrypoint.telemetry = _MR_REPORT
agent = _market_race_entrypoint
kaggle_submission_agent = _market_race_entrypoint
'''


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = BASE.read_text(encoding="utf-8")
    variants = ("cross_slot_robust", "cross_slot_nominal", "sell_slots_robust")
    rows = []
    for name in variants:
        folder = OUT / name
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / "main.py"
        target.write_text(source + WRAPPER.replace("__MODE__", name), encoding="utf-8")
        rows.append({"variant": name, "sha256": sha(target)})
    (OUT / "manifest.json").write_text(json.dumps(rows, indent=2) + "\n",
                                        encoding="utf-8")
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
