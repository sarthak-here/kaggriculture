"""Observation -> feature encoder for behaviour cloning (#63).

THIS FILE IS SHARED BY TRAINING AND INFERENCE. The dataset extractor and the
live agent must both call it, because any drift between how features are built
at train time and at play time silently destroys the policy -- and that failure
is invisible in training metrics. It is also why constants come from
`game_data` rather than being re-typed here: the public agent shipped a copy of
MARKET_PARAMS that went stale after the 1.32.7 hinge patch and mispriced carrot
by 89% (#60). One source of truth.

Design notes
------------
`actTimeout` is **1 second per step** and a farm runs up to ~15 units, so the
encoder is built around one idea: everything that does not depend on which unit
we are deciding for is computed ONCE per step and reused.

    encode_step(obs, config)  ->  StepCache   (global vector + grid tensor)
    encode_unit(cache, i)     ->  per-unit vector

The intended network exploits the same split -- project `global` and `grid`
once per step, project the small per-unit vector per unit, and add. That keeps
~15 decisions per step comfortably inside the timeout.

Board is 10x10. A tile is one of:
    "LOCKED"  (not owned)      -> channel 0
    None      (owned, empty)   -> channel 1
    dict      (PLANT / PASTURE / WEED)
"""

import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import game_data as gd

BOARD = 10
PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
            "EGG", "MILK", "WOOL", "FERTILIZER"]
CROPS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON"]
ANIMALS = ["COW", "SHEEP", "GOOSE"]
CARRIABLE = PRODUCTS + ANIMALS
SHOPS = ["BAKERY", "PIZZA_SHOP", "BRUNCH_SPOT", "YARN_STORE",
         "ICE_CREAM_SHOP", "PET_CAFE", "SMOOTHIE_SHOP", "FARMERS_MARKET"]
QUADRANTS = ["NW", "NE", "SW", "SE"]

# --- grid channels ---------------------------------------------------------
GRID_CHANNELS = [
    "locked", "empty", "is_plant", "is_pasture", "is_weed",
    "crop_wheat", "crop_carrot", "crop_tomato", "crop_strawberry", "crop_melon",
    "watered_today", "thirst", "yield_ready", "fertilized", "fertilizer_available",
    "has_animal", "animal_fed", "animal_cared", "animal_hunger", "care_bonus",
    "crop_age", "lifespan_left",
]
C = len(GRID_CHANNELS)
GRID_DIM = C * BOARD * BOARD


def _log(x):
    return math.log1p(max(0.0, float(x)))


def _get(d, k, default=0):
    if isinstance(d, dict):
        v = d.get(k, default)
        return default if v is None else v
    return default


# ---------------------------------------------------------------------------
# per-step encoding
# ---------------------------------------------------------------------------

class StepCache(object):
    """Everything shared by all units deciding at one step."""

    __slots__ = ("glob", "grid", "obs", "seat", "farm", "tiles",
                 "shed_pos", "work", "nearest")

    def __init__(self, glob, grid, obs, seat, farm, tiles, shed_pos, work, nearest):
        self.glob = glob
        self.grid = grid
        self.obs = obs
        self.seat = seat
        self.farm = farm
        self.tiles = tiles
        self.shed_pos = shed_pos
        self.work = work
        self.nearest = nearest


def _tile_channels(tile, day, step):
    """Encode one tile into C channels."""
    out = np.zeros(C, dtype=np.float32)
    if tile is None:            # owned but empty -> plantable
        out[1] = 1.0
        return out
    if not isinstance(tile, dict):   # "LOCKED" (or anything unexpected)
        out[0] = 1.0
        return out

    kind = tile.get("kind")
    if kind == "PLANT":
        out[2] = 1.0
    elif kind == "PASTURE":
        out[3] = 1.0
    elif kind == "WEED":
        out[4] = 1.0

    crop = tile.get("crop")
    if crop in CROPS:
        out[5 + CROPS.index(crop)] = 1.0

    out[10] = 1.0 if tile.get("watered_today") else 0.0
    out[11] = min(3.0, float(_get(tile, "consecutive_unwatered"))) / 3.0
    out[12] = min(6.0, float(_get(tile, "yield_units"))) / 6.0
    fert_until = float(_get(tile, "fertilized_until_day", -1))
    out[13] = 1.0 if fert_until >= day else 0.0
    out[14] = 1.0 if tile.get("fertilizer_available") else 0.0

    animal = tile.get("animal")
    if animal:
        out[15] = 1.0
        out[16] = 1.0 if tile.get("fed_today") else 0.0
        out[17] = 1.0 if tile.get("cared_today") else 0.0
        out[18] = min(3.0, float(_get(tile, "consecutive_unfed"))) / 3.0
        out[19] = min(1.0, float(_get(tile, "pending_care_bonus")))

    planted = float(_get(tile, "planted_day", -1))
    if planted >= 0:
        out[20] = min(30.0, day - planted) / 30.0
    lifespan = float(_get(tile, "max_lifespan_step", -1))
    if lifespan > 0:
        out[21] = max(0.0, min(1.0, (lifespan - step) / 240.0))
    return out


