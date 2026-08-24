"""Build Farmers/Pizza/YARN crop mutants from the best compatible suffix."""

import ast
import base64
import copy
import json
from pathlib import Path
import zlib

from extract_kaito_v46 import assignment, decode_json


SOURCE = Path("variants/v46_fp_allseats/ep96863782_s1_p216/main.py")
OUT = Path("variants/v46_tomato_mutants")


def encoded(routes):
    payload = base64.b85encode(zlib.compress(
        json.dumps(routes, separators=(",", ":")).encode(), 9
    )).decode("ascii")
    return ("_V44_ROUTES = json.loads(zlib.decompress(base64.b85decode(%r))"
            ".decode(\"utf-8\"))" % payload)


def mutate(route, mode):
    result = copy.deepcopy(route)
    delayed = []
    for step in range(216, len(result)):
        action = result[step]
        for key in ("farmer", "hands", "market"):
            value = action.get(key)
            if not value:
                continue
            rows = value if key in ("hands", "market") else [value]
            kept = []
            for operation in rows:
                operation = list(operation)
                if len(operation) > 1 and operation[1] == "CARROT":
                    if operation[0] in ("BUY_SEED", "PLANT"):
                        operation[1] = "TOMATO"
                    elif operation[0] == "SELL":
                        if mode == "all":
                            operation[1] = "TOMATO"
                        elif mode == "late":
                            operation[1] = "TOMATO"
                            delayed.append(operation)
                            continue
                        elif mode == "hold":
                            continue
                kept.append(operation)
            action[key] = kept if key in ("hands", "market") else (
                kept[0] if kept else ["PASS"]
            )
    if mode == "late":
        for offset, operation in enumerate(delayed):
            target = 690 + offset
            result[target].setdefault("market", []).append(operation)
    return result


def main():
    source = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(SOURCE))
    node = assignment(tree, "_V44_ROUTES")
    base = decode_json(node)
    lines = source.splitlines(keepends=True)
    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    for mode in ("all", "hold", "late"):
        routes = dict(base)
        routes["yarn_third"] = mutate(base["yarn_third"], mode)
        variant_lines = list(lines)
        newline = "\r\n" if lines[node.lineno - 1].endswith("\r\n") else "\n"
        variant_lines[node.lineno - 1:node.end_lineno] = [encoded(routes) + newline]
        variant = "".join(variant_lines)
        target = OUT / ("tomato_" + mode) / "main.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(variant, encoding="utf-8")
        compile(variant, str(target), "exec")
        index.append({"name": "tomato_" + mode, "path": str(target)})
        print("built", target)
    (OUT / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
