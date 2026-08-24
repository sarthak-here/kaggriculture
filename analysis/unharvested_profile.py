"""Measure crops still harvestable when a Kaggriculture match ends.

Usage:
  python analysis/unharvested_profile.py replay.json
  python analysis/unharvested_profile.py agent_a.py agent_b.py seed [order]
"""

import collections
import json
import sys

from kaggle_environments import make


def terminal_profile(steps, seat):
    final = steps[-1][seat]
    obs = final["observation"]
    farm = obs["farms"][seat]
    prices = (obs.get("market") or {}).get("prices") or {}
    units = collections.Counter()
    tiles = collections.Counter()
    positions = []
    for y, row in enumerate(farm.get("tiles") or []):
        for x, tile in enumerate(row):
            if not isinstance(tile, dict) or not tile.get("crop"):
                continue
            crop = str(tile["crop"])
            amount = max(0, int(tile.get("yield_units", 0) or 0))
            if amount:
                units[crop] += amount
                tiles[crop] += 1
                positions.append((x, y, crop, amount))
    value = {crop: amount * int(prices.get(crop, 0) or 0)
             for crop, amount in units.items()}
    late_harvests = 0
    for state in steps[max(0, len(steps) - 25):]:
        action = state[seat].get("action")
        if not isinstance(action, dict):
            continue
        rows = [action.get("farmer"), *(action.get("hands") or [])]
        late_harvests += sum(1 for row in rows
                             if isinstance(row, list) and row[:1] == ["HARVEST"])
    return {
        "reward": final.get("reward"),
        "units": dict(units),
        "tiles": dict(tiles),
        "value": value,
        "total_value": sum(value.values()),
        "positions": positions,
        "last_day_harvest_actions": late_harvests,
    }


def report(label, profile):
    print(label, "reward", profile["reward"])
    print("  harvestable units", profile["units"])
    print("  occupied ready tiles", profile["tiles"])
    print("  value at terminal prices", profile["value"],
          "total", profile["total_value"])
    print("  last-day HARVEST actions", profile["last_day_harvest_actions"])
    print("  positions", profile["positions"])


def main():
    if len(sys.argv) == 2:
        replay = json.load(open(sys.argv[1], encoding="utf-8"))
        steps = replay["steps"]
        names = (replay.get("info") or {}).get("TeamNames") or ["seat0", "seat1"]
        for seat in (0, 1):
            report("seat%d %s" % (seat, names[seat]), terminal_profile(steps, seat))
        return

    a, b, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
    order = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    entries = [a, b] if order == 0 else [b, a]
    seats = [0, 1] if order == 0 else [1, 0]
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run(entries)
    report("A", terminal_profile(env.steps, seats[0]))
    report("B", terminal_profile(env.steps, seats[1]))


if __name__ == "__main__":
    main()
