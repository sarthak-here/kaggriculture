"""Build v46 with separate compatible suffixes for its three pf_all losses."""

import ast
import base64
import gzip
import json
from pathlib import Path
import zlib

from extract_kaito_v46 import assignment, decode_json


SOURCE = Path("agents/current_kaito_v46.py")
TARGET = Path("variants/v46_three_suffix/main.py")
SMOOTHIE_SMOOTHIE = Path(
    "route_mining/active_lineage/route-98451967-seat0.json.gz"
)
SMOOTHIE_BAKERY = Path(
    "route_mining/active_lineage/route-98276177-seat0.json.gz"
)
BRANCH_STEP = 216


def load_route(path):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def prefix_length(left, right):
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return index
    return min(len(left), len(right))


def tomato_route(route):
    route = json.loads(json.dumps(route))
    for action in route[BRANCH_STEP:]:
        operations = [action.get("farmer")]
        operations.extend(action.get("hands", []) or [])
        operations.extend(action.get("market", []) or [])
        for operation in operations:
            if (isinstance(operation, list) and len(operation) > 1
                    and operation[1] == "CARROT"):
                operation[1] = "TOMATO"
    return route


def encoded_assignment(name, value):
    payload = base64.b85encode(zlib.compress(
        json.dumps(value, separators=(",", ":")).encode("utf-8"), 9
    )).decode("ascii")
    return (
        "%s = json.loads(zlib.decompress(base64.b85decode(%r))"
        ".decode(\"utf-8\"))" % (name, payload)
    )


def main():
    source = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(SOURCE))
    module_node = assignment(tree, "_V44_MODULES")
    route_node = assignment(tree, "_V44_ROUTES")
    modules = decode_json(module_node)
    routes = decode_json(route_node)

    first = load_route(SMOOTHIE_SMOOTHIE)
    second = load_route(SMOOTHIE_BAKERY)
    third = tomato_route(first)
    for label, route in (("smoothie/smoothie", first),
                         ("smoothie/bakery", second),
                         ("farmers/pizza tomato", third)):
        prefix = prefix_length(routes["default"], route)
        if prefix < BRANCH_STEP:
            raise ValueError("%s route diverges at %d" % (label, prefix))
        print(label, "compatible prefix", prefix)

    routes["yarn_third"] = first
    routes["yarn_third_bakery"] = second
    routes["yarn_third_farmers"] = third

    gold = modules["v44.gold_floor"]
    old_routes = 'ROUTES = ("default", "yarn_first", "yarn_second", "yarn_third")'
    new_routes = (
        'ROUTES = ("default", "yarn_first", "yarn_second", "yarn_third", '
        '"yarn_third_bakery", "yarn_third_farmers")'
    )
    if gold.count(old_routes) != 1:
        raise ValueError("ROUTES marker not unique")
    gold = gold.replace(old_routes, new_routes)
    marker = "    if (\n        config.yarn_third_enabled\n"
    alt = (
        "    if (\n"
        "        config.yarn_third_enabled\n"
        "        and len(shops) >= 3\n"
        "        and (shops[0], shops[1], shops[2])\n"
        "        == ('FARMERS_MARKET', 'PIZZA_SHOP', 'YARN_STORE')\n"
        "        and step >= int(config.yarn_third_start)\n"
        "    ):\n"
        "        return 'yarn_third_farmers'\n"
        "    if (\n"
        "        config.yarn_third_enabled\n"
        "        and len(shops) >= 3\n"
        "        and (shops[0], shops[1], shops[2])\n"
        "        == ('SMOOTHIE_SHOP', 'BAKERY', 'YARN_STORE')\n"
        "        and step >= int(config.yarn_third_start)\n"
        "    ):\n"
        "        return 'yarn_third_bakery'\n"
        "    if (\n"
        "        config.yarn_third_enabled\n"
    )
    if gold.count(marker) != 1:
        raise ValueError("yarn-third marker not unique")
    modules["v44.gold_floor"] = gold.replace(marker, alt)

    replacements = {
        module_node.lineno - 1: (
            module_node.end_lineno,
            encoded_assignment("_V44_MODULES", modules),
        ),
        route_node.lineno - 1: (
            route_node.end_lineno,
            encoded_assignment("_V44_ROUTES", routes),
        ),
    }
    lines = source.splitlines(keepends=True)
    for start in sorted(replacements, reverse=True):
        end, replacement = replacements[start]
        newline = "\r\n" if lines[start].endswith("\r\n") else "\n"
        lines[start:end] = [replacement + newline]
    variant = "".join(lines)
    variant = variant.replace(
        "'yarn_third_prefixes': (('BRUNCH_SPOT', 'PET_CAFE'), "
        "('PET_CAFE', 'FARMERS_MARKET'))",
        "'yarn_third_prefixes': (('SMOOTHIE_SHOP', 'SMOOTHIE_SHOP'),)",
    )
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(variant, encoding="utf-8")
    compile(variant, str(TARGET), "exec")
    print("wrote", TARGET, "bytes", len(variant.encode("utf-8")))


if __name__ == "__main__":
    main()
