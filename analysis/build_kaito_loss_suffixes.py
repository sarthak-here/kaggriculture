"""Build isolated Kaito descendants with one exact-prefix loss suffix."""

import argparse
import ast
import base64
import gzip
import json
from pathlib import Path
import zlib

from extract_kaito_v46 import assignment, decode_json
from mine_compatible_routes import prefix_length


def encoded_routes(routes):
    payload = base64.b85encode(zlib.compress(
        json.dumps(routes, separators=(",", ":")).encode("utf-8"), 9
    )).decode("ascii")
    return ("_V44_ROUTES = json.loads(zlib.decompress(base64.b85decode(%r))"
            ".decode(\"utf-8\"))" % payload)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path,
                        default=Path("submit_v46_three_suffix/main.py"))
    parser.add_argument("--manifest", type=Path,
                        default=Path("route_mining/kaito_loss_suffixes/compatible_routes.json"))
    parser.add_argument("--output", type=Path,
                        default=Path("variants/kaito_loss_suffixes"))
    args = parser.parse_args()

    source = args.source.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(args.source))
    node = assignment(tree, "_V44_ROUTES")
    routes = decode_json(node)
    lines = source.splitlines(keepends=True)
    rows = json.loads(args.manifest.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    built = []

    for row in rows:
        with gzip.open(row["route_file"], "rt", encoding="utf-8") as handle:
            candidate = json.load(handle)
        slot = row["slot"]
        prefix = prefix_length(routes[slot], candidate)
        if prefix != row["prefix"]:
            raise ValueError("prefix mismatch for %s" % row["name"])
        modified = dict(routes)
        modified[slot] = routes[slot][:prefix] + candidate[prefix:]
        variant_lines = list(lines)
        newline = "\r\n" if lines[node.lineno - 1].endswith("\r\n") else "\n"
        variant_lines[node.lineno - 1:node.end_lineno] = [
            encoded_routes(modified) + newline
        ]
        variant = "".join(variant_lines)
        compile(variant, row["name"], "exec")
        target = args.output / row["name"] / "main.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(variant, encoding="utf-8")
        built.append({**row, "path": str(target)})
        print("built", row["name"])

    target = args.output / "index.json"
    target.write_text(json.dumps(built, indent=2), encoding="utf-8")
    print("wrote", target)


if __name__ == "__main__":
    main()