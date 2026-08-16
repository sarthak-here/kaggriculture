"""
Kaggriculture agent — v10: the Sarthak Sharma program.

v10 replaces v8/v9's reactive investment logic with a transcribed,
schedule-driven capital plan (verified move-identical across two winning
replays, 90639993 + 90689237, both ~$117-122k), executed on top of
the reactive unit layer we already validated on the ladder (feed routing,
care loop, mid-day flush, final-day haul-home, plant guard).

The program, as mined:
- t1: 5 HIRE + 2 COW + 2 SHEEP + 7 wheat seed + 12 melon seed + 5 feed
  wheat (exactly 10 order lines). Emerges here from the target curves
  below rather than a hardcoded turn-1 special case, so it self-heals if
  anything fails.
- Land on a SCHEDULE, not reactively: Q2 at day 7, Q3 at day 11. Never Q4.
- Herd waves ride the land: 2c+2s day 0 -> +2c d7, +1c d8, +1c d9,
  +2c+2s d10, +2s d11 -> 8 COW + 6 SHEEP complete by day 11, then frozen.
  No goose, ever.
- Structures form a tight ring at the shed (manhattan 0-2, including the
  four center tiles) so the daily feed round trip costs 0-2 steps forever.
- Planting waves keyed to land: d0 Q1 = 12 melon + 7 wheat; d7 Q2 = 19
  strawberry; d10 = second melon wave into the tiles wave 1 freed; d11
  Q3 = 23 strawberry; wheat fills everything else, with an aggressive
  endgame wheat conversion (2-day cycle lands through day 29).
- Hires: cheap skeleton crew days 1-6 (hoard cash for the d7-11 burst),
  then ramp to ~14/day.
- Selling: NO hold window. Trickle everything continuously; the late-game
  revenue skew comes from PRODUCTION timing (strawberry's 4 yields land
  d17-27 by biology, wave-2 melon lands d20, endgame wheat lands d27-29),
  not from hoarding inventory. This is why v9's hold window was both
  unnecessary and fatal (it starved the payroll); v10 deletes it.

Engine budget: everything O(units + tiles), no search. agent() must stay
the LAST top-level function in this file (kaggle_environments loads the
last callable).
"""
from game_data import (CROPS, ANIMALS, land_cost, sell_quantity,
                       predicted_price, daily_demand)

# Sellable via shed flush / haul. WHEAT excluded normally (ambiguous with
# feed round trips) but included once liquidating, when FEED is disabled.
SELLABLE_PRODUCTS = (set(CROPS) - {"WHEAT"}) | {spec["product"] for spec in ANIMALS.values()} | {"FERTILIZER"}
ONGOING_CROPS = {c for c, spec in CROPS.items() if spec.get("kind") == "ongoing"}

DAYS_LEFT_TO_STOP_PLANTING = 2       # wheat planted day 27 (days_left=3) still lands day 29
DAYS_LEFT_TO_STOP_ANIMALS = 5        # don't buy/replace herd members that can't pay back
MAX_MARKET_ORDERS = 10               # engine cap on order LINES per turn
TERMINAL_SWEEP_STEP = 716            # last 4 steps of 720: start emptying the shed
TERMINAL_SWEEP_ALL_STEP = 718        # from here, re-sell even what is already queued
TERMINAL_SWEEP_ORDER = ("CARROT", "EGG", "FERTILIZER", "MELON", "MILK",
                        "STRAWBERRY", "TOMATO", "WHEAT", "WOOL")
MIN_OPERATING_CASH_RESERVE = 300     # untouched by investment, keeps seeds/feed flowing
OPENING_CASH_RESERVE = 50            # d0-1: the turn-1 feed wheat IS the buffer
OPENING_RESERVE_LAST_DAY = 1
HIRE_MIN_RESERVE = 2
MAX_MARGINAL_HIRE_COST = 400         # fib is uncapped; hands past ~14 can't earn their cost back
SHED_CAPACITY = 100
SHED_OVERFLOW_SAFETY = 0.85
MIN_SELL_PRICE_RATIO = 0.7

# ---- the transcribed schedule ----
LAND_SCHEDULE = {2: 7}         # quadrant count -> earliest day to buy it
                               # Q3 on day 10 matches what the frontier agents do
                               # (#34b). ~34 earlier configurations lost on the day
                               # 7-15 cash wall; re-enabled by explicit request.
MELON_TARGET = 12                    # sustained while day <= MELON_LAST_PLANT_DAY
MELON_LAST_PLANT_DAY = 13            # wave 2 at d10-11 fits; later melon can't finish
STRAWBERRY_LAST_PLANT_DAY = 13       # program stops at d11; 10-day first yield makes later marginal
TILES_PER_UNIT_TARGET = 4
ANIMAL_TILES_PER_UNIT = 3
EARLY_HANDS_CAP = 4                  # skeleton crew days 1-6 (program: 0-4/day)
DROP_MIN_TYPES = 3      # item types that make DROP beat a PLACE chain
TRAVEL_CAP = 2                    # prefer work within this manhattan radius
FULL_HANDS_CAP = 9                   # measured optimum. 14 was copied from a bot we
                                     # later found was replaying a recording; hands 13
                                     # and 14 alone cost fib(12)+fib(13) = $610/DAY,
                                     # ~$14k over d7-29, against ~$8k of extra output.
LAST_BUILDOUT_DAY = 13               # while building out, land/herd beat upkeep chores
WHEAT_FILL_RESERVE_TILES = 7         # wheat seed money held back from the premium pick
WHEAT_PICKUP_CAP = 4                 # wheat a unit may withdraw per shed visit

