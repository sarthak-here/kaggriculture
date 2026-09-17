"""Extract and hash-verify the public jaxa623 2780 notebook artifact."""
import ast
import base64
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "kaggle_downloads/jaxa623_2780_worlds_95cis/2780-beyond-48-0-128-128-worlds-with-95-cis.ipynb"
OUT = ROOT / "public_candidates/jaxa2780_20260917/main.py"


def assignment(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return ast.literal_eval(node.value)
    raise KeyError(name)


def main():
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    source = next(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code" and "BLOB =" in "".join(cell.get("source", []))
    )
    tree = ast.parse(source)
    blob = assignment(tree, "BLOB")
    expected = assignment(tree, "MAIN_SHA256")
    raw = gzip.decompress(base64.b85decode(blob))
    actual = hashlib.sha256(raw).hexdigest()
    assert actual == expected
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(raw)
    provenance = {
        "notebook": "jaxa623/2780-beyond-48-0-128-128-worlds-with-95-cis",
        "main_sha256": actual,
        "extracted_from": str(NOTEBOOK.relative_to(ROOT)),
    }
    (OUT.parent / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(OUT.relative_to(ROOT), len(raw), actual)


if __name__ == "__main__":
    main()
