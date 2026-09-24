"""Build narrowly different demand-timing controllers for held-out screening.

The public controller's final extension reapplies its SELL-block optimizer from
step 216 onward.  These variants change only that last decision.  The complete
parent policy, legality guards, quantities, and physical actions stay intact.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public_candidates/current_20260924/demand_timing/main.py"
OUT = ROOT / "variants/demand_timing_20260924"

OLD = "if int(observation['step']) >= 216 and _ig_standard(configuration):"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    if source.count(OLD) != 1:
        raise RuntimeError(f"expected one final timing gate, found {source.count(OLD)}")

    gates = {
        "start120": "if int(observation['step']) >= 120 and _ig_standard(configuration):",
        "start360": "if int(observation['step']) >= 360 and _ig_standard(configuration):",
        "start504": "if int(observation['step']) >= 504 and _ig_standard(configuration):",
        "clone_gate": (
            "if (int(observation['step']) >= 216 and _ig_standard(configuration) and "
            "_v44y_clone_gate(observation)):"
        ),
    }
    rows = []
    for name, gate in gates.items():
        folder = OUT / name
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / "main.py"
        target.write_text(source.replace(OLD, gate), encoding="utf-8")
        rows.append({"variant": name, "gate": gate, "sha256": sha(target)})

    # Independent opening-cash probe previously preserved every broad-panel
    # outcome on the old foundation while repairing one live-loss diagnostic.
    # Keep it exact and self-disabling when the parent's opening is different.
    opening8 = source + r'''

# Independent opening-cash probe.  It preserves five net WHEAT while reducing
# the step-0 round trip from 20/15 to 8/3.  If the parent opening differs, this
# wrapper is a strict no-op.
_DT8_PARENT = agent
_DT8_REPORT = {"changed": 0, "errors": 0}
def _demand_timing_opening8(observation, configuration=None):
    action = _DT8_PARENT(observation, configuration)
    try:
        if int(observation.get("step", 0)) == 0:
            _DT8_REPORT.update(changed=0, errors=0)
            market = [list(order) for order in (action.get("market") or [])]
            expected = [["BUY_PRODUCT", "WHEAT", 20],
                        ["SELL", "WHEAT", 15],
                        ["BUY_SEED", "WHEAT", 1]]
            if market[:3] == expected:
                market[:2] = [["BUY_PRODUCT", "WHEAT", 8],
                              ["SELL", "WHEAT", 3]]
                action = dict(action, market=market)
                _DT8_REPORT["changed"] += 1
    except Exception:
        _DT8_REPORT["errors"] += 1
    return action
_demand_timing_opening8.telemetry = _DT8_REPORT
agent = _demand_timing_opening8
kaggle_submission_agent = _demand_timing_opening8
'''
    folder = OUT / "opening8"
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "main.py"
    target.write_text(opening8, encoding="utf-8")
    rows.append({"variant": "opening8", "gate": "exact step-0 20/15 -> 8/3",
                 "sha256": sha(target)})

    manifest = OUT / "manifest.json"
    manifest.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(manifest)
    for row in rows:
        print(row["variant"], row["sha256"])


if __name__ == "__main__":
    main()
