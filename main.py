"""
Kaggriculture agent — v1 (single farmer, no hands/animals/land yet).

Design per STRATEGY.md, scoped to what's actually buildable inside the
engine's real constraints (actTimeout=1s/turn, remainingOverageTime=60s
total — see kaggriculture.json): every-turn decisions are O(tiles), no
per-turn simulation/search. Crop choice is ROI-scored from the documented
yield/price constants, not hardcoded to one crop.

Priority order each turn, matching STRATEGY.md's "never miss" rule:
  1. Harvest anything ready (money sitting on the ground)
  2. Water anything unwatered today (missing this turns a plant into a weed)
  3. Plant the best-ROI affordable crop on an empty owned tile
  4. Clear a weed
  5. Move toward the nearest pending task
Selling: everything currently in the shed goes up for sale every turn
(refined later — task #11 will chunk sales against the price curve instead
of dumping it all at once).
Endgame: in the last 2 days, stop planting, just harvest/sell out.
"""
from game_data import CROPS, predicted_price

DAYS_LEFT_TO_STOP_PLANTING = 2


def log(*a):
    import sys
    print(*a, file=sys.stderr)


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def step_toward(pos, target):
    dx = target[0] - pos[0]
    dy = target[1] - pos[1]
    if dx == 0 and dy == 0:
        return "PASS"
    if abs(dx) >= abs(dy):
        return "EAST" if dx > 0 else "WEST"
    return "SOUTH" if dy > 0 else "NORTH"


def is_plant(tile):
    return isinstance(tile, dict) and tile.get("kind") == "PLANT"


def is_weed(tile):
    return isinstance(tile, dict) and tile.get("kind") == "WEED"


def iter_owned_tiles(farm):
    """Yields (x, y, tile) for every unlocked tile on this farm."""
    for y, row in enumerate(farm["tiles"]):
        for x, tile in enumerate(row):
            if tile != "LOCKED":
                yield x, y, tile


def best_crop_to_plant(money, seeds, market_prices, days_left):
    """ROI-scored crop choice: profit per tile per day at current market
    prices, restricted to crops that can complete at least one harvest
    before the season ends and that we can afford."""
    best, best_score = None, float("-inf")
    for crop, spec in CROPS.items():
        if spec["first_yield_day"] > days_left:
            continue  # wouldn't even yield once before the season ends
        if spec["seed_cost"] > money:
            continue
        price = market_prices.get(crop, spec["base_price"])
        occupancy = spec["max_yield_day"]
        total_yield = spec["yield_per_tile_day"] * occupancy
        revenue = total_yield * price
        profit_per_day = (revenue - spec["seed_cost"]) / max(occupancy, 1)
        if profit_per_day > best_score:
            best, best_score = crop, profit_per_day
    return best


def find_nearest(farmer_pos, candidates):
    """candidates: list of (x, y, ...). Returns the closest one, or None."""
    if not candidates:
        return None
    return min(candidates, key=lambda c: manhattan(farmer_pos, (c[0], c[1])))


def agent(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    day = obs["day"]
    days_left = 30 - day

    fx, fy = me["farmer"]
    tile = me["tiles"][fy][fx]

    market = []
    action = {"farmer": ["PASS"], "hands": [], "market": market}

    # ---- selling: dump everything currently in the shed ----
    for item, count in private.get("shed", {}).items():
        if count > 0:
            market.append(["SELL", item, count])

    liquidating = days_left <= DAYS_LEFT_TO_STOP_PLANTING

    # ---- 1. harvest if standing on a ready plant ----
    if is_plant(tile):
        crop = tile["crop"]
        spec = CROPS[crop]
        crop_age = day - tile["planted_day"]
        ready = tile["yield_units"] > 0 and crop_age >= spec["first_yield_day"]
        if ready:
            action["farmer"] = ["HARVEST"]
            return action

    # ---- 2. water if standing on an unwatered plant worth keeping alive ----
    if is_plant(tile) and not tile["watered_today"]:
        action["farmer"] = ["WATER"]
        return action

    # ---- 3. plant on an empty tile if standing on one ----
    if tile is None and not liquidating:
        crop = best_crop_to_plant(me["money"], private["seeds"], obs["market"]["prices"], days_left)
        if crop is not None:
            have_seed = private["seeds"].get(crop, 0) > 0
            if have_seed:
                action["farmer"] = ["PLANT", crop]
                return action
            elif me["money"] >= CROPS[crop]["seed_cost"]:
                market.append(["BUY_SEED", crop, 1])
                # seed won't be usable until next turn once purchased; fall
                # through to movement/other work this turn

    # ---- 4. clear a weed if standing on one ----
    if is_weed(tile):
        action["farmer"] = ["DIG"]
        return action

    # ---- 5. otherwise, move toward the most useful nearby task ----
    owned = list(iter_owned_tiles(me))

    needs_harvest = [
        (x, y) for x, y, t in owned
        if is_plant(t) and t["yield_units"] > 0
        and (day - t["planted_day"]) >= CROPS[t["crop"]]["first_yield_day"]
    ]
    needs_water = [
        (x, y) for x, y, t in owned
        if is_plant(t) and not t["watered_today"]
    ]
    empty_tiles = [(x, y) for x, y, t in owned if t is None]
    weeds = [(x, y) for x, y, t in owned if is_weed(t)]

    target = None
    if needs_harvest:
        target = find_nearest((fx, fy), needs_harvest)
    elif needs_water:
        target = find_nearest((fx, fy), needs_water)
    elif not liquidating and empty_tiles:
        crop = best_crop_to_plant(me["money"], private["seeds"], obs["market"]["prices"], days_left)
        if crop is not None and (private["seeds"].get(crop, 0) > 0 or me["money"] >= CROPS[crop]["seed_cost"]):
            target = find_nearest((fx, fy), empty_tiles)
            if private["seeds"].get(crop, 0) == 0 and me["money"] >= CROPS[crop]["seed_cost"]:
                market.append(["BUY_SEED", crop, 1])
    elif weeds:
        target = find_nearest((fx, fy), weeds)

    if target is not None:
        action["farmer"] = [step_toward((fx, fy), target)]

    return action
