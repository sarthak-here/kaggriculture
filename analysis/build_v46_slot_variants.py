"""Build isolated v46 variants by replacing one route slot from a manifest."""

import ast
import base64
import gzip
import json
from pathlib import Path
import sys
import zlib

from extract_kaito_v46 import assignment, decode_json


def encoded_routes(routes):
    payload = base64.b85encode(zlib.compress(
        json.dumps(routes, separators=(",", ":")).encode("utf-8"), 9
    )).decode("ascii")
    return (
        "_V44_ROUTES = json.loads(zlib.decompress(base64.b85decode(%r))"
        ".decode(\"utf-8\"))" % payload
    )


def main():
    manifest = Path(sys.argv[1])
    slot = sys.argv[2]
    output = Path(sys.argv[3])
    source_path = Path(sys.argv[4]) if len(sys.argv) > 4 else Path(
        "variants/v46_two_suffix/main.py"
    )
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(source_path))
    node = assignment(tree, "_V44_ROUTES")
    base_routes = decode_json(node)
    rows = json.loads(manifest.read_text(encoding="utf-8"))
    lines = source.splitlines(keepends=True)
    output.mkdir(parents=True, exist_ok=True)
    built = []

    for row in rows:
        with gzip.open(row["route_file"], "rt", encoding="utf-8") as handle:
            route = json.load(handle)
        routes = dict(base_routes)
        routes[slot] = route
        variant_lines = list(lines)
        newline = "\r\n" if lines[node.lineno - 1].endswith("\r\n") else "\n"
        variant_lines[node.lineno - 1:node.end_lineno] = [
            encoded_routes(routes) + newline
        ]
        variant = "".join(variant_lines)
        target = output / row["name"] / "main.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(variant, encoding="utf-8")
        compile(variant, str(target), "exec")
        built.append({**row, "path": str(target)})
        print("built", row["name"])

    (output / "index.json").write_text(json.dumps(built, indent=2),
                                        encoding="utf-8")
    print("built variants", len(built))


if __name__ == "__main__":
    main()
