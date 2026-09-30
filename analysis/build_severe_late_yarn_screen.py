"""Apply the compatible step-153 YARN-second gate to ten preserved routes."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "variants" / "severe_v45v48_yarn_screen_20260930"
TARGET = ROOT / "variants" / "severe_late_yarn_screen_20260930"

LAYER = r'''

_LATE_SCREEN_MODE = "base"


def _late_screen_clean(action):
    if not isinstance(action, dict) or not isinstance(action.get("market"), list):
        return action
    cleaned = []
    for order in action["market"]:
        if not isinstance(order, list) or not order or order[0] == "PASS":
            continue
        if order[0] in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL", "SELL"):
            if len(order) < 3:
                continue
            try:
                if int(order[2]) <= 0:
                    continue
            except (TypeError, ValueError):
                continue
        cleaned.append(order)
    if cleaned == action["market"]:
        return action
    out = dict(action)
    out["market"] = cleaned[:10]
    return out


def severe_late_yarn_screen_agent(obs):
    global _LATE_SCREEN_MODE, _BRIDGE_MODE
    step = int(_v44_get(obs, "step", 0) or 0)
    if step == 0:
        _LATE_SCREEN_MODE = "base"
    if step == 153:
        seat = 1 if int(_v44_get(obs, "player", 0) or 0) == 1 else 0
        farms = list(_v44_get(obs, "farms", []) or [])
        rival = farms[1 - seat] if len(farms) > 1 else {}
        hands = len(list(_v44_get(rival, "hands", []) or []))
        herd = [
            _v44_get(tile, "animal", None)
            for row in list(_v44_get(rival, "tiles", []) or [])
            for tile in list(row or [])
            if isinstance(tile, dict) and _v44_get(tile, "animal", None)
        ]
        cows = sum(animal == "COW" for animal in herd)
        sheep = sum(animal == "SHEEP" for animal in herd)
        shops = list(_v44_get(_v44_get(obs, "town", {}), "unlocked_shops", []) or [])
        _LATE_SCREEN_MODE = "specialist" if (
            len(shops) >= 2
            and shops[1] == "YARN_STORE"
            and hands >= 8
            and cows == 4
            and sheep == 2
        ) else "base"
    _BRIDGE_MODE = _LATE_SCREEN_MODE
    return _late_screen_clean(_V44_POLICY(obs, None))
'''


def main():
    count = 0
    for source in sorted(SOURCE.glob("*/main.py")):
        target = TARGET / source.parent.name / "main.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        output = source.read_text(encoding="utf-8").rstrip() + "\n" + LAYER
        compile(output, str(target), "exec")
        target.write_text(output, encoding="utf-8")
        print(target.relative_to(ROOT))
        count += 1
    print("built", count)


if __name__ == "__main__":
    main()
