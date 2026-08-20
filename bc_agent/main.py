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


def _market_orders(cache, obs, shed, money):
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
        ops.append(F.label_action(choice, 0))

    action = {
        "farmer": ops[0] if ops else ["PASS"],
        "hands": ops[1:],
        "market": _market_orders(cache, obs, shed, money),
    }
    return action