# ---- opportunistic carrot (kaggle-environments 1.32.7 / PR #1399) ----
# 1.32.7 gave CARROT, TOMATO and EGG a "hinge" scarcity curve: flat up to a
# deficit of T, then quadratic. CARROT has the sharpest one (T=450,
# below_target 1.00) and nobody in the meta grows it, so in 35% of measured
# games it ends the season past the knee -- median $63/unit but a long tail
# ($594 observed). A carrot tile is $20 and 3 days for 4 units, so it competes
# with nothing but wheat fill and needs no forecast: we read the live price.
# Deliberately placed BELOW strawberry/melon so the proven opening is untouched;
# early in the game the deficit is small and this gate simply never fires.
CARROT_MIN_MARGINAL_PRICE = 70       # 2x base. Below this a tile is worth more as wheat.
CARROT_MAX_TILES = 16                # past this our own supply flattens the spike


def herd_target(day):
    """Transcribed herd curve: (cows, sheep) wanted as of `day`."""
    # The public frontier route (episode 91603791) opens with FOUR SHEEP and one
    # cow, spending ~$2,982 of the $3,000 start on turn 0. Sheep first-yield on
    # DAY 6 -- two days before cows -- and wool is base $200 against milk's $160,
    # so the early economy is wool-funded. That matches the measured day-6 gap
    # (their $1,569 v our $559, #37). Every earlier herd arm was cow-first.
    if day < 7:
        cows = 0
    elif day == 7:
        cows = 4
    elif day == 8:
        cows = 5
    elif day == 9:
        cows = 6
    else:
        cows = 8
    sheep = 4 if day < 10 else (4 if day == 10 else 6)
    return cows, sheep


def adaptive_herd(day, unlocked_shops):
    """Split the herd between COW and SHEEP by what the town actually buys.

    Since 1.32.6 (PR #1394) shops are drawn WITH replacement, so a town can open
    with no YARN_STORE at all -- and then wool demand is 1/day from the town centre
    alone and wool trades at the $1 floor (measured $2.00 on seed 2001 while
    strawberry sat at $212). v26's sheep-first opening was tuned before that patch,
    when a yarn store was far likelier to exist.

    Total herd size is unchanged; only the split adapts, and only from day 7, by
    which point ~3 shops have unlocked. Days 0-6 keep the proven opening because
    the town has revealed nothing yet.
    """
    cows, sheep = herd_target(day)
    if day < 7 or not unlocked_shops:
        return cows, sheep
    wool = daily_demand("WOOL", unlocked_shops)
    milk = daily_demand("MILK", unlocked_shops)
    total = cows + sheep
    if wool + milk <= 0:
        return cows, sheep
    # Never let one species go to zero outright -- a single animal of each keeps
    # the fertiliser stream and hedges a late shop unlock.
    want_sheep = int(round(total * wool / float(wool + milk)))
    want_sheep = max(1, min(total - 1, want_sheep))
    return total - want_sheep, want_sheep


def strawberry_target(quadrants, day):
    if day > STRAWBERRY_LAST_PLANT_DAY:
        return 0
    if quadrants >= 3:
        return 42
    if quadrants == 2:
        return 28
    return 0


def sell_priority(item, qty, market_inventory, unlocked_shops):
    """Rank a SELL order by the price damage it suffers if it is delayed.

    We used to rank by gross revenue (qty * current price), which puts big cheap
    orders ahead of small orders sitting on a steep part of the curve. The public
    3,094-scoring agent ranks by IMPACT instead -- qty * (price now - price after
    this order lands) -- so the order with the most to lose from waiting goes
    first, which matters because both players' orders interleave in one market and
    the steep-glut goods (melon `sq`, wool `sq`) collapse fastest.

    The urgency term nudges an item up when its inventory is already above I0
    relative to how fast the town drains it.
    """
    inv = market_inventory.get(item, 10000)
    now = predicted_price(item, inv)
    later = predicted_price(item, inv + qty)
    impact = qty * max(0, now - later)
    if impact <= 0:
        return 0.0
    demand = max(0.25, daily_demand(item, unlocked_shops))
    excess = max(0, inv + qty - 10000)
    urgency = min(1.0, (excess / demand) / 10.0)
    return impact * (1.0 + 0.25 * urgency)


def carrot_tiles_wanted(market_inventory, unlocked_shops, days_left,
                        plantable_empties, committed_units=0):
    """How many tiles of carrot the coming scarcity spike can absorb.

    Two things make this a projection rather than a price check:

    * We are paid at HARVEST, not at planting, and the town keeps eating carrot
      the whole time ours is growing. Gating on today's price fired two days too
      late -- the price ran $68 -> $101 over the final three days, so the crop
      went in on day 26-27 and half of it was still in the ground at the buzzer.
      daily_demand() reads the actual unlocked shops, so the forward price is
      exact for the shops already open.
    * Every carrot we sell puts a unit back into inventory and slides us down
      the hinge, so the spike is a finite pool, not a price. Walk the curve and
      stop where the marginal unit stops beating what the tile earns as wheat.
      `committed_units` is the crop already standing plus what is in the shed:
      without it this re-sizes to the whole spike every single turn and plants
      several times the supply the spike can actually absorb.

    Returns 0 when the market will not be short, which is the common case.
    """
    spec = CROPS["CARROT"]
    # Age the crop can reach and still be sold before the last day.
    grow = min(spec["max_yield_day"], days_left - 1)
    if grow < spec["first_yield_day"]:
        return 0
    inv = market_inventory.get("CARROT", 10000)
    inv_at_harvest = (inv - daily_demand("CARROT", unlocked_shops) * grow
                      + committed_units)
    if predicted_price("CARROT", inv_at_harvest) < CARROT_MIN_MARGINAL_PRICE:
        return 0
    per_tile = spec["max_yield"]
    cap_units = min(plantable_empties, CARROT_MAX_TILES) * per_tile
    units = 0
    while units < cap_units and \
            predicted_price("CARROT", inv_at_harvest + units) >= CARROT_MIN_MARGINAL_PRICE:
        units += 1
    return units // per_tile


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


