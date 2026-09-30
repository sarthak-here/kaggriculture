"""Strict execution audit for historical agents on Kaggriculture 1.32.7.

Checks the callable Kaggle will select, compares the repaired Flexonafft market
formula with the installed engine, and validates every recorded action over a
full current-rule game.  This is a compatibility audit, not a strength test.
"""

from __future__ import annotations

import json
import os
import runpy
from collections import Counter
from pathlib import Path

import kaggle_environments
from kaggle_environments import make
from kaggle_environments.agent import get_last_callable
from kaggle_environments.envs.kaggriculture.kaggriculture import (
    ANIMALS,
    CROPS,
    MARKET_I0,
    MARKET_PARAMS,
    PRODUCTS,
    market_price,
)


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "current_rule_execution_audit_20260930.json"

AGENTS = {
    "pf_all": ROOT / "variants" / "pf_all" / "main.py",
    "v45_prefund": ROOT / "variants" / "v45_prefund_10_exported" / "main.py",
    "v48_clear_queue": ROOT / "public_candidates" / "v48_clear_queue_20260918" / "main.py",
    "step1010": ROOT / "variants" / "step1010_brunch_missed_pasture_recovery_20260928" / "main.py",
    "severe_114720494": ROOT / "variants" / "severe_114720494_route_20260928" / "main.py",
    "flexonafft_repaired": ROOT / "variants" / "flexonafft_current_rules_20260930" / "main.py",
}

if os.environ.get("KAG_NOOP_FREE") == "1":
    cohort_root = ROOT / "variants" / "noop_free_20260930"
    AGENTS = {name: cohort_root / name / "main.py" for name in AGENTS}
    OUT = ROOT / "analysis" / "noop_free_execution_audit_20260930.json"

UNIT_OPS = {
    "NORTH", "SOUTH", "EAST", "WEST", "PASS", "PICKUP", "DROP", "PLACE",
    "PLANT", "WATER", "HARVEST", "FERTILIZE", "BUILD_COOP",
    "BUILD_PASTURE", "DIG", "FEED", "COLLECT_FERTILIZER", "CARE",
}
MARKET_OPS = {"BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL", "SELL", "HIRE", "BUY_LAND"}
ITEMS = set(PRODUCTS) | set(CROPS) | set(ANIMALS)


def validate_unit(action, where):
    problems = []
    if not isinstance(action, list) or not action:
        return [f"{where}: unit action is not a nonempty list: {action!r}"]
    op = action[0]
    if op not in UNIT_OPS:
        problems.append(f"{where}: unknown unit op {op!r}")
    if op == "PLANT" and (len(action) < 2 or action[1] not in CROPS):
        problems.append(f"{where}: invalid PLANT {action!r}")
    if op in {"PICKUP", "PLACE"} and (len(action) < 2 or action[1] not in ITEMS):
        problems.append(f"{where}: invalid item action {action!r}")
    if op in {"PICKUP", "PLACE"} and len(action) >= 3:
        if not isinstance(action[2], int) or isinstance(action[2], bool) or action[2] <= 0:
            problems.append(f"{where}: invalid quantity {action!r}")
    return problems


def validate_action(action, expected_hands, where):
    problems = []
    if not isinstance(action, dict):
        return [f"{where}: action is not a dict: {action!r}"]
    problems.extend(validate_unit(action.get("farmer", ["PASS"]), f"{where}.farmer"))
    hands = action.get("hands", [])
    if not isinstance(hands, list):
        problems.append(f"{where}: hands is not a list")
    else:
        if len(hands) > expected_hands:
            problems.append(f"{where}: emitted {len(hands)} hand actions for {expected_hands} hands")
        for i, hand in enumerate(hands):
            problems.extend(validate_unit(hand, f"{where}.hands[{i}]"))
    market = action.get("market", [])
    if not isinstance(market, list):
        problems.append(f"{where}: market is not a list")
        return problems
    if len(market) > 10:
        problems.append(f"{where}: emitted {len(market)} market orders (limit 10)")
    for i, order in enumerate(market):
        label = f"{where}.market[{i}]"
        if not isinstance(order, list) or not order:
            problems.append(f"{label}: malformed {order!r}")
            continue
        op = order[0]
        if op not in MARKET_OPS:
            problems.append(f"{label}: unknown op {op!r}")
            continue
        if op in {"HIRE", "BUY_LAND"}:
            continue
        if len(order) < 3:
            problems.append(f"{label}: missing item/quantity {order!r}")
            continue
        item, quantity = order[1], order[2]
        allowed = set(CROPS) if op == "BUY_SEED" else set(ANIMALS) if op == "BUY_ANIMAL" else set(PRODUCTS)
        if op == "BUY_PRODUCT":
            allowed = {"WHEAT", "FERTILIZER"}
        if item not in allowed:
            problems.append(f"{label}: invalid item {item!r} for {op}")
        if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
            problems.append(f"{label}: invalid quantity {quantity!r}")
    return problems


