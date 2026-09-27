"""Compare exact Cha22 and the combined slot schedule on affected replays."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_w13_isolated import play


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "public_candidates/current_20260925/cha22/main.py"
CANDIDATE = ROOT / "variants/cha22_slot_schedule_v1_20260927/main.py"
MANIFEST = ROOT / "analysis/cha22_slot_race_tapes/manifest.json"
OUTPUT = ROOT / "analysis/cha22_slot_race_tapes/results.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", type=Path, default=CANDIDATE)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    cases = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rows = []
    for case in cases:
        tape = ROOT / case["tape"]
        for label, agent in (("base", BASE), ("candidate", args.candidate)):
            result = play(str(agent), str(tape), int(case["seed"]), int(case["own_seat"]))
            rows.append({"label": label, **case, **result})
            print(case["episode"], label, result["status"], result.get("a"), result.get("b"),
                  result.get("a_telemetry", {}).get("slot_fires"), flush=True)
    comparisons = []
    for case in cases:
        pair = [row for row in rows if row["episode"] == case["episode"]]
        base = next(row for row in pair if row["label"] == "base")
        candidate = next(row for row in pair if row["label"] == "candidate")
        base_margin = base.get("a", 0) - base.get("b", 0)
        candidate_margin = candidate.get("a", 0) - candidate.get("b", 0)
        comparisons.append({"episode": case["episode"], "live_result": case["result"],
                            "base_margin": base_margin, "candidate_margin": candidate_margin,
                            "margin_gain": candidate_margin - base_margin,
                            "fires": candidate.get("a_telemetry", {}).get("slot_fires")})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({"rows": rows, "comparisons": comparisons}, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps(comparisons, indent=2))
    return 1 if any(row["status"] != "DONE" for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
