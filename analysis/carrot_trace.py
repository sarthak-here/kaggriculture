"""Trace the carrot arm through one game: planted -> ripened -> shed -> sold.

The duel showed 16 carrot tiles planted but only 12 units sold, so most of the
crop is leaking somewhere between the tile and the market. This prints the daily
lifecycle so the leak is visible.

Run:  .venv/Scripts/python.exe analysis/carrot_trace.py [seed]
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kaggle_environments import make
from kaggle_environments.envs.kaggriculture.kaggriculture import MARKET_I0, market_price

TURNS_PER_DAY = 24
SEAT = 0


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 2001
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run(["main.py", "main.py"])

    sold_by_day = {}
    planted_by_day = {}
    for i, step in enumerate(env.steps):
        day = i // TURNS_PER_DAY
        act = step[SEAT].get("action")
        if not isinstance(act, dict):
            continue
        for row in (act.get("market") or []):
            if isinstance(row, (list, tuple)) and len(row) > 2 \
                    and row[0] == "SELL" and row[1] == "CARROT":
                sold_by_day[day] = sold_by_day.get(day, 0) + int(row[2])
        units = [act.get("farmer")] + list(act.get("hands") or [])
        for u in units:
            if isinstance(u, (list, tuple)) and len(u) >= 2 \
                    and u[0] == "PLANT" and u[1] == "CARROT":
                planted_by_day[day] = planted_by_day.get(day, 0) + 1

    print(f"seed {seed}   final reward {env.steps[-1][SEAT]['reward']:,.0f}")
    print("=" * 78)
    print("day  planted  ripe_tiles  tile_units  shed  sold  price  deficit")
    print("=" * 78)
    for i in range(0, len(env.steps), TURNS_PER_DAY):
        day = i // TURNS_PER_DAY
        obs = env.steps[i][SEAT]["observation"]
        farm = obs["farms"][SEAT] if "farms" in obs else None
        if farm is None:
            continue
        ripe = 0
        tile_units = 0
        for row in farm["tiles"]:
            for t in row:
                if isinstance(t, dict) and t.get("kind") == "PLANT" \
                        and t.get("crop") == "CARROT":
                    ripe += 1
                    tile_units += t.get("yield_units", 0)
        shed = env.steps[i][SEAT]["observation"].get("private", {}).get("shed", {})
        inv = env.steps[i][0]["observation"]["market"]["inventory"]["CARROT"]
        print(f"{day:>3}  {planted_by_day.get(day,0):>7}  {ripe:>10}  {tile_units:>10}"
              f"  {shed.get('CARROT',0):>4}  {sold_by_day.get(day,0):>4}"
              f"  ${market_price('CARROT', inv):<5} {MARKET_I0-inv:>6}")

    print("=" * 78)
    print(f"total planted {sum(planted_by_day.values())}   "
          f"total sold {sum(sold_by_day.values())}")
    final_shed = env.steps[-1][SEAT]["observation"].get("private", {}).get("shed", {})
    print(f"carrots stranded in shed at end: {final_shed.get('CARROT', 0)}")


if __name__ == "__main__":
    main()
