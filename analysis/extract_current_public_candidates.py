"""Extract exact agents from the 2026-09-24 public-notebook refresh.

Notebook cells are parsed as Python syntax and only literal assignments are
accepted.  No notebook code is executed.  Every extracted source is compiled
and checked against the SHA-256 published by its notebook when available.
"""
from __future__ import annotations

import ast
import base64
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile
import zlib


ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "public_candidates" / "incoming_20260924"
OUTPUT = ROOT / "public_candidates" / "current_20260924"


def notebook_assignments(path: Path) -> dict[str, object]:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    values: dict[str, object] = {}
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        try:
            tree = ast.parse("".join(cell.get("source", [])))
        except SyntaxError:
            continue
        for node in tree.body:
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if len(targets) != 1 or not isinstance(targets[0], ast.Name):
                continue
            try:
                values[targets[0].id] = ast.literal_eval(node.value)
            except (TypeError, ValueError):
                call = node.value
                if (isinstance(call, ast.Call) and len(call.args) == 1
                        and isinstance(call.func, ast.Attribute)
                        and isinstance(call.func.value, ast.Name)
                        and call.func.value.id == "base64"
                        and call.func.attr == "b64decode"):
                    try:
                        values[targets[0].id] = base64.b64decode(ast.literal_eval(call.args[0]))
                        continue
                    except (TypeError, ValueError):
                        pass
                # Accept only ''.join((literal, ...)); this is how large blobs
                # are split without changing their bytes.
                if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
                        and isinstance(call.func.value, ast.Constant)
                        and call.func.value.value == "" and call.func.attr == "join"
                        and len(call.args) == 1):
                    continue
                try:
                    parts = ast.literal_eval(call.args[0])
                except (TypeError, ValueError):
                    continue
                if isinstance(parts, (tuple, list)) and all(isinstance(x, str) for x in parts):
                    values[targets[0].id] = "".join(parts)
    return values


def tar_main(blob: bytes) -> bytes:
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:*") as archive:
        member = archive.extractfile("main.py")
        if member is None:
            raise RuntimeError("archive lacks root-level main.py")
        return member.read()


def extract_source(name: str, values: dict[str, object]) -> tuple[bytes, str | None]:
    if name == "demand_timing":
        source = tar_main(base64.b64decode(values["ARCHIVE_B64"]))
        expected = str(values["EXPECTED_MAIN_SHA256"])
    elif name == "population_robust":
        source = zlib.decompress(base64.b85decode(values["MAIN_BLOB"]))
        expected = str(values["EXPECTED_MAIN_SHA256"])
    elif name == "rescue7":
        source = tar_main(values["ARCHIVE_BYTES"])
        manifest = values.get("EVALUATION_MANIFEST") or {}
        expected = str(manifest.get("candidate_source_sha256")) if isinstance(manifest, dict) else None
    elif name == "shepherd_ledger":
        source = gzip.decompress(base64.b64decode(values["AGENT_B64"])).replace(b"\r\n", b"\n")
        expected = "ae44d83baf39ae2cf203d3617d0e9d7846d4a8b379b00c3ebd3734f1cfb5fbf3"
    elif name == "v57_funding":
        source = zlib.decompress(base64.b85decode(values["SOURCE_BLOB"]))
        expected = str(values["EXPECTED_MAIN_SHA256"])
    else:
        raise KeyError(name)
    return source, expected


def main() -> None:
    manifest: dict[str, object] = {}
    for folder in sorted(DOWNLOADS.iterdir()):
        if not folder.is_dir():
            continue
        notebook = next(folder.glob("*.ipynb"))
        values = notebook_assignments(notebook)
        source, expected = extract_source(folder.name, values)
        actual = hashlib.sha256(source).hexdigest()
        if expected and actual != expected:
            raise RuntimeError(f"{folder.name}: hash mismatch {actual} != {expected}")
        compile(source, f"{folder.name}/main.py", "exec")
        target = OUTPUT / folder.name / "main.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source)
        manifest[folder.name] = {
            "notebook": str(notebook.relative_to(ROOT)),
            "path": str(target.relative_to(ROOT)),
            "sha256": actual,
            "bytes": len(source),
        }
        print(folder.name, len(source), actual)
    report = ROOT / "analysis" / "current_public_candidates_20260924.json"
    report.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
