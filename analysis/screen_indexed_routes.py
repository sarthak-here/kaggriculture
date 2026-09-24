"""Screen every indexed route on its source seed against one opponent."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_w13_isolated import play


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("index", type=Path)
    parser.add_argument("opponent", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    candidates = json.loads(args.index.read_text(encoding="utf-8"))
    output = {"index": str(args.index), "opponent": str(args.opponent), "rows": []}
    for candidate in candidates:
        path = ROOT / candidate["path"]
        for order in (0, 1):
            result = play(str(path.resolve()), str(args.opponent.resolve()),
                          int(candidate["seed"]), order)
            result["source"] = candidate
            output["rows"].append(result)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
            print({key: result.get(key) for key in
                   ("seed", "order", "status", "a", "b")},
                  "episode", candidate["episode"], flush=True)
    done = [row for row in output["rows"] if row["status"] == "DONE"]
    margins = [row["a"] - row["b"] for row in done]
    output["summary"] = {
        "wins": sum(value > 0 for value in margins),
        "losses": sum(value < 0 for value in margins),
        "ties": sum(value == 0 for value in margins),
        "failures": len(output["rows"]) - len(done),
        "mean_margin": sum(margins) / len(margins) if margins else None,
    }
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(output["summary"])


if __name__ == "__main__":
    main()
