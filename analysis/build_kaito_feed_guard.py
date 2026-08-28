"""Build isolated Kaito descendants with a reserve-safe wheat feed guard."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "submit_v46_three_suffix" / "main.py"
OUT = ROOT / "variants" / "kaito_feed_guard"
MARKER = "\ndef _kaggle_submission_entrypoint(obs, configuration=None):\n"

CONFIGS = {
    "s240_t2_b4_c1000": (240, 2, 4, 1000),
    "s240_t2_b8_c1000": (240, 2, 8, 1000),
    "s240_t4_b8_c1000": (240, 4, 8, 1000),
    "s160_t2_b8_c1500": (160, 2, 8, 1500),
}


WRAPPER = r'''
_KAITO_BASE_AGENT = agent
_KAITO_FEED_CONFIG = {config!r}


def agent(obs, configuration=None):
    result = _KAITO_BASE_AGENT(obs, configuration)
    start, threshold, batch, cash_floor = _KAITO_FEED_CONFIG
    step = int(_v44_get(obs, "step", 0) or 0)
    if step < start or step >= 696:
        return result
    seat = 1 if int(_v44_get(obs, "player", 0) or 0) == 1 else 0
    farms = list(_v44_get(obs, "farms", []) or [])
    farm = farms[seat] if seat < len(farms) else {{}}
    animals = 0
    for row in (_v44_get(farm, "tiles", []) or []):
        for tile in (row or []):
            if isinstance(tile, dict) and tile.get("animal"):
                animals += 1
    if animals <= 0:
        return result
    private = _v44_get(obs, "private", {{}}) or {{}}
    shed = _v44_get(private, "shed", {{}}) or {{}}
    wheat = max(0, int(_v44_get(shed, "WHEAT", 0) or 0))
    if wheat > threshold:
        return result
    market_orders = [list(order) for order in (result.get("market", []) or [])]
    if len(market_orders) >= 10:
        return result
    if any(len(order) >= 2 and order[1] == "WHEAT" for order in market_orders):
        return result
    money = float(_v44_get(farm, "money", 0) or 0)
    prices = _v44_get(_v44_get(obs, "market", {{}}) or {{}}, "prices", {{}}) or {{}}
    quote = max(1, int(_v44_get(prices, "WHEAT", 1) or 1))
    affordable = max(0, int((money - cash_floor) // (quote + 5)))
    quantity = min(batch, affordable)
    if quantity <= 0:
        return result
    market_orders.append(["BUY_PRODUCT", "WHEAT", quantity])
    result["market"] = market_orders
    return result
'''


def main() -> int:
    source = BASE.read_text(encoding="utf-8")
    if source.count(MARKER) != 1:
        raise RuntimeError("submission entrypoint marker not unique")
    OUT.mkdir(parents=True, exist_ok=True)
    for name, config in CONFIGS.items():
        target = OUT / name
        target.mkdir(parents=True, exist_ok=True)
        patched = source.replace(MARKER, WRAPPER.format(config=config) + MARKER)
        (target / "main.py").write_text(patched, encoding="utf-8")
        print(target.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
