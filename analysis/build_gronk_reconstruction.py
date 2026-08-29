"""Reconstruct Gronk's episode-102674510 action route inside frozen Kaito guards."""

from __future__ import annotations

import ast
import base64
import json
from pathlib import Path
import zlib

from extract_kaito_v46 import assignment, decode_json
from mine_compatible_routes import route_of


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "submit_v46_three_suffix" / "main.py"
REPLAY = ROOT / "loss_analysis" / "kaito_soil_router_current" / "episode-102674510-replay.json"
TARGET = ROOT / "variants" / "panel_gronk" / "main.py"


def encoded(routes: dict) -> str:
    payload = base64.b85encode(zlib.compress(
        json.dumps(routes, separators=(",", ":")).encode("utf-8"), 9
    )).decode("ascii")
    return ("_V44_ROUTES = json.loads(zlib.decompress(base64.b85decode(%r))"
            ".decode(\"utf-8\"))" % payload)


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    node = assignment(tree, "_V44_ROUTES")
    route_names = decode_json(node).keys()
    replay = json.loads(REPLAY.read_text(encoding="utf-8"))
    route = route_of(replay, 0)
    routes = {name: route for name in route_names}
    lines = source.splitlines(keepends=True)
    newline = "\r\n" if lines[node.lineno - 1].endswith("\r\n") else "\n"
    lines[node.lineno - 1:node.end_lineno] = [encoded(routes) + newline]
    patched = "".join(lines)
    compile(patched, str(TARGET), "exec")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(patched, encoding="utf-8")
    print(TARGET.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
