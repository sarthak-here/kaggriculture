"""What actually breaks when we add a third quadrant?

Five controlled tests said Q3 loses, but "the policy cannot work the extra tiles" was
a guess. This measures it: per day, how many owned tiles are planted, how many of those
got watered, how many crops died unwatered, how many units are idle, and how far they
walk. Run it on a 2-quadrant and a 3-quadrant build and diff the columns.

Run:  .venv/Scripts/python.exe analysis/tile_utilization.py <agent> [seed]
"""

import sys
import os
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kaggle_environments import make

TURNS_PER_DAY = 24
SEAT = 0
QUADRANT_ORIGIN = {"NW": (0, 0), "NE": (5, 0), "SW": (0, 5), "SE": (5, 5)}


def owned_tile_count(farm):
    """Tiles inside the quadrants this farm owns."""
    n = 0
    for q in farm["unlocked_quadrants"]:
        ox, oy = QUADRANT_ORIGIN[q]
        for y in range(oy, oy + 5):
            for x in range(ox, ox + 5):
                n += 1
    return n


def main():
    agent = sys.argv[1] if len(sys.argv) > 1 else "main.py"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2001

    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run([agent, agent])

    print(f"{agent}  seed {seed}  reward {env.steps[-1][SEAT]['reward']:,.0f}")
    print("=" * 96)
    print("day  own  plant  bare  watered  unwat  ripe_held  idle_u  acts/unit  "
          "died  yield/tile")
    print("=" * 96)

    prev_plants = {}
    for i in range(0, len(env.steps), TURNS_PER_DAY):
        window = env.steps[i:i + TURNS_PER_DAY]
        obs_end = window[-1][SEAT]["observation"]
        farm = obs_end["farms"][SEAT]

        own = owned_tile_count(farm)
        planted = watered = unwatered = ripe_held = 0
        yield_units = 0
        cur_plants = {}
        for y, row in enumerate(farm["tiles"]):
            for x, t in enumerate(row):
                if isinstance(t, dict) and t.get("kind") == "PLANT":
                    planted += 1
                    cur_plants[(x, y)] = t.get("crop")
                    if t.get("watered_today"):
                        watered += 1
                    else:
                        unwatered += 1
                    yu = t.get("yield_units", 0)
                    yield_units += yu
                    if yu > 0:
                        ripe_held += 1

        # crops that vanished without being harvested are deaths (rough proxy:
        # a tile that held a plant yesterday and is empty today with no harvest)
        died = 0
        for pos, crop in prev_plants.items():
            if pos not in cur_plants:
                ty, tx = pos[1], pos[0]
                t = farm["tiles"][ty][tx]
                if t is None or (isinstance(t, dict) and t.get("kind") == "WEED"):
                    died += 1
        prev_plants = cur_plants

        # unit activity over the day
        acts = 0
        idle = 0
        units_seen = 0
        for st in window:
            a = st[SEAT].get("action")
            if not isinstance(a, dict):
                continue
            ops = [a.get("farmer")] + list(a.get("hands") or [])
            for op in ops:
                if not op:
                    continue
                units_seen += 1
                if op[0] in ("PASS",):
                    idle += 1
                else:
                    acts += 1
        per_unit = acts / max(1, units_seen)
        bare = own - planted
        ypt = yield_units / max(1, planted)

        print(f"{i//TURNS_PER_DAY:>3} {own:>4} {planted:>6} {bare:>5} {watered:>8}"
              f" {unwatered:>6} {ripe_held:>10} {idle:>7} {per_unit:>10.2f}"
              f" {died:>5} {ypt:>11.2f}")


if __name__ == "__main__":
    main()