def encode_step(obs, configuration=None):
    """Build the per-step shared features. Call once per step, per seat."""
    seat = int(_get(obs, "player", 0))
    farms = list(_get(obs, "farms", []) or [])
    farm = farms[seat] if seat < len(farms) else {}
    opp = farms[1 - seat] if len(farms) > 1 else {}

    day = float(_get(obs, "day"))
    hour = float(_get(obs, "hour"))
    step = float(_get(obs, "step"))
    market = _get(obs, "market", {}) or {}
    prices = _get(market, "prices", {}) or {}
    inventory = _get(market, "inventory", {}) or {}
    private = _get(obs, "private", {}) or {}
    shed = _get(private, "shed", {}) or {}
    seeds = _get(private, "seeds", {}) or {}
    shops = list(_get(_get(obs, "town", {}) or {}, "unlocked_shops", []) or [])

    # ---- grid ----
    tiles = _get(farm, "tiles", []) or []
    grid = np.zeros((C, BOARD, BOARD), dtype=np.float32)
    work = {"thirsty": 0, "harvest": 0, "plantable": 0, "weeds": 0,
            "unfed": 0, "uncared": 0, "fert": 0, "planted": 0}
    # nearest work of each kind, as (dy, dx) later relative to a unit
    targets = {k: [] for k in ("thirsty", "harvest", "plantable", "weeds",
                               "unfed", "uncared", "fert")}
    for y in range(min(BOARD, len(tiles))):
        row = tiles[y]
        for x in range(min(BOARD, len(row))):
            t = row[x]
            grid[:, y, x] = _tile_channels(t, day, step)
            if not isinstance(t, dict):
                if t is None:
                    work["plantable"] += 1
                    targets["plantable"].append((y, x))
                continue
            kind = t.get("kind")
            if kind == "WEED":
                work["weeds"] += 1
                targets["weeds"].append((y, x))
            if kind == "PLANT":
                work["planted"] += 1
                if not t.get("watered_today"):
                    work["thirsty"] += 1
                    targets["thirsty"].append((y, x))
                if float(_get(t, "yield_units")) > 0:
                    work["harvest"] += 1
                    targets["harvest"].append((y, x))
            if t.get("animal"):
                if not t.get("fed_today"):
                    work["unfed"] += 1
                    targets["unfed"].append((y, x))
                if not t.get("cared_today"):
                    work["uncared"] += 1
                    targets["uncared"].append((y, x))
            if t.get("fertilizer_available"):
                work["fert"] += 1
                targets["fert"].append((y, x))

    # ---- global vector ----
    g = []
    g += [day / 30.0, hour / 24.0, step / 720.0,
          math.sin(2 * math.pi * hour / 24.0), math.cos(2 * math.pi * hour / 24.0),
          (30.0 - day) / 30.0]
    money = float(_get(farm, "money"))
    opp_money = float(_get(opp, "money"))
    g += [_log(money) / 10.0, _log(opp_money) / 10.0,
          1.0 if money > opp_money else 0.0,
          min(2.0, money / max(1.0, opp_money)) / 2.0]
    hands = list(_get(farm, "hands", []) or [])
    g += [len(hands) / 16.0, float(_get(farm, "hires_today")) / 16.0,
          len(list(_get(opp, "hands", []) or [])) / 16.0]

    quads = list(_get(farm, "unlocked_quadrants", []) or [])
    opp_quads = list(_get(opp, "unlocked_quadrants", []) or [])
    g += [1.0 if q in quads else 0.0 for q in QUADRANTS]
    g += [1.0 if q in opp_quads else 0.0 for q in QUADRANTS]

    g += [_log(_get(seeds, c)) / 4.0 for c in CROPS]
    g += [_log(_get(shed, p)) / 5.0 for p in PRODUCTS]
    g += [_log(_get(shed, a)) / 3.0 for a in ANIMALS]
    shed_total = sum(float(_get(shed, k)) for k in list(shed) or [])
    cap = float(_get(configuration or {}, "shedCapacity", 100)) or 100.0
    g += [min(1.5, shed_total / cap)]

    # market: price relative to base, and scarcity in units of T (the hinge input)
    for p in PRODUCTS:
        params = gd.MARKET_PARAMS[p]
        base = float(params["base"])
        T = float(params["T"])
        I0 = float(params["I0"])
        price = float(_get(prices, p, base))
        inv = float(_get(inventory, p, I0))
        g += [min(4.0, price / base) / 4.0,
              max(-2.0, min(2.0, (I0 - inv) / T)) / 2.0]
    g += [1.0 if s in shops else 0.0 for s in SHOPS]
    g += [min(1.0, gd.daily_demand(p, shops) / 60.0) for p in PRODUCTS]

    g += [work[k] / 25.0 for k in ("thirsty", "harvest", "plantable", "weeds",
                                   "unfed", "uncared", "fert", "planted")]

    glob = np.asarray(g, dtype=np.float32)

    shed_pos = _find_shed(tiles)
    return StepCache(glob, grid.reshape(-1), obs, seat, farm, tiles,
                     shed_pos, work, targets)


