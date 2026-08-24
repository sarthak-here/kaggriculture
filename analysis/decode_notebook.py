"""Decode the agent source embedded in a public Kaggriculture notebook.

Authors ship their agent as a literal blob and reconstruct it in a setup cell.
The encodings vary and our first decoder assumed one shape (b85 + zlib), so it
silently failed on the two notebooks that mattered most:

- stevenleehans  -- b85 with NO compression (the plaintext starts `\"\"\"K`)
- kaitofukami    -- b85 + zlib, but the blob is ~200 concatenated string
                    literals inside a parenthesised expression, so a regex that
                    grabs one quoted run only ever saw the first fragment

So: find every string-literal assignment with `ast` (which joins implicit
concatenation for free), then try each decode path and keep whatever compiles
as Python. Never exec the notebook -- these are other competitors' files.

Usage: python analysis/decode_notebook.py <notebook-dir-or-.ipynb> [out.py]
"""

import ast
import base64
import bz2
import gzip
import hashlib
import io
import json
import lzma
import os
import sys
import tarfile
import zlib

UNWRAP = [
    ("raw", lambda b: b),
    ("zlib", zlib.decompress),
    ("gzip", gzip.decompress),
    ("lzma", lzma.decompress),
    ("bz2", bz2.decompress),
]


def notebook_source(path):
    """Concatenate every code cell. Accepts a .ipynb, a .py, or a directory."""
    if os.path.isdir(path):
        hits = [f for f in os.listdir(path) if f.endswith((".ipynb", ".py"))]
        if not hits:
            raise SystemExit("no notebook or script in %s" % path)
        path = os.path.join(path, sorted(hits)[0])
    if path.endswith(".py"):
        return open(path, encoding="utf-8").read(), path
    nb = json.load(open(path, encoding="utf-8"))
    cells = [c for c in nb["cells"] if c.get("cell_type") == "code"]
    return "\n".join("".join(c.get("source", [])) for c in cells), path


def writefile_cell(path):
    """Some notebooks ship the agent in the clear via `%%writefile main.py`."""
    if os.path.isdir(path):
        hits = [f for f in os.listdir(path) if f.endswith(".ipynb")]
        if not hits:
            return None
        path = os.path.join(path, sorted(hits)[0])
    if not path.endswith(".ipynb"):
        return None
    nb = json.load(open(path, encoding="utf-8"))
    for c in nb["cells"]:
        if c.get("cell_type") != "code":
            continue
        src = "".join(c.get("source", []))
        head = src.lstrip().split("\n", 1)
        if len(head) == 2 and head[0].strip().startswith("%%writefile"):
            if "main.py" in head[0]:
                return head[1]
    return None


def candidate_blobs(src, minlen=1000):
    """Every long string constant assigned to a name, longest first.

    `ast` resolves implicit concatenation, which is the whole point: the
    kaitofukami payload is a parenthesised run of ~200 adjacent literals.
    """
    out = []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return out
    # Resolve literal fragment lists followed by "".join(PAYLOAD_PARTS).
    # Only constants are evaluated; notebook code is never executed.
    symbols = {}
    for node in tree.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        val = node.value
        tgt = node.targets[0] if isinstance(node, ast.Assign) else node.target
        name = getattr(tgt, "id", None)
        if not name:
            continue
        try:
            literal = ast.literal_eval(val)
        except (ValueError, TypeError):
            literal = None
        if isinstance(literal, str):
            symbols[name] = literal
        elif isinstance(literal, (list, tuple)) and all(
            isinstance(part, str) for part in literal
        ):
            symbols[name] = list(literal)
        elif (
            isinstance(val, ast.Call)
            and isinstance(val.func, ast.Attribute)
            and val.func.attr == "join"
            and len(val.args) == 1
            and isinstance(val.args[0], ast.Name)
            and val.args[0].id in symbols
        ):
            try:
                sep = ast.literal_eval(val.func.value)
            except (ValueError, TypeError):
                sep = None
            parts = symbols[val.args[0].id]
            if isinstance(sep, str) and isinstance(parts, list):
                symbols[name] = sep.join(parts)

    for name, value in symbols.items():
        blob = "".join(value) if isinstance(value, list) else value
        if len(blob) >= minlen:
            out.append((name, blob))

    for node in ast.walk(tree):
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        val = node.value
        if isinstance(val, ast.Constant) and isinstance(val.value, str):
            if len(val.value) >= minlen:
                tgt = node.targets[0] if isinstance(node, ast.Assign) else node.target
                name = getattr(tgt, "id", "?")
                out.append((name, val.value))
    # De-duplicate aliases such as PAYLOAD_PARTS and AGENT_PAYLOAD.
    unique = {}
    for name, blob in out:
        unique.setdefault(blob, name)
    return sorted(((name, blob) for blob, name in unique.items()),
                  key=lambda kv: -len(kv[1]))


def as_python(data):
    """Return decoded text if `data` is compilable Python, else None."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return None
    try:
        compile(text, "main.py", "exec")
    except (SyntaxError, ValueError):
        return None
    return text


def from_tar(data):
    """Some payloads are a tarball of the submission; pull main.py out."""
    try:
        tf = tarfile.open(fileobj=io.BytesIO(data))
    except tarfile.TarError:
        return None
    for m in tf.getmembers():
        if m.name.endswith("main.py"):
            f = tf.extractfile(m)
            return as_python(f.read()) if f else None
    return None


def decode(blob):
    """Try b85/b64 x each compressor, then tar. Returns (text, how) or None."""
    text = blob.strip()
    for enc, fn in (("b85", base64.b85decode), ("b64", base64.b64decode)):
        try:
            raw = fn(text)
        except Exception:                                        # noqa: BLE001
            continue
        for label, unwrap in UNWRAP:
            try:
                data = unwrap(raw)
            except Exception:                                    # noqa: BLE001
                continue
            got = as_python(data) or from_tar(data)
            if got:
                return got, "%s+%s" % (enc, label), data
    return None


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    src, path = notebook_source(sys.argv[1])
    print("source: %s (%d chars)" % (os.path.basename(path), len(src)))
    out = sys.argv[2] if len(sys.argv) > 2 else "decoded_agent.py"

    plain = writefile_cell(sys.argv[1])
    if plain and as_python(plain.encode("utf-8")):
        open(out, "w", encoding="utf-8").write(plain)
        print("PLAIN %%writefile main.py -> wrote %s (%d chars)" % (out, len(plain)))
        return

    blobs = candidate_blobs(src)
    # Cell magics can invalidate the concatenated source while the payload cell
    # remains plain Python. Fall back to parsing each code cell independently.
    if not blobs and path.endswith(".ipynb"):
        nb = json.load(open(path, encoding="utf-8"))
        for cell in nb.get("cells", []):
            if cell.get("cell_type") == "code":
                blobs.extend(candidate_blobs("".join(cell.get("source", []))))
        blobs.sort(key=lambda kv: -len(kv[1]))
    print("candidate blobs: %s" % [(n, len(v)) for n, v in blobs[:6]])

    for name, blob in blobs:
        got = decode(blob)
        if not got:
            continue
        text, how, data = got
        print("DECODED %s via %s -> %d bytes, sha256 %s"
              % (name, how, len(data), hashlib.sha256(data).hexdigest()[:16]))
        open(out, "w", encoding="utf-8").write(text)
        print("wrote %s (%d chars)" % (out, len(text)))
        return
    raise SystemExit("no blob decoded to Python")


if __name__ == "__main__":
    main()
