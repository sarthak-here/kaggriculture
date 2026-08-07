"""
Kaggriculture agent — v3: adds animals (coop/pasture, feed/care/harvest,
fertilizer collection) on top of v2's multi-unit crops/land/hiring.

Design per STRATEGY.md, scoped to the engine's real per-turn budget
(actTimeout=1s, remainingOverageTime=60s total — kaggriculture.json):
every-turn work here is O(units + tiles), no per-turn search/simulation.

Key mechanic (verified against the engine source, not just the rules text):
FEED and PLACE consume from the ACTING UNIT'S OWN inventory, not the shed.
So feeding/placing is a two-step, multi-turn dance per unit: stand
shed-adjacent and PICKUP the item into inventory, then walk it to the
animal/structure and act. Both steps are re-derived fresh from the
observation every turn (private["inventories"][i] tells us exactly what
each unit is currently carrying) rather than tracked as separate state.

Priority per unit each turn (STRATEGY.md's "never miss" rule first):
  1. If on an animal tile: harvest ready product > collect fertilizer >
     feed (if carrying wheat) > care
  2. Harvest if standing on a ready plant
  3. Water if standing on an unwatered plant
  4. Pick up wheat/animal from the shed if adjacent and it's needed
  5. Plant the best-ROI affordable crop / build a structure / place an
     animal, whichever applies to the tile we're standing on
  6. Clear a weed
  7. Otherwise move toward the nearest unclaimed pending task
Land/hiring/animal-investment are evaluated once per turn against simple
ROI/utilization gates. Selling still dumps the whole shed every turn
(task #11 will chunk this against the price curve instead).
"""
from game_data import CROPS, ANIMALS, land_cost, sell_quantity

DAYS_LEFT_TO_STOP_PLANTING = 2
DAYS_LEFT_TO_STOP_EXPANDING = 5
DAYS_LEFT_TO_STOP_ANIMAL_INVESTMENT = 8
TILES_PER_UNIT_TARGET = 4  # rough capacity a single farmer/hand can keep up with
MIN_CASH_BUFFER_FOR_ANIMALS = 5000
MIN_OPERATING_CASH_RESERVE = 400  # kept untouched by land purchases, for ongoing seed/operating costs
SHED_CAPACITY = 100  # not exposed in the observation; matches the documented default
SHED_OVERFLOW_SAFETY = 0.85  # above this fraction full, sell regardless of price to avoid discard
MIN_SELL_PRICE_RATIO = 0.7  # don't sell a unit whose marginal price would fall below this fraction of current


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


def is_structure(tile):
    return isinstance(tile, dict) and tile.get("kind") in ("COOP", "PASTURE")


def has_animal(tile):
    return is_structure(tile) and "animal" in tile


def iter_owned_tiles(farm):
    for y, row in enumerate(farm["tiles"]):
        for x, tile in enumerate(row):
            if tile != "LOCKED":
                yield x, y, tile


def shed_adjacent_tiles(board_size):
    half = board_size // 2
    return [(half - 1, half - 1), (half, half - 1), (half - 1, half), (half, half)]


def best_crop_to_plant(money, market_prices, days_left):
    """ROI-scored crop choice at current spot price. (Tried discounting
    this for our own future price impact -- i.e. treating a heavy melon
    commitment as self-crashing melon's price -- since melon scores
    ~6-8x every other crop undiscounted and the competition organizer
    called an undiscounted melon monocrop one of the strongest metas
    seen during balancing. Reverted: local testing (2026-08-07, 3 fixed
    seeds vs starter) showed it net-negative -- melon's price never
    actually dropped much below base in practice, because sell_quantity
    already throttles real selling pressure at the point of sale and
    town consumption keeps draining inventory. The pre-emptive discount
    was strictly more pessimistic than reality and left real value
    on the table. If this becomes a real problem against tougher ladder
    opponents who also compete hard for the melon market, revisit with
    a softer discount informed by real replay data, not a static
    assume-it-all-sells-at-once formula.)"""
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


def best_animal_to_get(money, market_prices, days_left):
    """Steady-state profit/day estimate: production rate * price, minus
    1 wheat/day feed cost, minus (structure + animal cost) amortized over
    the days actually left to produce. Ignores the CARE bonus (upside
    only, keeps the estimate conservative)."""
    wheat_price = market_prices.get("WHEAT", CROPS["WHEAT"]["base_price"])
    best, best_score = None, float("-inf")
    for animal, spec in ANIMALS.items():
        total_cost = spec["cost"] + 200  # +structure cost estimate (coop/pasture has no listed price; treated as bundled capital outlay)
        if total_cost > money:
            continue
        productive_days = days_left - spec["first_yield_day"]
        if productive_days <= spec["interval"] * 2:
            continue  # not enough runway to be worth it
        price = market_prices.get(spec["product"], spec["base_price"])
        revenue = (productive_days / spec["interval"]) * price
        feed_cost = days_left * wheat_price
        profit_per_day = (revenue - feed_cost - total_cost) / days_left
        if profit_per_day > best_score:
            best, best_score = animal, profit_per_day
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


