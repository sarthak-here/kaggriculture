"""Build Kaito variants that preempt visible non-clone milk competition."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "submit_v46_three_suffix" / "main.py"
OUT = ROOT / "variants" / "kaito_soil_preempt"

CONFIGS = {
    "milk_h12_b10": ("MILK", 12, 10),
    "milk_h24_b10": ("MILK", 24, 10),
    "milk_h48_b10": ("MILK", 48, 10),
    "milk_h24_b20": ("MILK", 24, 20),
    "wheat_h12_b10": ("WHEAT", 12, 10),
    "wheat_h24_b10": ("WHEAT", 24, 10),
    "wheat_h48_b10": ("WHEAT", 48, 10),
    "wheat_h24_b20": ("WHEAT", 24, 20),
}


def main() -> int:
    source = BASE.read_text(encoding="utf-8")
    needle = "'exposure_preempt': False, 'wheat_market_maker': False"
    if source.count(needle) != 1:
        raise RuntimeError("expected one dormant exposure-preempt config")
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (item, lookahead, batch) in CONFIGS.items():
        config = (
            "'exposure_preempt': True, "
            f"'exposure_item': '{item}', "
            "'exposure_active_start': 216, "
            "'exposure_active_stop': 680, "
            f"'exposure_lookahead': {lookahead}, "
            "'exposure_minimum_opponent_animals': 7, "
            "'exposure_minimum_price_ratio': 0.80, "
            f"'exposure_maximum_batch': {batch}, "
            "'wheat_market_maker': False"
        )
        target = OUT / name
        target.mkdir(parents=True, exist_ok=True)
        (target / "main.py").write_text(source.replace(needle, config), encoding="utf-8")
        print(target.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