def find_nearest_unclaimed(pos, candidates, claimed, cap=None):
    """`cap` bounds how far a unit will walk for this task (manhattan). It is
    a preference, not a restriction: decide_unit_action is retried without a
    cap when nothing is in range, so far tiles are still served."""
    options = [c for c in candidates if c not in claimed]
    if cap is not None:
        options = [c for c in options
                   if abs(pos[0] - c[0]) + abs(pos[1] - c[1]) <= cap]
    if not options:
        return None
    return min(options, key=lambda c: (pos[0] - c[0]) ** 2 + (pos[1] - c[1]) ** 2)


def held_seed_to_plant(seed_budget):
    held = [(crop, n) for crop, n in seed_budget.items() if n > 0]
    if not held:
        return None
    return max(held, key=lambda c: c[1])[0]


def drop_safe(inv, ctx):
    """True when the unit's whole inventory can go to the shed in one DROP.

    Unsafe to DROP while carrying something with a purpose: feed wheat or
    fertilizer that a pickup run still wants, or an animal on its way to a
    structure. DROP takes everything, so one kept item vetoes it.
    """
    for item, n in inv.items():
        if n <= 0:
            continue
        if item in ANIMALS:
            return False
        if item == "WHEAT" and ctx["wheat_pickup_wanted"] > 0:
            return False
        if item == "FERTILIZER" and ctx["fert_pickup_wanted"] > 0:
            return False
    return True


def flush_order(inv, items, prices):
    """(item, qty) held from `items`, most valuable first.

    `items` is a SET OF STRINGS, and Python randomizes str hashing per
    process, so iterating it directly made which goods reached the shed a
    PYTHONHASHSEED accident (measured: same seed, identical agents, scores
    85,989 / 83,884 / 84,910). A unit can only PLACE one item per turn, so
    this order decides what gets banked -- sort by value, not alphabetically,
    and tie-break on name so it is fully deterministic.
    """
    held = [(i, inv.get(i, 0)) for i in items if inv.get(i, 0) > 0]
    held.sort(key=lambda kv: (-(kv[1] * float(prices.get(kv[0], 0) or 0)), kv[0]))
    return held


def _fib(n):
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a



def fert_worth_it(tile, day):
    """Does fertiliser on THIS tile today buy anything? Ongoing crops only on a
    production checkpoint inside the fertiliser window; one-time crops only
    inside the bonus window and below cap; melon never (caps on water alone)."""
    spec = CROPS[tile["crop"]]
    age = day - tile["planted_day"]
    if spec["kind"] == "ongoing":
        for ahead in (0, 1, 2):
            since = (day + ahead + 1) - tile["planted_day"] - spec["first_yield_day"]
            if since >= 0 and since % spec["interval"] == 0:
                return True
        return False
    if tile["crop"] == "MELON":
        return False
    window_start = (spec["max_yield_day"] + 1) // 2
    return (window_start <= age <= spec["max_yield_day"]
            and tile["yield_units"] < spec["max_yield"])


def water_before_harvest(tile, day):
    """A one-time crop still inside its yield window gains +1 (+2 fertilized)
    from being watered, and that gain lands on the WATER action itself. The
    harvest branch runs first, so without this the last window day is taken at
    yield N when one more WATER would have made it N+1/N+2. The tile survives
    to the end of max_yield_day, so both fit in the same day."""
    spec = CROPS[tile["crop"]]
    if spec["kind"] == "ongoing" or tile["watered_today"]:
        return False
    age = day - tile["planted_day"]
    window_start = (spec["max_yield_day"] + 1) // 2
    return (window_start <= age <= spec["max_yield_day"]
            and tile["yield_units"] < spec["max_yield"])


def worth_harvesting(tile, day, days_left):
    """One-time crops keep ACCUMULATING yield through their bonus window (+1 per
    watered day, +2 fertilised), so harvesting the moment they turn ripe throws
    most of the crop away: wheat is ripe at age 2 with ~2 units but reaches 4
    (6 fertilised) by age 4. Wait for the cap or the end of the window --
    whichever comes first -- since decay only starts after max_yield_day.
    Ongoing crops bank each production immediately, so take those at once."""
    spec = CROPS[tile["crop"]]
    age = day - tile["planted_day"]
    if age < spec["first_yield_day"]:
        return False
    if spec["kind"] == "ongoing":
        return True
    if tile["yield_units"] >= spec["max_yield"]:
        return True
    if age >= spec["max_yield_day"]:
        return True
    return days_left <= 2



# ---- territory ownership -----------------------------------------------------
# 37% of all unit-turns are spent walking. Every previous fix changed WHICH task
# a unit took; none changed the fact that units criss-cross the whole farm. Here
# each task tile is owned by its NEAREST unit, so a unit works a compact
# territory and its next job is usually adjacent to its last one. Priority order
# is untouched -- it just applies within the territory first. If a unit's
# territory is clear it falls back to the global lists, so nothing goes unworked.
def territories(unit_positions, tile_lists):
    """[{tier: [tiles]} per unit] -- every tile owned by its nearest unit."""
    owned = [{k: [] for k in tile_lists} for _ in unit_positions]
    if not unit_positions:
        return owned
    for tier, tiles in tile_lists.items():
        for t in tiles:
            best, bd = 0, None
            for ui, p in enumerate(unit_positions):
                d = (p[0] - t[0]) ** 2 + (p[1] - t[1]) ** 2
                if bd is None or d < bd:
                    best, bd = ui, d
            owned[best][tier].append(t)
    return owned


