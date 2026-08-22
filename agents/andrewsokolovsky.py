IL_OVERLAY_TEMPLATE = r'''

# === V21-R1 SAFE IMITATION ROUTER ===
# This overlay does NOT predict raw farmer/hand/market actions.
# It only chooses among the already embedded complete experts at the same
# three route-selection decision points used by V21-R1.

import math as _il_math
import json as _il_json
import hashlib as _il_hashlib

_IL_PRODUCTS = ("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON","EGG","MILK","WOOL","FERTILIZER")
_IL_CROPS = ("WHEAT","CARROT","TOMATO","STRAWBERRY","MELON")
_IL_ANIMALS = ("GOOSE","COW","SHEEP")
_IL_SHOPS = ("BAKERY","PIZZA_SHOP","BRUNCH_SPOT","YARN_STORE","ICE_CREAM_SHOP","PET_CAFE","SMOOTHIE_SHOP","FARMERS_MARKET")
_IL_BASE_PRICE = {"WHEAT":25.0,"CARROT":35.0,"TOMATO":60.0,"STRAWBERRY":120.0,"MELON":250.0,"EGG":50.0,"MILK":160.0,"WOOL":200.0,"FERTILIZER":100.0}
_IL_SCALE_T = {"WHEAT":400.0,"CARROT":450.0,"TOMATO":200.0,"STRAWBERRY":100.0,"MELON":300.0,"EGG":332.0,"MILK":122.0,"WOOL":105.0,"FERTILIZER":200.0}
_IL_SHOP_PRODUCTS = {
    "BAKERY": ("EGG","WHEAT"),
    "PIZZA_SHOP": ("MILK","TOMATO","WHEAT"),
    "BRUNCH_SPOT": ("EGG","WHEAT","STRAWBERRY"),
    "YARN_STORE": ("WOOL",),
    "ICE_CREAM_SHOP": ("STRAWBERRY","MILK","WHEAT"),
    "PET_CAFE": ("CARROT",),
    "SMOOTHIE_SHOP": ("STRAWBERRY","MILK"),
    "FARMERS_MARKET": ("WHEAT","CARROT","TOMATO","STRAWBERRY"),
}

_IL_MODEL_BUNDLE = __MODEL_BUNDLE__
_IL_FORCE = __FORCE_BUNDLE__
_IL_ENABLE_LOG = __ENABLE_LOG__
_IL_HISTORY = {0: {}, 1: {}}
_IL_LAST_DELTA = {0: {}, 1: {}}
_IL_LOG = {0: [], 1: []}
_IL_DECISIONS = {0: {}, 1: {}}

def _il_clip(x, lo=-5.0, hi=5.0):
    try:
        x = float(x)
    except Exception:
        return 0.0
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x

def _il_money_scale(x):
    try:
        return _il_math.log1p(max(0.0, float(x))) / 12.5
    except Exception:
        return 0.0

def _il_tile_summary(farm):
    crop_counts = {k:0.0 for k in _IL_CROPS}
    crop_yield = {k:0.0 for k in _IL_CROPS}
    animal_counts = {k:0.0 for k in _IL_ANIMALS}
    animal_yield = {k:0.0 for k in _IL_ANIMALS}
    weeds = 0.0
    pasture = 0.0
    coop = 0.0
    empty_struct = 0.0
    tiles = list((farm or {}).get("tiles", []) or [])
    for row in tiles:
        for tile in list(row or []):
            if tile == "WEED":
                weeds += 1.0
                continue
            if not isinstance(tile, dict):
                continue
            if tile.get("kind") == "WEED":
                weeds += 1.0
            crop = tile.get("crop")
            if crop in crop_counts:
                crop_counts[crop] += 1.0
                crop_yield[crop] += max(0.0, float(tile.get("yield_units", 0) or 0))
            animal = tile.get("animal")
            if animal in animal_counts:
                animal_counts[animal] += 1.0
                animal_yield[animal] += max(0.0, float(tile.get("yield_units", 0) or 0))
            kind = tile.get("kind")
            if kind == "PASTURE":
                pasture += 1.0
                if not animal:
                    empty_struct += 1.0
            elif kind == "COOP":
                coop += 1.0
                if not animal:
                    empty_struct += 1.0
    return crop_counts, crop_yield, animal_counts, animal_yield, weeds, pasture, coop, empty_struct

def _il_tick(obs):
    seat = _seat(obs)
    step = int(obs.get("step", 0) or 0)
    farms = list(obs.get("farms", []) or [])
    own = farms[seat] if len(farms) > seat else {}
    opp = farms[1-seat] if len(farms) >= 2 else {}
    market = obs.get("market", {}) or {}
    inv = market.get("inventory", {}) or {}
    current = {
        "step": step,
        "own_money": float(own.get("money", 0) or 0),
        "opp_money": float(opp.get("money", 0) or 0),
        "market": {p: float(inv.get(p, 10000) or 0) for p in _IL_PRODUCTS},
    }
    if step == 0 or step < int(_IL_HISTORY[seat].get("step", -1)):
        _IL_HISTORY[seat] = {}
        _IL_LAST_DELTA[seat] = {
            "own_money": 0.0,
            "opp_money": 0.0,
            "market": {p:0.0 for p in _IL_PRODUCTS},
        }
        _IL_LOG[seat] = []
        _IL_DECISIONS[seat] = {}
    prev = _IL_HISTORY.get(seat) or {}
    if prev:
        prev_market = prev.get("market", {}) or {}
        _IL_LAST_DELTA[seat] = {
            "own_money": current["own_money"] - float(prev.get("own_money", current["own_money"])),
            "opp_money": current["opp_money"] - float(prev.get("opp_money", current["opp_money"])),
            "market": {
                p: current["market"][p] - float(prev_market.get(p, current["market"][p]))
                for p in _IL_PRODUCTS
            },
        }
    _IL_HISTORY[seat] = current

def _il_known_demand_per_day(shops, item):
    demand = 0.0 if item == "FERTILIZER" else 1.0
    for shop in shops:
        products = _IL_SHOP_PRODUCTS.get(shop, ())
        if item in products:
            demand += 12.0 if len(products) == 1 else 6.0
    return demand

def _il_features(obs):
    seat = _seat(obs)
    step = int(obs.get("step", 0) or 0)
    day = int(obs.get("day", step // 24) or 0)
    hour = int(obs.get("hour", step % 24) or 0)
    farms = list(obs.get("farms", []) or [])
    own = farms[seat] if len(farms) > seat else {}
    opp = farms[1-seat] if len(farms) >= 2 else {}
    private = obs.get("private", {}) or {}
    town = obs.get("town", {}) or {}
    shops = list(town.get("unlocked_shops", []) or [])
    market = obs.get("market", {}) or {}
    prices = market.get("prices", {}) or {}
    inventory = market.get("inventory", {}) or {}
    last = _IL_LAST_DELTA.get(seat, {}) or {}
    last_market = last.get("market", {}) or {}

    f = []
    f.extend([
        float(seat),
        step / 719.0,
        day / 30.0,
        hour / 23.0,
        _il_money_scale(own.get("money", 0)),
        _il_money_scale(opp.get("money", 0)),
        _il_clip((float(own.get("money", 0) or 0) - float(opp.get("money", 0) or 0)) / 50000.0),
        _il_clip(float(last.get("own_money", 0) or 0) / 5000.0),
        _il_clip(float(last.get("opp_money", 0) or 0) / 5000.0),
        min(1.0, len(list(own.get("hands", []) or [])) / 20.0),
        min(1.0, len(list(opp.get("hands", []) or [])) / 20.0),
        min(1.0, float(own.get("hires_today", 0) or 0) / 20.0),
        min(1.0, float(opp.get("hires_today", 0) or 0) / 20.0),
        min(1.0, len(list(own.get("unlocked_quadrants", []) or [])) / 4.0),
        min(1.0, len(list(opp.get("unlocked_quadrants", []) or [])) / 4.0),
        min(1.0, len(shops) / 8.0),
    ])

    shop_counts = {s:0 for s in _IL_SHOPS}
    for s in shops:
        if s in shop_counts:
            shop_counts[s] += 1
    for s in _IL_SHOPS:
        f.append(shop_counts[s] / 8.0)
    for pos in range(3):
        value = shops[pos] if pos < len(shops) else None
        for s in _IL_SHOPS:
            f.append(1.0 if value == s else 0.0)

    for p in _IL_PRODUCTS:
        base = _IL_BASE_PRICE[p]
        inv = float(inventory.get(p, 10000) or 0)
        price = float(prices.get(p, base) or 0)
        f.extend([
            _il_clip(price / base, 0.0, 8.0) / 8.0,
            _il_clip((10000.0 - inv) / _IL_SCALE_T[p], -5.0, 5.0) / 5.0,
            _il_clip(_il_known_demand_per_day(shops, p) / 50.0, 0.0, 5.0) / 5.0,
            _il_clip(float(last_market.get(p, 0) or 0) / 100.0, -5.0, 5.0) / 5.0,
        ])

    for farm in (own, opp):
        cc, cy, ac, ay, weeds, pasture, coop, empty_struct = _il_tile_summary(farm)
        for p in _IL_CROPS:
            f.append(min(1.0, cc[p] / 25.0))
        for p in _IL_CROPS:
            f.append(min(1.0, cy[p] / 100.0))
        for a in _IL_ANIMALS:
            f.append(min(1.0, ac[a] / 25.0))
        for a in _IL_ANIMALS:
            f.append(min(1.0, ay[a] / 100.0))
        f.extend([
            min(1.0, weeds / 25.0),
            min(1.0, pasture / 25.0),
            min(1.0, coop / 25.0),
            min(1.0, empty_struct / 25.0),
        ])

    shed = private.get("shed", {}) or {}
    seeds = private.get("seeds", {}) or {}
    inventories = list(private.get("inventories", []) or [])
    for p in _IL_PRODUCTS:
        f.append(min(2.0, max(0.0, float(shed.get(p, 0) or 0)) / 100.0))
    for c in _IL_CROPS:
        f.append(min(2.0, max(0.0, float(seeds.get(c, 0) or 0)) / 100.0))
    carry = {p:0.0 for p in _IL_PRODUCTS}
    for bag in inventories:
        if isinstance(bag, dict):
            for p in _IL_PRODUCTS:
                carry[p] += max(0.0, float(bag.get(p, 0) or 0))
    for p in _IL_PRODUCTS:
        f.append(min(2.0, carry[p] / 100.0))
    return f

def _il_sigmoid(z):
    if z >= 0:
        e = _il_math.exp(-min(60.0, z))
        return 1.0 / (1.0 + e)
    e = _il_math.exp(max(-60.0, z))
    return e / (1.0 + e)

def _il_probability(gate, features):
    bundle = _IL_MODEL_BUNDLE.get(gate) or {}
    if not bundle.get("enabled"):
        return None, None
    mean = bundle.get("mean") or []
    scale = bundle.get("scale") or []
    models = bundle.get("models") or []
    if len(mean) != len(features) or len(scale) != len(features) or not models:
        return None, None
    x = [
        (float(v) - float(m)) / (float(s) if abs(float(s)) > 1e-12 else 1.0)
        for v,m,s in zip(features, mean, scale)
    ]
    probs = []
    for model in models:
        coef = model.get("coef") or []
        if len(coef) != len(x):
            continue
        z = float(model.get("intercept", 0.0))
        z += sum(float(a)*float(b) for a,b in zip(coef, x))
        probs.append(_il_sigmoid(z))
    if not probs:
        return None, None
    p = sum(probs) / len(probs)
    spread = (sum((q-p)*(q-p) for q in probs) / len(probs)) ** 0.5
    return p, spread

def _il_state_hash(obs):
    # Hash only information legitimately present in the current observation.
    # This is used by the training notebook to prove that counterfactual forks
    # share the exact same pre-decision state.
    payload = {
        "step": obs.get("step"),
        "day": obs.get("day"),
        "hour": obs.get("hour"),
        "player": obs.get("player"),
        "farms": obs.get("farms"),
        "private": obs.get("private"),
        "market": obs.get("market"),
        "town": obs.get("town"),
    }
    raw = _il_json.dumps(payload, sort_keys=True, separators=(",",":"), default=str)
    return _il_hashlib.sha256(raw.encode("utf-8")).hexdigest()

def _il_decide(gate, obs, baseline):
    seat = _seat(obs)
    features = _il_features(obs)
    force = _IL_FORCE.get(gate, None)
    p = None
    spread = None
    if force is not None:
        choice = bool(force)
        reason = "forced"
    else:
        p, spread = _il_probability(gate, features)
        bundle = _IL_MODEL_BUNDLE.get(gate) or {}
        threshold = float(bundle.get("threshold", 1.0))
        threshold_hi = float(bundle.get("threshold_hi", threshold))
        threshold_lo = float(bundle.get("threshold_lo", 1.0 - threshold))
        max_spread = float(bundle.get("max_spread", 0.12))
        choice = bool(baseline)
        reason = "fallback"
        if p is not None and spread is not None and spread <= max_spread:
            if p >= threshold_hi:
                choice = True
                reason = "model_hi"
            elif p <= threshold_lo:
                choice = False
                reason = "model_lo"
    _IL_DECISIONS[seat][gate] = {
        "step": int(obs.get("step", 0) or 0),
        "baseline": bool(baseline),
        "choice": bool(choice),
        "p": p,
        "spread": spread,
        "reason": reason,
    }
    if _IL_ENABLE_LOG:
        _IL_LOG[seat].append({
            "gate": gate,
            "step": int(obs.get("step", 0) or 0),
            "state_hash": _il_state_hash(obs),
            "features": list(features),
            "baseline": int(bool(baseline)),
            "choice": int(bool(choice)),
            "p": p,
            "spread": spread,
            "reason": reason,
        })
    return bool(choice)

# Preserve the exact public V21-R1 route internals. Only the three high-level
# branch choices below differ when a high-confidence model overrides the manual rule.
def agent(obs, configuration=None):
    _il_tick(obs)
    step = int(obs.get("step", 0) or 0)
    seat = _seat(obs)
    farms = list(obs.get("farms", []) or [])
    opponent = farms[1 - seat] if len(farms) >= 2 else {}
    opponent_money = float(opponent.get("money", 3000) or 0)
    opponent_hires = int(opponent.get("hires_today", 0) or 0)

    if step == 0:
        _ROUTE[seat] = None
        _MARKET_OVERLAY[seat] = False
        _PREVIOUS_OPPONENT_MONEY[seat] = opponent_money
        _ROUTE_SELECTION[seat] = {"selected": "", "step": None, "signal": None}
        _PENDING_EARLY[seat] = False
        _PENDING_SHOP_ROUTE[seat] = False
        moon_action = _call(_MOON, obs, configuration)
        _call(_MUTOY, obs, configuration)
        _call(_MUNIB_BASE, obs, configuration)
        _call(_MUNIB_FR, obs, configuration)
        return moon_action

    if step == 1 and _ROUTE[seat] is None:
        manual_early = opponent_hires >= 4 and opponent_money <= 20
        use_mutoy = _il_decide("early", obs, manual_early)
        if use_mutoy:
            if _DEFER_EARLY_MUTOY_GATE:
                _PENDING_EARLY[seat] = True
            else:
                _select(seat, "mutoy", step, {"opening_money": opponent_money, "il": True})

    if _ROUTE[seat] == "mutoy":
        _PREVIOUS_OPPONENT_MONEY[seat] = opponent_money
        return _call(_MUTOY, obs, configuration)

    mutoy_action = _call(_MUTOY, obs, configuration) if _PENDING_EARLY[seat] else None
    moon_action = _call(_MOON, obs, configuration)
    munib_base_action = _call(_MUNIB_BASE, obs, configuration)
    munib_action = _call(_MUNIB_FR, obs, configuration)

    if _PENDING_EARLY[seat]:
        if step >= 144:
            shops = tuple(list((obs.get("town") or {}).get("unlocked_shops", []) or [])[:2])
            money_gate = (
                _DEFER_MOON_MAX_OPPONENT_MONEY is None
                or opponent_money <= float(_DEFER_MOON_MAX_OPPONENT_MONEY)
            )
            route = "moon" if shops in _DEFER_MOON_FIRST2 and money_gate else "mutoy"
            _PENDING_EARLY[seat] = False
            _select(
                seat,
                route,
                step,
                {
                    "opening_money": opponent_money,
                    "deferred_first2_shops": list(shops),
                },
            )
        if _ROUTE[seat] == "mutoy":
            return mutoy_action
        if _ROUTE[seat] is None:
            return mutoy_action

    available_shops = tuple(list((obs.get("town") or {}).get("unlocked_shops", []) or []))
    if _PENDING_SHOP_ROUTE[seat] and len(available_shops) >= 3:
        first3 = tuple(available_shops[:3])
        route = _DEFER_ROUTE_BY_FIRST3.get(first3, _DEFER_ROUTE_DEFAULT)
        _PENDING_SHOP_ROUTE[seat] = False
        _select(
            seat,
            route,
            step,
            {
                "shops": list(first3),
                "deferred_shop_route": True,
            },
        )

    previous = _PREVIOUS_OPPONENT_MONEY.get(seat)
    spend = None if previous is None else float(previous) - opponent_money
    if step == 217 and spend is not None:
        manual_overlay = spend >= 100
        _MARKET_OVERLAY[seat] = _il_decide("overlay", obs, manual_overlay)
    _PREVIOUS_OPPONENT_MONEY[seat] = opponent_money

    if (
        _ROUTE[seat] is None
        and not _PENDING_SHOP_ROUTE[seat]
        and moon_action != munib_action
    ):
        shops = tuple(available_shops[:3])
        first2 = tuple(shops[:2])
        if step < 200 and first2 in _DEFER_ROUTE_FIRST2:
            _PENDING_SHOP_ROUTE[seat] = True
            return moon_action
        bakery_regime = len(shops) >= 3 and shops[:3] == ("BAKERY", "BAKERY", "BAKERY")
        extra_regime = len(shops) >= 3 and shops[:3] in _EXTRA_MUNIB_SHOP_REGIMES
        manual_munib = bool(step < 200 or bakery_regime or extra_regime)
        use_munib = _il_decide("route", obs, manual_munib)
        route = "munib" if use_munib else "moon"
        _select(
            seat,
            route,
            step,
            {
                "shops": list(shops),
                "first_action_divergence": True,
                "market_overlay": bool(_MARKET_OVERLAY[seat]),
                "il": True,
            },
        )

    if _ROUTE[seat] == "munib":
        return munib_action
    if _PENDING_SHOP_ROUTE[seat]:
        return moon_action
    if _MARKET_OVERLAY[seat]:
        return _apply_market_delta(moon_action, munib_base_action, munib_action)
    return moon_action

def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)
'''
