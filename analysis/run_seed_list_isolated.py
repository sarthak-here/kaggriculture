"""Run paired-seat games over an explicit deterministic seed list."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path

from run_w13_isolated import play


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("a", type=Path)
    parser.add_argument("b", type=Path)
    parser.add_argument("--seeds", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if importlib.metadata.version("kaggle-environments") != "1.32.7":
        raise RuntimeError("This experiment is pinned to kaggle-environments 1.32.7")
    if args.output.exists():
        raise FileExistsError(args.output)
    seeds = [int(value) for value in args.seeds.split(",") if value.strip()]
    if not seeds or len(set(seeds)) != len(seeds):
        raise ValueError("Seeds must be a non-empty unique comma-separated list")
    a = args.a.resolve()
    b = args.b.resolve()
    payload = {
        "a": str(args.a),
        "b": str(args.b),
        "engine": "1.32.7",
        "seeds": seeds,
        "a_sha256": hashlib.sha256(a.read_bytes()).hexdigest(),
        "b_sha256": hashlib.sha256(b.read_bytes()).hexdigest(),
        "rows": [],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    for seed in seeds:
        for order in (0, 1):
            row = play(str(a), str(b), seed, order)
            payload["rows"].append(row)
            args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            print({key: row.get(key) for key in ("seed", "order", "status", "a", "b")}, flush=True)
    done = [row for row in payload["rows"] if row.get("status") == "DONE"]
    print(json.dumps({
        "wins": sum(row["a"] > row["b"] for row in done),
        "losses": sum(row["a"] < row["b"] for row in done),
        "ties": sum(row["a"] == row["b"] for row in done),
        "failures": len(payload["rows"]) - len(done),
    }))


if __name__ == "__main__":
    main()
