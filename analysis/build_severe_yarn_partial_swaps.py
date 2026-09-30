"""Build partial post-branch cow-to-sheep transaction substitutions."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "variants"
    / "severe_late_yarn_screen_20260930"
    / "114605783"
    / "main.py"
)
TARGET = ROOT / "variants" / "severe_yarn_partial_swaps_20260930"


LAYER = r'''

_YARN_SWAP_LIMIT = {limit}
_YARN_SWAP_COUNTS = {{"buy": 0, "pickup": 0, "place": 0}}


def _partial_cow_command(command, phase):
    global _YARN_SWAP_COUNTS
    updated = list(command) if isinstance(command, list) else command
    if not isinstance(updated, list) or len(updated) < 2:
        return updated
    if updated[0] != phase.upper() or updated[1] != "COW":
        return updated
    quantity = int(updated[2]) if len(updated) >= 3 else 1
    if quantity <= 0 or _YARN_SWAP_COUNTS[phase] + quantity > _YARN_SWAP_LIMIT:
        return updated
    updated[1] = "SHEEP"
    _YARN_SWAP_COUNTS[phase] += quantity
    return updated


def severe_yarn_partial_swap_agent(obs):
    global _YARN_SWAP_COUNTS
    step = int(_v44_get(obs, "step", 0) or 0)
    if step == 0:
        _YARN_SWAP_COUNTS = {{"buy": 0, "pickup": 0, "place": 0}}
    action = severe_late_yarn_screen_agent(obs)
    if _LATE_SCREEN_MODE != "specialist" or step < 154:
        return action
    out = dict(action)
    market = []
    for order in list(action.get("market", []) or []):
        updated = list(order) if isinstance(order, list) else order
        if (
            isinstance(updated, list)
            and len(updated) >= 3
            and updated[0] == "BUY_ANIMAL"
            and updated[1] == "COW"
        ):
            quantity = int(updated[2])
            if quantity > 0 and _YARN_SWAP_COUNTS["buy"] + quantity <= _YARN_SWAP_LIMIT:
                updated[1] = "SHEEP"
                _YARN_SWAP_COUNTS["buy"] += quantity
        market.append(updated)
    out["market"] = market
    out["farmer"] = _partial_cow_command(action.get("farmer", ["PASS"]), "pickup")
    if out["farmer"] == action.get("farmer", ["PASS"]):
        out["farmer"] = _partial_cow_command(action.get("farmer", ["PASS"]), "place")
    hands = []
    for command in list(action.get("hands", []) or []):
        updated = _partial_cow_command(command, "pickup")
        if updated == command:
            updated = _partial_cow_command(command, "place")
        hands.append(updated)
    out["hands"] = hands
    return out
'''


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8").rstrip()
    for limit in (1, 2, 3):
        target = TARGET / str(limit) / "main.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        output = source + "\n" + LAYER.format(limit=limit)
        compile(output, str(target), "exec")
        target.write_text(output, encoding="utf-8")
        print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()
