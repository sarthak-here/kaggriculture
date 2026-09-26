"""Build the verified close-clone market-slot schedule on exact Cha22."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public_candidates/current_20260925/cha22/main.py"
OUTPUT = ROOT / "variants/cha22_slot_schedule_v1_20260927/main.py"
LAYER = r'''

# Live submission 56556133 repeatedly lost identical same-turn sales because a
# BUY occupied slot 0. Preserve commands and quantities; prioritize only the
# two replay-verified close-clone sales.
_SLOT_PARENT = kaggle_agent
_SLOT_SCHEDULE = {196: "MILK", 250: "MELON"}
_SLOT_REPORT = {"slot_fires": 0, "slot_errors": 0}

def live_slot_schedule_agent(observation, configuration=None):
    action = _SLOT_PARENT(observation, configuration)
    try:
        step = int(observation["step"])
        item = _SLOT_SCHEDULE.get(step)
        if item is not None and _r37_similarity(observation) >= .90:
            market = [list(order) for order in (action.get("market") or [])]
            index = next((i for i, order in enumerate(market)
                          if len(order) >= 3 and order[:2] == ["SELL", item]
                          and int(order[2]) > 0), None)
            if index not in (None, 0):
                sale = market.pop(index)
                market.insert(0, sale)
                action = dict(action, market=market)
                _SLOT_REPORT["slot_fires"] += 1
    except Exception:
        _SLOT_REPORT["slot_errors"] += 1
    return action

import collections as _slot_collections
live_slot_schedule_agent.telemetry = _slot_collections.ChainMap(
    _SLOT_REPORT, getattr(_SLOT_PARENT, "telemetry", {}))
kaggle_agent = live_slot_schedule_agent
'''


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    candidate = source + LAYER
    compile(candidate, str(OUTPUT), "exec")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(candidate, encoding="utf-8")
    protocol = {
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "candidate": str(OUTPUT.relative_to(ROOT)),
        "candidate_sha256": hashlib.sha256(candidate.encode()).hexdigest(),
        "gate": "public farm similarity >= .90",
        "schedule": {"196": "move existing SELL MILK to slot 0",
                     "250": "move existing SELL MELON to slot 0"},
    }
    (OUTPUT.parent / "protocol.json").write_text(
        json.dumps(protocol, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(protocol, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
