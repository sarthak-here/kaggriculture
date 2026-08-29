"""Build Kaito + Soil routing with Gronk's step-160 PIZZA/YARN continuation."""

from __future__ import annotations

import ast
import base64
import json
from pathlib import Path
import zlib

from extract_kaito_v46 import assignment, decode_json
from mine_compatible_routes import route_of

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "variants" / "kaito_soil_router" / "main.py"
REPLAY = ROOT / "loss_analysis" / "kaito_soil_router_current" / "episode-102674510-replay.json"
TARGET = ROOT / "variants" / "kaito_gronk_router" / "main.py"
BRANCH_STEP = 160


def encoded(name: str, routes: dict) -> str:
    payload = base64.b85encode(zlib.compress(
        json.dumps(routes, separators=(",", ":")).encode("utf-8"), 9
    )).decode("ascii")
    return (f"{name} = json.loads(zlib.decompress(base64.b85decode({payload!r}))"
            ".decode(\"utf-8\"))")


ROUTER = r'''
_V44_POLICY = _v44_build(_V44_ROUTES, _V44_CONFIG)
_V44_LEAN_POLICY = _v44_build(_V44_LEAN_ROUTES, _V44_CONFIG)
_V44_GRONK_POLICY = _v44_build(_V44_GRONK_ROUTES, _V44_CONFIG)
_V44_LEAN_LATCH = {0: False, 1: False}
_V44_GRONK_LATCH = {0: False, 1: False}
_V44_ROUTER_LAST_STEP = {0: -1, 1: -1}


def agent(obs, configuration=None):
    try:
        step = int(_v44_get(obs, "step", 0) or 0)
        seat = 1 if int(_v44_get(obs, "player", 0) or 0) == 1 else 0
        if step == 0 or step < _V44_ROUTER_LAST_STEP[seat]:
            _V44_LEAN_LATCH[seat] = False
            _V44_GRONK_LATCH[seat] = False
        _V44_ROUTER_LAST_STEP[seat] = step

        if step > 1 and _V44_LEAN_LATCH[seat]:
            return _V44_LEAN_POLICY(obs, configuration)
        if step > 160 and _V44_GRONK_LATCH[seat]:
            return _V44_GRONK_POLICY(obs, configuration)

        base_action = _V44_POLICY(obs, configuration)
        gronk_action = None
        if step <= 160:
            gronk_action = _V44_GRONK_POLICY(obs, configuration)

        if step == 0:
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

        if step == 160 and not _V44_LEAN_LATCH[seat]:
            town = _v44_get(obs, "town", {})
            shops = list(_v44_get(town, "unlocked_shops", []) or [])
            _V44_GRONK_LATCH[seat] = shops[:2] == ["PIZZA_SHOP", "YARN_STORE"]

        if _V44_LEAN_LATCH[seat]:
            return _V44_LEAN_POLICY(obs, configuration)
        if _V44_GRONK_LATCH[seat]:
            return gronk_action
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
    replay = json.loads(REPLAY.read_text(encoding="utf-8"))
    gronk = route_of(replay, 0)
    gronk_routes = {name: route[:BRANCH_STEP] + gronk[BRANCH_STEP:]
                    for name, route in routes.items()}
    policy_start = source.index("_V44_POLICY = _v44_build(_V44_ROUTES, _V44_CONFIG)")
    entrypoint = source.index("def _kaggle_submission_entrypoint", policy_start)
    patched = (source[:policy_start]
               + encoded("_V44_GRONK_ROUTES", gronk_routes)
               + "\n\n" + ROUTER + "\n\n" + source[entrypoint:])
    compile(patched, str(TARGET), "exec")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(patched, encoding="utf-8")
    print(TARGET.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())