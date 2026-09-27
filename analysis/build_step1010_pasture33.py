"""Build a minimal Step1010 recovery for a weed-blocked early pasture.

In the live Oleg replay a weed blocked the route's step-33 BUILD_PASTURE.
Step1010 dug it, but later attempted PLACE COW on the still-empty tile.  The
original next two farmer commands are ineffective CARE and PASS, so this layer
uses those three turns for BUILD_PASTURE, PLACE COW, CARE and rejoins unchanged.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import zlib


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "variants/step1010_cha22_router_step144_brunch_brunch_20260927/main.py"
OUTPUT = ROOT / "variants/step1010_brunch_missed_pasture_recovery_20260928/main.py"


def main() -> int:
    blob = base64.b85encode(zlib.compress(PARENT.read_bytes(), 9)).decode("ascii")
    source = f'''# Minimal missed-pasture recovery over the frozen Step1010 BRUNCH router.
import base64 as _p33_b64
import copy as _p33_copy
import zlib as _p33_zlib

_P33_NS = {{"__name__": "step1010_brunch_parent", "__file__": "parent.py"}}
exec(compile(_p33_zlib.decompress(_p33_b64.b85decode({blob!r})), "parent.py", "exec"), _P33_NS)
_P33_PARENT = _P33_NS["step1010_cha22_router_agent"]
_P33_STATE = {{}}
_P33_REPORT = {{"calls": 0, "started": 0, "placed": 0, "cared": 0,
               "guard_rejected": 0}}

def step1010_brunch_pasture33_agent(observation, configuration=None):
    step = int(observation.get("step", -1))
    player = int(observation.get("player", 0))
    if step == 0:
        _P33_STATE[player] = 0
    state = _P33_STATE.get(player, 0)
    parent_observation = observation
    if state and step <= 144:
        parent_observation = _p33_copy.deepcopy(observation)
        farm_view = parent_observation["farms"][player]
        farm_view["tiles"][2][4] = None
        if step == 71:
            inventories = parent_observation.get("private", {{}}).get("inventories", [])
            if inventories:
                inventories[0]["COW"] = inventories[0].get("COW", 0) + 1
    action = _P33_PARENT(parent_observation, configuration)
    _P33_REPORT["calls"] += 1
    try:
        farm = observation["farms"][player]
        x, y = farm["farmer"]
        tile = farm["tiles"][y][x]
        inventory = observation.get("private", {{}}).get("inventories", [{{}}])[0]
        state = _P33_STATE.get(player, 0)
        if step == 69 and action.get("farmer") == ["PLACE", "COW"]:
            if tile is None and inventory.get("COW", 0) > 0:
                out = _p33_copy.deepcopy(action)
                out["farmer"] = ["BUILD_PASTURE"]
                _P33_STATE[player] = 1
                _P33_REPORT["started"] += 1
                return out
        elif step == 70 and state == 1:
            if (isinstance(tile, dict) and tile.get("kind") == "PASTURE"
                    and not tile.get("animal") and inventory.get("COW", 0) > 0):
                out = _p33_copy.deepcopy(action)
                out["farmer"] = ["PLACE", "COW"]
                _P33_STATE[player] = 2
                _P33_REPORT["placed"] += 1
                return out
            _P33_STATE[player] = 0
            _P33_REPORT["guard_rejected"] += 1
        elif step == 71 and state == 2:
            _P33_STATE[player] = 3
            if isinstance(tile, dict) and tile.get("animal") == "COW":
                out = _p33_copy.deepcopy(action)
                out["farmer"] = ["CARE"]
                _P33_REPORT["cared"] += 1
                return out
            _P33_REPORT["guard_rejected"] += 1
        return action
    except (KeyError, IndexError, TypeError, ValueError):
        _P33_REPORT["guard_rejected"] += 1
        return action

step1010_brunch_pasture33_agent.telemetry = _P33_REPORT
'''
    compile(source, str(OUTPUT), "exec")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(source, encoding="utf-8")
    output_bytes = OUTPUT.read_bytes()
    result = {
        "parent": str(PARENT.relative_to(ROOT)),
        "parent_sha256": hashlib.sha256(PARENT.read_bytes()).hexdigest(),
        "output": str(OUTPUT.relative_to(ROOT)),
        "output_sha256": hashlib.sha256(output_bytes).hexdigest(),
        "bytes": len(output_bytes),
        "change": "steps 69-71 recover a weed-blocked pasture using failed PLACE/CARE/PASS slots",
    }
    report = ROOT / "analysis/results/step1010_pasture33_build_20260928.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
