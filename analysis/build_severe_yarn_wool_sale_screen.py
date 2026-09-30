"""Build bounded wool-sale timing variants on the strict Severe YARN router."""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "variants" / "severe_yarn_late3_swap_20260930" / "main.py"
OUT = ROOT / "variants" / "severe_yarn_wool_sale_screen_20260930"

VARIANTS = {
    "existing_front": ("existing", 0, 0),
    "eager_front_t4": ("eager", 4, 0),
    "eager_front_t8": ("eager", 8, 0),
    "price200_front_t4": ("eager", 4, 200),
    "price220_front_t4": ("eager", 4, 220),
    "price240_front_t4": ("eager", 4, 240),
}

LAYER = r'''

_WOOL_MODE = {mode!r}
_WOOL_THRESHOLD = {threshold}
_WOOL_MIN_PRICE = {minimum_price}


def _severe_private_wool(obs):
    private = _v44_get(obs, "private", {{}}) or {{}}
    inventories = list(_v44_get(private, "inventories", []) or [])
    total = 0
    for inventory in inventories:
        try:
            total += int(_v44_get(inventory, "WOOL", 0) or 0)
        except (TypeError, ValueError):
            pass
    return total


def severe_yarn_wool_sale_agent(obs, configuration=None):
    action = severe_yarn_late3_swap_agent(obs)
    step = int(_v44_get(obs, "step", 0) or 0)
    if _LATE_SCREEN_MODE != "specialist" or step < 153:
        return action
    market = [list(order) for order in list(action.get("market", []) or [])]
    wool_indices = [
        index for index, order in enumerate(market)
        if len(order) >= 3 and order[0] == "SELL" and order[1] == "WOOL"
    ]
    if _WOOL_MODE == "existing":
        if not wool_indices or wool_indices[0] == 0:
            return action
        sale = market.pop(wool_indices[0])
        market.insert(0, sale)
    else:
        stock = _severe_private_wool(obs)
        prices = _v44_get(_v44_get(obs, "market", {{}}) or {{}}, "prices", {{}}) or {{}}
        price = float(_v44_get(prices, "WOOL", 0) or 0)
        if stock < _WOOL_THRESHOLD or price < _WOOL_MIN_PRICE:
            return action
        if wool_indices:
            sale = market.pop(wool_indices[0])
            sale[2] = max(int(sale[2]), stock)
            for index in reversed(wool_indices[1:]):
                market.pop(index - 1)
        elif len(market) < 10:
            sale = ["SELL", "WOOL", stock]
        else:
            return action
        market.insert(0, sale)
    out = dict(action)
    out["market"] = market[:10]
    return out
'''


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8").rstrip()
    for name, (mode, threshold, minimum_price) in VARIANTS.items():
        target = OUT / name / "main.py"
        output = source + "\n" + LAYER.format(
            mode=mode,
            threshold=threshold,
            minimum_price=minimum_price,
        )
        compile(output, str(target), "exec")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(output, encoding="utf-8")
        print(target.relative_to(ROOT))


if __name__ == "__main__":
    main()
