"""Safely extract a hash-verified agent embedded in a public notebook.

Supported formats are literal ``ARCHIVE_B85`` strings, literal chunks appended
to ``ARCHIVE_PARTS``, per-file zlib/base85 ``FILES`` dictionaries, and a plain
``%%writefile .../main.py`` cell. Notebook code is parsed, never executed.

Usage: python analysis/extract_public_notebook_agent.py NOTEBOOK OUTPUT_DIR
"""

from __future__ import annotations

import ast
import base64
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys
import tarfile
import zlib


def _safe_name(name: str) -> str:
    candidate = PurePosixPath(name)
    if candidate.is_absolute() or ".." in candidate.parts:
        raise ValueError(f"unsafe archive path: {name!r}")
    return candidate.as_posix()


def _literal_assignments(source: str) -> dict[str, object]:
    values: dict[str, object] = {}
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                try:
                    values[target.id] = ast.literal_eval(node.value)
                except (ValueError, TypeError):
                    pass
    return values


def _archive_parts(source: str) -> list[str]:
    parts: list[str] = []
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or len(node.args) != 1:
            continue
        func = node.func
        if not (
            isinstance(func, ast.Attribute)
            and func.attr == "append"
            and isinstance(func.value, ast.Name)
            and func.value.id == "ARCHIVE_PARTS"
        ):
            continue
        value = ast.literal_eval(node.args[0])
        if not isinstance(value, str):
            raise ValueError("ARCHIVE_PARTS append is not a literal string")
        parts.append(value)
    return parts


def _extract_tar(blob: bytes) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as archive:
        for member in archive.getmembers():
            name = _safe_name(member.name)
            if not member.isfile():
                raise ValueError(f"non-file archive member: {name!r}")
            handle = archive.extractfile(member)
            if handle is None:
                raise ValueError(f"could not read archive member: {name!r}")
            files[name] = handle.read()
    return files


def _notebook_cells(path: Path) -> list[str]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    return [
        "".join(cell.get("source", []))
        for cell in notebook.get("cells", [])
        if cell.get("cell_type") == "code"
    ]


def extract(path: Path) -> tuple[dict[str, bytes], dict[str, str]]:
    values: dict[str, object] = {}
    parts: list[str] = []
    writefile_main: bytes | None = None
    for source in _notebook_cells(path):
        if source.lstrip().startswith("%%writefile"):
            first, _, remainder = source.partition("\n")
            if first.rstrip().endswith("main.py"):
                writefile_main = remainder.encode("utf-8")
            continue
        try:
            values.update(_literal_assignments(source))
            parts.extend(_archive_parts(source))
        except SyntaxError:
            continue

    expected: dict[str, str] = {}
    if isinstance(values.get("EXPECTED"), dict):
        expected.update(values["EXPECTED"])
    if isinstance(values.get("EXPECTED_MAIN_SHA256"), str):
        expected["main.py"] = values["EXPECTED_MAIN_SHA256"]

    files: dict[str, bytes]
    encoded_archive = values.get("ARCHIVE_B85")
    if isinstance(encoded_archive, str) or parts:
        encoded = encoded_archive if isinstance(encoded_archive, str) else "".join(parts)
        blob = base64.b85decode("".join(encoded.split()).encode("ascii"))
        archive_hash = values.get("EXPECTED_ARCHIVE_SHA256")
        if isinstance(archive_hash, str):
            actual = hashlib.sha256(blob).hexdigest()
            if actual != archive_hash:
                raise ValueError(f"archive hash mismatch: {actual} != {archive_hash}")
        files = _extract_tar(blob)
    elif isinstance(values.get("FILES"), dict):
        files = {
            _safe_name(name): zlib.decompress(base64.b85decode(encoded))
            for name, encoded in values["FILES"].items()
        }
    elif writefile_main is not None:
        files = {"main.py": writefile_main}
    else:
        raise ValueError("no supported literal agent payload found")

    if "main.py" not in files:
        raise ValueError("payload has no top-level main.py")
    for name, digest in expected.items():
        if name not in files:
            raise ValueError(f"expected file missing: {name}")
        actual = hashlib.sha256(files[name]).hexdigest()
        if actual != digest:
            raise ValueError(f"hash mismatch for {name}: {actual} != {digest}")
    compile(files["main.py"], "main.py", "exec")
    return files, {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    source = Path(sys.argv[1])
    destination = Path(sys.argv[2])
    files, hashes = extract(source)
    for name, payload in files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)
        print(f"{hashes[name]}  {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
