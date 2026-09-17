"""Run one candidate against Shawn404's fixed episode-110040845 tape."""
import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path

from run_w13_isolated import play

ROOT = Path(__file__).resolve().parents[1]
TAPE = ROOT / "analysis/shawn404_110040845_controls_20260917/main.py"
SEED = 1006079789


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate")
    parser.add_argument("output")
    args = parser.parse_args()
    candidate = ROOT / args.candidate
    output = ROOT / args.output
    assert importlib.metadata.version("kaggle-environments") == "1.32.7"
    rows = []
    for order in (0, 1):
        row = play(str(candidate), str(TAPE), SEED, order)
        rows.append(row)
        print(order, row["status"], row.get("a"), row.get("b"), flush=True)
    result = {
        "candidate": args.candidate,
        "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
        "opponent": str(TAPE.relative_to(ROOT)),
        "seed": SEED,
        "limitation": "Opponent actions are fixed; this is a causal diagnostic, not a reactive-policy ranking.",
        "rows": rows,
    }
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    assert all(row["status"] == "DONE" for row in rows)


if __name__ == "__main__":
    main()
