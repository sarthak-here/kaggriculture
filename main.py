"""
Kaggriculture agent — v2: multi-unit (farmer + hired hands), land expansion,
farm-hand hiring. Animals/fertilizer/market-curve-aware selling are still
follow-up passes (see repo README).

Design per STRATEGY.md, scoped to the engine's real per-turn budget
(actTimeout=1s, remainingOverageTime=60s total — kaggriculture.json):
every-turn work here is O(units + tiles), no per-turn search/simulation.

Priority per unit each turn (STRATEGY.md's "never miss" rule comes first):
  1. Harvest if standing on a ready plant
  2. Water if standing on an unwatered plant
  3. Plant the best-ROI affordable crop if standing on an empty tile
  4. Clear a weed if standing on one
  5. Otherwise move toward the nearest unclaimed pending task
Land/hiring are evaluated once per turn against simple ROI/utilization
gates. Selling still dumps the whole shed every turn (task #11 will chunk
this against the price curve instead).
"""
from game_data import CROPS, land_cost

DAYS_LEFT_TO_STOP_PLANTING = 2
DAYS_LEFT_TO_STOP_EXPANDING = 5
TILES_PER_UNIT_TARGET = 4  # rough capacity a single farmer/hand can keep up with


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
    for y, row in enumerate(farm["tiles"]):
        for x, tile in enumerate(row):
            if tile != "LOCKED":
                yield x, y, tile


def best_crop_to_plant(money, market_prices, days_left):
    best, best_score = None, float("-inf")
    for crop, spec in CROPS.items():
        if spec["first_yield_day"] > days_left:
            continue
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


def find_nearest_unclaimed(pos, candidates, claimed):
    options = [c for c in candidates if c not in claimed]
    if not options:
        return None
    return min(options, key=lambda c: manhattan(pos, c))


def held_seed_to_plant(seed_budget):
    """Any seed already sitting in inventory should be planted before
    buying anything new — the 'best crop' recommendation can flicker
    turn to turn as our own sells nudge prices, and re-deriving it at
    plant time (instead of using whatever we already paid for) strands
    money on abandoned seed purchases."""
    held = [(crop, n) for crop, n in seed_budget.items() if n > 0]
    if not held:
        return None
    return max(held, key=lambda c: c[1])[0]


def decide_unit_action(pos, tile, day, seed_budget, plant_crop, liquidating,
                        claimed, needs_harvest, needs_water, empty_tiles, weeds):
    """Returns (op_list, target_claimed_or_None). Mutates `claimed` if a
    target tile is picked for movement (so other units don't also head
    there this turn), and decrements `seed_budget` on a PLANT so a second
    unit standing on another empty tile this same turn doesn't also try
    to plant a seed we've already committed — the engine plants NONE of
    them if two units plant the same under-stocked crop in one turn."""
    if is_plant(tile) and tile["yield_units"] > 0 and \
       (day - tile["planted_day"]) >= CROPS[tile["crop"]]["first_yield_day"]:
        return ["HARVEST"], None

    if is_plant(tile) and not tile["watered_today"]:
        return ["WATER"], None

    if tile is None and not liquidating:
        held = held_seed_to_plant(seed_budget)
        if held is not None:
            seed_budget[held] -= 1
            return ["PLANT", held], None

    if is_weed(tile):
        return ["DIG"], None

    if needs_harvest:
        t = find_nearest_unclaimed(pos, needs_harvest, claimed)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)], t
    if needs_water:
        t = find_nearest_unclaimed(pos, needs_water, claimed)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)], t
    if not liquidating and (held_seed_to_plant(seed_budget) is not None or plant_crop is not None) and empty_tiles:
        t = find_nearest_unclaimed(pos, empty_tiles, claimed)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)], t
    if weeds:
        t = find_nearest_unclaimed(pos, weeds, claimed)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)], t

    return ["PASS"], None


def agent(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    day = obs["day"]
    hour = obs["hour"]
    days_left = 30 - day
    market_prices = obs["market"]["prices"]

    market = []
    hands_actions = []

    liquidating = days_left <= DAYS_LEFT_TO_STOP_PLANTING

    # ---- sell everything currently in the shed ----
    for item, count in private.get("shed", {}).items():
        if count > 0:
            market.append(["SELL", item, count])

    # ---- land expansion: buy the next quadrant if we're using what we have ----
    owned = list(iter_owned_tiles(me))
    num_owned_tiles = len(owned)
    empty_tiles_all = [(x, y) for x, y, t in owned if t is None]
    utilization = 1 - (len(empty_tiles_all) / num_owned_tiles if num_owned_tiles else 1)
    next_land_cost = land_cost(len(me["unlocked_quadrants"]))
    if (next_land_cost is not None and days_left > DAYS_LEFT_TO_STOP_EXPANDING
            and me["money"] > next_land_cost * 2 and utilization > 0.8):
        market.append(["BUY_LAND"])

    # ---- hiring: only worth deciding at the start of the day (a hand
    # hired mid-day still costs the same but works fewer turns) ----
    if hour == 0 and not liquidating:
        max_useful_hands = max(0, num_owned_tiles // TILES_PER_UNIT_TARGET - 1)
        hires_today = me["hires_today"]
        fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
        while hires_today < max_useful_hands:
            idx = min(hires_today, len(fib) - 1)
            hire_cost = fib[idx]
            if me["money"] < hire_cost * 3:
                break
            market.append(["HIRE"])
            hires_today += 1

    # ---- per-unit actions ----
    empty_tiles = list(empty_tiles_all)
    needs_harvest = [
        (x, y) for x, y, t in owned
        if is_plant(t) and t["yield_units"] > 0
        and (day - t["planted_day"]) >= CROPS[t["crop"]]["first_yield_day"]
    ]
    needs_water = [(x, y) for x, y, t in owned if is_plant(t) and not t["watered_today"]]
    weeds = [(x, y) for x, y, t in owned if is_weed(t)]
    plant_crop = best_crop_to_plant(me["money"], market_prices, days_left) if not liquidating else None
    holding_any_seed = held_seed_to_plant(private["seeds"]) is not None
    if plant_crop is not None and not holding_any_seed and me["money"] >= CROPS[plant_crop]["seed_cost"]:
        market.append(["BUY_SEED", plant_crop, 1])

    claimed = set()
    seed_budget = dict(private["seeds"])  # shared, decremented as units commit to planting

    fx, fy = me["farmer"]
    ftile = me["tiles"][fy][fx]
    farmer_ops, _ = decide_unit_action(
        (fx, fy), ftile, day, seed_budget, plant_crop, liquidating,
        claimed, needs_harvest, needs_water, empty_tiles, weeds,
    )
    if ftile is None:
        empty_tiles = [t for t in empty_tiles if t != (fx, fy)]

    for hx, hy in me.get("hands", []):
        htile = me["tiles"][hy][hx]
        ops, _ = decide_unit_action(
            (hx, hy), htile, day, seed_budget, plant_crop, liquidating,
            claimed, needs_harvest, needs_water, empty_tiles, weeds,
        )
        hands_actions.append(ops)

    return {"farmer": farmer_ops, "hands": hands_actions, "market": market}
