"""Build a current-1.32.7 pricing child of frozen Flexonafft.

The historical agent already routes on observed unlocked shops and caps market
orders at ten.  This builder changes only the three products moved to the hinge
scarcity curve in engine 1.32.7 and extends its local price evaluator with the
engine formula.  The original decoded agent remains untouched.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "agents" / "flexonafft.py"
TARGET = ROOT / "variants" / "flexonafft_current_rules_20260930" / "main.py"


OLD_PARAMS = '''    "CARROT": (35, 10000, 450, "log", 0.2, "sqrt", 0.7),
    "TOMATO": (60, 10000, 200, "linear", 0.4, "sqrt", 0.6),
'''
NEW_PARAMS = '''    "CARROT": (35, 10000, 450, "hinge", 1.0, "sqrt", 0.7),
    "TOMATO": (60, 10000, 200, "hinge", 0.4, "sqrt", 0.6),
'''
OLD_EGG = '    "EGG": (50, 10000, 332, "linear", 0.4, "log", 0.2),'
NEW_EGG = '    "EGG": (50, 10000, 332, "hinge", 0.4, "log", 0.2),'

OLD_PRICE = '''def _shape(name, value):
    value = max(0.0, float(value))
    if name == "linear":
        return value
    if name == "sq":
        return value * value
    if name == "sqrt":
        return math.sqrt(value)
    if name == "log":
        return math.log1p(value)
    if name == "log10":
        return math.log10(1.0 + value)
    raise ValueError(name)


def _market_price(item, inventory):
    base, equilibrium, scale, below_func, below_target, above_func, above_target = _MARKET_PARAMS[item]
    if inventory < equilibrium:
        amplitude = below_target * base / _shape(below_func, scale)
        price = base + amplitude * _shape(below_func, equilibrium - inventory)
    else:
        amplitude = above_target * base / _shape(above_func, scale)
        price = base - amplitude * _shape(above_func, inventory - equilibrium)
    return max(_PRICE_FLOOR, int(round(price)))
'''

NEW_PRICE = '''def _shape(name, value, scale=None):
    value = max(0.0, float(value))
    if name == "linear":
        return value
    if name == "sq":
        return value * value
    if name == "sqrt":
        return math.sqrt(value)
    if name == "log":
        return math.log1p(value)
    if name == "log10":
        return math.log10(1.0 + value)
    if name == "hinge":
        if not scale or scale <= 0:
            return value
        u = value / float(scale)
        return u + 8.0 * max(0.0, u - 1.0) ** 2
    raise ValueError(name)


def _market_price(item, inventory):
    base, equilibrium, scale, below_func, below_target, above_func, above_target = _MARKET_PARAMS[item]
    if inventory < equilibrium:
        amplitude = below_target * base / _shape(below_func, scale, scale)
        price = base + amplitude * _shape(below_func, equilibrium - inventory, scale)
    else:
        amplitude = above_target * base / _shape(above_func, scale, scale)
        price = base - amplitude * _shape(above_func, inventory - equilibrium, scale)
    return max(_PRICE_FLOOR, int(round(price)))
'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise ValueError(f"expected one {label}, found {count}")
    return source.replace(old, new, 1)


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    candidate = replace_once(source, OLD_PARAMS, NEW_PARAMS, "crop parameter block")
    candidate = replace_once(candidate, OLD_EGG, NEW_EGG, "egg parameter")
    candidate = replace_once(candidate, OLD_PRICE, NEW_PRICE, "price evaluator")
    compile(candidate, str(TARGET), "exec")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(candidate, encoding="utf-8")
    print(TARGET)
    print("source_sha256", hashlib.sha256(source.encode()).hexdigest())
    print("target_sha256", hashlib.sha256(candidate.encode()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
