"""Profile OUR agent with the same columns q3_profile.py reports for real replays,
so our build curve can be laid next to a winning 3-quadrant build.

Run:  .venv/Scripts/python.exe analysis/our_profile.py <agent.py> [seed]
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kaggle_environments import make
from q3_profile import profile_player, land_days


def main():
    agent = sys.argv[1] if len(sys.argv) > 1 else "main.py"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2001
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run([agent, agent])

    steps = [[{"observation": s[0]["observation"]}, {"observation": s[0]["observation"]}]
             for s in env.steps]
    days = profile_player(steps, 0)
    print(f"{agent}  seed {seed}  reward {env.steps[-1][0]['reward']:,.0f}"
          f"  land {land_days(days)}")
    print("day   money  quads  hands  tiles  animals   crop mix")
    for d in days:
        if d["day"] % 2 and d["day"] > 15:
            continue
        mix = " ".join(f"{k[:4]}:{v}" for k, v in sorted(d["crops"].items()))
        print(f"{d['day']:>3} {d['money']:>7,.0f} {d['quads']:>6} {d['hands']:>6}"
              f" {d['planted']:>6} {d['animals']:>8}   {mix}")


if __name__ == "__main__":
    main()
