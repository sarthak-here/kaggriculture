"""Measure the CARROT/TOMATO/EGG scarcity spike introduced in kaggle-environments 1.32.7.

PR #1399 switched the *below-I0* (scarcity) branch of those three products from
linear/log to a "hinge": price = base + below_target*base*(u + 8*max(0,u-1)^2),
where u = deficit/T. Below the knee it is mild; above it, it runs away.

This script runs real episodes and records, per game:
  - the town's shop composition (now drawn WITH replacement, PR #1394)
  - the end-of-game inventory deficit for each product
  - the implied market price at that deficit

Run:  .venv/Scripts/python.exe analysis/market_scarcity.py [n_games]
"""

import sys
import os
import json
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kaggle_environments import make
from kaggle_environments.envs.kaggriculture.kaggriculture import (
    MARKET_PARAMS,
    MARKET_I0,
    SHOPS,
    market_price,
)

WATCH = ["CARROT", "TOMATO", "EGG"]
AGENT = "main.py"


def price_curve(item):
    """Deficit -> price table, to show where the knee bites."""
    T = MARKET_PARAMS[item]["T"]
    return [(int(u * T), market_price(item, MARKET_I0 - int(u * T)))
            for u in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0)]


def run_game(seed):
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run([AGENT, AGENT])
    obs = env.steps[-1][0]["observation"]
    market = obs["market"]
    town = obs["town"]
    inv = market["inventory"]
    return {
        "seed": seed,
        "shops": list(town.get("unlocked_shops", [])),
        "deficit": {p: MARKET_I0 - inv[p] for p in WATCH},
        "price": {p: market_price(p, inv[p], market.get("params")) for p in WATCH},
    }


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40

    print("=" * 68)
    print("PRICE CURVES  (deficit below I0=10000 -> unit price)")
    print("=" * 68)
    for item in WATCH:
        p = MARKET_PARAMS[item]
        knee = p["T"]
        cells = "  ".join(f"{d:>5}:${pr:<6}" for d, pr in price_curve(item))
        print(f"{item:<11} base=${p['base']:<4} knee T={knee:<4} {p['below_func']}")
        print(f"            {cells}")
    print()

    rows = []
    for i in range(n):
        seed = 1000 + i
        try:
            rows.append(run_game(seed))
        except Exception as e:  # keep going; report at the end
            print(f"  seed {seed} FAILED: {type(e).__name__}: {e}")
            continue
        r = rows[-1]
        d, pr = r["deficit"], r["price"]
        print(f"seed {seed}  " + "  ".join(
            f"{p[:3]} d={d[p]:>5} ${pr[p]:<6}" for p in WATCH))

    if not rows:
        print("no games completed")
        return

    print()
    print("=" * 68)
    print(f"SUMMARY over {len(rows)} games (agent: {AGENT} vs itself)")
    print("=" * 68)
    for item in WATCH:
        T = MARKET_PARAMS[item]["T"]
        base = MARKET_PARAMS[item]["base"]
        defs = sorted(r["deficit"][item] for r in rows)
        prices = sorted(r["price"][item] for r in rows)
        over_knee = sum(1 for r in rows if r["deficit"][item] > T)
        over_2x = sum(1 for r in rows if r["deficit"][item] > 2 * T)
        med = defs[len(defs) // 2]
        medp = prices[len(prices) // 2]
        print(f"\n{item}  (base ${base}, knee T={T})")
        print(f"  deficit   min {defs[0]:>6}  median {med:>6}  max {defs[-1]:>6}")
        print(f"  price     min ${prices[0]:<6} median ${medp:<6} max ${prices[-1]:<6}")
        print(f"  past knee (u>1): {over_knee}/{len(rows)} = {100*over_knee/len(rows):.0f}%"
              f"   |  u>2: {over_2x}/{len(rows)} = {100*over_2x/len(rows):.0f}%")

    print("\n" + "=" * 68)
    print("SHOP COMPOSITION (drawn with replacement)")
    print("=" * 68)
    allshops = Counter()
    for r in rows:
        allshops.update(r["shops"])
    for name, c in allshops.most_common():
        print(f"  {name:<16} {c:>4} instances  ({c/len(rows):.2f} per game)  -> {SHOPS[name]}")

    # Does a heavy draw of a carrot/tomato/egg shop predict the spike?
    print("\n" + "=" * 68)
    print("SPIKE vs SHOP DRAW")
    print("=" * 68)
    demanders = {p: [s for s, items in SHOPS.items() if p in items] for p in WATCH}
    for item in WATCH:
        T = MARKET_PARAMS[item]["T"]
        print(f"\n{item}: demanded by {demanders[item]}")
        buckets = {}
        for r in rows:
            # weight single-product shops x2, matching _town_consume's multiplier
            w = sum(2 if len(SHOPS[s]) == 1 else 1
                    for s in r["shops"] if s in demanders[item])
            buckets.setdefault(w, []).append(r["price"][item])
        for w in sorted(buckets):
            ps = buckets[w]
            print(f"  demand weight {w:>2}: {len(ps):>3} games, "
                  f"median price ${sorted(ps)[len(ps)//2]}")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "market_scarcity_results.json")
    with open(out, "w") as f:
        json.dump(rows, f, indent=1)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
