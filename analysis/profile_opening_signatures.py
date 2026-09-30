"""Print public farm signatures after each agent's opening action."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from kaggle_environments import make


def compact_farm(farm: dict) -> dict:
    tiles = []
    for row_index, row in enumerate(farm.get("tiles", [])):
        for column_index, tile in enumerate(row):
            if isinstance(tile, dict):
                tiles.append({
                    "position": [column_index, row_index],
                    "kind": tile.get("kind"),
                    "animal": tile.get("animal"),
                    "crop": tile.get("crop"),
                })
    return {
        "money": farm.get("money"),
        "farmer": farm.get("farmer"),
        "hands": farm.get("hands"),
        "hires_today": farm.get("hires_today"),
        "unlocked_quadrants": farm.get("unlocked_quadrants"),
        "tiles": tiles,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", type=Path)
    parser.add_argument("agents", nargs="+", type=Path)
    parser.add_argument("--seed", type=int, default=1_100_500)
    parser.add_argument("--step", type=int, default=1)
    args = parser.parse_args()

    rows = []
    for agent in args.agents:
        environment = make(
            "kaggriculture", configuration={"seed": args.seed}, debug=False
        )
        environment.run([str(args.reference.resolve()), str(agent.resolve())])
        observation = environment.steps[args.step][0]["observation"]
        rows.append({
            "agent": str(agent),
            "step": args.step,
            "signature": compact_farm(observation["farms"][1]),
        })
    print(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
