"""Build Cha22 variants that start its existing strict clone-race guard earlier."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public_candidates/current_20260925/cha22/main.py"
STARTS = (120, 144, 168, 192)
NEEDLE = "if standard and 216<=step<696 and _race_clone(observation,state):"
RESERVE_NEEDLE = "if not 192<=step<696:return action"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    if source.count(NEEDLE) != 1:
        raise ValueError("Cha22 clone-race activation site changed")
    if source.count(RESERVE_NEEDLE) != 1:
        raise ValueError("Cha22 reservation activation site changed")
    manifest = []
    for start in STARTS:
        candidate = source.replace(
            NEEDLE,
            f"if standard and {start}<=step<696 and _race_clone(observation,state):")
        candidate = candidate.replace(
            RESERVE_NEEDLE, f"if not {start}<=step<696:return action")
        output = ROOT / f"variants/cha22_race_reserve_start_{start}_20260926/main.py"
        output.parent.mkdir(parents=True, exist_ok=True)
        compile(candidate, str(output), "exec")
        output.write_text(candidate, encoding="utf-8")
        manifest.append({"start": start, "day": start / 24,
                         "path": str(output.relative_to(ROOT)),
                         "sha256": hashlib.sha256(candidate.encode()).hexdigest()})
    target = ROOT / "analysis/cha22_race_start_variants_20260926.json"
    target.write_text(json.dumps({
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "variants": manifest,
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
