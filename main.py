"""
Kaggriculture agent — v8: rebuilt around real top-player replay diagnostics
(2026-08-07), not the v1-v7 spot-price/single-product ROI model.

Four findings from mining top-5-leaderboard replays (episode analysis, not
guesswork) drove this rewrite:

1. The animal CARE bonus is the dominant lever, and it's an entire mechanic
   v1-v7 never modeled. Per the engine source (kaggriculture.py): CARE only
   builds pending_care_bonus on a day where the animal is BOTH cared_today
   AND fed_today; at each production checkpoint (every `interval` days) it
   yields base(1) + bonus, then the bonus resets to 0 unconditionally --
   missing FEED specifically on the checkpoint day forfeits the whole
   accumulated bonus. Disciplined daily feed+care gets a steady-state rate
   of (1+interval)/interval products/day (game_data.animal_daily_rate) --
   e.g. ~1.5 milk/day per cow, not the ~0.5/day the old ROI table assumed.
   This alone made animals look net-negative until days_left~18-19 when
   they're actually profitable from turn 1.
2. Market orders take a quantity arg (BUY_SEED/BUY_ANIMAL/BUY_PRODUCT/SELL;
   NOT HIRE, which is atomic). maxMarketOrdersPerTurn=10 caps ORDER LINES,
   not items, so one BUY_ANIMAL COW 4 line buys 4 cows. The old code always
   bought qty=1 and never modeled the 10-line budget explicitly, so SELL
   lines (one per shed item, up to 9 possible) could silently starve
   HIRE/BUY_* lines queued after them once the shed diversified.
3. Hiring isn't capped near 10 hands. fib(n) cost is uncapped (fib(13)=377,
   still cheap against a $50k+ economy); top players hire ~14/day, spread
   across a turn's 10-line order budget over a few hours each morning as
   cash allows.
4. Melon is a short-lived bridge, not a monocrop: its glut side is the
   steepest curve in the game (above_target=3.60, quadratic) and two
   players both leaning on it crashes it hard in real matches. Strawberry
   (ongoing, gentler glut curve) is the real scale crop. Winning players
   also stop expanding at 3 quadrants (skip the $4000 4th) and use the
   freed cash for hands/animals instead, and treat fertilizer collection
   as a real revenue line (sell what isn't used to fertilize crops).

Kept from v7 (still correct, re-verified against engine source this pass):
FEED/PLACE consume from the acting unit's own carried inventory, not the
shed -- pickup-then-walk-then-act is still a real multi-turn dance. Crops
DO decay (yield_units drains, then reverts to WEED) if left unharvested
past max_lifespan_step, so harvest still can't be deprioritized the way
animal harvest can (animal yield_units has no decay, only a max_held cap
-- confirmed absent from the engine's plant-only _decay_plants). Endgame
liquidation (dump everything, stop new investment) still applies as
`liquidating`.

Scoped to the engine's real per-turn budget (actTimeout=1s,
remainingOverageTime=60s total) -- everything here is O(units + tiles),
no per-turn search/simulation.
"""
from game_data import CROPS, ANIMALS, land_cost, sell_quantity, animal_daily_rate

# Everything sellable via the shed except WHEAT: a unit's carried WHEAT is
# ambiguous (harvested wheat to sell vs. wheat fetched for a feed round
# trip), so it's left alone and only ever reaches the shed via the normal
# end-of-day auto-drop or an explicit FEED.
SELLABLE_PRODUCTS = (set(CROPS) - {"WHEAT"}) | {spec["product"] for spec in ANIMALS.values()} | {"FERTILIZER"}

DAYS_LEFT_TO_STOP_PLANTING = 2
DAYS_LEFT_TO_STOP_EXPANDING = 5
DAYS_LEFT_TO_STOP_ANIMAL_INVESTMENT = 5
MAX_QUADRANTS = 3  # winning replays never buy the 4th (SE, $4000) -- 3 quadrants + hands/animals beats more idle land
EXPAND_WHEN_EMPTY_TILES_BELOW = 4  # buy the next quadrant only once land, not cash, is the binding constraint
MAX_MELON_TILES = 12  # melon is a bridge crop (fastest early cash) -- real matches show its glut crashes hard once both players lean on it
TILES_PER_UNIT_TARGET = 4  # rough crop-tile capacity a single farmer/hand can keep up with
ANIMAL_TILES_PER_UNIT = 3  # each animal needs a near-daily feed+care round trip -- roughly 3 animals is a hand's worth of upkeep
MAX_ANIMAL_BUYS_PER_TURN = 8  # bound a single turn's investment burst so it can't blow the whole bank in one shot
MAX_UNHOUSED_PER_SPECIES = 4  # don't buy an animal type faster than structures can be built for it
MAX_TOTAL_ANIMALS = 12  # hard population cap -- local testing showed the per-species/staffing gates alone still let the herd run to 19+ structures on a 75-tile farm, consuming 100% of realistic hand capacity on animal upkeep alone and starving crops down to ~10-20 tiles for the whole game
MAX_MARKET_ORDERS = 10  # engine hard cap: maxMarketOrdersPerTurn, shared across every order type
MIN_OPERATING_CASH_RESERVE = 400  # kept untouched by investment purchases, for ongoing seed/operating costs
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


