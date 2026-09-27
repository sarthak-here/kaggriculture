"""Build the recurrent early close-clone slot schedule on exact Cha22."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public_candidates/current_20260925/cha22/main.py"
OUTPUT = ROOT / "variants/cha22_slot_schedule_early_20260927/main.py"
SCHEDULE = {150: "WOOL", 196: "MILK", 249: "MELON",
            250: "MELON", 252: "MELON", 270: "MILK"}
LAYER = f'''

# Recurrent early close-clone quote races from submission 56556133. Late
# signatures are intentionally excluded after fresh exact-Cha22 regressions.
_ESLOT_PARENT = kaggle_agent
_ESLOT_SCHEDULE = {SCHEDULE!r}
_ESLOT_REPORT = {{"early_slot_fires": 0, "early_slot_errors": 0,
                  "early_slot_by_step": {{}}}}

def early_slot_schedule_agent(observation, configuration=None):
    action = _ESLOT_PARENT(observation, configuration)
    try:
        step = int(observation["step"])
        item = _ESLOT_SCHEDULE.get(step)
        if item is not None and _r37_similarity(observation) >= .90:
            market = [list(order) for order in (action.get("market") or [])]
            index = next((i for i, order in enumerate(market)
                          if len(order) >= 3 and order[:2] == ["SELL", item]
                          and int(order[2]) > 0), None)
            if index not in (None, 0):
                sale = market.pop(index); market.insert(0, sale)
                action = dict(action, market=market)
                _ESLOT_REPORT["early_slot_fires"] += 1
                key = str(step)
                _ESLOT_REPORT["early_slot_by_step"][key] = (
                    _ESLOT_REPORT["early_slot_by_step"].get(key, 0) + 1)
    except Exception:
        _ESLOT_REPORT["early_slot_errors"] += 1
    return action

import collections as _eslot_collections
early_slot_schedule_agent.telemetry = _eslot_collections.ChainMap(
    _ESLOT_REPORT, getattr(_ESLOT_PARENT, "telemetry", {{}}))
kaggle_agent = early_slot_schedule_agent
'''


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    candidate = source + LAYER
    compile(candidate, str(OUTPUT), "exec")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(candidate, encoding="utf-8")
    protocol = {"source": str(SOURCE.relative_to(ROOT)),
                "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                "candidate": str(OUTPUT.relative_to(ROOT)),
                "candidate_sha256": hashlib.sha256(candidate.encode()).hexdigest(),
                "gate": "public farm similarity >= .90", "schedule": SCHEDULE,
                "excluded": "all post-step270 signatures after fresh regression"}
    (OUTPUT.parent / "protocol.json").write_text(
        json.dumps(protocol, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(protocol, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
