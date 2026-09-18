"""Extract and hash-verify the user-provided V48 notebook artifact."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = Path(r"C:\Users\sarthak\Desktop\kaggriculture-v48-clear-the-queue.ipynb")
OUT = ROOT / "public_candidates/v48_clear_queue_20260918/main.py"


def assigned(tree, name):
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return node.value
    raise KeyError(name)


def main():
    notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    source = next(
        "".join(cell.get("source", []))
        for cell in notebook["cells"]
        if cell.get("cell_type") == "code" and "SOURCE_BYTES = b''.join" in "".join(cell.get("source", []))
    )
    tree = ast.parse(source)
    expected = ast.literal_eval(assigned(tree, "EXPECTED_MAIN_SHA256"))
    join_call = assigned(tree, "SOURCE_BYTES")
    assert isinstance(join_call, ast.Call) and join_call.args
    chunks = ast.literal_eval(join_call.args[0])
    raw = b"".join(chunks)
    actual = hashlib.sha256(raw).hexdigest()
    assert actual == expected, (actual, expected)
    compile(raw, "main.py", "exec")
    parsed = ast.parse(raw)
    entrypoint = [node.name for node in parsed.body if isinstance(node, ast.FunctionDef)][-1]
    assert entrypoint == "_e335_agent"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(raw)
    provenance = {
        "notebook": str(NOTEBOOK),
        "main_sha256": actual,
        "entrypoint": entrypoint,
        "notebook_claim": "36-0-0 over 72 games comparing V48 and V47 across three worlds and six opponent sources",
    }
    (OUT.parent / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(OUT.relative_to(ROOT), len(raw), actual, entrypoint)


if __name__ == "__main__":
    main()
