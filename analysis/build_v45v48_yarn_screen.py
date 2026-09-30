"""Retarget preserved Severe YARN bridges to the V45/V48 opening family.

The source candidates already pair Severe's base route with one reconstructed
YARN route.  This builder changes only the opponent gate: activate the route
when the rival's public turn-one state matches the current V45/V48 family.
"""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OLD_RETURN = "    return severe or step1010 or pf_all\n"
NEW_RETURN = """    return (
        hires == 0 and not hands and farmer == [4, 4]
        and abs(money - 2867.0) < 0.01 and center is None
    )
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=ROOT / "variants" / "yarn_bridge_screen_20260930",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=ROOT / "variants" / "severe_v45v48_yarn_screen_20260930",
    )
    args = parser.parse_args()

    count = 0
    for source_path in sorted(args.source.glob("*/main.py")):
        source = source_path.read_text(encoding="utf-8")
        if source.count(OLD_RETURN) != 1:
            raise ValueError(f"unexpected bridge signature in {source_path}")
        candidate = source.replace(OLD_RETURN, NEW_RETURN, 1)
        target_path = args.target / source_path.parent.name / "main.py"
        compile(candidate, str(target_path), "exec")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(candidate, encoding="utf-8")
        print(target_path.relative_to(ROOT))
        count += 1
    if count == 0:
        raise ValueError(f"no candidates found under {args.source}")
    print(f"built {count} V45/V48-gated candidates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