def best_crop_to_plant(money, market_prices, days_left, melon_tile_count):
    """ROI-scored crop choice at current spot price. Melon is excluded once
    MAX_MELON_TILES is reached -- undiscounted it scores far above every
    other crop, which is exactly the monocrop trap real replays show
    crashing melon's price once both players lean on it (its glut curve is
    quadratic, the steepest in the game)."""
    best, best_score = None, float("-inf")
    for crop, spec in CROPS.items():
        if crop == "MELON" and melon_tile_count >= MAX_MELON_TILES:
            continue
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


def rank_animals_to_buy(money, market_prices, days_left):
    """Profitable animals, best profit/day first, using the real
    steady-state care-bonus rate (see game_data.animal_daily_rate) instead
    of the old naive '1 product per interval' assumption. That old
    assumption made every animal look unprofitable until days_left~18-19;
    the real rate makes them profitable almost immediately, matching real
    replays that buy multiple animals turn 1 with starting cash."""
    wheat_price = market_prices.get("WHEAT", CROPS["WHEAT"]["base_price"])
    fert_price = market_prices.get("FERTILIZER", 100)
    ranked = []
    for animal, spec in ANIMALS.items():
        if spec["cost"] > money:
            continue
        productive_days = days_left - spec["first_yield_day"]
        if productive_days <= 0:
            continue
        rate = animal_daily_rate(animal)
        price = market_prices.get(spec["product"], spec["base_price"])
        # Fertilizer credit: every surviving animal drops ~1 fertilizer/day,
        # sellable -- offsets most or all of the feed cost below.
        daily_revenue = rate * price + fert_price * 0.8
        daily_feed_cost = wheat_price  # 1 wheat/day, required for the care bonus itself
        # The animal eats from the day it's placed, not from first yield --
        # first_yield_day days of pre-yield feed (plus ~1 day of buy ->
        # pickup -> place logistics lag) is real spend the amortized-cost
        # term below must also cover, not just the purchase price.
        daily_amortized_cost = (spec["cost"] + wheat_price * (spec["first_yield_day"] + 1)) / productive_days
        profit_per_day = daily_revenue - daily_feed_cost - daily_amortized_cost
        if profit_per_day > 0:
            ranked.append((animal, profit_per_day))
    ranked.sort(key=lambda t: -t[1])
    return [a for a, _ in ranked]


def find_nearest_unclaimed(pos, candidates, claimed):
    """Nearest unclaimed candidate to `pos`, by squared Euclidean distance
    (Manhattan ties constantly on a grid and min() breaks ties by iteration
    order, which reads as units drifting toward one corner)."""
    options = [c for c in candidates if c not in claimed]
    if not options:
        return None
    return min(options, key=lambda c: (pos[0] - c[0]) ** 2 + (pos[1] - c[1]) ** 2)


def find_best_build_site_unclaimed(candidates, claimed, shed_center):
    """Pick an empty tile for a new animal structure by proximity to the
    shed, not to whichever unit happens to be routing there -- feeding is a
    daily round trip (shed -> animal -> shed) for the rest of the season,
    so distance from the shed is a recurring cost, unlike the one-off walk
    to go build it."""
    options = [c for c in candidates if c not in claimed]
    if not options:
        return None
    return min(options, key=lambda c: (shed_center[0] - c[0]) ** 2 + (shed_center[1] - c[1]) ** 2)


def held_seed_to_plant(seed_budget):
    """Any seed already sitting in inventory should be planted before
    buying anything new -- the 'best crop' recommendation can flicker turn
    to turn as our own sells nudge prices, and re-deriving it at plant time
    (instead of using whatever we already paid for) strands money on
    abandoned seed purchases."""
    held = [(crop, n) for crop, n in seed_budget.items() if n > 0]
    if not held:
        return None
    return max(held, key=lambda c: c[1])[0]


