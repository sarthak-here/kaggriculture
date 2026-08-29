"""Build a Kaito-default router with a narrowly detected Soil-family branch."""

from __future__ import annotations

import ast
import base64
import gzip
import json
from pathlib import Path
import zlib

from extract_kaito_v46 import assignment, decode_json


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "submit_v46_three_suffix" / "main.py"
MANIFEST = ROOT / "route_mining" / "kaito_early_branches" / "compatible_routes.json"
TARGET = ROOT / "variants" / "kaito_soil_router" / "main.py"
CANDIDATE = "ep94498749_s0_p24"


def encoded(name: str, routes: dict) -> str:
    payload = base64.b85encode(zlib.compress(
        json.dumps(routes, separators=(",", ":")).encode("utf-8"), 9
    )).decode("ascii")
    return (f"{name} = json.loads(zlib.decompress(base64.b85decode({payload!r}))"
            ".decode(\"utf-8\"))")


ROUTER = r'''
_V44_POLICY = _v44_build(_V44_ROUTES, _V44_CONFIG)
_V44_LEAN_POLICY = _v44_build(_V44_LEAN_ROUTES, _V44_CONFIG)
_V44_LEAN_LATCH = {0: False, 1: False}
_V44_LEAN_LAST_STEP = {0: -1, 1: -1}


def agent(obs, configuration=None):
    try:
        step = int(_v44_get(obs, "step", 0) or 0)
        seat = 1 if int(_v44_get(obs, "player", 0) or 0) == 1 else 0
        if step == 0 or step < _V44_LEAN_LAST_STEP[seat]:
            _V44_LEAN_LATCH[seat] = False
        _V44_LEAN_LAST_STEP[seat] = step

        # Once the branch is latched, avoid evaluating the unused base policy.
        # Both policies are sizeable, and Kaggle allows only one second per step.
        if step > 1 and _V44_LEAN_LATCH[seat]:
            return _V44_LEAN_POLICY(obs, configuration)

        base_action = _V44_POLICY(obs, configuration)
        if step == 0:
            # Both policies have the exact same opening action.  Calling the
            # lean policy here initializes its private state without changing
            # the emitted action.
            _V44_LEAN_POLICY(obs, configuration)
            return base_action

        if step == 1:
            farms = list(_v44_get(obs, "farms", []) or [])
            opponent = farms[1 - seat] if len(farms) >= 2 else {}
            opponent_hands = len(_v44_get(opponent, "hands", []) or [])
            opponent_money = float(_v44_get(opponent, "money", 0) or 0)
            opponent_quads = len(_v44_get(opponent, "unlocked_quadrants", []) or [])
            _V44_LEAN_LATCH[seat] = (
                opponent_hands == 5
                and opponent_money <= 10.0
                and opponent_quads == 1
            )

        if _V44_LEAN_LATCH[seat]:
            return _V44_LEAN_POLICY(obs, configuration)
        return base_action
    except Exception:
        seat = 1 if int(_v44_get(obs, "player", 0) or 0) == 1 else 0
        farms = list(_v44_get(obs, "farms", []) or [])
        farm = farms[seat] if seat < len(farms) else {}
        return {
            "farmer": ["PASS"],
            "hands": [["PASS"] for _ in (_v44_get(farm, "hands", []) or [])],
            "market": [],
        }
'''


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    routes = decode_json(assignment(tree, "_V44_ROUTES"))
    row = next(row for row in json.loads(MANIFEST.read_text(encoding="utf-8"))
               if row["name"] == CANDIDATE)
    route_file = Path(row["route_file"])
    if not route_file.is_absolute():
        route_file = ROOT / route_file
    with gzip.open(route_file, "rt", encoding="utf-8") as handle:
        candidate = json.load(handle)
    prefix = int(row["prefix"])
    lean_routes = {name: route[:prefix] + candidate[prefix:]
                   for name, route in routes.items()}

    policy_start = source.index("_V44_POLICY = _v44_build(_V44_ROUTES, _V44_CONFIG)")
    entrypoint = source.index("def _kaggle_submission_entrypoint", policy_start)
    patched = (
        source[:policy_start]
        + encoded("_V44_LEAN_ROUTES", lean_routes)
        + "\n\n"
        + ROUTER
        + "\n\n"
        + source[entrypoint:]
    )
    compile(patched, str(TARGET), "exec")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(patched, encoding="utf-8")
    print(TARGET.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
