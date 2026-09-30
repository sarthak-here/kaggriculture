"""Build sheep-heavy ablations on the best state-compatible YARN route.

The late router stays on Severe until step 153.  Only after the structural
YARN-second signature selects route 114605783 do these variants rewrite
future animal purchases; unit actions and every non-animal order are left
unchanged.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "variants"
    / "severe_late_yarn_screen_20260930"
    / "114605783"
    / "main.py"
)
TARGET = ROOT / "variants" / "severe_yarn_herd_swaps_20260930"


LAYER = r'''

_YARN_HERD_SWAP = {mode!r}


def severe_yarn_herd_swap_agent(obs):
    action = severe_late_yarn_screen_agent(obs)
    step = int(_v44_get(obs, "step", 0) or 0)
    if _LATE_SCREEN_MODE != "specialist" or step < 154:
        return action
    market = []
    changed = False
    for order in list(action.get("market", []) or []):
        updated = list(order) if isinstance(order, list) else order
        if isinstance(updated, list) and len(updated) >= 3 and updated[0] == "BUY_ANIMAL":
            animal = updated[1]
            if (_YARN_HERD_SWAP in ("cow", "cow_flow") and animal == "COW") or (
                _YARN_HERD_SWAP == "goose" and animal == "GOOSE"
            ) or (_YARN_HERD_SWAP == "both" and animal in ("COW", "GOOSE")):
                updated[1] = "SHEEP"
                changed = True
        market.append(updated)
    out = dict(action)
    if changed:
        out["market"] = market
    if _YARN_HERD_SWAP == "cow_flow":
        farmer = list(out.get("farmer", ["PASS"]) or ["PASS"])
        if len(farmer) >= 2 and farmer[0] in ("PICKUP", "PLACE") and farmer[1] == "COW":
            farmer[1] = "SHEEP"
            out["farmer"] = farmer
            changed = True
        hands = []
        for command in list(out.get("hands", []) or []):
            updated = list(command) if isinstance(command, list) else command
            if (
                isinstance(updated, list)
                and len(updated) >= 2
                and updated[0] in ("PICKUP", "PLACE")
                and updated[1] == "COW"
            ):
                updated[1] = "SHEEP"
                changed = True
            hands.append(updated)
        out["hands"] = hands
    return out if changed else action
'''


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8").rstrip()
    for mode in ("cow", "goose", "both", "cow_flow"):
        target = TARGET / mode / "main.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        output = source + "\n" + LAYER.format(mode=mode)
        compile(output, str(target), "exec")
        target.write_text(output, encoding="utf-8")
        print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()