def decide_unit_action(pos, tile, inv, day, hour, final_day, seed_budget, liquidating,
                       claimed, needs_harvest, needs_water, empty_tiles, weeds, ctx, unit_idx=None,
                       travel_cap=None):
    """One unit's action. Mutates claimed/seed_budget/ctx budgets so units
    acting later this turn don't collide with earlier commitments."""
    flush_items = SELLABLE_PRODUCTS | {"WHEAT"} if liquidating else SELLABLE_PRODUCTS

    # ---- on an animal tile ----
    # Each unit evaluates this against the START-of-turn observation, so
    # every unit standing on the same pen saw cared_today == False and all
    # issued CARE; one landed, the rest burned their turn. Measured 24 CARE
    # actions for ~14 animals (1.7x), ~200 wasted unit-turns a game.
    # tile_acted records what has been claimed on a tile THIS turn, keyed by
    # (pos, action): different actions on one tile all succeed, only the
    # duplicate of a given action is wasted.
    if has_animal(tile):
        done = ctx["tile_acted"]
        if tile["yield_units"] > 0 and (pos, "HARVEST") not in done:
            done.add((pos, "HARVEST"))
            return ["HARVEST"]
        if tile["fertilizer_available"] and (pos, "COLLECT") not in done:
            done.add((pos, "COLLECT"))
            return ["COLLECT_FERTILIZER"]
        # During liquidation only animals still carrying a banked care
        # bonus get fed (forfeiting a banked bonus on the final checkpoint
        # trades ~$300-500 of product for ~$50 of wheat).
        if not tile["fed_today"] and inv.get("WHEAT", 0) > 0 and \
           (pos, "FEED") not in done and \
           (not liquidating or tile.get("pending_care_bonus", 0) > 0):
            done.add((pos, "FEED"))
            return ["FEED"]
        if (not tile["cared_today"] and not liquidating
                and (pos, "CARE") not in done):
            done.add((pos, "CARE"))
            return ["CARE"]

    # Crops decay if left unharvested; harvest-on-tile stays top priority.
    if (is_plant(tile) and tile["yield_units"] > 0
            and worth_harvesting(tile, day, ctx["days_left"])
            and not water_before_harvest(tile, day)
            and (pos, "HARVEST") not in ctx["tile_acted"]):
        ctx["tile_acted"].add((pos, "HARVEST"))
        return ["HARVEST"]

    # ---- final-day haul-home: no rollover after day 29, so carried goods
    # that don't reach the shed are worth $0 ----
    if final_day:
        carried = flush_order(inv, flush_items, ctx["prices"])
        if carried:
            nearest_shed = min(ctx["shed_tiles"], key=lambda t: manhattan(pos, t))
            # One PLACE per turn, so N distinct item types need N turns AT the
            # shed on top of the walk. Leaving at hour+dist>=22 only ever
            # banked the first type and stranded the rest.
            if hour + manhattan(pos, nearest_shed) + (len(carried) - 1) >= 22:
                if pos in ctx["shed_tiles"]:
                    # One DROP banks every type; the PLACE chain stranded all
                    # but the first when the deadline bit.
                    if len(carried) >= 2 and drop_safe(inv, ctx):
                        return ["DROP"]
                    item, n = carried[0]
                    return ["PLACE", item, n]
                else:
                    return [step_toward(pos, nearest_shed)]

    if (is_plant(tile) and not tile["watered_today"]
            and (pos, "WATER") not in ctx["tile_acted"]):
        ctx["tile_acted"].add((pos, "WATER"))
        return ["WATER"]

    if (is_plant(tile) and tile["watered_today"] and inv.get("FERTILIZER", 0) > 0
            and tile.get("fertilized_until_day", -1) < day + 1
            and fert_worth_it(tile, day)
            and (pos, "FERTILIZE") not in ctx["tile_acted"]):
        ctx["tile_acted"].add((pos, "FERTILIZE"))
        return ["FERTILIZE"]

    # place a carried animal on any compatible empty structure
    if is_structure(tile) and "animal" not in tile:
        for animal in ANIMALS:
            if ANIMALS[animal]["structure"] == tile["kind"] and inv.get(animal, 0) > 0:
                return ["PLACE", animal]

    # ---- shed-adjacent services ----
    if pos in ctx["shed_tiles"]:
        if ctx["wheat_pickup_wanted"] > 0 and inv.get("WHEAT", 0) == 0:
            # Cap the withdrawal, not the purchase. Measured: we pull 4.94
            # wheat per PICKUP against the reference's 2.59 and drain the shed
            # from ~43 at h0 to 11.5 by midday (it holds 29.4) -- and the
            # drained shed is what re-arms the stateless feed top-up. 2.59 is
            # demonstrably enough for the same 320 feeds. This leaves the buy
            # rule alone, so the surplus stays in the shed as the insurance
            # experiment #8 proved it has to be.
            n = min(ctx["wheat_pickup_wanted"], ctx["shed"].get("WHEAT", 0),
                    WHEAT_PICKUP_CAP)
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
        # mid-day flush of sellable products (PLACE per item, never DROP —
        # DROP would dump feed wheat mid-round-trip)
        _carried = flush_order(inv, flush_items, ctx["prices"])
        if len(_carried) >= DROP_MIN_TYPES and drop_safe(inv, ctx):
            return ["DROP"]          # whole inventory in one action
        for item, n in _carried:
            if item == "FERTILIZER" and ctx["fert_pickup_wanted"] > 0:
                continue
            if item == "WHEAT" and ctx["wheat_pickup_wanted"] > 0:
                continue
            return ["PLACE", item, n]

    if tile is None and not liquidating:
        # BUILD only on a designated ring site near the shed — never on
        # whatever empty tile a unit happens to cross (that scattered
        # structures across the farm and made every future feed trip pay
        # for it).
        if pos in ctx["build_sites"]:
            for kind in ("PASTURE", "COOP"):
                if ctx["build_wanted"].get(kind, 0) > 0:
                    ctx["build_wanted"][kind] -= 1
                    ctx["build_sites"].discard(pos)
                    return [f"BUILD_{kind}"]
        # fresh seeds start at consecutive_unwatered=1: planting on the
        # day's last turn is a guaranteed weed. Hour 22 is safe (on-tile
        # WATER fires next turn).
        if hour < 23 and pos not in ctx["build_sites"]:
            held = held_seed_to_plant(seed_budget)
            if held is not None:
                seed_budget[held] -= 1
                return ["PLANT", held]

    if is_weed(tile):
        return ["DIG"]

    # ---- movement, priority-ordered ----
    # wheat carriers deliver feed before anything else (missed feeds with
    # wheat in circulation were v8's biggest documented leak)
    if inv.get("WHEAT", 0) > 0 and ctx["animals_need_feed"]:
        t = find_nearest_unclaimed(pos, ctx["animals_need_feed"], claimed, travel_cap)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    _mine = ctx["territory"][unit_idx] if unit_idx is not None and ctx.get("territory") else None
    if _mine:
        for _tier, _pool in (("harvest", needs_harvest), ("animal", ctx["animals_need_visit"]),
                             ("water", needs_water)):
            _cand = _mine.get(_tier) or []
            if _cand:
                t = find_nearest_unclaimed(pos, _cand, claimed, travel_cap)
                if t:
                    claimed.add(t)
                    return [step_toward(pos, t)]
    if needs_harvest:
        t = find_nearest_unclaimed(pos, needs_harvest, claimed, travel_cap)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    if ctx["animals_need_visit"]:
        candidates = ctx["animals_need_visit"]
        if inv.get("WHEAT", 0) == 0:
            # `feed_only` excludes only tiles whose SOLE need is feed, so a
            # tile needing feed AND care still pulls a wheat-less unit: it
            # does the care half, leaves, and the feed needs a second trip.
            # Measured: 5,705 animal-tile visits vs the reference's 3,288 on
            # the same herd. While the shed can supply wheat, skip every
            # feed-needing tile and fetch wheat first (block below) so the
            # animal is served in one trip instead of two.
            skip = ctx["needs_feed_set"] if ctx["wheat_fetchable"] else ctx["feed_only"]
            if skip:
                candidates = [c for c in candidates if c not in skip]
        t = find_nearest_unclaimed(pos, candidates, claimed, travel_cap)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    # Fetch wheat before the remaining movement options, so a unit that just
    # skipped feed-needing animals goes to arm itself rather than wandering
    # off to water. Bounded by wheat_pickup_wanted, which the PICKUP decrements.
    if (inv.get("WHEAT", 0) == 0 and ctx["wheat_fetchable"]
            and ctx["fetch_budget"] > 0 and ctx["animals_need_feed"]):
        t = min(ctx["shed_tiles"], key=lambda s: manhattan(pos, s))
        if t != pos:
            # Bounded: dispatch at most one fetcher per unfed animal. Without
            # this every wheat-less unit stampedes the shed, drains it, and
            # the stateless feed top-up re-fires against the empty shed --
            # measured +$17,147 of wheat and -$16,636 of score.
            ctx["fetch_budget"] -= 1
            return [step_toward(pos, t)]  # shed tiles stay unclaimed, shared
    for animal in ANIMALS:
        if inv.get(animal, 0) > 0:
            kind = ANIMALS[animal]["structure"]
            t = find_nearest_unclaimed(pos, ctx["structures_need_animal"].get(kind, []), claimed, travel_cap)
            if t:
                claimed.add(t)
                return [step_toward(pos, t)]
            break
    # Buildout: while the herd is still being placed, getting a structure up
    # beats a watering round. A pasture that lands a day earlier is a day of
    # production plus a day of care bonus; a plant survives to the rollover.
    if (not liquidating and day <= LAST_BUILDOUT_DAY and ctx["unhoused_total"] > 0
            and any(n > 0 for n in ctx["build_wanted"].values()) and ctx["build_sites"]):
        t = find_nearest_unclaimed(pos, list(ctx["build_sites"]), claimed, travel_cap)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    if needs_water:
        t = find_nearest_unclaimed(pos, needs_water, claimed, travel_cap)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    if ctx["animals_need_feed"] and ctx["wheat_pickup_wanted"] > 0 and ctx["shed"].get("WHEAT", 0) > 0:
        t = find_nearest_unclaimed(pos, ctx["shed_tiles"], claimed)
        if t:
            return [step_toward(pos, t)]  # shed tiles stay unclaimed, shared
    # Planting outranks weeds and fertilizer while land is still filling: a
    # held seed that never reaches dirt is a tile producing nothing for the
    # rest of the game, while a weed or a skipped fert day costs one crop-day.
    if (not liquidating and day <= LAST_BUILDOUT_DAY and empty_tiles
            and held_seed_to_plant(seed_budget) is not None):
        plantable = [e for e in empty_tiles if e not in ctx["build_sites"]]
        t = find_nearest_unclaimed(pos, plantable, claimed, travel_cap)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    # Fertilizer ahead of weeds: a carrier that detours to dig is a fert unit
    # not applied, and ongoing-crop coverage is the entire point of carrying it.
    if inv.get("FERTILIZER", 0) > 0:
        target = find_nearest_unclaimed(pos, ctx["fert_targets_ongoing"], claimed, travel_cap)
        if target is None:
            target = find_nearest_unclaimed(pos, ctx["fert_targets_onetime"], claimed, travel_cap)
        if target:
            claimed.add(target)
            return [step_toward(pos, target)]
    if weeds:
        t = find_nearest_unclaimed(pos, weeds, claimed, travel_cap)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    if not liquidating and any(n > 0 for n in ctx["build_wanted"].values()) and ctx["build_sites"]:
        t = find_nearest_unclaimed(pos, list(ctx["build_sites"]), claimed, travel_cap)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]
    if not liquidating and (held_seed_to_plant(seed_budget) is not None) and empty_tiles:
        plantable = [e for e in empty_tiles if e not in ctx["build_sites"]]
        t = find_nearest_unclaimed(pos, plantable, claimed, travel_cap)
        if t:
            claimed.add(t)
            return [step_toward(pos, t)]

    return ["PASS"]


