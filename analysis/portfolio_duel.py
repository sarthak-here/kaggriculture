"""Paired-seat duel that reports win rate PER ROUTE BUCKET (#73).

A portfolio agent uses a different route depending on the shop roll, so a global
win rate hides which bucket actually improved. Swapping the 10c4s route and
measuring overall is close to useless: the other four buckets are noise on top.

The shop roll is NOT a pure function of the seed -- `_end_of_day` draws weed
spawns from the same RNG before it picks a shop, so what the agents do changes
which shops unlock. So we do not pre-map seeds to buckets; we record the bucket
each game actually landed in and group the results afterwards.

Usage: python analysis/portfolio_duel.py A.py B.py [n_seeds]
Honours KAG_SEED_BASE like duel.py.
"""

import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kaggle_environments import make  # noqa: E402

from portfolio import label_for  # noqa: E402

SEED_BASE = int(os.environ.get("KAG_SEED_BASE", 5000))

# The rare buckets almost never come up on arbitrary seeds -- 10c4s covers ~48%
# of them. KAG_BUCKET restricts the run to seeds that `portfolio.py` observed
# landing in that bucket, so a 6c8s route can actually be judged where it is used.
BUCKET = os.environ.get("KAG_BUCKET", "").strip()


def seed_list(n):
    if not BUCKET:
        return [SEED_BASE + i for i in range(n)]
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "portfolio", "seed_label.json")
    mapping = json.load(open(path))
    seeds = sorted(int(k) for k, v in mapping.items() if v == BUCKET)
    if not seeds:
        raise SystemExit("no mapped seeds for bucket %r" % BUCKET)
    return seeds[:n]


def play(a, b, seed):
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run([a, b])
    last = env.steps[-1]
    rewards = [s["reward"] for s in last]
    obs = last[0]["observation"]
    shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
    return rewards, label_for(shops), shops


def main():
    a, b = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 8

    per = collections.defaultdict(lambda: {"w": 0, "l": 0, "m": []})
    tot = {"w": 0, "l": 0, "m": []}

    seeds = seed_list(n)
    print("seeds: %s%s" % (seeds[:8], " ..." if len(seeds) > 8 else ""))
    for seed in seeds:
        rolls = []
        for order in (0, 1):
            first, second = (a, b) if order == 0 else (b, a)
            try:
                rewards, label, shops = play(first, second, seed)
            except Exception as exc:                       # noqa: BLE001
                print("  seed %d order %d FAILED: %s" % (seed, order, str(exc)[:70]))
                continue
            rolls.append("%d:%s:%s" % (order, label, ">".join(shops[:3])))
            ra, rb = (rewards[0], rewards[1]) if order == 0 else (rewards[1], rewards[0])
            margin = ra - rb
            bucket = per[label]
            if ra > rb:
                bucket["w"] += 1
                tot["w"] += 1
            elif rb > ra:
                bucket["l"] += 1
                tot["l"] += 1
            bucket["m"].append(margin)
            tot["m"].append(margin)
        print("  seed %d done [%s]" % (seed, "; ".join(rolls)), flush=True)

    print("\n%-24s %6s %6s %9s %10s" % ("route bucket", "A win", "A loss", "win rate", "margin"))
    for label, d in sorted(per.items(), key=lambda kv: -(kv[1]["w"] + kv[1]["l"])):
        dec = d["w"] + d["l"]
        wr = 100.0 * d["w"] / dec if dec else 0.0
        mm = sum(d["m"]) / len(d["m"]) if d["m"] else 0.0
        print("%-24s %6d %6d %8.1f%% %+10.0f" % (label, d["w"], d["l"], wr, mm))

    dec = tot["w"] + tot["l"]
    print("%-24s %6d %6d %8.1f%% %+10.0f"
          % ("ALL", tot["w"], tot["l"],
             100.0 * tot["w"] / dec if dec else 0.0,
             sum(tot["m"]) / len(tot["m"]) if tot["m"] else 0.0))


if __name__ == "__main__":
    main()
