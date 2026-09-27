"""Evaluate reconstructed worker-action suffix ablations on source worlds."""
from __future__ import annotations

import json
from pathlib import Path

from run_w13_isolated import play


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "variants/cha22_slot_schedule_v2_20260927/main.py"
VARIANTS = ROOT / "analysis/cha22_suffix_ablations_20260927.json"
MANIFEST = ROOT / "analysis/cha22_slot_race_tapes/manifest.json"
OUTPUT = ROOT / "analysis/cha22_suffix_ablation_results_20260927.json"
EPISODE_FOR = {"love": 113418129, "shiji": 113471121}


def main() -> int:
    variants = json.loads(VARIANTS.read_text(encoding="utf-8"))["variants"]
    cases = {int(row["episode"]): row for row in
             json.loads(MANIFEST.read_text(encoding="utf-8"))}
    rows = []
    baselines = {}
    for family, episode in EPISODE_FOR.items():
        case = cases[episode]
        result = play(str(BASE), str(ROOT / case["tape"]),
                      int(case["seed"]), int(case["own_seat"]))
        baselines[family] = result
        rows.append({"mode": f"{family}_base", "episode": episode, **result})
    for variant in variants:
        family = variant["mode"].split("_", 1)[0]
        case = cases[EPISODE_FOR[family]]
        result = play(str(ROOT / variant["candidate"]), str(ROOT / case["tape"]),
                      int(case["seed"]), int(case["own_seat"]))
        base = baselines[family]
        row = {"mode": variant["mode"], "episode": case["episode"], **result,
               "base_margin": base.get("a", 0) - base.get("b", 0)}
        row["margin"] = result.get("a", 0) - result.get("b", 0)
        row["margin_gain"] = row["margin"] - row["base_margin"]
        rows.append(row)
        print(variant["mode"], result["status"], row["margin"], row["margin_gain"],
              result.get("a_telemetry", {}).get("suffix_fires"), flush=True)
    OUTPUT.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return 1 if any(row["status"] != "DONE" for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
