"""Build causal worker-action ablations for two residual close-clone losses."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "variants/cha22_slot_schedule_v2_20260927/main.py"
MODES = {
    "love_wheat_worker": {598: (6, ["PLANT", "WHEAT"])},
    "love_wheat_full": {598: (6, ["PLANT", "WHEAT"])},
    "love_late_pass": {671: (8, ["PASS"])},
    "love_all": {598: (6, ["PLANT", "WHEAT"]), 671: (8, ["PASS"])},
    "shiji_dig": {183: (6, ["DIG"])},
    "shiji_pass": {623: (1, ["PASS"])},
    "shiji_care": {666: (8, ["CARE"])},
    "shiji_all": {183: (6, ["DIG"]), 623: (1, ["PASS"]), 666: (8, ["CARE"])},
}


def layer(mode: str, overrides: dict) -> str:
    remove_carrot = mode in {"love_wheat_full", "love_all"}
    return f'''

# Diagnostic suffix ablation reconstructed from live close-clone replays.
_SFX_PARENT = kaggle_agent
_SFX_OVERRIDES = {overrides!r}
_SFX_REMOVE_CARROT_598 = {remove_carrot!r}
_SFX_REPORT = {{"suffix_fires": 0, "suffix_errors": 0}}

def suffix_ablation_agent(observation, configuration=None):
    action = _SFX_PARENT(observation, configuration)
    try:
        step = int(observation["step"])
        override = _SFX_OVERRIDES.get(step)
        if override is not None and _r37_similarity(observation) >= .98:
            hand_index, command = override
            hands = [list(row) for row in (action.get("hands") or [])]
            if hand_index < len(hands):
                hands[hand_index] = list(command)
                market = [list(row) for row in (action.get("market") or [])]
                if step == 598 and _SFX_REMOVE_CARROT_598:
                    market = [row for row in market
                              if not (len(row) >= 3 and row[:2] == ["BUY_SEED", "CARROT"])]
                action = dict(action, hands=hands, market=market)
                _SFX_REPORT["suffix_fires"] += 1
    except Exception:
        _SFX_REPORT["suffix_errors"] += 1
    return action

import collections as _sfx_collections
suffix_ablation_agent.telemetry = _sfx_collections.ChainMap(
    _SFX_REPORT, getattr(_SFX_PARENT, "telemetry", {{}}))
kaggle_agent = suffix_ablation_agent
'''


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    rows = []
    for mode, overrides in MODES.items():
        candidate = source + layer(mode, overrides)
        target = ROOT / f"variants/cha22_suffix_{mode}_20260927/main.py"
        compile(candidate, str(target), "exec")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(candidate, encoding="utf-8")
        rows.append({"mode": mode, "overrides": overrides,
                     "candidate": str(target.relative_to(ROOT)),
                     "sha256": hashlib.sha256(candidate.encode()).hexdigest()})
    output = ROOT / "analysis/cha22_suffix_ablations_20260927.json"
    output.write_text(json.dumps({"source": str(SOURCE.relative_to(ROOT)),
                                  "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
                                  "gate": "public farm similarity >= .98", "variants": rows},
                                 indent=2) + "\n", encoding="utf-8")
    print(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