def price_equivalence():
    namespace = runpy.run_path(str(AGENTS["flexonafft_repaired"]))
    repaired_price = namespace["_market_price"]
    mismatches = []
    comparisons = 0
    for item, params in MARKET_PARAMS.items():
        scale = params["T"]
        points = {
            0, MARKET_I0 - 3 * scale, MARKET_I0 - 2 * scale,
            MARKET_I0 - scale, MARKET_I0 - scale // 2, MARKET_I0 - 1,
            MARKET_I0, MARKET_I0 + 1, MARKET_I0 + scale // 2,
            MARKET_I0 + scale, MARKET_I0 + 2 * scale, MARKET_I0 + 3 * scale,
            MARKET_I0 + 10000,
        }
        for inventory in sorted(max(0, value) for value in points):
            expected = market_price(item, inventory)
            actual = repaired_price(item, inventory)
            comparisons += 1
            if actual != expected:
                mismatches.append({"item": item, "inventory": inventory, "engine": expected, "agent": actual})
    return {"comparisons": comparisons, "mismatches": mismatches}


def main():
    missing = [str(path) for path in AGENTS.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing agent files: {missing}")

    result = {
        "engine_version": kaggle_environments.__version__,
        "price_equivalence": price_equivalence(),
        "agents": {},
    }
    opponent = str(AGENTS["step1010"])
    for index, (name, path) in enumerate(AGENTS.items()):
        source = path.read_text(encoding="utf-8")
        selected = get_last_callable(source, path=str(path))
        seed = 1100400 + index
        env = make("kaggriculture", configuration={"seed": seed}, debug=False)
        env.run([str(path), opponent])
        findings = []
        actions = Counter()
        statuses = Counter()
        for step_index, step in enumerate(env.steps):
            state = step[0]
            statuses[str(state.get("status"))] += 1
            action = state.get("action")
            if action is None:
                continue
            # env.steps[k].action was chosen from env.steps[k-1].observation;
            # the recorded observation is post-interpreter (and at day boundaries
            # already has its hands cleared).  Validate cardinality against the
            # observation the agent actually saw.
            prior_state = env.steps[step_index - 1][0] if step_index else state
            obs = prior_state.get("observation") or {}
            farms = obs.get("farms") or []
            player = int(obs.get("player", 0))
            expected_hands = len(farms[player].get("hands", [])) if len(farms) > player else 0
            findings.extend(validate_action(action, expected_hands, f"step[{step_index}]"))
            for order in action.get("market", []) or []:
                if isinstance(order, list) and order:
                    actions[f"market:{order[0]}"] += 1
            farmer = action.get("farmer")
            if isinstance(farmer, list) and farmer:
                actions[f"farmer:{farmer[0]}"] += 1
            for hand in action.get("hands", []) or []:
                if isinstance(hand, list) and hand:
                    actions[f"hand:{hand[0]}"] += 1
        final_state = env.steps[-1][0]
        final_obs = final_state["observation"]
        shops = list((final_obs.get("town") or {}).get("unlocked_shops") or [])
        duplicates = sorted(shop for shop, count in Counter(shops).items() if count > 1)
        accepted_noops = [
            item for item in findings
            if "unknown op 'PASS'" in item
            or "invalid quantity 0" in item
            or "malformed []" in item
        ]
        noop_types = Counter()
        for item in accepted_noops:
            if "unknown op 'PASS'" in item:
                noop_types["market_pass"] += 1
            elif "invalid quantity 0" in item:
                noop_types["zero_quantity"] += 1
            elif "malformed []" in item:
                noop_types["empty_order"] += 1
        hard_problems = [item for item in findings if item not in accepted_noops]
        result["agents"][name] = {
            "path": str(path.relative_to(ROOT)),
            "seed": seed,
            "selected_callable": getattr(selected, "__name__", type(selected).__name__),
            "steps": len(env.steps),
            "final_status": final_state.get("status"),
            "reward": final_state.get("reward"),
            "shops": shops,
            "duplicate_shops": duplicates,
            "action_counts": dict(sorted(actions.items())),
            "status_counts": dict(statuses),
            "accepted_noop_findings": accepted_noops[:100],
            "accepted_noop_count": len(accepted_noops),
            "accepted_noop_types": dict(sorted(noop_types.items())),
            "hard_problems": hard_problems[:100],
            "hard_problem_count": len(hard_problems),
        }
        print(f"{name}: status={final_state.get('status')} reward={final_state.get('reward')} "
              f"steps={len(env.steps)} hard={len(hard_problems)} noops={len(accepted_noops)} "
              f"duplicates={duplicates} "
              f"callable={getattr(selected, '__name__', type(selected).__name__)}")

    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    total_problems = sum(row["hard_problem_count"] for row in result["agents"].values())
    total_noops = sum(row["accepted_noop_count"] for row in result["agents"].values())
    price_mismatches = len(result["price_equivalence"]["mismatches"])
    print(f"price comparisons={result['price_equivalence']['comparisons']} mismatches={price_mismatches}")
    print(f"hard action problems={total_problems}; accepted no-op findings={total_noops}; wrote {OUT}")
    return 1 if total_problems or price_mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
