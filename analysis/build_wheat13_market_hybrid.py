"""Build a shop-bucket hybrid of frozen Kaito and the W13 market-phase route.

The first validation blocks localised the market-phase candidate's Kaito losses
to the default and first-YARN routes.  Keep those slots byte-for-byte from
frozen Kaito and use the market-phase route only for second/third-YARN slots.
The output remains a standalone candidate and does not modify either source.
"""

from __future__ import annotations

import argparse
import ast
import base64
import json
from pathlib import Path
import zlib

from extract_kaito_v46 import assignment, decode_json


ROOT = Path(__file__).resolve().parents[1]
KAITO_SLOTS = {"default", "yarn_first", "bakery_capital"}


def encoded(routes: dict) -> str:
    payload = base64.b85encode(zlib.compress(
        json.dumps(routes, separators=(",", ":")).encode("utf-8"), 9
    )).decode("ascii")
    return ("_V44_ROUTES = json.loads(zlib.decompress(base64.b85decode(%r))"
            ".decode(\"utf-8\"))" % payload)


def load_routes(path: Path) -> tuple[str, ast.Assign, dict]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    node = assignment(tree, "_V44_ROUTES")
    return source, node, decode_json(node)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--kaito", type=Path,
        default=ROOT / "submit_v46_three_suffix" / "main.py",
    )
    parser.add_argument(
        "--market", type=Path,
        default=ROOT / "variants" / "wheat13_market_phase" / "main.py",
    )
    parser.add_argument(
        "--target", type=Path,
        default=ROOT / "variants" / "wheat13_market_hybrid" / "main.py",
    )
    args = parser.parse_args()

    market_source, market_node, market_routes = load_routes(args.market)
    _, _, kaito_routes = load_routes(args.kaito)
    if market_routes.keys() != kaito_routes.keys():
        raise ValueError("route slot sets differ")

    routes = {
        name: kaito_routes[name] if name in KAITO_SLOTS else market_routes[name]
        for name in market_routes
    }
    lines = market_source.splitlines(keepends=True)
    newline = "\r\n" if lines[market_node.lineno - 1].endswith("\r\n") else "\n"
    lines[market_node.lineno - 1:market_node.end_lineno] = [encoded(routes) + newline]
    patched = "".join(lines)
    compile(patched, str(args.target), "exec")
    args.target.parent.mkdir(parents=True, exist_ok=True)
    args.target.write_text(patched, encoding="utf-8")
    print(args.target)
    print("Kaito slots:", ", ".join(sorted(KAITO_SLOTS)))
    print("Market slots:", ", ".join(sorted(set(routes) - KAITO_SLOTS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
