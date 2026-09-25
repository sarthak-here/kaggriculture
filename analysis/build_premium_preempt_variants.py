"""Build bounded premium-sale preemption variants on frozen demand_timing."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "public_candidates/current_20260924/demand_timing/main.py"
OUT = ROOT / "variants/premium_preempt_20260925"

TEMPLATE = r'''

# Premium sale preemption experiment, 2026-09-25.
# Move only quantities already scheduled by the active route within the next
# H turns. Farming, purchases, products, and total planned quantities are not
# changed. Future duplicate orders naturally become no-ops after stock is sold.
_PP_PARENT = agent
_PP_HORIZON = {horizon}
_PP_PRODUCTS = ("MILK", "WOOL", "STRAWBERRY")
_PP_FLOOR = {{"MILK": 80, "WOOL": 100, "STRAWBERRY": 60}}
_PP_REPORT = dict(calls=0, changed_turns=0, advanced_units=0, errors=0)


def _pp_future_orders(player, step):
    chassis = _IMPL.chassis
    native = chassis.players.get(player) or {{}}
    route = native.get("route", 0)
    totals = {{p: 0 for p in _PP_PRODUCTS}}
    for turn in range(step + 1, min(719, step + 1 + _PP_HORIZON)):
        tape = chassis.routes.get(2 if turn >= 648 else route) or chassis.routes.get(route)
        planned = tape[turn] if tape and turn < len(tape) and isinstance(tape[turn], dict) else {{}}
        for order in planned.get("market") or []:
            if len(order) >= 3 and order[0] == "SELL" and order[1] in totals:
                totals[order[1]] += max(0, int(order[2]))
    return totals


def premium_preempt_agent(observation, configuration=None):
    action = _PP_PARENT(observation, configuration)
    _PP_REPORT["calls"] += 1
    try:
        step = int(observation["step"])
        if step >= 718:
            return action
        player = int(observation["player"])
        future = _pp_future_orders(player, step)
        if not any(future.values()):
            return action
        market = [list(order) for order in (action.get("market") or [])]
        stock = dict(projected_shed(action, FarmView(observation)))
        prices = observation["market"]["prices"]
        changed = 0
        for product in _PP_PRODUCTS:
            quantity = min(int(stock.get(product, 0)), future[product])
            if quantity <= 0 or prices.get(product, 0) < _PP_FLOOR[product]:
                continue
            for order in market:
                if len(order) >= 3 and order[0] == "SELL" and order[1] == product:
                    order[2] = int(order[2]) + quantity
                    break
            else:
                if len(market) >= 10:
                    continue
                market.insert(0, ["SELL", product, quantity])
            changed += quantity
        if not changed:
            return action
        out = dict(action)
        out["market"] = market[:10]
        _PP_REPORT["changed_turns"] += 1
        _PP_REPORT["advanced_units"] += changed
        state = _RACE_STATE.get(player)
        if state and state.get("step") == step and state.get("prev_action") is not None:
            state["prev_action"] = out
        return out
    except Exception:
        _PP_REPORT["errors"] += 1
        return action


premium_preempt_agent.telemetry = _PP_REPORT
agent = premium_preempt_agent
kaggle_submission_agent = premium_preempt_agent
'''


def main():
    base = BASE.read_text(encoding="utf-8-sig").rstrip()
    for horizon in (1, 2, 4):
        path = OUT / f"h{horizon}" / "main.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(base + TEMPLATE.format(horizon=horizon), encoding="utf-8")
        print(path)


if __name__ == "__main__":
    main()
