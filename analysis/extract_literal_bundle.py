"""Extract a hash-verified length-prefixed notebook bundle without executing it.

Usage: python analysis/extract_literal_bundle.py NOTEBOOK.ipynb OUTPUT_DIR
"""

from __future__ import annotations

import ast
import base64
import hashlib
import json
import lzma
from pathlib import Path
import sys


def literal_assignments(source: str) -> dict[str, object]:
    values: dict[str, object] = {}
    tree = ast.parse(source)
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        if target.id not in {"EXPECTED_SHA256", "PAYLOAD_B85"}:
            continue
        values[target.id] = ast.literal_eval(node.value)
    return values


def notebook_literals(path: Path) -> dict[str, object]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    values: dict[str, object] = {}
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        try:
            values.update(literal_assignments("".join(cell.get("source", []))))
        except SyntaxError:
            continue
    return values


def decode_bundle(encoded: str) -> dict[str, bytes]:
    blob = lzma.decompress(base64.b85decode(encoded))
    cursor = 0
    count = int.from_bytes(blob[cursor:cursor + 2], "big")
    cursor += 2
    files: dict[str, bytes] = {}
    for _ in range(count):
        name_size = int.from_bytes(blob[cursor:cursor + 2], "big")
        cursor += 2
        name = blob[cursor:cursor + name_size].decode("utf-8")
        cursor += name_size
        payload_size = int.from_bytes(blob[cursor:cursor + 8], "big")
        cursor += 8
        payload = blob[cursor:cursor + payload_size]
        cursor += payload_size
        candidate = Path(name)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise ValueError(f"unsafe bundle path: {name!r}")
        files[name] = payload
    if cursor != len(blob):
        raise ValueError(f"trailing bundle bytes: {len(blob) - cursor}")
    return files


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    notebook_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    values = notebook_literals(notebook_path)
    expected = values.get("EXPECTED_SHA256")
    encoded = values.get("PAYLOAD_B85")
    if not isinstance(expected, dict) or not isinstance(encoded, str):
        raise ValueError("notebook lacks literal EXPECTED_SHA256/PAYLOAD_B85")
    files = decode_bundle(encoded)
    if set(files) != set(expected):
        raise ValueError(f"manifest mismatch: files={sorted(files)} expected={sorted(expected)}")
    for name, payload in files.items():
        digest = hashlib.sha256(payload).hexdigest()
        if digest != expected[name]:
            raise ValueError(f"hash mismatch for {name}: {digest} != {expected[name]}")
        target = output_dir / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        print(f"{digest}  {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