def decide_unit_action(pos, tile, inv, day, hour, final_day, seed_budget, plant_crop, liquidating,
                        claimed, needs_harvest, needs_water, empty_tiles, weeds,
                        ctx):
    """Returns op_list. Mutates `claimed`/`seed_budget`/ctx budgets so a
    second unit acting later this same turn doesn't collide with what an
    earlier unit already committed to (the engine silently no-ops or fails
    an over-committed action rather than queuing it)."""
    # WHEAT is normally excluded from flush/haul (ambiguous: harvested-to-
    # sell vs fetched-for-feed) -- but once liquidating, FEED is disabled
    # entirely (see the animal-tile branch below), so any carried WHEAT is
    # unambiguously sellable, and stranding it uncounted would leave real
    # money on the table with no offsetting benefit.
    flush_items = SELLABLE_PRODUCTS | {"WHEAT"} if liquidating else SELLABLE_PRODUCTS

    # ---- animal tile we're standing on ----
    # Not gated on "can this animal still produce again" -- feeding is
    # cheap (~$25-50) and the CARE bonus (game_data.animal_daily_rate) only
    # accrues on days the animal is BOTH fed AND cared, so missing a day
    # for a marginal runway saving forfeits far more than it saves.
    if has_animal(tile):
        if tile["yield_units"] > 0:
            return ["HARVEST"]
        if tile["fertilizer_available"]:
            return ["COLLECT_FERTILIZER"]
        if not tile["fed_today"] and inv.get("WHEAT", 0) > 0 and not liquidating:
            return ["FEED"]
        if not tile["cared_today"] and not liquidating:
            return ["CARE"]

    # Crops (unlike animals) decay once ready and left unharvested --
    # yield_units drains and the tile reverts to WEED -- so harvest still
    # can't be deprioritized below animal upkeep the way animal-harvest can.
    if is_plant(tile) and tile["yield_units"] > 0 and \
       (day - tile["planted_day"]) >= CROPS[tile["crop"]]["first_yield_day"]:
        return ["HARVEST"]

    # ---- final-day haul-home: SELL only sells shed contents, and unit
    # inventories only auto-drop at day rollover -- there's no rollover
    # after day 29, so anything harvested on the final day that isn't hand-
    # carried to the shed and PLACEd is worth exactly $0. Before the
    # deadline (last possible turn to still make it back), keep working
    # normally -- a harvest it can't deliver is worthless, but hauling too
    # early wastes turns that could still harvest something nearby.
    if final_day:
        carried_sellable = any(inv.get(item, 0) > 0 for item in flush_items)
        if carried_sellable:
            nearest_shed = min(ctx["shed_tiles"], key=lambda t: manhattan(pos, t))
            if hour + manhattan(pos, nearest_shed) >= 22:
                if pos in ctx["shed_tiles"]:
                    for item in flush_items:
                        n = inv.get(item, 0)
                        if n > 0:
                            return ["PLACE", item, n]
                else:
                    return [step_toward(pos, nearest_shed)]

    if is_plant(tile) and not tile["watered_today"]:
        return ["WATER"]

    # Opportunistic fertilize: only on a tile already watered today (never
    # delay watering for this) and not already covered, using carried
    # fertilizer. Doubles that tile's next watering yield for ~2 days.
    if (is_plant(tile) and tile["watered_today"] and inv.get("FERTILIZER", 0) > 0
            and tile.get("fertilized_until_day", -1) < day + 1):
        return ["FERTILIZE"]

    # ---- place a carried animal on any compatible empty structure ----
    # PASTURE accepts COW or SHEEP, COOP only GOOSE -- no need to
    # pre-assign a structure to a specific species, any match works.
    if is_structure(tile) and "animal" not in tile:
        for animal in ANIMALS:
            if ANIMALS[animal]["structure"] == tile["kind"] and inv.get(animal, 0) > 0:
                return ["PLACE", animal]

    # ---- shed pickups: wheat/fertilizer for the round trip, or a
    # purchased animal with a home slot waiting ----
    if pos in ctx["shed_tiles"]:
        if ctx["wheat_pickup_wanted"] > 0 and inv.get("WHEAT", 0) == 0:
            n = min(ctx["wheat_pickup_wanted"], ctx["shed"].get("WHEAT", 0))
            if n > 0:
                ctx["wheat_pickup_wanted"] -= n
                return ["PICKUP", "WHEAT", n]
        if ctx["fert_pickup_wanted"] > 0 and inv.get("FERTILIZER", 0) == 0:
            n = min(ctx["fert_pickup_wanted"], ctx["shed"].get("FERTILIZER", 0))
            if n > 0:
                ctx["fert_pickup_wanted"] -= n
                return ["PICKUP", "FERTILIZER", n]
        for animal in ctx["pickup_priority"]:
            kind = ANIMALS[animal]["structure"]
            if (inv.get(animal, 0) == 0 and ctx["shed"].get(animal, 0) > 0
                    and ctx["home_slots"].get(kind, 0) > 0):
                ctx["home_slots"][kind] -= 1
                return ["PICKUP", animal, 1]
        # Mid-day flush: harvested products otherwise sit unsellable in a
        # unit's inventory until the end-of-day auto-drop, lagging sales by
        # up to half a day. Uses PLACE <item> n (per product), never DROP --
        # DROP empties the whole inventory, which would dump WHEAT a unit
        # is carrying out to feed an animal, undoing that round trip
        # mid-mission. Carried FERTILIZER is only flushed once nothing else
        # still wants to pick more up (ctx["fert_pickup_wanted"] spent) --
        # otherwise this could flush fertilizer one unit just fetched for
        # fertilizing right back into the shed.
        for item in flush_items:
            if item == "FERTILIZER" and ctx["fert_pickup_wanted"] > 0:
                continue
            n = inv.get(item, 0)
            if n > 0:
                return ["PLACE", item, n]

    if tile is None and not liquidating:
        for kind in ("PASTURE", "COOP"):
            if ctx["build_wanted"].get(kind, 0) > 0:
                ctx["build_wanted"][kind] -= 1
                return [f"BUILD_{kind}"]
        # A fresh seed starts at consecutive_unwatered=1 (no grace period
        # per the rules doc) -- planted on the day's last turn with no
        # chance to water before rollover, it's a guaranteed weed by
        # morning: seed cost lost, plus a DIG later. Hour 22 is still fine
        # (the unit is standing right on it; next turn's on-tile WATER
        # branch above fires deterministically before anything else can
        # claim the unit). Seed buying itself stays ungated -- seeds keep
        # overnight, only the act of planting is time-sensitive.
        if hour < 23:
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
    # Animal upkeep (harvest/fertilizer/feed/care), merged into one
    # high-priority category -- this used to rank behind crop watering and
    # weeding, which is exactly why the care bonus rarely accrued: with
    # limited hands, anything else pending always won the priority fight.
    if ctx["animals_need_visit"]:
        # A unit not carrying wheat can't actually FEED, so don't send it
        # to a tile whose only outstanding need is feed -- it would arrive,
        # find nothing else to do (CARE/HARVEST/fertilizer already done),
        # and waste the trip. Leave those for a wheat-carrying unit.
        candidates = ctx["animals_need_visit"]
        if inv.get("WHEAT", 0) == 0 and ctx["feed_only"]:
            candidates = [c for c in candidates if c not in ctx["feed_only"]]
        t = find_nearest_unclaimed(pos, candidates, claimed)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    # Carrying an animal with nowhere placed yet -- deliver it before
    # picking up any new task; it's dead weight in inventory otherwise.
    for animal in ANIMALS:
        if inv.get(animal, 0) > 0:
            kind = ANIMALS[animal]["structure"]
            t = find_nearest_unclaimed(pos, ctx["structures_need_animal"].get(kind, []), claimed)
            if t:
                claimed.add(t)
                return [step_toward(pos, t)]
            break
    if needs_water:
        t = find_nearest_unclaimed(pos, needs_water, claimed)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    if ctx["animals_need_feed_no_wheat"] and ctx["wheat_pickup_wanted"] > 0 and ctx["shed"].get("WHEAT", 0) > 0:
        t = find_nearest_unclaimed(pos, ctx["shed_tiles"], claimed)
        if t:
            return [step_toward(pos, t)]  # don't claim a shed tile, others may need it too
    # Weeds block land use for as long as they sit there -- moved above
    # planting/building so they get regular attention instead of being
    # starved out in the late game (spotted directly from watching a
    # replay: money growth visibly slows turn ~500-720 while opponents'
    # farms stay clear).
    if weeds:
        t = find_nearest_unclaimed(pos, weeds, claimed)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    if not liquidating and any(n > 0 for n in ctx["build_wanted"].values()) and empty_tiles:
        t = find_best_build_site_unclaimed(empty_tiles, claimed, ctx["shed_center"])
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    if not liquidating and (held_seed_to_plant(seed_budget) is not None or plant_crop is not None) and empty_tiles:
        t = find_nearest_unclaimed(pos, empty_tiles, claimed)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]

    return ["PASS"]


