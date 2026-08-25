"""Print day-level farm composition and money for a downloaded replay."""

import collections
import json
import sys


def counts(farm):
    crops = collections.Counter()
    animals = collections.Counter()
    ready = collections.Counter()
    weeds = 0
    for row in farm.get("tiles", []) or []:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            if tile.get("crop"):
                crop = str(tile["crop"])
                crops[crop] += 1
                ready[crop] += max(0, int(tile.get("yield_units", 0) or 0))
            if tile.get("animal"):
                animals[str(tile["animal"])] += 1
            weeds += int(tile.get("kind") == "WEED")
    return crops, animals, ready, weeds


def compact(counter):
    return ",".join("%s%d" % (key[:2], value)
                    for key, value in sorted(counter.items()) if value) or "-"


def main():
    replay = json.load(open(sys.argv[1], encoding="utf-8"))
    steps = replay["steps"]
    names = (replay.get("info") or {}).get("TeamNames") or ["seat0", "seat1"]
    me = next(i for i, name in enumerate(names) if "Sarthak" in str(name))
    seats = [me, 1 - me]
    final = steps[-1][0]["observation"]
    shops = (final.get("town") or {}).get("unlocked_shops") or []
    print("episode", (replay.get("info") or {}).get("EpisodeId"),
          "seed", (replay.get("info") or {}).get("seed"),
          "seat", me, "opponent", names[1 - me])
    print("shops", ">".join(shops))
    print("day | us money     gap q crops/animals ready W shed | op money q crops/animals ready W shed")
    for day in range(0, 31):
        index = min(day * 24, len(steps) - 1)
        row = []
        for seat in seats:
            obs = steps[index][seat]["observation"]
            farm = obs["farms"][seat]
            crops, animals, ready, weeds = counts(farm)
            shed = sum(max(0, int(value or 0))
                       for value in ((obs.get("private") or {}).get("shed") or {}).values())
            row.append((float(farm.get("money", 0) or 0),
                        len(farm.get("unlocked_quadrants") or []), compact(crops),
                        compact(animals), sum(ready.values()), weeds, shed))
        gap = row[0][0] - row[1][0]
        print("%3d | %8.0f %+8.0f %d %-12s/%-9s %3d %2d %3d | %8.0f %d %-12s/%-9s %3d %2d %3d"
              % (day, row[0][0], gap, *row[0][1:], *row[1]))


if __name__ == "__main__":
    main()
