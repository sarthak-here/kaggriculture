"""Build Kaito-guarded lean routes sharing an exact early prefix."""

from __future__ import annotations

import argparse
import ast
import base64
import gzip
import json
from pathlib import Path
import zlib

from extract_kaito_v46 import assignment, decode_json
from mine_compatible_routes import prefix_length


ROOT = Path(__file__).resolve().parents[1]


def encoded_routes(routes: dict) -> str:
    payload = base64.b85encode(zlib.compress(
        json.dumps(routes, separators=(",", ":")).encode("utf-8"), 9
    )).decode("ascii")
    return ("_V44_ROUTES = json.loads(zlib.decompress(base64.b85decode(%r))"
            ".decode(\"utf-8\"))" % payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path,
                        default=Path("submit_v46_three_suffix/main.py"))
    parser.add_argument("--manifest", type=Path,
                        default=Path("route_mining/kaito_early_branches/compatible_routes.json"))
    parser.add_argument("--output", type=Path,
                        default=Path("variants/kaito_early_branches"))
    args = parser.parse_args()

    source = (ROOT / args.source).read_text(encoding="utf-8")
    tree = ast.parse(source)
    node = assignment(tree, "_V44_ROUTES")
    routes = decode_json(node)
    lines = source.splitlines(keepends=True)
    rows = json.loads((ROOT / args.manifest).read_text(encoding="utf-8"))
    output = ROOT / args.output
    output.mkdir(parents=True, exist_ok=True)
    built = []

    for row in rows:
        route_file = Path(row["route_file"])
        if not route_file.is_absolute():
            route_file = ROOT / route_file
        with gzip.open(route_file, "rt", encoding="utf-8") as handle:
            candidate = json.load(handle)
        prefix = int(row["prefix"])
        modified = {}
        for name, base in routes.items():
            actual = prefix_length(base, candidate)
            if actual < prefix:
                raise ValueError(f"{row['name']} incompatible with {name}: {actual} < {prefix}")
            modified[name] = base[:prefix] + candidate[prefix:]
        variant_lines = list(lines)
        newline = "\r\n" if lines[node.lineno - 1].endswith("\r\n") else "\n"
        variant_lines[node.lineno - 1:node.end_lineno] = [encoded_routes(modified) + newline]
        variant = "".join(variant_lines)
        compile(variant, row["name"], "exec")
        target = output / row["name"] / "main.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(variant, encoding="utf-8")
        built.append({**row, "path": str(target.relative_to(ROOT))})
        print("built", row["name"])

    (output / "index.json").write_text(json.dumps(built, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
