"""Can we predict the end-game CARROT/TOMATO/EGG spike early enough to act on it?

TOMATO needs 8 days from seed to first yield, so the plant/no-plant call has to be
made around day 10-16. This records the market deficit for each watched product on
every day of the game, then asks: does a linear extrapolation from day d predict the
day-29 deficit well enough to gate a planting decision?

Run:  .venv/Scripts/python.exe analysis/scarcity_trajectory.py [n_games]
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kaggle_environments import make
from kaggle_environments.envs.kaggriculture.kaggriculture import (
    MARKET_PARAMS, MARKET_I0, SHOPS, market_price,
)

WATCH = ["CARROT", "TOMATO", "EGG"]
AGENT = "main.py"
TURNS_PER_DAY = 24
DECIDE_DAYS = [8, 10, 12, 14, 16]


def run_game(seed):
    """Return per-day deficit series for each watched product."""
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run([AGENT, AGENT])
    series = {p: [] for p in WATCH}
    for i, step in enumerate(env.steps):
        if i % TURNS_PER_DAY:
            continue
        inv = step[0]["observation"]["market"]["inventory"]
        for p in WATCH:
            series[p].append(MARKET_I0 - inv[p])
    shops = list(env.steps[-1][0]["observation"]["town"].get("unlocked_shops", []))
    return {"seed": seed, "series": series, "shops": shops}


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    rows = []
    for i in range(n):
        seed = 5000 + i
        try:
            r = run_game(seed)
        except Exception as e:
            print(f"seed {seed} FAILED: {type(e).__name__}: {e}")
            continue
        rows.append(r)
        fin = {p: r["series"][p][-1] for p in WATCH}
        print(f"seed {seed}  final deficit  " +
              "  ".join(f"{p[:3]}={fin[p]:>5}" for p in WATCH))

    if not rows:
        print("no games completed")
        return

    ndays = min(len(r["series"][WATCH[0]]) for r in rows)
    print(f"\n{len(rows)} games, {ndays} days recorded\n")

    # Mean deficit trajectory - is accumulation roughly linear in day?
    print("=" * 70)
    print("MEAN DEFICIT BY DAY")
    print("=" * 70)
    print("day  " + "".join(f"{p[:3]:>10}" for p in WATCH))
    for d in range(0, ndays, 2):
        cells = ""
        for p in WATCH:
            m = sum(r["series"][p][d] for r in rows) / len(rows)
            cells += f"{m:>10.0f}"
        print(f"{d:>3}  {cells}")

    # Prediction quality: extrapolate deficit linearly from day d to the final day.
    print("\n" + "=" * 70)
    print("LINEAR EXTRAPOLATION FROM DAY d  ->  FINAL DEFICIT")
    print("predicted = deficit(d) * (final_day / d)")
    print("=" * 70)
    final_day = ndays - 1
    for p in WATCH:
        T = MARKET_PARAMS[p]["T"]
        print(f"\n{p} (knee T={T})")
        for d in DECIDE_DAYS:
            if d >= ndays:
                continue
            errs, hits, miss, false_pos = [], 0, 0, 0
            for r in rows:
                cur = r["series"][p][d]
                actual = r["series"][p][final_day]
                pred = cur * (final_day / d) if d else 0
                if actual:
                    errs.append(abs(pred - actual) / actual)
                # gate: would "predicted past the knee" have been the right call?
                if pred > T and actual > T:
                    hits += 1
                elif pred <= T and actual > T:
                    miss += 1
                elif pred > T and actual <= T:
                    false_pos += 1
            mae = 100 * sum(errs) / len(errs) if errs else float("nan")
            print(f"  day {d:>2}: mean abs err {mae:>5.1f}%   "
                  f"gate u>1  hit {hits:>2}  missed {miss:>2}  false-alarm {false_pos:>2}")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "scarcity_trajectory_results.json")
    with open(out, "w") as f:
        json.dump(rows, f, indent=1)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
