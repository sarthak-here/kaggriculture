"""Convert only the three independent late cow transactions to sheep."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "variants"
    / "severe_late_yarn_screen_20260930"
    / "114605783"
    / "main.py"
)
TARGET = ROOT / "variants" / "severe_yarn_late3_swap_20260930" / "main.py"


LAYER = r'''

_LATE3_ENABLED = False


def _late3_command(command):
    updated = list(command) if isinstance(command, list) else command
    if (
        isinstance(updated, list)
        and len(updated) >= 2
        and updated[0] in ("PICKUP", "PLACE")
        and updated[1] == "COW"
    ):
        updated[1] = "SHEEP"
    return updated


def severe_yarn_late3_swap_agent(obs):
    global _LATE3_ENABLED
    action = severe_late_yarn_screen_agent(obs)
    step = int(_v44_get(obs, "step", 0) or 0)
    if step == 0:
        _LATE3_ENABLED = False
    if step == 153 and _LATE_SCREEN_MODE == "specialist":
        seat = 1 if int(_v44_get(obs, "player", 0) or 0) == 1 else 0
        farms = list(_v44_get(obs, "farms", []) or [])
        rival = farms[1 - seat] if len(farms) > 1 else {}
        rival_money = float(_v44_get(rival, "money", 0) or 0)
        _LATE3_ENABLED = rival_money <= 1300
    if not _LATE3_ENABLED or not 220 <= step <= 228:
        return action
    out = dict(action)
    out["market"] = [
        [order[0], "SHEEP", order[2]]
        if isinstance(order, list)
        and len(order) >= 3
        and order[0] == "BUY_ANIMAL"
        and order[1] == "COW"
        else list(order) if isinstance(order, list) else order
        for order in list(action.get("market", []) or [])
    ]
    out["farmer"] = _late3_command(action.get("farmer", ["PASS"]))
    out["hands"] = [_late3_command(command) for command in action.get("hands", [])]
    return out
'''


def main() -> None:
    output = SOURCE.read_text(encoding="utf-8").rstrip() + "\n" + LAYER
    compile(output, str(TARGET), "exec")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(output, encoding="utf-8")
    print(TARGET.relative_to(ROOT))


if __name__ == "__main__":
    main()
