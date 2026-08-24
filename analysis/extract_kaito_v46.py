"""Statically extract v46's bundled modules and routes without importing it.

The public agent executes bundled Python at import time.  This utility only
parses its syntax tree, reads literal payload strings, and decodes JSON data.
"""

import argparse
import ast
import base64
import json
from pathlib import Path
import zlib


def assignment(tree, name):
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == name
               for target in node.targets):
            return node.value
    raise ValueError("assignment not found: %s" % name)


def b85_literal(node):
    """Find the literal argument to b85decode below an expression."""
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        func = child.func
        if (isinstance(func, ast.Attribute) and func.attr == "b85decode"
                and child.args):
            value = ast.literal_eval(child.args[0])
            if not isinstance(value, (str, bytes)):
                raise TypeError("b85 payload is not a literal string")
            return value
    raise ValueError("b85decode call not found")


def decode_json(node):
    payload = b85_literal(node)
    raw = base64.b85decode(payload)
    return json.loads(zlib.decompress(raw).decode("utf-8"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("agent", type=Path)
    parser.add_argument("--modules-dir", type=Path,
                        default=Path("agents/kaito_v46_modules"))
    parser.add_argument("--routes", type=Path,
                        default=Path("analysis/kaito_v46_routes.json"))
    args = parser.parse_args()

    source = args.agent.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(args.agent))
    modules = decode_json(assignment(tree, "_V44_MODULES"))
    routes = decode_json(assignment(tree, "_V44_ROUTES"))

    args.modules_dir.mkdir(parents=True, exist_ok=True)
    for name, module_source in modules.items():
        target = args.modules_dir / (name.replace(".", "_") + ".py")
        target.write_text(module_source, encoding="utf-8")
    args.routes.parent.mkdir(parents=True, exist_ok=True)
    args.routes.write_text(json.dumps(routes, indent=2, sort_keys=True),
                           encoding="utf-8")

    print("modules:", len(modules))
    print("routes type:", type(routes).__name__)
    if isinstance(routes, dict):
        print("route keys:", sorted(routes))
    print("wrote:", args.modules_dir, args.routes)


if __name__ == "__main__":
    main()
