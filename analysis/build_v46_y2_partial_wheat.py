"""Build partial late carrot-to-wheat YARN-second variants."""

import ast
import base64
import copy
import json
from pathlib import Path
import zlib

from extract_kaito_v46 import assignment, decode_json


SOURCE = Path("variants/v46_three_suffix/main.py")
OUT = Path("variants/v46_y2_partial_wheat")


def encoded(routes):
    payload = base64.b85encode(zlib.compress(
        json.dumps(routes, separators=(",", ":")).encode(), 9
    )).decode("ascii")
    return ("_V44_ROUTES = json.loads(zlib.decompress(base64.b85decode(%r))"
            ".decode(\"utf-8\"))" % payload)


def mutate(route, count):
    result = copy.deepcopy(route)
    converted = 0
    for action in result[153:]:
        market = action.get("market", []) or []
        for operation in list(market):
            if operation[:2] == ["BUY_SEED", "CARROT"]:
                total = int(operation[2])
                operation[2] = total - count
                market.append(["BUY_SEED", "WHEAT", count])
        units = [action.get("farmer")]
        units.extend(action.get("hands", []) or [])
        for operation in units:
            if (converted < count and isinstance(operation, list)
                    and operation[:2] == ["PLANT", "CARROT"]):
                operation[1] = "WHEAT"
                converted += 1
    if converted != count:
        raise ValueError("converted %d of requested %d" % (converted, count))
    return result


def main():
    source = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(SOURCE))
    node = assignment(tree, "_V44_ROUTES")
    base = decode_json(node)
    lines = source.splitlines(keepends=True)
    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    for count in (2, 4, 6, 8, 10, 12):
        routes = dict(base)
        routes["yarn_second"] = mutate(base["yarn_second"], count)
        variant_lines = list(lines)
        newline = "\r\n" if lines[node.lineno - 1].endswith("\r\n") else "\n"
        variant_lines[node.lineno - 1:node.end_lineno] = [encoded(routes) + newline]
        variant = "".join(variant_lines)
        target = OUT / ("wheat_%02d" % count) / "main.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(variant, encoding="utf-8")
        compile(variant, str(target), "exec")
        index.append({"name": "wheat_%02d" % count, "path": str(target)})
        print("built", target)
    (OUT / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
