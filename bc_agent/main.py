"""BC agent v1 (#64) -- a cloned policy, not a replay.

Two numpy models over one shared per-step encoding (`features.py`):

    unit policy    35 classes, one decision per farmer/hand   (val acc 0.798)
    market policy  28 classes, emit + quantity, per step      (val F1 0.604)

Why this is not the replay path: a recorded route fires action #347 at step 347
regardless of state and desyncs the moment a weed lands on a different tile
(frozen trace = 2,857, EXPERIMENTS #57). This conditions every decision on the
live observation, so drift is not a failure mode -- there is no cursor to lose.

LEGALITY MASKING is deliberate and conservative. A cloned policy will happily
emit PLANT with no seed or HARVEST on bare earth, and an illegal op wastes that
unit's turn. Only *certainly* illegal classes are masked -- over-masking would
suppress good actions the model learned and is harder to notice than the
occasional wasted turn.
"""

import json
import os
import sys

import numpy as np

import features as F
import game_data as gd


def _find(name):
    """Locate a weight file.

    kaggle_environments exec's the agent WITHOUT `__file__`, so the usual
    dirname(__file__) trick raises NameError at import time. It does put the
    agent's own directory on sys.path (that is how `import game_data` resolves),
    so search there.
    """
    candidates = []
    try:
        candidates.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    candidates.extend(sys.path)
    candidates.append(os.getcwd())
    for d in candidates:
        try:
            p = os.path.join(d, name)
            if os.path.exists(p):
                return p
        except (TypeError, ValueError):
            continue
    raise IOError("cannot locate %s (searched %d paths)" % (name, len(candidates)))


_UNIT = np.load(_find("bc_model.npz"))
_MKT = np.load(_find("bc_market.npz"))

_Wg, _Wr, _Wu = _UNIT["Wg"], _UNIT["Wr"], _UNIT["Wu"]
_b, _Wo, _bo = _UNIT["b"], _UNIT["Wo"], _UNIT["bo"]

_MWg, _MWr, _Mb = _MKT["Wg"], _MKT["Wr"], _MKT["b"]
_MWe, _Mbe = _MKT["We"], _MKT["be"]
_MWq, _Mbq = _MKT["Wq"], _MKT["bq"]
_MTHR = _MKT["thr"]

MAX_ORDERS = 10
NEG = -1e9


def _get(d, k, default=0):
    if isinstance(d, dict):
        v = d.get(k, default)
        return default if v is None else v
    return default


def _tile_at(cache, x, y):
    if 0 <= y < len(cache.tiles) and 0 <= x < len(cache.tiles[y]):
        return cache.tiles[y][x]
    return "LOCKED"


SHED_ACCESS = {(4, 4), (4, 5), (5, 4), (5, 5)}   # engine _shed_access_tiles(10)


