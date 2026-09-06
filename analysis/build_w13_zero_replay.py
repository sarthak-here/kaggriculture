"""Build W13 with DIG+retry weed repair but no delayed replay tail."""
from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import json
from pathlib import Path
import zlib


def assignment(source: str, name: str):
    return next(
        node
        for node in ast.parse(source).body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == name for target in node.targets)
    )


def decode(node):
    payload = max(
        (
            value.value
            for value in ast.walk(node.value)
            if isinstance(value, ast.Constant) and isinstance(value.value, str)
        ),
        key=len,
    )
    return json.loads(zlib.decompress(base64.b85decode(payload)))


def encode(name: str, value) -> str:
    payload = base64.b85encode(
        zlib.compress(json.dumps(value, separators=(",", ":")).encode(), 9)
    ).decode()
    return (
        f"{name} = json.loads(zlib.decompress(base64.b85decode({payload!r}))"
        '.decode("utf-8"))\n'
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    source = args.source.read_text()
    node = assignment(source, "_V44_MODULES")
    modules = decode(node)
    planner = modules["v23.planner"]
    old = "weed_replay_steps: int = 8"
    new = "weed_replay_steps: int = 0"
    if planner.count(old) != 1:
        raise RuntimeError(f"expected one replay setting, found {planner.count(old)}")
    modules["v23.planner"] = planner.replace(old, new)
    lines = source.splitlines(keepends=True)
    lines[node.lineno - 1 : node.end_lineno] = [encode("_V44_MODULES", modules)]
    candidate = "".join(lines)
    compile(candidate, str(args.output), "exec")
    args.output.parent.mkdir(parents=True, exist_ok=False)
    args.output.write_text(candidate)
    print(
        {
            "source_sha256": hashlib.sha256(args.source.read_bytes()).hexdigest(),
            "output_sha256": hashlib.sha256(args.output.read_bytes()).hexdigest(),
            "module": "v23.planner",
            "weed_replay_steps": 0,
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
