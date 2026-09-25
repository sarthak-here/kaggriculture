"""Statically audit packed Kaggriculture agents without executing their code.

Literal ``exec`` payloads are decoded with the whitelist in decode_notebook.py
and recursively parsed. Dynamic/unresolved execution is always reported.
"""

from __future__ import annotations

import argparse
import ast
import base64
import bz2
import gzip
import json
import lzma
from pathlib import Path
import zlib

from decode_notebook import literal_payload


DANGEROUS_MODULES = {
    "ctypes", "ftplib", "http", "multiprocessing", "os", "pathlib",
    "requests", "shutil", "socket", "subprocess", "urllib",
}
DANGEROUS_CALLS = {
    "eval", "open", "rename", "replace", "rmdir", "rmtree",
    "system", "popen", "unlink", "urlopen", "connect", "send", "sendall",
    "write", "write_bytes", "write_text", "read_bytes", "read_text",
}


def call_name(node: ast.AST) -> str:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def literal_with_aliases(node: ast.AST, aliases: dict[str, str]):
    """Literal codec evaluator that also honors ordinary import aliases."""
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):
        return node.value
    if isinstance(node, (ast.List, ast.Tuple)):
        return [literal_with_aliases(item, aliases) for item in node.elts]
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
        return literal_payload(node)
    if node.func.attr == "join" and len(node.args) == 1:
        separator = literal_with_aliases(node.func.value, aliases)
        parts = literal_with_aliases(node.args[0], aliases)
        if not isinstance(parts, list) or not all(isinstance(x, type(separator)) for x in parts):
            raise ValueError("invalid literal join")
        return separator.join(parts)
    module = getattr(node.func.value, "id", None)
    module = aliases.get(module, module)
    codecs = {
        ("base64", "b85decode"): base64.b85decode,
        ("base64", "b64decode"): base64.b64decode,
        ("zlib", "decompress"): zlib.decompress,
        ("gzip", "decompress"): gzip.decompress,
        ("lzma", "decompress"): lzma.decompress,
        ("bz2", "decompress"): bz2.decompress,
    }
    fn = codecs.get((module, node.func.attr))
    if fn is None or len(node.args) != 1 or node.keywords:
        raise ValueError("unsupported literal codec")
    value = literal_with_aliases(node.args[0], aliases)
    if isinstance(value, str):
        value = value.encode("ascii")
    return fn(value)


def unwrap_exec_arg(node: ast.AST, aliases: dict[str, str]):
    """Return literal exec source, or None when the expression is dynamic."""
    if isinstance(node, ast.Call) and call_name(node.func) == "compile" and node.args:
        node = node.args[0]
    try:
        value = literal_with_aliases(node, aliases)
    except (ValueError, TypeError, OSError, EOFError):
        return None
    if isinstance(value, bytes):
        try:
            return value.decode("utf-8")
        except UnicodeDecodeError:
            return None
    return value if isinstance(value, str) else None


def audit_source(source: str, label: str, depth: int = 0, seen=None):
    seen = set() if seen is None else seen
    key = (label, hash(source))
    if key in seen:
        return []
    seen.add(key)
    findings = []
    try:
        tree = ast.parse(source, filename=label)
    except SyntaxError as exc:
        return [{"kind": "syntax_error", "source": label, "line": exc.lineno, "detail": str(exc)}]

    aliases = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                aliases[alias.asname or alias.name] = alias.name

    for node in ast.walk(tree):
        line = getattr(node, "lineno", None)
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0]
                if root in DANGEROUS_MODULES:
                    findings.append({"kind": "sensitive_import", "source": label, "line": line, "detail": alias.name})
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".", 1)[0]
            if root in DANGEROUS_MODULES:
                findings.append({"kind": "sensitive_import", "source": label, "line": line, "detail": node.module})
        elif isinstance(node, ast.Call):
            name = call_name(node.func)
            leaf = name.rsplit(".", 1)[-1]
            if leaf == "exec":
                nested = unwrap_exec_arg(node.args[0], aliases) if node.args else None
                if nested is None:
                    findings.append({"kind": "unresolved_exec", "source": label, "line": line, "detail": name})
                elif depth >= 12:
                    findings.append({"kind": "exec_depth_limit", "source": label, "line": line, "detail": name})
                else:
                    nested_label = f"{label}:exec@{line}"
                    findings.extend(audit_source(nested, nested_label, depth + 1, seen))
            elif leaf in DANGEROUS_CALLS and ("." not in name or name.split(".", 1)[0] in DANGEROUS_MODULES):
                findings.append({"kind": "sensitive_call", "source": label, "line": line, "detail": name})
    return findings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--json", dest="json_path")
    args = parser.parse_args()
    report = {}
    for raw in args.paths:
        path = Path(raw)
        source = path.read_text(encoding="utf-8-sig")
        findings = audit_source(source, str(path))
        report[str(path)] = {
            "characters": len(source),
            "findings": findings,
            "safe_for_local_test": not findings,
        }
        print(f"{path}: {'PASS' if not findings else 'REVIEW'} ({len(findings)} findings)")
        for finding in findings:
            print(f"  {finding['kind']} {finding['source']}:{finding['line']} {finding['detail']}")
    if args.json_path:
        Path(args.json_path).write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
