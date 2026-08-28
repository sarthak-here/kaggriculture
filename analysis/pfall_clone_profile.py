"""Measure pf_all's live clone-distance gate across its current losses."""

from __future__ import annotations

import sys

import collections
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "loss_analysis" / "pfall_current"
KEYS = tuple(sorted(("WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
                     "COW", "SHEEP", "GOOSE", "PASTURE", "COOP", "WEED")))


def signature(farm):
    counts = {key: 0 for key in KEYS}
    for row in farm.get("tiles", []) or []:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            for field in ("crop", "animal", "kind"):
                value = str(tile.get(field, "")).upper()
                if value in counts:
                    counts[value] += 1
                    break
    return (len(farm.get("hands", []) or []),
            len(farm.get("unlocked_quadrants", []) or []),
            tuple(counts[key] for key in KEYS))


def distance(obs):
    left, right = map(signature, obs["farms"][:2])
    return (abs(left[0] - right[0]) + 3 * abs(left[1] - right[1])
            + sum(abs(a - b) for a, b in zip(left[2], right[2])))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    profiles = json.load(open(CORPUS / "profiles.json", encoding="utf-8"))
    by_episode = {row["episode"]: row for row in profiles}
    rows = []
    for path in CORPUS.glob("episode-*-replay.json"):
        episode = int(path.name.split("-")[1])
        replay = json.load(open(path, encoding="utf-8"))
        values = []
        for index in range(120, min(681, len(replay.get("steps") or []))):
            obs = replay["steps"][index][0].get("observation")
            if isinstance(obs, dict):
                values.append(distance(obs))
        row = by_episode[episode]
        counts = {threshold: sum(value <= threshold for value in values)
                  for threshold in (0, 2, 6, 12)}
        streak = current = 0
        for value in values:
            current = current + 1 if value <= 2 else 0
            streak = max(streak, current)
        rows.append({**row, "min_clone": min(values), "mean_clone": statistics.mean(values),
                     "turns": counts, "streak2": streak})
    for label, group in (
        ("ALL", rows),
        ("CLOSE", [row for row in rows if row["margin"] >= -2500]),
        ("SEVERE", [row for row in rows if row["margin"] <= -8000]),
        ("10C4S", [row for row in rows if row["bucket"] == "10c4s_3q"]),
        ("YARN", [row for row in rows if "6c12s" in row["bucket"]]),
    ):
        print(label, len(group),
              "any<=6", sum(row["turns"][6] > 0 for row in group),
              "any<=2", sum(row["turns"][2] > 0 for row in group),
              "streak24<=2", sum(row["streak2"] >= 24 for row in group),
              "mean turns<=6 %.1f" % statistics.mean(row["turns"][6] for row in group))
    print("\nclosest losses")
    for row in sorted(rows, key=lambda value: (-value["turns"][6], value["margin"]))[:25]:
        print("%d m%+6.0f s%d %-22s <=6 %3d <=2 %3d streak %3d min %2d %s" % (
            row["episode"], row["margin"], row["seat"], row["bucket"],
            row["turns"][6], row["turns"][2], row["streak2"], row["min_clone"],
            row["opponent"][:20]))


if __name__ == "__main__":
    main()