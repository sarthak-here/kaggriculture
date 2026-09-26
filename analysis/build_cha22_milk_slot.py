"""Put Cha22's step-196 MILK sale first only against a strict worker clone."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public_candidates/current_20260925/cha22/main.py"
OUTPUT = ROOT / "variants/cha22_milk_slot_similarity90_20260926/main.py"
LAYER = r'''

# Live submission 56556133: four close-clone losses sold the same 12 MILK
# units on step 196 but lost the quote because MILK occupied slot 1.  Preserve
# every quantity and worker command; only move that existing sale to slot 0.
_MS196_PARENT = kaggle_agent
_MS196_REPORT = {"ms196_fires": 0, "ms196_errors": 0}

def milk_slot_196_agent(observation, configuration=None):
    action = _MS196_PARENT(observation, configuration)
    try:
        player = int(observation["player"])
        if (int(observation["step"]) == 196
                and _r37_similarity(observation) >= .90):
            market = [list(order) for order in (action.get("market") or [])]
            index = next((i for i, order in enumerate(market)
                          if len(order) >= 3 and order[:2] == ["SELL", "MILK"]
                          and int(order[2]) > 0), None)
            if index not in (None, 0):
                milk = market.pop(index)
                market.insert(0, milk)
                action = dict(action, market=market)
                _MS196_REPORT["ms196_fires"] += 1
    except Exception:
        _MS196_REPORT["ms196_errors"] += 1
    return action

import collections as _ms196_collections
milk_slot_196_agent.telemetry = _ms196_collections.ChainMap(
    _MS196_REPORT, getattr(_MS196_PARENT, "telemetry", {}))
kaggle_agent = milk_slot_196_agent
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
        "gate": "step 196, public farm similarity >= .90",
        "change": "move existing positive SELL MILK order to slot 0",
    }
    (OUTPUT.parent / "protocol.json").write_text(
        json.dumps(protocol, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(protocol, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
