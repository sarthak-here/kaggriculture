"""Why do ~15 owned tiles sit bare all game?

tile_utilization.py showed we own 50 tiles and plant only 34-36 from day 7 onward.
This instruments the seed-buying decision itself -- the gate that decides whether we
even try to fill a tile -- by re-implementing its inputs from the observation each day:
empty tiles, reserved build sites, whether a unit is already holding a seed, cash, and
what the target crop deficits actually are.

Run:  .venv/Scripts/python.exe analysis/seed_pipeline.py <agent> [seed]
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kaggle_environments import make

TURNS_PER_DAY = 24
SEAT = 0
QUADRANT_ORIGIN = {"NW": (0, 0), "NE": (5, 0), "SW": (0, 5), "SE": (5, 5)}


def owned_positions(farm):
    out = []
    for q in farm["unlocked_quadrants"]:
        ox, oy = QUADRANT_ORIGIN[q]
        for y in range(oy, oy + 5):
            for x in range(ox, ox + 5):
                out.append((x, y))
    return out


def main():
    agent = sys.argv[1] if len(sys.argv) > 1 else "main.py"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2001
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run([agent, agent])

    print(f"{agent}  seed {seed}")
    print("=" * 92)
    print("day  own  empty  weeds  structs  seed_orders  seeds_held  money_eod  "
          "planted_today")
    print("=" * 92)

    for i in range(0, len(env.steps), TURNS_PER_DAY):
        window = env.steps[i:i + TURNS_PER_DAY]
        day = i // TURNS_PER_DAY
        obs_end = window[-1][SEAT]["observation"]
        farm = obs_end["farms"][SEAT]
        priv = obs_end.get("private", {}) or {}

        empty = weeds = structs = 0
        for (x, y) in owned_positions(farm):
            t = farm["tiles"][y][x]
            if t is None:
                empty += 1
            elif isinstance(t, dict):
                k = t.get("kind")
                if k == "WEED":
                    weeds += 1
                elif k in ("COOP", "PASTURE", "SHED", "BARN"):
                    structs += 1

        seed_orders = 0
        planted_today = 0
        for st in window:
            a = st[SEAT].get("action")
            if not isinstance(a, dict):
                continue
            for row in (a.get("market") or []):
                if row and row[0] == "BUY_SEED":
                    seed_orders += int(row[2]) if len(row) > 2 else 1
            for op in [a.get("farmer")] + list(a.get("hands") or []):
                if op and op[0] == "PLANT":
                    planted_today += 1

        seeds_held = sum((priv.get("seeds") or {}).values())
        print(f"{day:>3} {len(owned_positions(farm)):>4} {empty:>6} {weeds:>6}"
              f" {structs:>8} {seed_orders:>12} {seeds_held:>11}"
              f" {farm['money']:>10,.0f} {planted_today:>14}")


if __name__ == "__main__":
    main()