def decide_unit_action(pos, tile, inv, day, seed_budget, plant_crop, liquidating,
                        claimed, needs_harvest, needs_water, empty_tiles, weeds,
                        ctx):
    """Returns op_list. Mutates `claimed`/`seed_budget`/ctx budgets so a
    second unit acting later this same turn doesn't collide with what an
    earlier unit already committed to (the engine silently no-ops or
    fails an over-committed action rather than queuing it)."""
    # ---- animal tile we're standing on ----
    if has_animal(tile):
        if tile["yield_units"] > 0:
            return ["HARVEST"]
        if tile["fertilizer_available"]:
            return ["COLLECT_FERTILIZER"]
        # Feeding only pays off if another scheduled production can still
        # land before the season ends -- otherwise it just burns wheat
        # that's worth more sold. (Cheap approximation: checks the
        # animal's fixed interval, not this instance's exact next
        # production day, but that's enough to catch the true-waste case.)
        days_left = 30 - day
        can_still_produce = days_left >= ANIMALS[tile["animal"]]["interval"]
        if not tile["fed_today"] and inv.get("WHEAT", 0) > 0 and can_still_produce:
            return ["FEED"]
        if not tile["cared_today"] and can_still_produce:
            return ["CARE"]

    if is_plant(tile) and tile["yield_units"] > 0 and \
       (day - tile["planted_day"]) >= CROPS[tile["crop"]]["first_yield_day"]:
        return ["HARVEST"]

    if is_plant(tile) and not tile["watered_today"]:
        return ["WATER"]

    # ---- shed pickups: wheat for feeding, or a purchased animal to place ----
    if pos in ctx["shed_tiles"]:
        if ctx["wheat_pickup_wanted"] > 0 and inv.get("WHEAT", 0) == 0:
            n = min(ctx["wheat_pickup_wanted"], ctx["shed"].get("WHEAT", 0))
            if n > 0:
                ctx["wheat_pickup_wanted"] -= n
                return ["PICKUP", "WHEAT", n]
        if ctx["animal_to_place"] is not None and inv.get(ctx["animal_to_place"], 0) == 0:
            animal = ctx["animal_to_place"]
            if ctx["shed"].get(animal, 0) > 0 and ctx["animal_pickup_claimed"] < ctx["shed"].get(animal, 0):
                ctx["animal_pickup_claimed"] += 1
                return ["PICKUP", animal, 1]

    # ---- place a carried animal on a matching empty structure ----
    if is_structure(tile) and "animal" not in tile and ctx["animal_to_place"] is not None:
        if tile["kind"] == ANIMALS[ctx["animal_to_place"]]["structure"] and inv.get(ctx["animal_to_place"], 0) > 0:
            return ["PLACE", ctx["animal_to_place"]]

    if tile is None and not liquidating:
        if ctx["build_target"] is not None and not ctx["build_committed"]:
            ctx["build_committed"] = True
            return [f"BUILD_{ctx['build_target']}"]
        held = held_seed_to_plant(seed_budget)
        if held is not None:
            seed_budget[held] -= 1
            return ["PLANT", held]

    if is_weed(tile):
        return ["DIG"]

    # ---- movement toward the most useful unclaimed task ----
    if needs_harvest:
        t = find_nearest_unclaimed(pos, needs_harvest, claimed)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    if ctx["animals_need_harvest"]:
        t = find_nearest_unclaimed(pos, ctx["animals_need_harvest"], claimed)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    if ctx["animals_need_fertilizer"]:
        t = find_nearest_unclaimed(pos, ctx["animals_need_fertilizer"], claimed)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    if needs_water:
        t = find_nearest_unclaimed(pos, needs_water, claimed)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    if ctx["animals_need_feed"]:
        if inv.get("WHEAT", 0) > 0:
            t = find_nearest_unclaimed(pos, ctx["animals_need_feed"], claimed)
            if t:
                claimed.add(t)
                return [step_toward(pos, t)]
        elif ctx["wheat_pickup_wanted"] > 0 and ctx["shed"].get("WHEAT", 0) > 0:
            t = find_nearest_unclaimed(pos, ctx["shed_tiles"], claimed)
            if t:
                return [step_toward(pos, t)]  # don't claim a shed tile, others may need it too
    if (ctx["animal_to_place"] is not None and inv.get(ctx["animal_to_place"], 0) > 0
            and ctx["structures_need_animal"]):
        t = find_nearest_unclaimed(pos, ctx["structures_need_animal"], claimed)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    if (ctx["animal_to_place"] is not None and inv.get(ctx["animal_to_place"], 0) == 0
            and ctx["shed"].get(ctx["animal_to_place"], 0) > 0):
        t = find_nearest_unclaimed(pos, ctx["shed_tiles"], claimed)
        if t:
            return [step_toward(pos, t)]
    if not liquidating and (held_seed_to_plant(seed_budget) is not None or plant_crop is not None
                             or (ctx["build_target"] is not None and not ctx["build_committed"])) and empty_tiles:
        t = find_nearest_unclaimed(pos, empty_tiles, claimed)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    if ctx["animals_need_care"]:
        t = find_nearest_unclaimed(pos, ctx["animals_need_care"], claimed)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    if weeds:
        t = find_nearest_unclaimed(pos, weeds, claimed)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]

    return ["PASS"]


