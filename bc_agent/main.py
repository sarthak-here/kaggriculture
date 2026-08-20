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


def _legal_mask(cache, index, x, y, seeds, carried):
    """Conservative: mask only what is certainly illegal."""
    mask = np.zeros(F.N_UNIT_ACTIONS, dtype=np.float32)
    tile = _tile_at(cache, x, y)
    is_dict = isinstance(tile, dict)
    kind = tile.get("kind") if is_dict else None

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
    if not carried:
        mask[F.UNIT_ACTION_INDEX["DROP"]] = NEG

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


def _market_orders(cache, shed, money):
    glob = cache.glob.astype(np.float32)[None, :]
    grid = cache.grid.astype(np.float32)[None, :]
    h = np.maximum(glob @ _MWg + grid @ _MWr + _Mb, 0.0)
    emit = (h @ _MWe + _Mbe)[0]
    qty = np.expm1(np.clip((h @ _MWq + _Mbq)[0], 0.0, 6.0))

    fire = np.where(emit > _MTHR)[0]
    # strongest signal first: with a 10-line cap, order is a real decision
    fire = fire[np.argsort(-(emit[fire] - _MTHR[fire]))]

    orders = []
    for k in fire:
        name = F.MARKET_ACTIONS[int(k)]
        n = int(round(float(qty[k])))
        if n < 1:
            n = 1
        if name.startswith("SELL|"):
            item = name.split("|", 1)[1]
            held = int(float(_get(shed, item)))
            if held <= 0:
                continue
            n = min(n, held)
        elif name == "HIRE":
            n = min(n, 8)
        for line in F.market_order(int(k), n):
            orders.append(line)
            if len(orders) >= MAX_ORDERS:
                return orders
    return orders


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
        logits = logits + _legal_mask(cache, i, x, y, seeds, carried)
        choice = int(np.argmax(logits))
        if logits[choice] <= NEG / 2:
            ops.append(["PASS"])
            continue
        ops.append(F.label_action(choice, 0))

    action = {
        "farmer": ops[0] if ops else ["PASS"],
        "hands": ops[1:],
        "market": _market_orders(cache, shed, money),
    }
    return action
