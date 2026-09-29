"""Build the severe-loss route with proven Kaito routes in every YARN slot."""

from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import json
from pathlib import Path
import zlib

from extract_kaito_v46 import assignment, decode_json


ROOT = Path(__file__).resolve().parents[1]
YARN_SLOTS = {
    "yarn_first",
    "yarn_second",
    "yarn_third",
    "yarn_third_bakery",
    "yarn_third_farmers",
}


def encoded(routes: dict) -> str:
    payload = base64.b85encode(zlib.compress(
        json.dumps(routes, separators=(",", ":")).encode("utf-8"), 9
    )).decode("ascii")
    return (
        "_V44_ROUTES = json.loads(zlib.decompress(base64.b85decode(%r))"
        ".decode(\"utf-8\"))" % payload
    )


def load_routes(path: Path) -> tuple[str, ast.Assign, dict]:
    source = path.read_text(encoding="utf-8")
    node = assignment(ast.parse(source, filename=str(path)), "_V44_ROUTES")
    return source, node, decode_json(node)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base",
        type=Path,
        default=ROOT / "variants" / "severe_114720494_route_20260928" / "main.py",
    )
    parser.add_argument(
        "--yarn",
        type=Path,
        default=ROOT / "submit_v46_three_suffix" / "main.py",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=ROOT / "variants" / "severe_kaito_yarn_hybrid_20260929" / "main.py",
    )
    args = parser.parse_args()

    base_source, base_node, base_routes = load_routes(args.base)
    _, _, yarn_routes = load_routes(args.yarn)
    if base_routes.keys() != yarn_routes.keys():
        raise ValueError("route slot sets differ")
    missing = YARN_SLOTS - base_routes.keys()
    if missing:
        raise ValueError(f"missing YARN slots: {sorted(missing)}")

    routes = dict(base_routes)
    for name in YARN_SLOTS:
        routes[name] = yarn_routes[name]

    lines = base_source.splitlines(keepends=True)
    newline = "\r\n" if lines[base_node.lineno - 1].endswith("\r\n") else "\n"
    lines[base_node.lineno - 1:base_node.end_lineno] = [encoded(routes) + newline]
    candidate = "".join(lines)
    compile(candidate, str(args.target), "exec")
    args.target.parent.mkdir(parents=True, exist_ok=True)
    args.target.write_text(candidate, encoding="utf-8")
    print(args.target)
    print("SHA256", hashlib.sha256(candidate.encode()).hexdigest())
    print("YARN slots", ", ".join(sorted(YARN_SLOTS)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