def owned_structure_kind(me, pos):
    x, y = pos
    tile = me["tiles"][y][x]
    return tile.get("kind") if isinstance(tile, dict) else None


def agent(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    day = obs["day"]
    hour = obs["hour"]
    days_left = 30 - day
    market_prices = obs["market"]["prices"]
    board_size = len(me["tiles"])

    market = []
    hands_actions = []

    liquidating = days_left <= DAYS_LEFT_TO_STOP_PLANTING

    # ---- sell shed inventory, chunked against the price curve ----
    # Dumping everything at once craters premium goods (strawberry/melon/
    # milk/wool all have above_target > 1, crashing to the $1 floor fast on
    # a glut). Hold back whatever would sell for materially less than the
    # current price; it carries over and gets re-priced next turn as town
    # consumption drains market inventory back down. In the endgame or when
    # the shed is close to overflowing (capped at 100, excess discarded),
    # sell everything regardless — a held unit that never sells is worth $0.
    shed = private.get("shed", {})
    shed_total = sum(shed.values())
    force_sell_all = liquidating or shed_total >= SHED_CAPACITY * SHED_OVERFLOW_SAFETY
    market_inventory = obs["market"]["inventory"]
    for item, count in shed.items():
        if count <= 0:
            continue
        n = count if force_sell_all else sell_quantity(item, count, market_inventory.get(item, 10000), MIN_SELL_PRICE_RATIO)
        if n > 0:
            market.append(["SELL", item, n])

    # ---- land expansion: buy the next quadrant as soon as affordable ----
    # Used to gate this on utilization > 0.8 (only expand once already
    # tile-constrained) plus a 2x cash buffer. A real ranked match (episode
    # 90596561, 2026-08-07) showed this is badly too conservative: the
    # opponent bought all 4 quadrants by ~day 10 despite having very little
    # cash margin, while we crawled to 3 quadrants and never got the 4th at
    # all (blocked by our own DAYS_LEFT_TO_STOP_EXPANDING cutoff, having
    # waited too long). Their money pulled decisively ahead from day 18 on
    # (67k vs our 21k by day 28) -- more land is production capacity that
    # compounds over the remaining season, so it's worth buying proactively
    # ahead of need, not reactively once already full.
    #
    # But buying land alone isn't the whole story: a real match (episode
    # 90598933, 2026-08-07) showed the opposite failure mode when this
    # collides with an aggressive melon opening. Melon (the ROI-best crop
    # by a wide margin) takes 10 days to first yield, and this agent plants
    # every empty tile it can afford on sight -- so a fast start can dump
    # most of the starting $3000 into ~20 melon seeds within the first two
    # days. If land purchases then eat whatever cash is left over that same
    # window, money can get pinned near $0 for 10+ days straight (that
    # match: money oscillated $0-$334 from day 2 to day 22) with zero
    # operating cushion -- unable to hire, fertilize, or recover from bad
    # luck, even though the eventual harvest is coming. A MIN_OPERATING_CASH
    # reserve on top of the land cost itself keeps land purchases from
    # competing with the crop cycle's own cash needs during that gap.
    owned = list(iter_owned_tiles(me))
    num_owned_tiles = len(owned)
    empty_tiles_all = [(x, y) for x, y, t in owned if t is None]
    next_land_cost = land_cost(len(me["unlocked_quadrants"]))
    if (next_land_cost is not None and days_left > DAYS_LEFT_TO_STOP_EXPANDING
            and me["money"] > next_land_cost * 1.3 + MIN_OPERATING_CASH_RESERVE):
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

    # ---- animal task lists ----
    # Skip animals that can't produce again before the season ends --
    # feeding them would just burn wheat worth more sold.
    animals_need_feed = [
        (x, y) for x, y, t in owned
        if has_animal(t) and not t["fed_today"] and days_left >= ANIMALS[t["animal"]]["interval"]
    ]
    animals_need_harvest = [(x, y) for x, y, t in owned if has_animal(t) and t["yield_units"] > 0]
    animals_need_fertilizer = [(x, y) for x, y, t in owned if has_animal(t) and t["fertilizer_available"]]
    animals_need_care = [(x, y) for x, y, t in owned if has_animal(t) and not t["cared_today"]]
    structures_need_animal = [(x, y) for x, y, t in owned if is_structure(t) and "animal" not in t]
    animal_count = sum(1 for _, _, t in owned if has_animal(t))

    # top up wheat for feeding if we're running low relative to how many mouths we have.
    # Not once liquidating: buying wheat only to feed animals that won't get
    # another chance to produce before the season ends is pure waste --
    # that money is worth more banked (or that wheat worth more sold).
    shed_wheat = private.get("shed", {}).get("WHEAT", 0)
    if not liquidating and animal_count > 0 and shed_wheat < animal_count and me["money"] >= market_prices.get("WHEAT", 25):
        market.append(["BUY_PRODUCT", "WHEAT", animal_count - shed_wheat])

    # ---- decide whether to invest in a new animal this turn ----
    animal_to_place = None
    build_target = None
    if (not liquidating and days_left > DAYS_LEFT_TO_STOP_ANIMAL_INVESTMENT
            and me["money"] > MIN_CASH_BUFFER_FOR_ANIMALS and empty_tiles_all and not structures_need_animal):
        animal = best_animal_to_get(me["money"], market_prices, days_left)
        if animal is not None:
            build_target = ANIMALS[animal]["structure"]
    if structures_need_animal:
        # finish placing whatever the existing empty structure expects.
        # A structure is shared by 1-2 animal types (COOP->GOOSE only,
        # PASTURE->COW or SHEEP); tie-break PASTURE to COW consistently.
        structure_kind = owned_structure_kind(me, structures_need_animal[0])
        animal = next(a for a, spec in ANIMALS.items() if spec["structure"] == structure_kind)
        animal_to_place = animal
        # Check total held (shed + whatever a unit is already carrying
        # toward the structure), not just the shed: a picked-up animal
        # spends several turns in transit with shed count back at 0,
        # which would otherwise trigger a fresh BUY_ANIMAL every turn
        # along the way.
        carried = sum(inv.get(animal, 0) for inv in private.get("inventories", []))
        total_held = private.get("shed", {}).get(animal, 0) + carried
        if total_held == 0 and me["money"] >= ANIMALS[animal]["cost"]:
            market.append(["BUY_ANIMAL", animal, 1])

    # ---- per-unit actions ----
    empty_tiles = list(empty_tiles_all)
    needs_harvest = [
        (x, y) for x, y, t in owned
        if is_plant(t) and t["yield_units"] > 0
        and (day - t["planted_day"]) >= CROPS[t["crop"]]["first_yield_day"]
    ]
    needs_water = [(x, y) for x, y, t in owned if is_plant(t) and not t["watered_today"]]
    weeds = [(x, y) for x, y, t in owned if is_weed(t)]
    plant_crop = best_crop_to_plant(me["money"], market_prices, days_left) if (not liquidating and build_target is None) else None
    holding_any_seed = held_seed_to_plant(private["seeds"]) is not None
    if plant_crop is not None and not holding_any_seed and me["money"] >= CROPS[plant_crop]["seed_cost"]:
        market.append(["BUY_SEED", plant_crop, 1])

    claimed = set()
    seed_budget = dict(private["seeds"])  # shared, decremented as units commit to planting
    ctx = {
        "shed": private.get("shed", {}),
        "shed_tiles": shed_adjacent_tiles(board_size),
        "animals_need_feed": animals_need_feed,
        "animals_need_harvest": animals_need_harvest,
        "animals_need_fertilizer": animals_need_fertilizer,
        "animals_need_care": animals_need_care,
        "structures_need_animal": structures_need_animal,
        "wheat_pickup_wanted": len(animals_need_feed),
        "animal_to_place": animal_to_place,
        "animal_pickup_claimed": 0,
        "build_target": build_target,
        "build_committed": False,
    }

    units = [(me["farmer"], private["inventories"][0])]
    for i, (hx, hy) in enumerate(me.get("hands", [])):
        units.append(((hx, hy), private["inventories"][i + 1] if i + 1 < len(private["inventories"]) else {}))

    all_ops = []
    for (ux, uy), inv in units:
        utile = me["tiles"][uy][ux]
        ops = decide_unit_action(
            (ux, uy), utile, inv, day, seed_budget, plant_crop, liquidating,
            claimed, needs_harvest, needs_water, empty_tiles, weeds, ctx,
        )
        if utile is None and (ux, uy) in empty_tiles:
            empty_tiles.remove((ux, uy))
        all_ops.append(ops)

    farmer_ops = all_ops[0]
    hands_actions = all_ops[1:]

    return {"farmer": farmer_ops, "hands": hands_actions, "market": market}
