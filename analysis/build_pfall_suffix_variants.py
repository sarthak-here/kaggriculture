"""Build isolated pf_all variants from statically mined compatible suffixes."""

import argparse
import ast
import base64
import gzip
import json
from pathlib import Path
import re
import zlib

from extract_kaito_v46 import assignment, decode_json
from mine_compatible_routes import prefix_length
from mine_pfall_compatible_suffixes import ROUTE_VARS


def encoded_assignment(name, value):
    payload = base64.b85encode(zlib.compress(
        json.dumps(value, separators=(",", ":")).encode("utf-8"), 9
    )).decode("ascii")
    return ("%s = json.loads(zlib.decompress(base64.b85decode(%r))"
            ".decode('utf-8'))" % (name, payload))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", type=Path, default=Path("submit_pf_all/main.py"))
    parser.add_argument("--manifest", type=Path,
                        default=Path("route_mining/pfall_compatible/compatible_routes.json"))
    parser.add_argument("--output", type=Path, default=Path("variants/pfall_suffixes"))
    args = parser.parse_args()

    source = args.agent.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(args.agent))
    nodes = {label: assignment(tree, variable)
             for label, variable in ROUTE_VARS.items()}
    bases = {label: decode_json(node) for label, node in nodes.items()}
    rows = json.loads(args.manifest.read_text(encoding="utf-8"))["candidates"]
    args.output.mkdir(parents=True, exist_ok=True)

    built = []
    for row in rows:
        label = row["bucket"]
        route_path = Path(row["route_file"])
        with gzip.open(route_path, "rt", encoding="utf-8") as handle:
            candidate = json.load(handle)
        prefix = prefix_length(bases[label], candidate)
        if prefix != row["prefix"]:
            raise ValueError("prefix mismatch for %s" % route_path)
        merged = bases[label][:prefix] + candidate[prefix:]
        node = nodes[label]
        variable = ROUTE_VARS[label]
        lines = source.splitlines(keepends=True)
        newline = "\r\n" if lines[node.lineno - 1].endswith("\r\n") else "\n"
        lines[node.lineno - 1:node.end_lineno] = [
            encoded_assignment(variable, merged) + newline
        ]
        variant = "".join(lines)
        compile(variant, str(args.agent), "exec")
        short_bucket = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
        name = "ep%d_s%d_p%d_%s" % (
            row["episode_id"], row["seat"], prefix, short_bucket)
        target = args.output / name / "main.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(variant, encoding="utf-8")
        built.append({**row, "name": name, "agent": str(target)})
        print("built", name)

    target = args.output / "manifest.json"
    target.write_text(json.dumps(built, indent=2), encoding="utf-8")
    print("built", len(built), "variants; wrote", target)


if __name__ == "__main__":
    main()