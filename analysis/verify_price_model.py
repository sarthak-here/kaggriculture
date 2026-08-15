"""Assert game_data.predicted_price matches the engine's market_price exactly.

main.py sells through game_data.sell_quantity, which walks predicted_price. If the
replica drifts from the engine (as it did when 1.32.7 changed CARROT/TOMATO/EGG to
the hinge curve), every sell decision is made against a fictional market and nothing
visibly breaks. This is the regression test for that.

Run:  .venv/Scripts/python.exe analysis/verify_price_model.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_data import predicted_price, MARKET_PARAMS as OURS
from kaggle_environments.envs.kaggriculture.kaggriculture import (
    market_price, MARKET_PARAMS as ENGINE, MARKET_I0,
)

def main():
    # 1. parameter tables agree
    param_bad = []
    for item, ep in ENGINE.items():
        op = OURS.get(item)
        if op is None:
            param_bad.append(f"{item}: missing from game_data")
            continue
        for ekey, okey in (("base", "base"), ("T", "T"), ("I0", "I0"),
                           ("below_func", "below"), ("above_func", "above"),
                           ("below_target", "below_target"),
                           ("above_target", "above_target")):
            if ep[ekey] != op[okey]:
                param_bad.append(
                    f"{item}.{okey}: ours={op[okey]!r} engine={ep[ekey]!r}")

    print("=" * 60)
    print("PARAMETER TABLE")
    print("=" * 60)
    if param_bad:
        for b in param_bad:
            print("  MISMATCH  " + b)
    else:
        print(f"  OK - all {len(ENGINE)} products match the engine")

    # 2. prices agree across the full inventory range, both sides of I0
    print("\n" + "=" * 60)
    print("PRICE CURVE  (offsets from I0, scarcity and glut)")
    print("=" * 60)
    offsets = list(range(-3000, 3001, 1)) + [-9999, -5000, 5000, 20000]
    total_bad = 0
    for item in ENGINE:
        bad = []
        for off in offsets:
            inv = MARKET_I0 + off
            if inv < 0:
                continue
            e = market_price(item, inv)
            o = predicted_price(item, inv)
            if e != o:
                bad.append((inv, o, e))
        total_bad += len(bad)
        if bad:
            print(f"  {item:<11} {len(bad):>5} mismatches, first 3: " +
                  "  ".join(f"inv={i} ours={o} engine={e}" for i, o, e in bad[:3]))
        else:
            print(f"  {item:<11} OK ({len(offsets)} points)")

    print()
    if param_bad or total_bad:
        print(f"FAIL - {len(param_bad)} param mismatches, {total_bad} price mismatches")
        return 1
    print("PASS - replica is identical to the engine")
    return 0


if __name__ == "__main__":
    sys.exit(main())
