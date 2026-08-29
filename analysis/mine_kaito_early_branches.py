"""Mine lean routes that share Kaito's exact day-0 action.

An exact one-action prefix allows a branch decision on observation step 1,
after the opponent's opening market orders have become public farm state.
"""

from __future__ import annotations

import argparse
import ast
import gzip
import hashlib
import json
from pathlib import Path

from mine_compatible_routes import prefix_length, route_of
from extract_kaito_v46 import assignment, decode_json


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            return json.load(handle)
    return json.loads(path.read_text(encoding="utf-8"))


def final_family(replay: dict, seat: int) -> dict:
    obs = replay["steps"][-1][seat]["observation"]
    farm = obs["farms"][seat]
    animals = {"COW": 0, "SHEEP": 0, "GOOSE": 0}
    crops = {}
    for line in farm.get("tiles", []) or []:
        for tile in line:
            if not isinstance(tile, dict):
                continue
            animal = tile.get("animal")
            if animal in animals:
                animals[animal] += 1
            crop = tile.get("crop")
            if crop:
                crops[crop] = crops.get(crop, 0) + 1
    return {
        "quadrants": len(farm.get("unlocked_quadrants", []) or []),
        "hands": len(farm.get("hands", []) or []),
        "animals": animals,
        "crops": crops,
    }


def replay_paths() -> list[Path]:
    paths = list((ROOT / "replays_top").glob("episode-*-replay.json.gz"))
    for relative in (
        "route_mining/active_lineage",
        "loss_analysis/kaito_current",
        "loss_analysis/pfall_current",
        "loss_analysis/v46_submission",
    ):
        paths.extend((ROOT / relative).glob("episode-*-replay.json"))
    return sorted(set(paths))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=Path("route_mining/kaito_early_branches"))
    parser.add_argument("--minimum-prefix", type=int, default=1)
    args = parser.parse_args()

    source = (ROOT / "submit_v46_three_suffix/main.py").read_text(encoding="utf-8")
    routes = decode_json(assignment(ast.parse(source), "_V44_ROUTES"))
    base = routes["default"]
    output = ROOT / args.output
    output.mkdir(parents=True, exist_ok=True)
    unique = {}
    scanned = 0

    for path in replay_paths():
        replay = load(path)
        episode = int(path.name.split("-")[1])
        for seat in (0, 1):
            if not replay.get("steps") or seat >= len(replay["steps"][-1]):
                continue
            scanned += 1
            route = route_of(replay, seat)
            prefix = prefix_length(base, route)
            if prefix < args.minimum_prefix or prefix >= len(route):
                continue
            family = final_family(replay, seat)
            animals = family["animals"]
            total_animals = sum(animals.values())
            if family["quadrants"] > 3 or total_animals > 12:
                continue
            packed = json.dumps(route, separators=(",", ":"), sort_keys=True).encode()
            digest = hashlib.sha256(packed).hexdigest()
            final = replay["steps"][-1][seat]
            obs = final["observation"]
            shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
            opponent = replay["steps"][-1][1 - seat]
            row = {
                "name": f"ep{episode}_s{seat}_p{prefix}",
                "episode": episode,
                "seat": seat,
                "prefix": prefix,
                "reward": float(final.get("reward") or 0),
                "opponent_reward": float(opponent.get("reward") or 0),
                "margin": float(final.get("reward") or 0) - float(opponent.get("reward") or 0),
                "shops": shops,
                "family": family,
                "route_sha256": digest,
                "route_file": str((output / f"route-{episode}-seat{seat}.json.gz")
                                  .relative_to(ROOT)),
            }
            old = unique.get(digest)
            if old is None or (prefix, row["margin"]) > (old["prefix"], old["margin"]):
                with gzip.open(ROOT / row["route_file"], "wt", encoding="utf-8") as handle:
                    json.dump(route, handle, separators=(",", ":"))
                unique[digest] = row

    rows = sorted(unique.values(), key=lambda row: (-row["prefix"], -row["margin"]))
    (output / "compatible_routes.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"scanned seats {scanned}; unique lean day-0-compatible routes {len(rows)}")
    for row in rows[:40]:
        family = row["family"]
        print(row["name"], "margin", int(row["margin"]),
              "q", family["quadrants"], family["animals"],
              ">".join(row["shops"][:3]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