def _fib(n):
    """Matches the engine's hire-cost fib exactly: fib(0)=1, fib(1)=1,
    fib(2)=2, ... uncapped (fib(13)=377) -- still cheap against a $50k+
    economy, which is why top players hire to ~14/day instead of stopping
    at a $55 (index-9) self-imposed ceiling."""
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def agent(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    day = obs["day"]
    hour = obs["hour"]
    days_left = 30 - day
    market_prices = obs["market"]["prices"]
    board_size = len(me["tiles"])

    liquidating = days_left <= DAYS_LEFT_TO_STOP_PLANTING
    final_day = days_left <= 1

    owned = list(iter_owned_tiles(me))
    num_owned_tiles = len(owned)
    empty_tiles_all = [(x, y) for x, y, t in owned if t is None]
    shed = private.get("shed", {})
    inventories = private.get("inventories", [])

    def total_held(item):
        return shed.get(item, 0) + sum(inv.get(item, 0) for inv in inventories)

    # ---- sell shed inventory, chunked against the price curve ----
    # Dumping everything at once craters premium goods (strawberry/melon/
    # milk/wool all have above_target > 1, crashing to the $1 floor fast on
    # a glut). Hold back whatever would sell for materially less than the
    # current price; it carries over and gets re-priced next turn. In the
    # endgame or near shed overflow (capped at 100, excess discarded), sell
    # everything regardless -- a held unit that never sells is worth $0.
    shed_total = sum(shed.values())
    force_sell_all = liquidating or shed_total >= SHED_CAPACITY * SHED_OVERFLOW_SAFETY
    market_inventory = obs["market"]["inventory"]
    animal_count = sum(1 for _, _, t in owned if has_animal(t))
    orders_sell = []
    for item, count in shed.items():
        if count <= 0:
            continue
        # Animals can end up sitting in the shed between BUY_ANIMAL and
        # PICKUP (waiting on a structure). They aren't in PRODUCTS -- the
        # engine's SELL quoting silently drops an order for them -- but the
        # old shed.items() loop iterated everything and queued one anyway,
        # burning an order-line slot for nothing every turn an animal
        # waited in shed (confirmed via Fable's diff of a real v6 loss:
        # 'agent SELLs cows' in the action log, right after BUY_ANIMAL).
        if item in ANIMALS:
            continue
        sellable = count
        if item == "WHEAT" and not liquidating:
            # Reserve enough wheat to feed today's animals before selling
            # any surplus. Without this, a day with animal_count > 0 will
            # BUY_PRODUCT WHEAT to restock feed, then the very next turn
            # this loop sees shed wheat again and SELLs it (price still
            # looks sellable), then next turn buys it back again --
            # confirmed in local testing: WHEAT flip-flopped BUY/SELL every
            # single turn on day 2, bleeding money on the spread each round
            # trip for no gain, since the price impact of a buy+sell of the
            # same unit nets negative.
            sellable = max(0, count - animal_count)
        n = sellable if force_sell_all else sell_quantity(item, sellable, market_inventory.get(item, 10000), MIN_SELL_PRICE_RATIO)
        if n > 0:
            value = n * market_prices.get(item, 0)
            orders_sell.append((value, ["SELL", item, n]))
    orders_sell.sort(key=lambda t: -t[0])  # protect the highest-value sells if the order budget gets tight
    orders_sell = [o for _, o in orders_sell]

    # ---- animal task lists ----
    animals_need_feed = [(x, y) for x, y, t in owned if has_animal(t) and not t["fed_today"]]
    animals_need_feed_no_wheat = bool(animals_need_feed)
    animals_need_harvest = [(x, y) for x, y, t in owned if has_animal(t) and t["yield_units"] > 0]
    animals_need_fertilizer = [(x, y) for x, y, t in owned if has_animal(t) and t["fertilizer_available"]]
    animals_need_care = [(x, y) for x, y, t in owned if has_animal(t) and not t["cared_today"]]
    animals_need_visit = list(set(animals_need_harvest) | set(animals_need_fertilizer)
                               | set(animals_need_feed) | set(animals_need_care))
    other_needs = set(animals_need_harvest) | set(animals_need_fertilizer) | set(animals_need_care)
    feed_only = set(animals_need_feed) - other_needs
    structures_need_animal = {"PASTURE": [], "COOP": []}
    for x, y, t in owned:
        if is_structure(t) and "animal" not in t:
            structures_need_animal[t["kind"]].append((x, y))

    # top up wheat for feeding (not once liquidating -- new production
    # won't land in time, so unspent wheat is worth more sold than fed).
    shed_wheat = shed.get("WHEAT", 0)
    orders_wheat = []
    if not liquidating and animal_count > 0 and shed_wheat < animal_count and me["money"] >= market_prices.get("WHEAT", 25):
        orders_wheat.append(["BUY_PRODUCT", "WHEAT", animal_count - shed_wheat])

    # ---- hiring, phase 1: guarantee minimum staffing for the EXISTING
    # herd before spending anything on MORE animals. `hands` is wiped to
    # [] on every day rollover (confirmed in the engine source) -- every
    # hand is a fresh re-hire every single day. Local testing exposed a
    # death spiral: animal investment used to claim cash before hiring, so
    # on any day cash was tight, hands stayed at 0 -- with 0 hands, an
    # 18-animal herd gets fed by no one, escapes en masse after 2 missed
    # days, and the whole investment (and the cash spent on it) is lost.
    # Existing animals must be able to eat before new ones get bought.
    HIRE_MIN_RESERVE = 2
    active_tiles = num_owned_tiles - len(empty_tiles_all)
    animal_workload = sum(1 for _, _, t in owned if is_structure(t))
    min_hands_for_upkeep = 0 if liquidating else -(-animal_workload // ANIMAL_TILES_PER_UNIT)  # ceil div
    orders_hire = []
    hires_today = me["hires_today"]
    money_left = me["money"]
    if not liquidating:
        while hires_today < min_hands_for_upkeep:
            hire_cost = _fib(hires_today)
            if money_left < hire_cost + HIRE_MIN_RESERVE:
                break
            orders_hire.append(["HIRE"])
            money_left -= hire_cost
            hires_today += 1

    # ---- land expansion: buy up to 3 quadrants total, skip the 4th ----
    # Real matches consistently stop at 3 quadrants (never buy the $4000
    # SE) and redirect that cash to hands/animals instead. Budgeted off
    # money_left (net of phase-1 hiring), not raw me["money"] -- otherwise
    # this and the animal-investment budget below both claim the same cash
    # in the same turn (worst case: turn 1, $3000 passes the land check at
    # $1700, queues a $1000 BUY_LAND, then animal investment separately
    # budgets ~$2600 of that same $3000 -- ~$3600 committed against a $3000
    # bank, and which order the engine actually funds isn't something this
    # code controls). Also requires day >= 1: the real meta doesn't buy
    # land turn 1 either -- it goes all-in on animals+seeds and buys Q2/Q3
    # a week-plus in, funded from revenue, not starting cash. Buying land
    # turn 1 recreates the exact land-vs-opening liquidity crunch this
    # project already diagnosed once (a real match loss, documented above).
    # Also requires empty tiles to actually be scarce (<= EXPAND_WHEN_EMPTY_
    # TILES_BELOW): a cash-only gate fires as soon as a couple of good
    # sells push money over the threshold, regardless of whether the
    # CURRENT quadrant is even full yet -- land is only worth buying once
    # tiles, not cash, are the binding constraint. This is the honest
    # version of the old utilization gate: instead of a fuzzy "0.8 used"
    # threshold, it measures the thing that actually matters directly, and
    # naturally reproduces the meta's observed Q2~day7/Q3~day11 timing.
    orders_land = []
    next_land_cost = land_cost(len(me["unlocked_quadrants"]))
    if (next_land_cost is not None and len(me["unlocked_quadrants"]) < MAX_QUADRANTS
            and day >= 1 and days_left > DAYS_LEFT_TO_STOP_EXPANDING
            and len(empty_tiles_all) <= EXPAND_WHEN_EMPTY_TILES_BELOW
            and money_left > next_land_cost * 1.3 + MIN_OPERATING_CASH_RESERVE):
        orders_land.append(["BUY_LAND"])
        money_left -= next_land_cost

    # ---- animal investment: round-robin the ranked list, buying 1 of the
    # best-still-affordable species at a time until cash/per-turn caps
    # bite. This naturally diversifies (each pass buys a different
    # species) and is self-limiting turn to turn since spent cash is
    # reflected in next turn's `money` -- no persistent state needed.
    # Only gated by MAX_UNHOUSED_PER_SPECIES (don't buy an animal type
    # faster than structures can be built for it) -- NOT by empty land,
    # since by mid-game most land is already crops and an animal bought
    # ahead of its structure just waits a turn or two in the shed; gating
    # on empty land here previously blocked ever refilling structures that
    # already existed once free land ran low, which is exactly how the
    # herd, once thinned by a staffing gap, could never recover even with
    # cash in hand. ----
    # Growing the herd is only allowed once phase-1 fully staffed the
    # EXISTING one (hires_today reached min_hands_for_upkeep in cash terms,
    # not cut short by insufficient money) -- otherwise this is exactly the
    # bootstrapping trap that caused a real collapse in local testing:
    # buying animals faster than affordable staffing keeps outrunning cash,
    # so the care-bonus discipline the whole ROI model depends on never
    # actually happens, and every extra animal just adds unpaid feed risk.
    staffing_established = hires_today >= min_hands_for_upkeep
    total_animal_population = animal_count + sum(total_held(a) for a in ANIMALS)
    room_for_more = max(0, MAX_TOTAL_ANIMALS - total_animal_population)
    orders_animal_buy = []
    animal_buy_spend = 0
    if not liquidating and staffing_established and room_for_more > 0 and days_left > DAYS_LEFT_TO_STOP_ANIMAL_INVESTMENT:
        ranked = rank_animals_to_buy(money_left, market_prices, days_left)
        if ranked:
            # Reserve enough to keep planting cheap crops before the animal
            # budget gets first claim on the rest of the cash -- without
            # this, the round-robin buyer (first-claim on money_left, up to
            # MAX_TOTAL_ANIMALS) can sink most of turn 1's cash into animals
            # and keep first-claiming every dollar after, leaving crops to
            # live on scraps for a week while animals ramp toward their
            # first yield -- an empty, weed-growing Q1 for days, worth $0
            # the whole time. Fades to irrelevant mid-game as empty tiles
            # run out on their own.
            seed_reserve = min(len(empty_tiles_all), 15) * 20
            budget = money_left - MIN_OPERATING_CASH_RESERVE - seed_reserve
            unhoused_now = {a: total_held(a) for a in ANIMALS}
            to_buy = {}
            picks = 0
            attempts = 0
            while (budget > 0 and picks < MAX_ANIMAL_BUYS_PER_TURN and sum(to_buy.values()) < room_for_more
                   and ranked and attempts < 4 * len(ranked) + 4):
                attempts += 1
                species = ranked[picks % len(ranked)] if len(ranked) > 1 else ranked[0]
                cost = ANIMALS[species]["cost"]
                if cost > budget:
                    ranked = [a for a in ranked if a != species]
                    continue
                if unhoused_now.get(species, 0) >= MAX_UNHOUSED_PER_SPECIES:
                    picks += 1
                    continue
                to_buy[species] = to_buy.get(species, 0) + 1
                unhoused_now[species] = unhoused_now.get(species, 0) + 1
                budget -= cost
                animal_buy_spend += cost
                picks += 1
            for species, qty in to_buy.items():
                orders_animal_buy.append(["BUY_ANIMAL", species, qty])
    money_left -= animal_buy_spend

    # Structures needed for whatever's currently unhoused (bought-but-not-
    # placed, in shed or in transit) -- recomputed from observed state
    # every turn, so it self-resolves as structures get built or animals
    # get placed, independent of whether a NEW purchase happened this turn.
    empty_pasture = len(structures_need_animal["PASTURE"])
    empty_coop = len(structures_need_animal["COOP"])
    pasture_unhoused = max(0, total_held("COW") + total_held("SHEEP") - empty_pasture)
    coop_unhoused = max(0, total_held("GOOSE") - empty_coop)
    build_wanted = {"PASTURE": pasture_unhoused, "COOP": coop_unhoused}

    # ---- hiring, phase 2: top up toward the full workload-driven target
    # (tile work + upkeep) with whatever cash animal investment left
    # behind -- growth staffing, funded only after the existing herd's
    # upkeep and this turn's investment are both covered. Counts PENDING
    # work (held seeds not yet planted, structures queued to build,
    # animals bought but not yet placed) alongside tiles already in use --
    # without this, turn 1 always computes target_hands=0 (active_tiles=0,
    # animal_workload=0 before anything is built yet) and the farmer solo-
    # builds/plants the whole opening while the real meta runs ~5 hands
    # from turn 1. Also stops once the marginal hire's fib cost exceeds
    # what it can plausibly earn back that day -- fib is uncapped and a
    # mature 75-tile farm's raw tile/animal count can compute a target
    # near 19-20, where hands 15+ cost $610-4181/day each; the real meta
    # tops out around 14 hands/day for exactly this reason.
    MAX_MARGINAL_HIRE_COST = 400
    if not liquidating:
        pending = sum(private["seeds"].values()) + sum(build_wanted.values()) + sum(total_held(a) for a in ANIMALS)
        target_hands = max(
            0,
            round((active_tiles + pending) / TILES_PER_UNIT_TARGET + animal_workload / ANIMAL_TILES_PER_UNIT) - 1,
        )
        while hires_today < target_hands:
            hire_cost = _fib(hires_today)
            if hire_cost > MAX_MARGINAL_HIRE_COST:
                break
            if money_left < hire_cost + HIRE_MIN_RESERVE:
                break
            orders_hire.append(["HIRE"])
            money_left -= hire_cost
            hires_today += 1

    pickup_priority = list(rank_animals_to_buy(me["money"], market_prices, days_left))
    for a in ANIMALS:
        if a not in pickup_priority:
            pickup_priority.append(a)

    # ---- per-unit actions ----
    empty_tiles = list(empty_tiles_all)
    melon_tile_count = sum(1 for _, _, t in owned if is_plant(t) and t.get("crop") == "MELON")
    needs_harvest = [
        (x, y) for x, y, t in owned
        if is_plant(t) and t["yield_units"] > 0
        and (day - t["planted_day"]) >= CROPS[t["crop"]]["first_yield_day"]
    ]
    needs_water = [(x, y) for x, y, t in owned if is_plant(t) and not t["watered_today"]]
    weeds = [(x, y) for x, y, t in owned if is_weed(t)]
    # Uses money_left (already net of this turn's hire/animal commitments),
    # not raw me["money"] -- otherwise this can order seeds against cash
    # that animal investment already spent earlier this same turn, and the
    # engine either partially fills or silently drops the line.
    plant_crop = best_crop_to_plant(money_left, market_prices, days_left, melon_tile_count) \
        if not liquidating else None
    holding_any_seed = held_seed_to_plant(private["seeds"]) is not None
    orders_seed = []
    if plant_crop is not None and not holding_any_seed:
        seed_cost = CROPS[plant_crop]["seed_cost"]
        room = len(empty_tiles_all)
        if plant_crop == "MELON":
            room = min(room, max(0, MAX_MELON_TILES - melon_tile_count))
        affordable = int(max(0, money_left - MIN_OPERATING_CASH_RESERVE) // seed_cost) if seed_cost > 0 else 0
        qty = min(room, affordable)
        if qty > 0:
            orders_seed.append(["BUY_SEED", plant_crop, qty])

    fert_room_tiles = [
        (x, y) for x, y, t in owned
        if is_plant(t) and t["watered_today"] and t.get("fertilized_until_day", -1) < day + 1
    ]
    fert_pickup_wanted = min(shed.get("FERTILIZER", 0), len(fert_room_tiles)) if fert_room_tiles else 0

    claimed = set()
    seed_budget = dict(private["seeds"])  # shared, decremented as units commit to planting
    half = board_size // 2
    ctx = {
        "shed": shed,
        "shed_tiles": shed_adjacent_tiles(board_size),
        "shed_center": (half - 0.5, half - 0.5),
        "animals_need_visit": animals_need_visit,
        "feed_only": feed_only,
        "animals_need_feed_no_wheat": animals_need_feed_no_wheat,
        "structures_need_animal": structures_need_animal,
        # 0 once liquidating -- FEED is disabled during liquidation (see
        # decide_unit_action's animal-tile branch), so fetching wheat for
        # it is a pointless round trip with nothing at the other end.
        "wheat_pickup_wanted": 0 if liquidating else len(animals_need_feed),
        "fert_pickup_wanted": fert_pickup_wanted,
        "home_slots": {"PASTURE": empty_pasture, "COOP": empty_coop},
        "build_wanted": dict(build_wanted),
        "pickup_priority": pickup_priority,
    }

    units = [(me["farmer"], private["inventories"][0])]
    for i, (hx, hy) in enumerate(me.get("hands", [])):
        units.append(((hx, hy), private["inventories"][i + 1] if i + 1 < len(private["inventories"]) else {}))

    all_ops = []
    for (ux, uy), inv in units:
        utile = me["tiles"][uy][ux]
        ops = decide_unit_action(
            (ux, uy), utile, inv, day, hour, final_day, seed_budget, plant_crop, liquidating,
            claimed, needs_harvest, needs_water, empty_tiles, weeds, ctx,
        )
        if utile is None and (ux, uy) in empty_tiles:
            empty_tiles.remove((ux, uy))
        all_ops.append(ops)

    farmer_ops = all_ops[0]
    hands_actions = all_ops[1:]

    # ---- assemble market orders under the 10-line-per-turn engine cap ----
    # Feed wheat goes first, always: missing FEED on a production checkpoint
    # day forfeits the ENTIRE accumulated care bonus (the single most
    # valuable thing in this economy, per the whole point of this rewrite)
    # -- it's one order line and can never be allowed to fall off the end
    # of a busy turn's 10-line budget. Near shed overflow or liquidating,
    # protect SELL next (discarded inventory is a pure loss); otherwise
    # prioritize growth investment (hire/animal/land/seed).
    if force_sell_all:
        market = orders_wheat + orders_sell + orders_hire + orders_animal_buy + orders_land + orders_seed
    else:
        market = orders_wheat + orders_hire + orders_animal_buy + orders_land + orders_seed + orders_sell
    market = market[:MAX_MARKET_ORDERS]

    return {"farmer": farmer_ops, "hands": hands_actions, "market": market}
