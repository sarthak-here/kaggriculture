"""Build a support-filtered close-clone market-slot schedule on exact Cha22."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public_candidates/current_20260925/cha22/main.py"
OUTPUT = ROOT / "variants/cha22_slot_schedule_v2_20260927/main.py"
SCHEDULE = {150: "WOOL", 196: "MILK", 249: "MELON", 250: "MELON",
            252: "MELON", 270: "MILK", 529: "FERTILIZER",
            552: "STRAWBERRY", 668: "MILK", 673: "MILK",
            684: "STRAWBERRY"}
LAYER = f'''

# Slots selected from live submission 56556133 signatures having >=3 loss
# events, loss support >= win support, and >=40 aggregate recoverable coins.
_SLOT2_PARENT = kaggle_agent
_SLOT2_SCHEDULE = {SCHEDULE!r}
_SLOT2_REPORT = {{"slot2_fires": 0, "slot2_errors": 0, "slot2_by_step": {{}}}}

def live_slot_schedule_v2_agent(observation, configuration=None):
    action = _SLOT2_PARENT(observation, configuration)
    try:
        step = int(observation["step"])
        item = _SLOT2_SCHEDULE.get(step)
        if item is not None and _r37_similarity(observation) >= .90:
            market = [list(order) for order in (action.get("market") or [])]
            index = next((i for i, order in enumerate(market)
                          if len(order) >= 3 and order[:2] == ["SELL", item]
                          and int(order[2]) > 0), None)
            if index not in (None, 0):
                sale = market.pop(index)
                market.insert(0, sale)
                action = dict(action, market=market)
                _SLOT2_REPORT["slot2_fires"] += 1
                key = str(step)
                _SLOT2_REPORT["slot2_by_step"][key] = _SLOT2_REPORT["slot2_by_step"].get(key, 0) + 1
    except Exception:
        _SLOT2_REPORT["slot2_errors"] += 1
    return action

import collections as _slot2_collections
live_slot_schedule_v2_agent.telemetry = _slot2_collections.ChainMap(
    _SLOT2_REPORT, getattr(_SLOT2_PARENT, "telemetry", {{}}))
kaggle_agent = live_slot_schedule_v2_agent
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
        "selection": "loss_events>=3, loss_events>=win_events, aggregate recovery>=40",
        "schedule": SCHEDULE,
    }
    (OUTPUT.parent / "protocol.json").write_text(
        json.dumps(protocol, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(protocol, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
