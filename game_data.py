"""
Static game constants (from the Kaggriculture rules) and the price-prediction
formula, kept separate from decision logic in main.py.

These numbers are documented physical facts about the game, not decisions —
per STRATEGY.md's "never hardcode, always compute" this applies to *choices*
(which crop, when to sell), not to encoding the game's own fixed constants.
"""
import math

# yield_per_tile_day matches the "Yield / tile / day" column in the rules
# (unfertilized, watered daily, harvested at peak). max_yield is unfertilized.
CROPS = {
    "WHEAT":      {"kind": "one_time", "seed_cost": 10,  "base_price": 25,
                    "first_yield_day": 2,  "max_yield_day": 4,  "max_yield": 4,
                    "yield_per_tile_day": 0.80},
    "CARROT":     {"kind": "one_time", "seed_cost": 20,  "base_price": 35,
                    "first_yield_day": 2,  "max_yield_day": 3,  "max_yield": 3,
                    "yield_per_tile_day": 0.75},
    "TOMATO":     {"kind": "ongoing",  "seed_cost": 50,  "base_price": 60,
                    "first_yield_day": 8,  "max_yield_day": 11, "interval": 1,
                    "max_scheduled": 4, "yield_per_tile_day": 0.33},
    "STRAWBERRY": {"kind": "ongoing",  "seed_cost": 100, "base_price": 120,
                    "first_yield_day": 10, "max_yield_day": 16, "interval": 2,
                    "max_scheduled": 4, "yield_per_tile_day": 0.24},
    "MELON":      {"kind": "one_time", "seed_cost": 80,  "base_price": 250,
                    "first_yield_day": 10, "max_yield_day": 10, "max_yield": 6,
                    "yield_per_tile_day": 0.55},
}

ANIMALS = {
    "GOOSE": {"product": "EGG",  "cost": 300, "base_price": 50,  "structure": "COOP",
              "first_yield_day": 4, "interval": 1, "max_held": 4},
    "COW":   {"product": "MILK", "cost": 400, "base_price": 160, "structure": "PASTURE",
              "first_yield_day": 8, "interval": 2, "max_held": 6},
    "SHEEP": {"product": "WOOL", "cost": 500, "base_price": 200, "structure": "PASTURE",
              "first_yield_day": 6, "interval": 3, "max_held": 6},
}

LAND_COSTS = [1000, 2000, 4000]  # cost of the 1st/2nd/3rd extra quadrant bought

QUADRANT_ORIGIN = {  # (x, y) of a quadrant's top-left corner, boardSize=10 assumed
    "NW": (0, 0), "NE": (5, 0), "SW": (0, 5), "SE": (5, 5),
}

# Price function params (see competition rules "Price Function" table).
MARKET_PARAMS = {
    "WHEAT":      {"base": 25,  "I0": 10000, "T": 400, "below": "sqrt",   "below_target": 0.80, "above": "log",  "above_target": 0.20},
    "CARROT":     {"base": 35,  "I0": 10000, "T": 450, "below": "log",    "below_target": 0.20, "above": "sqrt", "above_target": 0.70},
    "TOMATO":     {"base": 60,  "I0": 10000, "T": 200, "below": "linear", "below_target": 0.40, "above": "sqrt", "above_target": 0.60},
    "STRAWBERRY": {"base": 120, "I0": 10000, "T": 100, "below": "sqrt",   "below_target": 0.70, "above": "linear", "above_target": 1.60},
    "MELON":      {"base": 250, "I0": 10000, "T": 300, "below": "log",    "below_target": 0.20, "above": "sq",   "above_target": 3.60},
    "EGG":        {"base": 50,  "I0": 10000, "T": 332, "below": "linear", "below_target": 0.40, "above": "log",  "above_target": 0.20},
    "MILK":       {"base": 160, "I0": 10000, "T": 122, "below": "sqrt",   "below_target": 0.60, "above": "linear", "above_target": 1.60},
    "WOOL":       {"base": 200, "I0": 10000, "T": 105, "below": "log",    "below_target": 0.20, "above": "sq",   "above_target": 3.20},
    "FERTILIZER": {"base": 100, "I0": 10000, "T": 200, "below": "linear", "below_target": 0.40, "above": "linear", "above_target": 0.40},
}


def _f(name, x):
    if name == "linear":
        return x
    if name == "sq":
        return x * x
    if name == "sqrt":
        return math.sqrt(x)
    if name == "log":
        return math.log(1 + x)
    if name == "log10":
        return math.log10(1 + x)
    raise ValueError(f"unknown shape fn {name}")


def predicted_price(item, inventory):
    """Replica of the engine's price(inv) formula, used to predict prices
    at hypothetical inventory levels (e.g. 'what will the price be after I
    sell N units') without needing to step the real environment."""
    p = MARKET_PARAMS[item]
    base, i0, t = p["base"], p["I0"], p["T"]
    diff = inventory - i0
    if diff == 0:
        return base
    sign = 1 if diff < 0 else -1
    shape = p["below"] if diff < 0 else p["above"]
    target = p["below_target"] if diff < 0 else p["above_target"]
    f_t = _f(shape, t)
    amp = target * base / f_t if f_t else 0
    price = base + sign * amp * _f(shape, abs(diff))
    return max(1, round(price))


def land_cost(num_quadrants_owned):
    """Cost of the next BUY_LAND purchase, given how many quadrants (incl.
    the free starting NW) are currently owned."""
    idx = num_quadrants_owned - 1
    if idx < 0 or idx >= len(LAND_COSTS):
        return None
    return LAND_COSTS[idx]
