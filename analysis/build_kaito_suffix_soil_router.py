"""Compose the mirror-winning Kaito suffix with the observable Soil branch."""

from pathlib import Path

import build_kaito_soil_router as base


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    base.SOURCE = (
        ROOT / "variants" / "kaito_loss_suffixes"
        / "ep100606696_s0_default_p243" / "main.py"
    )
    base.TARGET = ROOT / "variants" / "kaito_suffix_soil_router" / "main.py"
    return base.main()


if __name__ == "__main__":
    raise SystemExit(main())
