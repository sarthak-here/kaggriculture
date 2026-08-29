"""Build a Soil specialist plus clone-only Kaito mirror suffix router."""

from __future__ import annotations

import ast
import base64
import json
from pathlib import Path
import zlib

from extract_kaito_v46 import assignment, decode_json


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "variants" / "kaito_soil_router" / "main.py"
SUFFIX = (ROOT / "variants" / "kaito_loss_suffixes"
          / "ep100606696_s0_default_p243" / "main.py")
TARGET = ROOT / "variants" / "kaito_clone_soil_router" / "main.py"


def encoded(name: str, routes: dict) -> str:
    payload = base64.b85encode(zlib.compress(
        json.dumps(routes, separators=(",", ":")).encode("utf-8"), 9
    )).decode("ascii")
    return (f"{name} = json.loads(zlib.decompress(base64.b85decode({payload!r}))"
            ".decode(\"utf-8\"))")


ROUTER = r'''
_V44_POLICY = _v44_build(_V44_ROUTES, _V44_CONFIG)
_V44_LEAN_POLICY = _v44_build(_V44_LEAN_ROUTES, _V44_CONFIG)
_V44_CLONE_POLICY = _v44_build(_V44_CLONE_ROUTES, _V44_CONFIG)
_V44_LEAN_LATCH = {0: False, 1: False}
_V44_CLONE_LATCH = {0: False, 1: False}
_V44_CLONE_STREAK = {0: 0, 1: 0}
_V44_LAST_STEP = {0: -1, 1: -1}
_V44_CLONE_KEYS = tuple(sorted((
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "COW", "SHEEP", "GOOSE", "PASTURE", "COOP", "WEED",
)))


def _v44_clone_signature(farm):
    counts = {key: 0 for key in _V44_CLONE_KEYS}
    for row in (_v44_get(farm, "tiles", []) or []):
        for tile in row:
            if not isinstance(tile, dict):
                continue
            for field in ("crop", "animal", "kind"):
                value = str(tile.get(field, "")).upper()
                if value in counts:
                    counts[value] += 1
                    break
    return (
        len(_v44_get(farm, "hands", []) or []),
        len(_v44_get(farm, "unlocked_quadrants", []) or []),
        tuple(counts[key] for key in _V44_CLONE_KEYS),
    )


def _v44_clone_distance(farms):
    left, right = map(_v44_clone_signature, farms[:2])
    return (abs(left[0] - right[0]) + 3 * abs(left[1] - right[1])
            + sum(abs(a - b) for a, b in zip(left[2], right[2])))


def agent(obs, configuration=None):
    try:
        step = int(_v44_get(obs, "step", 0) or 0)
        seat = 1 if int(_v44_get(obs, "player", 0) or 0) == 1 else 0
        if step == 0 or step < _V44_LAST_STEP[seat]:
            _V44_LEAN_LATCH[seat] = False
            _V44_CLONE_LATCH[seat] = False
            _V44_CLONE_STREAK[seat] = 0
        _V44_LAST_STEP[seat] = step

        if step > 1 and _V44_LEAN_LATCH[seat]:
            return _V44_LEAN_POLICY(obs, configuration)
        if step > 243 and _V44_CLONE_LATCH[seat]:
            return _V44_CLONE_POLICY(obs, configuration)

        base_action = _V44_POLICY(obs, configuration)
        clone_action = None
        if step <= 243:
            clone_action = _V44_CLONE_POLICY(obs, configuration)

        if step == 0:
            _V44_LEAN_POLICY(obs, configuration)
            return base_action

        farms = list(_v44_get(obs, "farms", []) or [])
        if step == 1:
            opponent = farms[1 - seat] if len(farms) >= 2 else {}
            _V44_LEAN_LATCH[seat] = (
                len(_v44_get(opponent, "hands", []) or []) == 5
                and float(_v44_get(opponent, "money", 0) or 0) <= 10.0
                and len(_v44_get(opponent, "unlocked_quadrants", []) or []) == 1
            )
            if _V44_LEAN_LATCH[seat]:
                return _V44_LEAN_POLICY(obs, configuration)

        if 120 <= step <= 243 and len(farms) >= 2:
            if _v44_clone_distance(farms) <= 2:
                _V44_CLONE_STREAK[seat] += 1
            else:
                _V44_CLONE_STREAK[seat] = 0
            if _V44_CLONE_STREAK[seat] >= 24:
                _V44_CLONE_LATCH[seat] = True
        if step == 243:

            if _V44_CLONE_LATCH[seat]:
                return clone_action
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
    source_tree = ast.parse(source)
    suffix_tree = ast.parse(SUFFIX.read_text(encoding="utf-8"))
    clone_routes = decode_json(assignment(suffix_tree, "_V44_ROUTES"))
    policy_start = source.index("_V44_POLICY = _v44_build(_V44_ROUTES, _V44_CONFIG)")
    entrypoint = source.index("def _kaggle_submission_entrypoint", policy_start)
    patched = (source[:policy_start]
               + encoded("_V44_CLONE_ROUTES", clone_routes) + "\n\n"
               + ROUTER + "\n\n" + source[entrypoint:])
    compile(patched, str(TARGET), "exec")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(patched, encoding="utf-8")
    print(TARGET.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