def agent(obs):
    player = obs["player"]
    me = obs["farms"][player]
    private = obs["private"]
    day = obs["day"]
    hour = obs["hour"]
    days_left = 30 - day
    market_prices = obs["market"]["prices"]
    market_inventory = obs["market"]["inventory"]
    unlocked_shops = (obs.get("town") or {}).get("unlocked_shops", [])
    board_size = len(me["tiles"])
    half = board_size // 2
    shed_center = (half - 0.5, half - 0.5)

    liquidating = days_left <= DAYS_LEFT_TO_STOP_PLANTING
    final_day = days_left <= 1

    owned = list(iter_owned_tiles(me))
    empty_tiles_all = [(x, y) for x, y, t in owned if t is None]
    shed = private.get("shed", {})
    inventories = private.get("inventories", [])
    quadrants = len(me["unlocked_quadrants"])

    def total_held(item):
        return shed.get(item, 0) + sum(inv.get(item, 0) for inv in inventories)

    # ---- census ----
    placed = {"COW": 0, "SHEEP": 0, "GOOSE": 0}
    animals_need_feed, animals_need_harvest = [], []
    animals_need_fert, animals_need_care = [], []
    structures_need_animal = {"PASTURE": [], "COOP": []}
    crop_counts = {}
    weeds = []
    needs_harvest, needs_water = [], []
    for x, y, t in owned:
        if has_animal(t):
            placed[t["animal"]] = placed.get(t["animal"], 0) + 1
            if not t["fed_today"]:
                animals_need_feed.append((x, y))
            if t["yield_units"] > 0:
                animals_need_harvest.append((x, y))
            if t["fertilizer_available"]:
                animals_need_fert.append((x, y))
            if not t["cared_today"]:
                animals_need_care.append((x, y))
        elif is_structure(t):
            structures_need_animal[t["kind"]].append((x, y))
        elif is_plant(t):
            crop_counts[t["crop"]] = crop_counts.get(t["crop"], 0) + 1
            if t["yield_units"] > 0 and worth_harvesting(t, day, days_left):
                needs_harvest.append((x, y))
            if not t["watered_today"]:
                needs_water.append((x, y))
        elif is_weed(t):
            weeds.append((x, y))
    animal_count = sum(placed.values())
    animals_need_visit = list(set(animals_need_harvest) | set(animals_need_fert)
                              | set(animals_need_feed) | set(animals_need_care))
    other_needs = set(animals_need_harvest) | set(animals_need_fert) | set(animals_need_care)
    feed_only = set(animals_need_feed) - other_needs

    # Unhoused animals eat too once placed, and t1's freshly bought herd
    # needs feed the same day — count them for wheat purposes.
    unhoused = {a: total_held(a) for a in ANIMALS}
    feed_target = animal_count + sum(unhoused.values())
    bonus_carrying_unfed = sum(
        1 for x, y, t in owned
        if has_animal(t) and not t["fed_today"] and t.get("pending_care_bonus", 0) > 0
    )

    # ---- SELL: continuous trickle, chunked against the price curve.
    # No hold window (see module docstring: late revenue comes from the
    # planting schedule, not hoarding). Force-dump near overflow or in
    # liquidation. ----
    shed_total = sum(shed.values())
    force_sell_all = liquidating or shed_total >= SHED_CAPACITY * SHED_OVERFLOW_SAFETY
    orders_sell = []
    for item, count in shed.items():
        if count <= 0 or item in ANIMALS:
            continue
        sellable = count
        if item == "WHEAT":
            reserve = feed_target if not liquidating else bonus_carrying_unfed
            sellable = max(0, count - reserve)
        n = sellable if force_sell_all else sell_quantity(
            item, sellable, market_inventory.get(item, 10000), MIN_SELL_PRICE_RATIO)
        if n > 0:
            orders_sell.append((sell_priority(item, n, market_inventory,
                                              unlocked_shops), ["SELL", item, n]))
    orders_sell.sort(key=lambda t: -t[0])
    orders_sell = [o for _, o in orders_sell]

    # ---- feed wheat top-up (first in the order list, always) ----
    orders_wheat = []
    shed_wheat = shed.get("WHEAT", 0)
    wanted_feed_wheat = feed_target if not liquidating else bonus_carrying_unfed
    if wanted_feed_wheat > 0 and shed_wheat < wanted_feed_wheat and me["money"] >= market_prices.get("WHEAT", 25):
        orders_wheat.append(["BUY_PRODUCT", "WHEAT", wanted_feed_wheat - shed_wheat])

    money_left = me["money"]

    # ---- HIRING, phase 1: minimum upkeep staffing for the existing herd
    # (hands vanish nightly; an unstaffed herd escapes in 2 days) ----
    animal_workload = sum(1 for _, _, t in owned if is_structure(t))
    min_hands_for_upkeep = 0 if liquidating else -(-animal_workload // ANIMAL_TILES_PER_UNIT)
    orders_hire = []
    hires_today = me["hires_today"]
    if not liquidating:
        while hires_today < min_hands_for_upkeep:
            cost = _fib(hires_today)
            if money_left < cost + HIRE_MIN_RESERVE:
                break
            orders_hire.append(["HIRE"])
            money_left -= cost
            hires_today += 1

    # ---- LAND: transcribed fixed schedule (Q2 day 7, Q3 day 11), cash-guarded ----
    orders_land = []
    next_q = quadrants + 1
    if (next_q in LAND_SCHEDULE and day >= LAND_SCHEDULE[next_q] and not liquidating):
        cost = land_cost(quadrants)
        if cost is not None and money_left > cost + MIN_OPERATING_CASH_RESERVE:
            orders_land.append(["BUY_LAND"])
            money_left -= cost

    # ---- ANIMALS: deficit vs the transcribed herd curve (self-healing: an
    # escaped cow re-registers as a deficit and gets replaced while it
    # still pays) ----
    orders_animal = []
    if not liquidating and days_left > DAYS_LEFT_TO_STOP_ANIMALS and hires_today >= min_hands_for_upkeep:
        cow_t, sheep_t = adaptive_herd(day, (obs.get("town") or {}).get("unlocked_shops", []))
        for species, target in (("COW", cow_t), ("SHEEP", sheep_t)):
            deficit = target - (placed.get(species, 0) + unhoused.get(species, 0))
            if deficit <= 0:
                continue
            cost = ANIMALS[species]["cost"]
            affordable = int(max(0, money_left - MIN_OPERATING_CASH_RESERVE) // cost)
            qty = min(deficit, affordable)
            if qty > 0:
                orders_animal.append(["BUY_ANIMAL", species, qty])
                money_left -= qty * cost

    # ---- structures wanted for whatever's unhoused; ring sites at shed ----
    empty_pasture = len(structures_need_animal["PASTURE"])
    empty_coop = len(structures_need_animal["COOP"])
    # include this turn's purchases so building starts immediately
    pending_pasture = sum(q for o in orders_animal for s, q in [(o[1], o[2])] if ANIMALS[s]["structure"] == "PASTURE")
    pasture_unhoused = max(0, unhoused["COW"] + unhoused["SHEEP"] + pending_pasture - empty_pasture)
    coop_unhoused = max(0, unhoused["GOOSE"] - empty_coop)
    build_wanted = {"PASTURE": pasture_unhoused, "COOP": coop_unhoused}
    n_sites = sum(build_wanted.values())
    build_sites = set()
    if n_sites > 0 and empty_tiles_all:
        ring = sorted(empty_tiles_all,
                      key=lambda c: (shed_center[0] - c[0]) ** 2 + (shed_center[1] - c[1]) ** 2)
        build_sites = set(ring[:n_sites])

    # ---- HIRING, phase 2: transcribed ramp — skeleton crew days 1-6, full
    # crew from day 7, workload-shaped, marginal-cost capped. Hiring does
    # NOT stop during liquidation: days 28-29 still need a full harvest/
    # haul crew (every previous version ran the endgame with 0 hands,
    # stranding ready crops and animal products — the transcribed program
    # hires 9-10 on the final days; a hand costs fib-cheap against the
    # $1000+ of final-day product it rescues). ----
    active_tiles = len(owned) - len(empty_tiles_all)
    pending = sum(private["seeds"].values()) + n_sites + sum(unhoused.values())
    base_target = max(0, round((active_tiles + pending) / TILES_PER_UNIT_TARGET
                               + animal_workload / ANIMAL_TILES_PER_UNIT) - 1)
    if day == 0:
        target_hands = 5
    elif day < 7:
        target_hands = min(base_target, EARLY_HANDS_CAP)
    else:
        _cap = FULL_HANDS_CAP
        if len(empty_tiles_all) >= 20 and me["money"] > 5000:
            _cap = 11
        target_hands = min(base_target, _cap)
    while hires_today < target_hands:
        cost = _fib(hires_today)
        if cost > MAX_MARGINAL_HIRE_COST or money_left < cost + HIRE_MIN_RESERVE:
            break
        orders_hire.append(["HIRE"])
        money_left -= cost
        hires_today += 1

    # ---- SEEDS: transcribed planting waves as target deficits.
    # Priority: strawberry (land-keyed waves) > melon (sustained 12 through
    # day 13, incl. the d10 second wave into freed tiles) > wheat fill. ----
    orders_seed = []
    holding_any_seed = held_seed_to_plant(private["seeds"]) is not None
    plantable_empties = max(0, len(empty_tiles_all) - n_sites)
    if not liquidating and not holding_any_seed and plantable_empties > 0:
        straw_deficit = max(0, strawberry_target(quadrants, day) - crop_counts.get("STRAWBERRY", 0))
        melon_deficit = 0
        if day <= MELON_LAST_PLANT_DAY and days_left > CROPS["MELON"]["first_yield_day"]:
            melon_deficit = max(0, MELON_TARGET - crop_counts.get("MELON", 0))
        carrot_committed = (crop_counts.get("CARROT", 0) * CROPS["CARROT"]["max_yield"]
                            + shed.get("CARROT", 0))
        carrot_tiles = carrot_tiles_wanted(
            market_inventory, (obs.get("town") or {}).get("unlocked_shops", []),
            days_left, plantable_empties, carrot_committed)
        pick = None
        if straw_deficit > 0:
            pick, deficit = "STRAWBERRY", straw_deficit
        elif melon_deficit > 0:
            pick, deficit = "MELON", melon_deficit
        elif carrot_tiles > 0:
            pick, deficit = "CARROT", carrot_tiles
        elif days_left > CROPS["WHEAT"]["first_yield_day"]:
            pick, deficit = "WHEAT", plantable_empties
        # Hold back the wheat-fill money BEFORE the premium pick spends down
        # to the operating floor. Wheat is $10/tile against melon's $80, so
        # this trades ~1 melon for ~7 tiles that would otherwise sit bare for
        # the whole wave (measured: d0 left 10 plantable tiles with $8 spare).
        # Days 0-1 the opening is its own buffer: the feed wheat bought on
        # turn 1 covers the day's upkeep, so holding $300 back just prices us
        # out of ~4 premium seeds. The reference opening runs down to ~$50.
        op_reserve = (OPENING_CASH_RESERVE if day <= OPENING_RESERVE_LAST_DAY
                      else MIN_OPERATING_CASH_RESERVE)
        wheat_cost = CROPS["WHEAT"]["seed_cost"]
        wheat_reserve = 0
        if (pick is not None and pick != "WHEAT"
                and days_left > CROPS["WHEAT"]["first_yield_day"]):
            wheat_reserve = wheat_cost * min(WHEAT_FILL_RESERVE_TILES, plantable_empties)
        bought = 0
        if pick is not None:
            seed_cost = CROPS[pick]["seed_cost"]
            affordable = int(max(0, money_left - op_reserve - wheat_reserve) // seed_cost) if seed_cost else 0
            qty = min(deficit, plantable_empties, affordable)
            if qty > 0:
                orders_seed.append(["BUY_SEED", pick, qty])
                money_left -= qty * seed_cost
                bought = qty
        # Wheat fill for whatever the premium pick didn't cover. Only ONE
        # crop was ever ordered per turn, so a strawberry/melon wave left
        # every remaining tile bare until the wave finished planting.
        leftover = plantable_empties - bought
        if (pick != "WHEAT" and leftover > 0
                and days_left > CROPS["WHEAT"]["first_yield_day"]):
            affordable = int(max(0, money_left - op_reserve) // wheat_cost) if wheat_cost else 0
            wqty = min(leftover, affordable, WHEAT_FILL_RESERVE_TILES)
            if wqty > 0:
                orders_seed.append(["BUY_SEED", "WHEAT", wqty])
                money_left -= wqty * wheat_cost

    # ---- fertilizer targeting: ongoing crops first (double production on
    # a $120+ strawberry beats +2/day on wheat), surplus gets sold ----
    fert_room_ongoing = [
        (x, y) for x, y, t in owned
        if is_plant(t) and t["crop"] in ONGOING_CROPS and t["watered_today"]
        and t.get("fertilized_until_day", -1) < day + 1
    ]
    fert_room_onetime = [
        (x, y) for x, y, t in owned
        if is_plant(t) and t["crop"] not in ONGOING_CROPS and t["watered_today"]
        and t.get("fertilized_until_day", -1) < day + 1
    ]
    fert_pickup_wanted = min(shed.get("FERTILIZER", 0), len(fert_room_ongoing) + len(fert_room_onetime))

    # ---- per-unit actions ----
    claimed = set()
    seed_budget = dict(private["seeds"])
    ctx = {
        "shed": shed,
        "shed_tiles": shed_adjacent_tiles(board_size),
        "days_left": days_left,
        "prices": market_prices,
        "animals_need_visit": animals_need_visit,
        "animals_need_feed": animals_need_feed,
        "feed_only": feed_only,
        "needs_feed_set": set(animals_need_feed),
        "fetch_budget": len(animals_need_feed),
        # Early game only: the one-trip benefit shows up as +$3,195 of d15
        # cash, but every extra pickup drains the shed and the stateless feed
        # top-up re-buys against it (+$11,729 over d10-29). Take the early
        # half of the trade and leave the late half alone.
        "wheat_fetchable": (len(animals_need_feed) > 0
                            and shed.get("WHEAT", 0) > 0
                            and day <= 9
                            and not liquidating),
        "structures_need_animal": structures_need_animal,
        "wheat_pickup_wanted": len(animals_need_feed) if not liquidating else bonus_carrying_unfed,
        "fert_pickup_wanted": fert_pickup_wanted,
        "fert_targets_ongoing": fert_room_ongoing,
        "fert_targets_onetime": fert_room_onetime,
        "home_slots": {"PASTURE": empty_pasture, "COOP": empty_coop},
        "build_wanted": dict(build_wanted),
        "unhoused_total": sum(unhoused.values()),
        "build_sites": build_sites,
        "pickup_priority": ["COW", "SHEEP", "GOOSE"],
    }

    empty_tiles = list(empty_tiles_all)
    units = [(me["farmer"], inventories[0] if inventories else {})]
    for i, (hx, hy) in enumerate(me.get("hands", [])):
        units.append(((hx, hy), inventories[i + 1] if i + 1 < len(inventories) else {}))

    ctx["tile_acted"] = set()      # per-turn, like `claimed`
    ctx["territory"] = territories(
        [p for p, _ in units],
        {"harvest": needs_harvest, "animal": animals_need_visit, "water": needs_water})

    all_ops = []
    for _ui, ((ux, uy), inv) in enumerate(units):
        utile = me["tiles"][uy][ux]
        ops = decide_unit_action(
            (ux, uy), utile, inv, day, hour, final_day, seed_budget, liquidating,
            claimed, needs_harvest, needs_water, empty_tiles, weeds, ctx, _ui,
            TRAVEL_CAP,
        )
        if ops == ["PASS"]:
            # nothing worth doing nearby -- the PASS path commits nothing, so
            # re-ask with the whole farm in scope rather than idle.
            ops = decide_unit_action(
                (ux, uy), utile, inv, day, hour, final_day, seed_budget, liquidating,
                claimed, needs_harvest, needs_water, empty_tiles, weeds, ctx, _ui,
                None,
            )
        if utile is None and (ux, uy) in empty_tiles:
            empty_tiles.remove((ux, uy))
        all_ops.append(ops)

    # ---- assemble market orders under the 10-line cap.
    # Feed wheat first always (a dropped feed order can forfeit a whole
    # care bonus); sells jump the queue when the shed is at risk. ----
    if force_sell_all:
        # HIRE ahead of SELL. On d28-29 one wheat line plus up to 9 product
        # sell lines filled the 10-line cap and dropped every HIRE, so v11's
        # deliberate "keep hiring through liquidation" change never executed
        # and the endgame still ran with 0 hands -- which is also why goods
        # sat unhauled. A dropped sell carries to the next turn; a dropped
        # hire is gone for the day.
        market = orders_wheat + orders_hire + orders_sell + orders_animal + orders_land + orders_seed
    else:
        market = orders_wheat + orders_hire + orders_animal + orders_land + orders_seed + orders_sell
    market = market[:MAX_MARKET_ORDERS]

    # ---- terminal sweep: on the last few steps, dump whatever is still in the
    # shed. Normal liquidation reserves feed wheat and is capped at 10 lines, so
    # goods that arrive late (a day-29 carrot harvest) can sit there to the
    # buzzer -- measured 6 stranded carrots even with the arm working. Anything
    # unsold at the end is worth exactly zero, so on the final steps every
    # remaining line is spent selling, cheapest-to-carry first. ----
    _step = day * 24 + hour
    if _step >= TERMINAL_SWEEP_STEP:
        planned = {}
        for o in market:
            if o and o[0] == "SELL":
                planned[o[1]] = planned.get(o[1], 0) + int(o[2])
        for item in TERMINAL_SWEEP_ORDER:
            if len(market) >= MAX_MARKET_ORDERS:
                break
            held = shed.get(item, 0)
            extra = (held if _step >= TERMINAL_SWEEP_ALL_STEP
                     else held - planned.get(item, 0))
            if extra > 0:
                market.append(["SELL", item, extra])

    return {"farmer": all_ops[0], "hands": all_ops[1:], "market": market}
