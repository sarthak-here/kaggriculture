"""Build isolated Step1010/Cha22 shop routers for direct validation.

Both parents are embedded in separate namespaces so their global controller
state cannot collide.  Both are kept warm until the routing decision.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import zlib


ROOT = Path(__file__).resolve().parents[1]
STEP = ROOT / "variants/idle_seller_step1010_20260927/main.py"
CHA = ROOT / "variants/cha22_slot_schedule_early_20260927/main.py"
SHOPS = ("YARN_STORE", "PET_CAFE", "FARMERS_MARKET", "BRUNCH_SPOT",
         "PIZZA_SHOP", "SMOOTHIE_SHOP", "BAKERY", "ICE_CREAM_SHOP")


def packed(path: Path) -> str:
    return base64.b85encode(zlib.compress(path.read_bytes(), 9)).decode("ascii")


def source(decision_step: int, cha_patterns: tuple[tuple[str, ...], ...]) -> str:
    step_blob = packed(STEP)
    cha_blob = packed(CHA)
    return f'''# Apache-2.0 parent notices are retained inside both embedded sources.
import base64 as _rt_b64
import zlib as _rt_zlib

_RT_STEP_NS = {{"__name__": "step1010_embedded", "__file__": "step1010.py"}}
_RT_CHA_NS = {{"__name__": "cha22_embedded", "__file__": "cha22.py"}}
exec(compile(_rt_zlib.decompress(_rt_b64.b85decode({step_blob!r})), "step1010.py", "exec"), _RT_STEP_NS)
exec(compile(_rt_zlib.decompress(_rt_b64.b85decode({cha_blob!r})), "cha22.py", "exec"), _RT_CHA_NS)
_RT_STEP = _RT_STEP_NS["step1010_step1009_fixed_point_agent"]
_RT_CHA = _RT_CHA_NS["early_slot_schedule_agent"]
_RT_DECISION_STEP = {decision_step}
_RT_CHA_PATTERNS = {cha_patterns!r}
_RT_STATE = {{}}
_RT_REPORT = {{"step": _RT_DECISION_STEP, "step_selected": 0, "cha_selected": 0,
              "warm_calls": 0, "errors": 0, "patterns": {{}}}}

def _rt_similarity(observation):
    farms = observation["farms"]
    player = int(observation["player"])
    own, rival = farms[player], farms[1-player]
    if own["unlocked_quadrants"] != rival["unlocked_quadrants"]:
        return 0.0
    matches = total = 0
    for left_row, right_row in zip(own["tiles"], rival["tiles"]):
        for left, right in zip(left_row, right_row):
            a = (left.get("crop"), left.get("animal")) if isinstance(left, dict) else (None, None)
            b = (right.get("crop"), right.get("animal")) if isinstance(right, dict) else (None, None)
            if a != (None, None) or b != (None, None):
                total += 1
                matches += a == b
    return matches / total if total >= 8 else 0.0

def step1010_cha22_router_agent(observation, configuration=None):
    step = int(observation.get("step", 0))
    player = int(observation.get("player", 0))
    if step == 0 or player not in _RT_STATE:
        _RT_STATE[player] = None
        _RT_REPORT.update(step_selected=0, cha_selected=0, warm_calls=0,
                          errors=0, patterns={{}})
    selected = _RT_STATE[player]
    if selected == "step":
        return _RT_STEP(observation, configuration)
    if selected == "cha":
        return _RT_CHA(observation, configuration)
    try:
        step_action = _RT_STEP(observation, configuration)
        cha_action = _RT_CHA(observation, configuration)
        _RT_REPORT["warm_calls"] += 2
        if step < _RT_DECISION_STEP:
            return step_action
        shops = tuple(observation["town"].get("unlocked_shops", []))
        width = len(_RT_CHA_PATTERNS[0]) if _RT_CHA_PATTERNS else 0
        pattern = shops[:width]
        use_cha = pattern in _RT_CHA_PATTERNS and _rt_similarity(observation) >= 0.90
        selected = "cha" if use_cha else "step"
        _RT_STATE[player] = selected
        _RT_REPORT[selected + "_selected"] += 1
        key = ">".join(pattern) if pattern else "NONE"
        _RT_REPORT["patterns"][key] = _RT_REPORT["patterns"].get(key, 0) + 1
        return cha_action if use_cha else step_action
    except Exception:
        _RT_REPORT["errors"] += 1
        _RT_STATE[player] = "step"
        return _RT_STEP(observation, configuration)

step1010_cha22_router_agent.telemetry = _RT_REPORT
'''


def multistage_source() -> str:
    base = source(216, ())
    layer = '''

# Staged survivor composition.  Each branch was first validated independently
# against both exact parents; unmatched states remain exact Step1010.
_MS_STATE = {}
_MS_REPORT = {"step_selected": 0, "cha_selected": 0, "warm_calls": 0,
              "errors": 0, "reasons": {}}
_MS_144 = {("BRUNCH_SPOT", "BRUNCH_SPOT"),
           ("BAKERY", "PIZZA_SHOP")}
_MS_216 = {("ICE_CREAM_SHOP", "BRUNCH_SPOT", "YARN_STORE"),
           ("YARN_STORE", "SMOOTHIE_SHOP", "YARN_STORE")}

def step1010_cha22_multistage_agent(observation, configuration=None):
    step = int(observation.get("step", 0))
    player = int(observation.get("player", 0))
    if step == 0 or player not in _MS_STATE:
        _MS_STATE[player] = None
        _MS_REPORT.update(step_selected=0, cha_selected=0, warm_calls=0,
                          errors=0, reasons={})
    selected = _MS_STATE[player]
    if selected == "step":
        return _RT_STEP(observation, configuration)
    if selected == "cha":
        return _RT_CHA(observation, configuration)
    try:
        step_action = _RT_STEP(observation, configuration)
        cha_action = _RT_CHA(observation, configuration)
        _MS_REPORT["warm_calls"] += 2
        shops = tuple(observation["town"].get("unlocked_shops", []))
        reason = None
        if step >= 72 and shops[:1] == ("PET_CAFE",):
            reason = "72:PET_CAFE"
        elif step >= 144 and shops[:2] in _MS_144:
            reason = "144:" + ">".join(shops[:2])
        elif step >= 216 and shops[:3] in _MS_216:
            reason = "216:" + ">".join(shops[:3])
        if reason is not None and _rt_similarity(observation) >= 0.90:
            _MS_STATE[player] = "cha"
            _MS_REPORT["cha_selected"] += 1
            _MS_REPORT["reasons"][reason] = _MS_REPORT["reasons"].get(reason, 0) + 1
            return cha_action
        if step >= 216:
            _MS_STATE[player] = "step"
            _MS_REPORT["step_selected"] += 1
        return step_action
    except Exception:
        _MS_REPORT["errors"] += 1
        _MS_STATE[player] = "step"
        return _RT_STEP(observation, configuration)

step1010_cha22_multistage_agent.telemetry = _MS_REPORT
'''
    return base + layer


def main() -> int:
    specs = {
        "step72_pet": (72, (("PET_CAFE",),)),
        "step144_strict": (144, (
            ("BRUNCH_SPOT", "BRUNCH_SPOT"),
            ("PET_CAFE", "BAKERY"),
            ("PET_CAFE", "YARN_STORE"),
        )),
        "step216_ice_brunch_yarn": (216, (
            ("ICE_CREAM_SHOP", "BRUNCH_SPOT", "YARN_STORE"),
        )),
        "step144_brunch_brunch": (144, (
            ("BRUNCH_SPOT", "BRUNCH_SPOT"),
        )),
        "step144_bakery_pizza": (144, (
            ("BAKERY", "PIZZA_SHOP"),
        )),
        "step144_bakery_yarn": (144, (
            ("BAKERY", "YARN_STORE"),
        )),
        "step216_yarn_smoothie_yarn": (216, (
            ("YARN_STORE", "SMOOTHIE_SHOP", "YARN_STORE"),
        )),
        "step144_all_close": (144, tuple(
            (left, right) for left in SHOPS for right in SHOPS
        )),
    }
    manifest = {}
    for name, (decision, patterns) in specs.items():
        output = ROOT / f"variants/step1010_cha22_router_{name}_20260927/main.py"
        candidate = source(decision, patterns)
        compile(candidate, str(output), "exec")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(candidate, encoding="utf-8")
        manifest[name] = {
            "path": str(output.relative_to(ROOT)),
            "sha256": hashlib.sha256(candidate.encode()).hexdigest(),
            "bytes": len(candidate.encode()),
            "decision_step": decision,
            "cha_patterns": patterns,
        }
    name = "multistage"
    output = ROOT / f"variants/step1010_cha22_router_{name}_20260927/main.py"
    candidate = multistage_source()
    compile(candidate, str(output), "exec")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(candidate, encoding="utf-8")
    manifest[name] = {
        "path": str(output.relative_to(ROOT)),
        "sha256": hashlib.sha256(candidate.encode()).hexdigest(),
        "bytes": len(candidate.encode()),
        "decision_steps": [72, 144, 216],
        "fallback": "exact Step1010",
    }
    protocol = {
        "step_parent": str(STEP.relative_to(ROOT)),
        "step_sha256": hashlib.sha256(STEP.read_bytes()).hexdigest(),
        "cha_parent": str(CHA.relative_to(ROOT)),
        "cha_sha256": hashlib.sha256(CHA.read_bytes()).hexdigest(),
        "candidates": manifest,
    }
    out = ROOT / "analysis/results/step1010_cha22_router_build_20260927.json"
    out.write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(protocol, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
