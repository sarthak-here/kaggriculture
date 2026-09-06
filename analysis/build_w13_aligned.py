"""Build a W13 variant that keeps the fixed route but disables weed replay."""
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    source = args.source.read_text()
    old = "'controller': 'sparse'"
    new = "'controller': 'aligned'"
    if source.count(old) != 1:
        raise RuntimeError(f"expected one controller setting, found {source.count(old)}")
    candidate = source.replace(old, new)
    args.output.parent.mkdir(parents=True, exist_ok=False)
    args.output.write_text(candidate)
    print(
        {
            "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
            "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
            "changed_bytes": sum(a != b for a, b in zip(source, candidate)),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