def _legal_mask(cache, index, x, y, seeds, carried, shed):
    """Mask what the ENGINE would reject. Nothing is forced.

    #66 measured what top agents do when standing on obvious work, and it rules
    out forcing: on a ready crop they HARVEST only 18% of the time, on a thirsty
    crop they WATER 45%, at the shed holding goods they DROP 18%. Units walk
    THROUGH tiles constantly, so local state does not determine the action --
    a "always harvest a ready tile" guard would deviate from expert play, not
    correct toward it.

    What IS safe is refusing actions the engine silently discards, since those
    cost the unit its turn for nothing. v1 left PICKUP unmasked and it became
    the second-most-common action (166 emissions in six days, ~15% vs 1.88% in
    the corpus), every one of them wasted.
    """
    mask = np.zeros(F.N_UNIT_ACTIONS, dtype=np.float32)
    tile = _tile_at(cache, x, y)
    is_dict = isinstance(tile, dict)
    kind = tile.get("kind") if is_dict else None
    at_shed = (x, y) in SHED_ACCESS
    carrying = sum(float(v) for v in (carried or {}).values())

    # PICKUP: engine requires shed adjacency AND stock of that item in the shed.
    for item in F.CARRIABLE:
        if not at_shed or float(_get(shed, item)) <= 0:
            mask[F.UNIT_ACTION_INDEX["PICKUP|%s" % item]] = NEG

    # DROP: engine requires shed adjacency AND something in hand.
    if not at_shed or carrying <= 0:
        mask[F.UNIT_ACTION_INDEX["DROP"]] = NEG

    # moves that would leave the board
    if y <= 0:
        mask[F.UNIT_ACTION_INDEX["NORTH"]] = NEG
    if y >= F.BOARD - 1:
        mask[F.UNIT_ACTION_INDEX["SOUTH"]] = NEG
    if x <= 0:
        mask[F.UNIT_ACTION_INDEX["WEST"]] = NEG
    if x >= F.BOARD - 1:
        mask[F.UNIT_ACTION_INDEX["EAST"]] = NEG

    if not (is_dict and kind == "PLANT" and not tile.get("watered_today")):
        mask[F.UNIT_ACTION_INDEX["WATER"]] = NEG
    if not (is_dict and float(_get(tile, "yield_units")) > 0):
        mask[F.UNIT_ACTION_INDEX["HARVEST"]] = NEG
    if not (is_dict and tile.get("animal")):
        mask[F.UNIT_ACTION_INDEX["CARE"]] = NEG
        mask[F.UNIT_ACTION_INDEX["FEED"]] = NEG
    if not (is_dict and kind == "WEED"):
        mask[F.UNIT_ACTION_INDEX["DIG"]] = NEG
    if not (is_dict and tile.get("fertilizer_available")):
        mask[F.UNIT_ACTION_INDEX["COLLECT_FERTILIZER"]] = NEG

    # planting needs bare owned ground AND a seed of that crop
    plantable = tile is None
    for crop in F.CROPS:
        idx = F.UNIT_ACTION_INDEX["PLANT|%s" % crop]
        if not plantable or float(_get(seeds, crop)) <= 0:
            mask[idx] = NEG
    if not plantable:
        mask[F.UNIT_ACTION_INDEX["BUILD_PASTURE"]] = NEG
        mask[F.UNIT_ACTION_INDEX["BUILD_COOP"]] = NEG

    # placing an animal requires carrying it
    for animal in F.ANIMALS:
        if float(_get(carried, animal)) <= 0:
            mask[F.UNIT_ACTION_INDEX["PLACE|%s" % animal]] = NEG
    return mask


MOVE_SET = ("NORTH", "SOUTH", "EAST", "WEST")


def _step_toward(x, y, tx, ty):
    """One legal board step from (x,y) toward (tx,ty); longer axis first."""
    dx, dy = tx - x, ty - y
    options = []
    if abs(dx) >= abs(dy):
        options = [("EAST" if dx > 0 else "WEST") if dx else None,
                   ("SOUTH" if dy > 0 else "NORTH") if dy else None]
    else:
        options = [("SOUTH" if dy > 0 else "NORTH") if dy else None,
                   ("EAST" if dx > 0 else "WEST") if dx else None]
    for opt in options:
        if opt:
            return opt
    return None


def _assign_move(cache, x, y, carrying, seeds, claimed):
    """Where should this unit walk? Returns a direction, or None to keep the model's.

    #67: through the agent's own inference path the policy scores 0.916 on
    expert states -- the wiring is fine -- and its errors are overwhelmingly
    MOVE-vs-MOVE (WEST->SOUTH, EAST->SOUTH). Direction is exactly where BC is
    weakest, because several routes to the same tile are equally good so top-1
    accuracy is low by construction. But it is also the error that COMPOUNDS:
    a unit sent the wrong way never arrives, so it never harvests, and the farm
    starves.

    So keep the learned decision about WHAT to do on a tile, and make WHERE TO
    WALK deterministic. `claimed` stops the whole crew converging on one tile.
    """
    if carrying >= 4:
        return _step_toward(x, y, 4, 4)          # shed access corner

    order = ["harvest", "thirsty"]
    if any(float(_get(seeds, c)) > 0 for c in F.CROPS):
        order.append("plantable")
    order += ["unfed", "uncared", "fert", "weeds"]

    best = None
    best_key = None
    for kind in order:
        for (ty, tx) in cache.nearest.get(kind, ()):
            if (tx, ty) in claimed:
                continue
            d = abs(tx - x) + abs(ty - y)
            key = (order.index(kind), d)
            if best_key is None or key < best_key:
                best_key, best = key, (tx, ty)
        if best is not None:
            break                                 # respect the priority order
    if best is None:
        return None
    claimed.add(best)
    if (best[0], best[1]) == (x, y):
        return None                               # already there; let the model act
    return _step_toward(x, y, best[0], best[1])


def _fib(n):
    a, b = 1, 1
    for _ in range(int(n)):
        a, b = b, a + b
    return a


