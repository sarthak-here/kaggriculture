"""Profile Kaito variants against Soil on an explicit paired-seat seed set.

The regular duel harness retains rewards but not full trajectories.  This tool
reruns only the requested seeds, feeds the trajectories through the established
per-step economy profiler, and writes compact JSON suitable for experiment
records.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from kaggle_environments import make

from v46_loss_pattern import profile


ROOT = Path(__file__).resolve().parents[1]


def profile_game(agent: Path, opponent: Path, seed: int, order: int) -> dict:
    players = [str(agent), str(opponent)] if order == 0 else [str(opponent), str(agent)]
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run(players)
    names = ["Sarthak Kaito", "Soil"] if order == 0 else ["Soil", "Sarthak Kaito"]
    payload = {
        "steps": env.steps,
        "info": {"TeamNames": names, "EpisodeId": 0, "seed": seed},
    }
    handle, path = tempfile.mkstemp(prefix="kaito-soil-", suffix=".json")
    os.close(handle)
    try:
        Path(path).write_text(json.dumps(payload), encoding="utf-8")
        row = profile(path)
    finally:
        Path(path).unlink(missing_ok=True)
    row["order"] = order
    row["result"] = "W" if row["margin"] > 0 else "L" if row["margin"] < 0 else "T"
    return row


def compact(row: dict) -> dict:
    keys = (
        "seed", "order", "result", "margin", "prefix", "bucket",
        "day12_gap", "day18_gap", "max_lead", "final_gap",
    )
    out = {key: row[key] for key in keys}
    for side in ("us", "op"):
        out[side] = {key: row[side][key] for key in (
            "reward", "income", "spend", "quads", "hands", "animals",
            "animal_mix", "crops", "crop_mix", "ready_value", "shed_units",
            "harvests", "waters", "feed_units", "weed_burden", "max_weeds",
            "d12_animals", "d12_animal_mix", "d12_crops", "d12_crop_mix",
        )}
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("agent")
    parser.add_argument("opponent")
    parser.add_argument("--seeds", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    agent = (ROOT / args.agent).resolve()
    opponent = (ROOT / args.opponent).resolve()
    seeds = [int(value) for value in args.seeds.split(",")]
    rows = []
    for seed in seeds:
        for order in (0, 1):
            row = compact(profile_game(agent, opponent, seed, order))
            rows.append(row)
            print(
                f"{seed} o{order} {row['result']} {row['margin']:+,.0f} "
                f"d12 {row['day12_gap']:+,.0f} d18 {row['day18_gap']:+,.0f} "
                f"{row['prefix']}"
            )
    output = (ROOT / args.out).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
