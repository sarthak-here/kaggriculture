"""Build four isolated branches around the September 23 demand-preserving agent.

The source artifact already contains named exports for the final market layers.
Keeping the full source in each output makes Kaggle's single-file loader behavior
identical while the appended final callable selects one explicit branch.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "variants" / "panel23_demand350" / "main.py"
OUTPUT_ROOT = ROOT / "variants"


BRANCHES = {
    "panel23_demand_full": """

# Panel 23 branch: unchanged v350 production path.
def _panel23_submission_entry(observation, configuration=None):
    return _v350_agent(observation, configuration)
""",
    "panel23_demand_net_only": """

# Panel 23 ablation: retain fertilizer wash netting but skip its second reorder.
def _panel23_submission_entry(observation, configuration=None):
    return _v339_agent(observation, configuration)
""",
    "panel23_demand_reorder_only": """

# Panel 23 ablation: retain robust market ordering but skip fertilizer wash netting.
def _panel23_submission_entry(observation, configuration=None):
    return _v336_agent(observation, configuration)
""",
    "panel23_demand_guarded_supply": """

# Panel 23 hybrid: v350 plus one conservative late seed/product top-up.
# Unlike the public v16 probe, this never enlarges land or animal purchases and
# requires a visible 15k cash reserve before adding one eighth to the first order.
_P23_SUPPLY_STATE = {"last_step": -1, "fired": False}
_P23_SUPPLY_REPORT = {"opened": 0, "errors": 0}

def _panel23_submission_entry(observation, configuration=None):
    try:
        step = int(observation.get("step", 0))
        if step == 0 or step <= _P23_SUPPLY_STATE["last_step"]:
            _P23_SUPPLY_STATE["fired"] = False
            if step == 0:
                _P23_SUPPLY_REPORT.update(opened=0, errors=0)
        _P23_SUPPLY_STATE["last_step"] = step
        action = _v350_agent(observation, configuration)
        player = int(observation.get("player", 0))
        money = int(observation["farms"][player].get("money", 0))
        if _P23_SUPPLY_STATE["fired"] or not (480 <= step < 718) or money < 15000:
            return action
        orders = [list(order) if isinstance(order, list) else order
                  for order in (action.get("market") or [])]
        for slot, order in enumerate(orders):
            if (not isinstance(order, list) or len(order) < 3 or
                    order[0] not in ("BUY_SEED", "BUY_PRODUCT")):
                continue
            quantity = int(order[2])
            if quantity <= 0:
                continue
            orders[slot] = order[:2] + [quantity + max(1, (quantity + 7) // 8)]
            _P23_SUPPLY_STATE["fired"] = True
            _P23_SUPPLY_REPORT["opened"] += 1
            changed = dict(action)
            changed["market"] = orders
            return changed
        return action
    except Exception:
        _P23_SUPPLY_REPORT["errors"] += 1
        try:
            return action
        except Exception:
            return _v350_agent(observation, configuration)

_panel23_submission_entry.telemetry = _P23_SUPPLY_REPORT
""",
}


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    manifest = {
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "branches": {},
    }
    for name, suffix in BRANCHES.items():
        output = OUTPUT_ROOT / name / "main.py"
        output.parent.mkdir(parents=True, exist_ok=True)
        rendered = source.rstrip() + suffix
        compile(rendered, str(output), "exec")
        output.write_text(rendered, encoding="utf-8")
        manifest["branches"][name] = {
            "path": str(output.relative_to(ROOT)),
            "sha256": hashlib.sha256(rendered.encode()).hexdigest(),
        }
    manifest_path = ROOT / "analysis" / "panel23_demand_variants_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