def _hire_block_cost(already, want):
    return sum(_fib(already + i) for i in range(max(0, want)))


CREW_TARGET = 9          # #52: bounded on both sides, 9 is optimal
CASH_FLOOR = 150.0       # must survive the night; a 9-hand crew costs 88
HIRE_LINES = 5           # of the 10 order slots, hiring may claim at most this many
SELL_TRIGGER = 6         # sell whenever the shed holds this much; the corpus sells constantly
SEED_BATCH = 8           # cap seed bought per step so one batch cannot drain the bankroll
OPENING_STEPS = 120      # 5 days: where #61 says the fixed schedule ends and policy begins

try:
    with open(_find("opening_schedule.json")) as _fh:
        _SCHEDULE = json.load(_fh)
except Exception:                                    # noqa: BLE001
    _SCHEDULE = {}


def _market_orders(cache, obs, shed, money, seeds_now):
    """Learned orders, wrapped in the economic guards a clone cannot learn.

    A pure BC market head walks into a death spiral: it overbuys, ends the day
    broke, cannot re-hire in the morning (the engine wipes `hands` every night),
    stops planting, and never recovers. That state -- broke, 3 hands -- appears
    nowhere in the corpus, so every prediction inside it is extrapolation. The
    guards below keep the agent inside the distribution it was trained on.
    """
    glob = cache.glob.astype(np.float32)[None, :]
    grid = cache.grid.astype(np.float32)[None, :]
    h = np.maximum(glob @ _MWg + grid @ _MWr + _Mb, 0.0)
    emit = (h @ _MWe + _Mbe)[0]
    qty = np.expm1(np.clip((h @ _MWq + _Mbq)[0], 0.0, 6.0))

    farm = cache.farm
    hands = len(list(_get(farm, "hands", []) or []))
    hires_today = int(float(_get(farm, "hires_today")))
    market = _get(obs, "market", {}) or {}
    prices = _get(market, "prices", {}) or {}
    inv = _get(market, "inventory", {}) or {}
    day = int(float(_get(obs, "day")))
    step = int(float(_get(obs, "step")))

    orders = []
    budget = float(money)

    # --- OPENING SCRIPT (#67) -------------------------------------------
    # For the first OPENING_STEPS the capital plan is a fixed schedule, not a
    # policy: cross-episode agreement in the dominant cluster is 1.000 on days
    # 0-2 and 0.951 on day 4 (#61, #67). Replaying it is safe in a way replaying
    # a unit route is NOT -- a HIRE is a HIRE wherever the units stand, so there
    # is no position to desync. The point is to hand the learned policy a farm at
    # expert scale on day 5, instead of the quarter-scale farm it was drifting
    # into and had never seen in training (#66).
    if step < OPENING_STEPS and _SCHEDULE:
        for raw in _SCHEDULE.get(str(step), []):
            if len(orders) >= MAX_ORDERS:
                break
            verb = raw[0]
            if verb in ("HIRE", "BUY_LAND"):
                cost = _fib(hires_today + sum(1 for o in orders if o[0] == "HIRE"))
                if verb == "HIRE" and cost <= budget - 1:
                    orders.append(["HIRE"])
                    budget -= cost
                continue
            item = raw[1]
            n = int(raw[2]) if len(raw) > 2 else 1
            if verb == "SELL":
                n = min(n, int(float(_get(shed, item))))
                if n <= 0:
                    continue
                orders.append(["SELL", item, n])
                budget += n * float(_get(prices, item, 0))
                continue
            if verb == "BUY_SEED":
                unit = float(gd.CROPS[item]["seed_cost"])
            elif verb == "BUY_ANIMAL":
                unit = float(gd.ANIMALS[item]["cost"])
            else:
                unit = float(_get(prices, item, gd.MARKET_PARAMS[item]["base"]))
            n = min(n, int(max(0.0, budget) // max(1.0, unit)))
            if n <= 0:
                continue
            orders.append([verb, item, n])
            budget -= n * unit

    # --- GUARD D: BUY LAND ON THE EXPERT SCHEDULE (#68) -----------------
    # EXPERIMENTS #48/#56 closed land after ~35 negative configurations -- but
    # every one of those was measured with our HAND-WRITTEN policy, which could
    # not work the extra tiles. All six top episodes buy it on the same tight
    # clock: quadrant 2 on day 6-7, quadrant 3 on day 10-11, without exception.
    # With expert per-step execution the tiles get worked, so the old verdict
    # does not transfer. This is the one place the ledger's "do not re-open" is
    # conditional on a policy we are no longer running.
    empty_now = cache.work.get("plantable", 0)
    owned = len(list(_get(farm, "unlocked_quadrants", []) or []))
    # A/B TWICE, both negative: land ON = 172/5,622/584 (before cash fix) and
    # 4,632/7,704/5,205 (after) vs OFF = 13,888/15,426/10,181 and
    # 16,651/21,158/21,222. Experts buy quadrant 2 on day 6 and 3 on day 10, but
    # they can AFFORD it by then and we cannot -- #56 holds for the BC agent too.
    if False and 1 <= owned <= 2 and empty_now <= 4:
        target_day = 6 if owned == 1 else 10
        if day >= target_day:
            cost = float(gd.LAND_COSTS[owned - 1])
            if budget >= cost + CASH_FLOOR and len(orders) < MAX_ORDERS:
                orders.append(["BUY_LAND"])
                budget -= cost

    # --- GUARD C: KEEP THE LAND FULL (#68) ------------------------------
    # The scale gap, measured. Ryo Hasegawa (168,259) runs `empty` tiles at ZERO
    # from day 3 onward -- 21 planted by day 3, 53 by day 12 -- holding only 0-8
    # seeds at a time because every seed bought is planted at once. Our agent sat
    # on 25 EMPTY tiles with 12-15 planted. That single difference is the whole
    # 4x production gap; it is a capital-allocation rule, not a policy subtlety.
    #
    # So: buy enough seed to cover every empty tile, every step, cash permitting.
    # Crop choice follows the value model (#53) and the yield clock -- wheat is
    # cheap and yields on day 2, melon/strawberry are worth far more but need 10
    # days, so they stop being buyable near the end.
    empty = empty_now
    seed_held = sum(int(float(_get(seeds_now, c))) for c in F.CROPS)
    deficit = empty - seed_held
    if deficit > 0 and budget > CASH_FLOOR:
        # Crop choice must be CASH-AWARE, not just clock-aware. Melon seed is $80
        # against wheat's $10, so leading with melon while poor drains exactly the
        # cash the farm needs to keep hiring and to reach the land price. Wheat
        # yields on day 2 and funds the expensive crops; melon/strawberry are
        # worth far more per tile but need 10 days and a bankroll.
        days_left = 30 - day
        rich = budget > 2500
        if days_left <= 4:
            plan = ["WHEAT"]
        elif days_left <= 12:
            plan = ["WHEAT", "CARROT"]
        elif rich:
            plan = ["MELON", "STRAWBERRY", "WHEAT"]
        else:
            plan = ["WHEAT", "MELON", "STRAWBERRY"]
        # and never sink the whole bankroll into one step's worth of seed
        deficit = min(deficit, SEED_BATCH)
        for crop in plan:
            if deficit <= 0 or len(orders) >= MAX_ORDERS:
                break
            unit = float(gd.CROPS[crop]["seed_cost"])
            n = min(deficit, int(max(0.0, budget - CASH_FLOOR) // max(1.0, unit)))
            if n <= 0:
                continue
            orders.append(["BUY_SEED", crop, n])
            budget -= n * unit
            deficit -= n

    # --- GUARD A: rebuild the crew every morning ------------------------
    # Hiring is Fibonacci-cheap (9 hands = 88 total) and the crew is wiped
    # nightly, so this is close to unconditionally correct.
    # HIRE_LINES caps how many of the 10 order slots hiring may take. Without
    # it the crew rebuild ate all ten lines, no BUY_SEED could ever be emitted,
    # the farm planted NOTHING for 30 days and scored 1. The corpus opening
    # spends exactly 5 lines on HIRE and the other 5 on seed and stock, so
    # hiring is spread across the morning rather than done in one step.
    want = max(0, CREW_TARGET - hands)
    if want and _hire_block_cost(hires_today, 1) <= budget:
        got = 0
        while got < want and got < HIRE_LINES and len(orders) < HIRE_LINES:
            cost = _fib(hires_today + got)
            if cost > budget - 1:
                break
            orders.append(["HIRE"])
            budget -= cost
            got += 1

    # --- GUARD B: sell when broke, and sweep at the buzzer ---------------
    terminal = step >= 716
    shed_total = sum(int(float(_get(shed, i))) for i in F.PRODUCTS)
    if budget < CASH_FLOOR or terminal or shed_total >= SELL_TRIGGER:
        held = [(item, int(float(_get(shed, item)))) for item in F.PRODUCTS]
        held = [(i, n) for i, n in held if n > 0]

        def value(pair):
            item, n = pair
            price = float(_get(prices, item, gd.MARKET_PARAMS[item]["base"]))
            return n * price
        for item, n in sorted(held, key=value, reverse=True):
            if len(orders) >= MAX_ORDERS:
                break
            if terminal:
                sell = n
            else:
                sell = gd.sell_quantity(item, n, int(float(_get(inv, item, 10000))))
                sell = max(1, min(n, int(sell)))
            orders.append(["SELL", item, int(sell)])
            budget += sell * float(_get(prices, item, 0))

    # --- learned orders, cheapest-signal-last, all affordability checked --
    fire = np.where(emit > _MTHR)[0]
    fire = fire[np.argsort(-(emit[fire] - _MTHR[fire]))]
    if step < OPENING_STEPS:
        fire = []          # the script owns the opening capital plan
    have_sold = {o[1] for o in orders if o[0] == "SELL"}

    for k in fire:
        if len(orders) >= MAX_ORDERS:
            break
        name = F.MARKET_ACTIONS[int(k)]
        n = max(1, int(round(float(qty[k]))))

        if name == "HIRE":
            continue                      # guard A owns hiring
        if name == "BUY_LAND":
            continue                      # #56: land is 12/12 negative for us
        if name.startswith("SELL|"):
            item = name.split("|", 1)[1]
            if item in have_sold:
                continue
            n = min(n, int(float(_get(shed, item))))
            if n <= 0:
                continue
            orders.append(["SELL", item, n])
            budget += n * float(_get(prices, item, 0))
            continue

        # --- buys: never spend past the floor --------------------------
        verb, arg = name.split("|", 1)
        if verb == "BUY_SEED":
            unit = float(gd.CROPS[arg]["seed_cost"])
        elif verb == "BUY_ANIMAL":
            unit = float(gd.ANIMALS[arg]["cost"])
        else:
            unit = float(_get(prices, arg, gd.MARKET_PARAMS[arg]["base"]))
        spendable = max(0.0, budget - CASH_FLOOR)
        n = min(n, int(spendable // max(1.0, unit)))
        if n <= 0:
            continue
        orders.append([verb, arg, n])
        budget -= n * unit

    return orders[:MAX_ORDERS]


def agent(obs, configuration=None):
    cache = F.encode_step(obs, configuration or {})
    private = _get(obs, "private", {}) or {}
    seeds = _get(private, "seeds", {}) or {}
    shed = _get(private, "shed", {}) or {}
    inventories = list(_get(private, "inventories", []) or [])
    money = float(_get(cache.farm, "money"))

    positions = F.unit_positions(cache)
    n_units = len(positions)

    # Shared half of the network: ONE matmul for the whole step.
    glob = cache.glob.astype(np.float32)
    grid = cache.grid.astype(np.float32)
    shared = glob @ _Wg + grid @ _Wr + _b

    ops = []
    claimed = set()
    for i in range(n_units):
        vec = F.encode_unit(cache, i)
        if vec is None:
            ops.append(["PASS"])
            continue
        h = np.maximum(shared + vec.astype(np.float32) @ _Wu, 0.0)
        logits = h @ _Wo + _bo
        x, y = int(positions[i][0]), int(positions[i][1])
        carried = inventories[i] if i < len(inventories) else {}
        logits = logits + _legal_mask(cache, i, x, y, seeds, carried, shed)
        choice = int(np.argmax(logits))
        if logits[choice] <= NEG / 2:
            ops.append(["PASS"])
            continue
        name = F.UNIT_ACTIONS[choice]
        if name in MOVE_SET:
            carrying = sum(float(v) for v in (carried or {}).values())
            better = _assign_move(cache, x, y, carrying, seeds, claimed)
            if better is not None and logits[F.UNIT_ACTION_INDEX[better]] > NEG / 2:
                ops.append([better])
                continue
        ops.append(F.label_action(choice, 0))

    action = {
        "farmer": ops[0] if ops else ["PASS"],
        "hands": ops[1:],
        "market": _market_orders(cache, obs, shed, money, seeds),
    }
    return action
