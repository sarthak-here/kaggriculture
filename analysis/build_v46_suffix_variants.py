"""Build v46 variants with statically mined, prefix-compatible YARN suffixes."""

import ast
import base64
import gzip
import json
from pathlib import Path
import zlib

from extract_kaito_v46 import assignment, decode_json


SOURCE = Path("agents/current_kaito_v46.py")
MANIFEST = Path("route_mining/active_lineage/compatible_routes.json")
OUT = Path("variants/v46_suffixes")
BRANCH_STEP = 216


def prefix_length(left, right):
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return index
    return min(len(left), len(right))


def replace_assignment(source, node, replacement):
    lines = source.splitlines(keepends=True)
    start = node.lineno - 1
    end = node.end_lineno
    newline = "\r\n" if lines[start].endswith("\r\n") else "\n"
    lines[start:end] = [replacement + newline]
    return "".join(lines)


def main():
    source = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(SOURCE))
    route_node = assignment(tree, "_V44_ROUTES")
    base_routes = decode_json(route_node)
    rows = json.loads(MANIFEST.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    built = []

    for row in rows:
        route_path = Path(row["route_file"])
        with gzip.open(route_path, "rt", encoding="utf-8") as handle:
            candidate = json.load(handle)
        prefix = prefix_length(base_routes["default"], candidate)
        if prefix < BRANCH_STEP or prefix == len(candidate):
            continue

        routes = dict(base_routes)
        routes["yarn_third"] = candidate
        payload = base64.b85encode(zlib.compress(
            json.dumps(routes, separators=(",", ":")).encode("utf-8"), 9
        )).decode("ascii")
        replacement = (
            "_V44_ROUTES = json.loads(zlib.decompress(base64.b85decode(%r))"
            ".decode(\"utf-8\"))" % payload
        )
        variant = replace_assignment(source, route_node, replacement)
        variant = variant.replace(
            "'yarn_third_prefixes': (('BRUNCH_SPOT', 'PET_CAFE'), "
            "('PET_CAFE', 'FARMERS_MARKET'))",
            "'yarn_third_prefixes': (('SMOOTHIE_SHOP', 'SMOOTHIE_SHOP'), "
            "('SMOOTHIE_SHOP', 'BAKERY'))",
        )
        name = "ep%d_p%d" % (row["episode_id"], prefix)
        target = OUT / name / "main.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(variant, encoding="utf-8")
        built.append({"name": name, "path": str(target), **row})
        print("built", name, ">".join(row["shops"][:3]))

    (OUT / "index.json").write_text(json.dumps(built, indent=2),
                                     encoding="utf-8")
    print("built variants", len(built))


if __name__ == "__main__":
    main()
