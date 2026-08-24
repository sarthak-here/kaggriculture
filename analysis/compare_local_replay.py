"""Show where two local Kaggriculture agents separate in a paired replay.

Usage: python analysis/compare_local_replay.py A.py B.py SEED [ORDER]
ORDER 0 runs [A,B]; ORDER 1 runs [B,A] while still reporting A first.
"""

import collections
import sys

from kaggle_environments import make


def farm_counts(farm):
    crops = collections.Counter()
    animals = collections.Counter()
    weeds = 0
    for row in farm.get("tiles", []) or []:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            if tile.get("crop"):
                crops[str(tile["crop"])] += 1
            if tile.get("animal"):
                animals[str(tile["animal"])] += 1
            if tile.get("kind") == "WEED":
                weeds += 1
    return crops, animals, weeds


def compact(counter):
    return ",".join("%s%d" % (key[:2], value)
                    for key, value in sorted(counter.items())) or "-"


def snapshot(env, step, physical_seat):
    state = env.steps[step][physical_seat]
    obs = state["observation"]
    farm = obs["farms"][physical_seat]
    crops, animals, weeds = farm_counts(farm)
    private = obs.get("private", {}) or {}
    shed = private.get("shed", {}) or {}
    return {
        "money": float(farm.get("money", 0) or 0),
        "quads": len(farm.get("unlocked_quadrants", []) or []),
        "hands": len(farm.get("hands", []) or []),
        "crops": compact(crops),
        "animals": compact(animals),
        "weeds": weeds,
        "shed": sum(int(value or 0) for value in shed.values()),
    }


def main():
    a, b, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
    order = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    entries = [a, b] if order == 0 else [b, a]
    seats = [0, 1] if order == 0 else [1, 0]
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run(entries)

    final_obs = env.steps[-1][0]["observation"]
    shops = list((final_obs.get("town", {}) or {}).get("unlocked_shops", []) or [])
    print("seed", seed, "order", order, "shops", ">".join(shops))
    print("day | A money  B money    gap | Aq Ah crop/animal W sh | Bq Bh crop/animal W sh")
    for day in range(0, 31):
        step = min(719, day * 24)
        sa = snapshot(env, step, seats[0])
        sb = snapshot(env, step, seats[1])
        print(
            "%3d | %7.0f %7.0f %+7.0f | %d %2d %-13s/%-9s %d %2d | "
            "%d %2d %-13s/%-9s %d %2d"
            % (
                day, sa["money"], sb["money"], sa["money"] - sb["money"],
                sa["quads"], sa["hands"], sa["crops"], sa["animals"],
                sa["weeds"], sa["shed"],
                sb["quads"], sb["hands"], sb["crops"], sb["animals"],
                sb["weeds"], sb["shed"],
            )
        )


if __name__ == "__main__":
    main()
