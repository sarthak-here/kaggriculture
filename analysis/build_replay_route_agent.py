"""Rebuild a replay actor's route inside frozen Kaito execution guards.

The route is copied into every selector slot so this tests the replay policy as
a coherent candidate base.  It does not claim state-compatible suffixing.
"""

from __future__ import annotations

import argparse
import ast
import base64
import json
from pathlib import Path
import zlib

from extract_kaito_v46 import assignment, decode_json
from mine_compatible_routes import route_of


ROOT = Path(__file__).resolve().parents[1]


def encoded(routes: dict) -> str:
    payload = base64.b85encode(zlib.compress(
        json.dumps(routes, separators=(",", ":")).encode("utf-8"), 9
    )).decode("ascii")
    return ("_V44_ROUTES = json.loads(zlib.decompress(base64.b85decode(%r))"
            ".decode(\"utf-8\"))" % payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("replay", type=Path)
    parser.add_argument("seat", type=int, choices=(0, 1))
    parser.add_argument("target", type=Path)
    parser.add_argument("--source", type=Path,
                        default=ROOT / "submit_v46_three_suffix" / "main.py")
    args = parser.parse_args()

    source = args.source.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(args.source))
    node = assignment(tree, "_V44_ROUTES")
    route_names = decode_json(node).keys()
    replay = json.loads(args.replay.read_text(encoding="utf-8"))
    route = route_of(replay, args.seat)
    routes = {name: route for name in route_names}

    lines = source.splitlines(keepends=True)
    newline = "\r\n" if lines[node.lineno - 1].endswith("\r\n") else "\n"
    lines[node.lineno - 1:node.end_lineno] = [encoded(routes) + newline]
    patched = "".join(lines)
    compile(patched, str(args.target), "exec")
    args.target.parent.mkdir(parents=True, exist_ok=True)
    args.target.write_text(patched, encoding="utf-8")
    print(args.target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
