"""Build exact Cha22 variants with only the confirmed-clone sale horizon changed."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "public_candidates/current_20260925/cha22/main.py"
OUT = ROOT / "variants/cha22_clone_horizon_20260926"
OLD = "_RACE_HORIZON_MIRROR=24"


def main() -> None:
    source = BASE.read_text(encoding="utf-8-sig")
    if source.count(OLD) != 1:
        raise ValueError(f"expected exactly one {OLD!r}, found {source.count(OLD)}")
    for horizon in (32, 48, 72):
        target = OUT / f"h{horizon}" / "main.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        revised = source.replace(OLD, f"_RACE_HORIZON_MIRROR={horizon}")
        target.write_text(revised, encoding="utf-8", newline="")
        print(target)


if __name__ == "__main__":
    main()
