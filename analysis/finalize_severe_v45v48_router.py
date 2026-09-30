"""Freeze the selected V45/V48-gated Severe router with market normalization."""

from __future__ import annotations

import hashlib
from pathlib import Path

from build_noop_free_cohort import SUFFIX


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT / "variants" / "severe_v45v48_yarn_screen_20260930"
    / "114605783" / "main.py"
)
TARGET = (
    ROOT / "variants" / "severe_v45v48_yarn_114605783_20260930"
    / "main.py"
)


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    selected_callable = "_kaggle_submission_entrypoint"
    normalized = "\n".join(line.rstrip() for line in source.splitlines())
    output = normalized.rstrip() + "\n" + SUFFIX.format(
        callable_name=selected_callable
    )
    compile(output, str(TARGET), "exec")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    output_bytes = output.encode("utf-8")
    TARGET.write_bytes(output_bytes)
    print(TARGET.relative_to(ROOT))
    print("bytes", len(output_bytes))
    print("sha256", hashlib.sha256(output_bytes).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
