"""Build state-compatible one/two-sheep variants from traced late transactions."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT / "variants" / "severe_late_yarn_screen_20260930" / "114605783" / "main.py"
)
OUT = ROOT / "variants" / "severe_yarn_exact_partial_swaps_20260930"

LAYER = r'''

_EXACT_SWAP_ENABLED = False
_EXACT_SWAP_COUNT = {count}
_EXACT_SWAP_MAX_RIVAL_MONEY = {max_rival_money}


def _exact_swap_worker(action, actor, operation):
    out = dict(action)
    if actor == 0:
        command = list(out.get("farmer", ["PASS"]))
        if len(command) >= 2 and command[0] == operation and command[1] == "COW":
            command[1] = "SHEEP"
            out["farmer"] = command
        return out
    hands = [list(command) for command in list(out.get("hands", []) or [])]
    index = actor - 1
    if 0 <= index < len(hands):
        command = hands[index]
        if len(command) >= 2 and command[0] == operation and command[1] == "COW":
            command[1] = "SHEEP"
            hands[index] = command
            out["hands"] = hands
    return out


def severe_yarn_exact_partial_swap_agent(obs, configuration=None):
    global _EXACT_SWAP_ENABLED
    action = severe_late_yarn_screen_agent(obs)
    step = int(_v44_get(obs, "step", 0) or 0)
    if step == 0:
        _EXACT_SWAP_ENABLED = False
    if step == 153 and _LATE_SCREEN_MODE == "specialist":
        seat = 1 if int(_v44_get(obs, "player", 0) or 0) == 1 else 0
        farms = list(_v44_get(obs, "farms", []) or [])
        rival = farms[1 - seat] if len(farms) > 1 else {{}}
        rival_money = float(_v44_get(rival, "money", 0) or 0)
        _EXACT_SWAP_ENABLED = rival_money <= _EXACT_SWAP_MAX_RIVAL_MONEY
    if not _EXACT_SWAP_ENABLED:
        return action
    if step == 220:
        out = dict(action)
        market = [list(order) for order in list(action.get("market", []) or [])]
        changed = 0
        for order in market:
            if changed >= _EXACT_SWAP_COUNT:
                break
            if len(order) >= 3 and order[0] == "BUY_ANIMAL" and order[1] == "COW":
                order[1] = "SHEEP"
                changed += 1
        out["market"] = market
        return out
    if step == 221:
        return _exact_swap_worker(action, 7, "PICKUP")
    if _EXACT_SWAP_COUNT >= 2 and step == 222:
        return _exact_swap_worker(action, 8, "PICKUP")
    if step == 224:
        return _exact_swap_worker(action, 7, "PLACE")
    if _EXACT_SWAP_COUNT >= 2 and step == 228:
        return _exact_swap_worker(action, 8, "PLACE")
    return action
'''


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8").rstrip()
    for label, count, max_rival_money in (
        ("low_1", 1, 1300),
        ("low_2", 2, 1300),
        ("all_1", 1, 1000000000),
        ("all_2", 2, 1000000000),
    ):
        target = OUT / label / "main.py"
        output = source + "\n" + LAYER.format(
            count=count,
            max_rival_money=max_rival_money,
        )
        compile(output, str(target), "exec")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(output, encoding="utf-8")
        print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()