def _find_shed(tiles):
    """The shed is not in the tile grid; fall back to board centre."""
    return (BOARD // 2, BOARD // 2)



# ---------------------------------------------------------------------------
# per-unit encoding
# ---------------------------------------------------------------------------

PATCH = 5          # egocentric window, odd
PATCH_CHANNELS = [2, 4, 10, 11, 12, 15, 16, 17, 14, 1]   # indices into GRID_CHANNELS
UNIT_PATCH_DIM = PATCH * PATCH * len(PATCH_CHANNELS)


def unit_positions(cache):
    """[farmer, hand0, hand1, ...] as (x, y)."""
    farm = cache.farm
    out = [tuple(_get(farm, "farmer", [0, 0]) or [0, 0])]
    for h in list(_get(farm, "hands", []) or []):
        out.append(tuple(h))
    return out


def encode_unit(cache, index):
    """Per-unit feature vector. index 0 = farmer, 1.. = hands."""
    positions = unit_positions(cache)
    if index >= len(positions):
        return None
    x, y = int(positions[index][0]), int(positions[index][1])

    private = _get(cache.obs, "private", {}) or {}
    inventories = list(_get(private, "inventories", []) or [])
    carried = inventories[index] if index < len(inventories) else {}

    u = [1.0 if index == 0 else 0.0,          # is farmer
         min(1.0, index / 16.0),
         x / float(BOARD), y / float(BOARD)]
    # quadrant one-hot
    qx, qy = (0 if x < BOARD // 2 else 1), (0 if y < BOARD // 2 else 1)
    quad = ["NW", "NE", "SW", "SE"][qy * 2 + qx]
    u += [1.0 if q == quad else 0.0 for q in QUADRANTS]

    u += [_log(_get(carried, k)) / 3.0 for k in CARRIABLE]
    total_carried = sum(float(v) for v in (carried or {}).values())
    u += [min(1.0, total_carried / 6.0), 1.0 if total_carried else 0.0]

    sy, sx = cache.shed_pos
    u += [(sx - x) / float(BOARD), (sy - y) / float(BOARD),
          (abs(sx - x) + abs(sy - y)) / float(2 * BOARD)]

    # tile under the unit
    tile = None
    if 0 <= y < len(cache.tiles) and 0 <= x < len(cache.tiles[y]):
        tile = cache.tiles[y][x]
    day = float(_get(cache.obs, "day"))
    step = float(_get(cache.obs, "step"))
    u += list(_tile_channels(tile, day, step))

    # direction + distance to the nearest work of each type
    for kind in ("thirsty", "harvest", "plantable", "weeds", "unfed", "uncared", "fert"):
        best, bd = None, 1e9
        for (ty, tx) in cache.nearest[kind]:
            d = abs(tx - x) + abs(ty - y)
            if d < bd:
                bd, best = d, (ty, tx)
        if best is None:
            u += [0.0, 0.0, 1.0, 0.0]
        else:
            u += [(best[1] - x) / float(BOARD), (best[0] - y) / float(BOARD),
                  min(1.0, bd / float(2 * BOARD)), 1.0]

    # egocentric patch
    grid = cache.grid.reshape(C, BOARD, BOARD)
    half = PATCH // 2
    patch = np.zeros((len(PATCH_CHANNELS), PATCH, PATCH), dtype=np.float32)
    for pi, ch in enumerate(PATCH_CHANNELS):
        for dy in range(-half, half + 1):
            for dx in range(-half, half + 1):
                yy, xx = y + dy, x + dx
                if 0 <= yy < BOARD and 0 <= xx < BOARD:
                    patch[pi, dy + half, dx + half] = grid[ch, yy, xx]
    u += list(patch.reshape(-1))

    return np.asarray(u, dtype=np.float32)


def dims(obs, configuration=None):
    """Report the encoder's output dimensions (used by the trainer)."""
    cache = encode_step(obs, configuration)
    unit = encode_unit(cache, 0)
    return {"global": int(cache.glob.shape[0]),
            "grid": int(cache.grid.shape[0]),
            "unit": int(unit.shape[0])}


# ---------------------------------------------------------------------------
# action vocabulary  (shared contract: trainer AND agent must use this list)
# ---------------------------------------------------------------------------
# Derived from what the top-10 corpus actually emits (analysis/action_space.py:
# 27 observed classes, top 20 covering 99.74%), then completed so every legal
# op has a slot even if the sample never used it -- a class that is never
# predicted costs one logit, a MISSING class silently mislabels data.

MOVES = ["NORTH", "SOUTH", "EAST", "WEST"]
SIMPLE_OPS = ["PASS", "WATER", "HARVEST", "CARE", "FEED", "DIG",
              "FERTILIZE", "COLLECT_FERTILIZER", "DROP",
              "BUILD_PASTURE", "BUILD_COOP"]

UNIT_ACTIONS = (
    MOVES
    + SIMPLE_OPS
    + ["PLANT|%s" % c for c in CROPS]
    + ["PICKUP|%s" % i for i in CARRIABLE]
    + ["PLACE|%s" % a for a in ANIMALS]
)
UNIT_ACTION_INDEX = {name: i for i, name in enumerate(UNIT_ACTIONS)}
N_UNIT_ACTIONS = len(UNIT_ACTIONS)

# PICKUP carries a count (observed 1-6); predicted by a small separate head so
# it does not multiply the main vocabulary.
MAX_PICKUP = 6


def action_label(op):
    """Engine op (list/tuple) -> (class index, pickup count) or None if unmappable."""
    if not op:
        return None
    verb = str(op[0])
    if verb in UNIT_ACTION_INDEX and len(op) == 1:
        return UNIT_ACTION_INDEX[verb], 0
    if verb in ("PLANT", "PICKUP", "PLACE") and len(op) >= 2:
        key = "%s|%s" % (verb, op[1])
        idx = UNIT_ACTION_INDEX.get(key)
        if idx is None:
            return None
        count = 0
        if verb == "PICKUP" and len(op) >= 3:
            try:
                count = max(0, min(MAX_PICKUP, int(op[2])))
            except (TypeError, ValueError):
                count = 0
        return idx, count
    idx = UNIT_ACTION_INDEX.get(verb)
    return (idx, 0) if idx is not None else None


def label_action(index, count=0):
    """Inverse of action_label: class index -> engine op."""
    name = UNIT_ACTIONS[int(index)]
    if "|" not in name:
        return [name]
    verb, arg = name.split("|", 1)
    if verb == "PICKUP" and count:
        return [verb, arg, int(count)]
    return [verb, arg]


# ---------------------------------------------------------------------------
# market order vocabulary (second model; 80.35% of steps emit nothing)
# ---------------------------------------------------------------------------

MARKET_ACTIONS = (
    ["HIRE", "BUY_LAND"]
    + ["SELL|%s" % p for p in PRODUCTS]
    + ["BUY_SEED|%s" % c for c in CROPS]
    + ["BUY_ANIMAL|%s" % a for a in ANIMALS]
    + ["BUY_PRODUCT|%s" % p for p in PRODUCTS]
)
MARKET_ACTION_INDEX = {n: i for i, n in enumerate(MARKET_ACTIONS)}
N_MARKET_ACTIONS = len(MARKET_ACTIONS)


def market_label(order):
    """Engine market order -> (class index, quantity). HIRE/BUY_LAND count as 1."""
    if not order:
        return None
    verb = str(order[0])
    if verb in ("HIRE", "BUY_LAND"):
        return MARKET_ACTION_INDEX[verb], 1
    if len(order) < 2:
        return None
    key = "%s|%s" % (verb, order[1])
    idx = MARKET_ACTION_INDEX.get(key)
    if idx is None:
        return None
    qty = 1
    if len(order) >= 3:
        try:
            qty = max(1, int(order[2]))
        except (TypeError, ValueError):
            qty = 1
    return idx, qty


def market_order(index, quantity):
    """Inverse: class index + quantity -> engine order line(s)."""
    name = MARKET_ACTIONS[int(index)]
    if name in ("HIRE", "BUY_LAND"):
        return [[name]] * max(1, int(quantity))
    verb, arg = name.split("|", 1)
    return [[verb, arg, max(1, int(quantity))]]
