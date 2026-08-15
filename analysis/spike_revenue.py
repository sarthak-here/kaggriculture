"""How much money can we actually realise from a CARROT/TOMATO/EGG spike?

The headline price is the price of the FIRST unit sold. Every unit we sell puts one
back into market inventory, shrinking the deficit and sliding us back down the hinge,
so revenue is sub-linear in volume. This prices that decay honestly and compares it
against the opportunity cost of the tile.

Run:  .venv/Scripts/python.exe analysis/spike_revenue.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kaggle_environments.envs.kaggriculture.kaggriculture import (
    CROPS, ANIMALS, MARKET_PARAMS, MARKET_I0, market_price,
)

# Observed end-of-game deficits from analysis/market_scarcity.py, 40 games.
OBSERVED = {
    "CARROT": {"median": 354, "p90": 700, "max": 1038},
    "TOMATO": {"median": 228, "p90": 380, "max": 462},
    "EGG":    {"median": 264, "p90": 450, "max": 570},
}


def sell_revenue(item, deficit, n):
    """Revenue from dumping n units into a market that is `deficit` below I0.

    Each sale raises inventory by 1 (engine: _commit_unit), so the next unit
    prices one step further down the curve.
    """
    total = 0
    inv = MARKET_I0 - deficit
    for _ in range(n):
        total += market_price(item, inv)
        inv += 1
    return total


def marginal(item, deficit, n):
    return market_price(item, MARKET_I0 - deficit + n)


def main():
    print("=" * 74)
    print("REVENUE vs VOLUME  (dumping n units at once into a given deficit)")
    print("=" * 74)
    for item, obs in OBSERVED.items():
        base = MARKET_PARAMS[item]["base"]
        print(f"\n{item}  base ${base}  knee T={MARKET_PARAMS[item]['T']}")
        for label in ("median", "p90", "max"):
            d = obs[label]
            row = []
            for n in (4, 12, 24, 48, 96):
                rev = sell_revenue(item, d, n)
                row.append(f"n={n:<3}${rev:<7,} (${rev//n}/u)")
            print(f"  deficit {d:>5} ({label:>6}): " + "  ".join(row))

    print("\n" + "=" * 74)
    print("TILE ECONOMICS  (one tile, planted with `days_left` days remaining)")
    print("=" * 74)
    print("Yield model from CROPS: first_yield_day, then every `interval` days if")
    print("ongoing, max_yield units per harvest.\n")

    def units_from_tile(crop, days_left):
        c = CROPS[crop]
        if days_left < c["first_yield_day"]:
            return 0
        if not c["ongoing"]:
            return c["max_yield"]
        harvests = 1 + (days_left - c["first_yield_day"]) // max(1, c["interval"])
        return harvests * c["max_yield"]

    for crop in ("CARROT", "TOMATO", "STRAWBERRY", "MELON", "WHEAT"):
        c = CROPS[crop]
        row = []
        for dl in (3, 6, 10, 16, 22):
            row.append(f"{dl}d:{units_from_tile(crop, dl):>3}u")
        print(f"  {crop:<11} seed ${c['seed']:<4} fy{c['first_yield_day']:<3} "
              f"int{c['interval']}  ongoing={str(c['ongoing']):<5}  " + "  ".join(row))

    print("\n" + "=" * 74)
    print("HEAD TO HEAD: value of one tile over the last `days_left` days")
    print("Spike crops priced at their observed deficits; staples at base price.")
    print("(Staple base prices are optimistic - we already glut strawberry/melon.)")
    print("=" * 74)
    for dl in (4, 6, 10, 16):
        print(f"\n  --- {dl} days left ---")
        rows = []
        for crop in ("CARROT", "TOMATO", "STRAWBERRY", "MELON", "WHEAT"):
            u = units_from_tile(crop, dl)
            seed = CROPS[crop]["seed"]
            if crop in OBSERVED:
                for label in ("median", "p90"):
                    d = OBSERVED[crop][label]
                    rev = sell_revenue(crop, d, u) - seed
                    rows.append((rev, f"{crop}({label})", u, rev))
            else:
                rev = u * MARKET_PARAMS[crop]["base"] - seed
                rows.append((rev, crop, u, rev))
        for _, name, u, rev in sorted(rows, reverse=True):
            print(f"    {name:<20} {u:>3} units  net ${rev:>8,}")

    print("\n" + "=" * 74)
    print("EGG / GOOSE")
    print("=" * 74)
    g = ANIMALS["GOOSE"]
    print(f"  GOOSE ${g['cost']}, first yield day {g['first_yield_day']}, "
          f"every {g['interval']}d, max_held {g['max_held']}")
    for dl in (6, 10, 16, 22):
        if dl < g["first_yield_day"]:
            continue
        harvests = 1 + (dl - g["first_yield_day"]) // g["interval"]
        units = harvests * g["max_held"]
        for label in ("median", "p90"):
            d = OBSERVED["EGG"][label]
            rev = sell_revenue("EGG", d, units) - g["cost"]
            print(f"  {dl:>2}d left: {units:>3} eggs  ({label:>6} deficit {d:>4})"
                  f"  net ${rev:>8,}")


if __name__ == "__main__":
    main()
