"""Build current-rule children from historical route portfolios.

The current Step1010 chassis keeps its market controller, hinge pricing,
shop-prefix selector, execution guards, and final Kaggle entrypoint.  Each
child receives one historical agent's complete ``_V44_ROUTES`` mapping.

Several agents are wrappers around compressed Python parents, so both route
extraction and replacement recurse through zlib/base85 source payloads.  JSON
payloads (modules and routes) are not executed while building.
"""

from __future__ import annotations

import ast
import base64
import hashlib
import json
from pathlib import Path
import zlib


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "variants" / "step1010_brunch_missed_pasture_recovery_20260928" / "main.py"
OUTPUT = ROOT / "variants" / "current_rule_compat_20260930"
DONORS = {
    "v48": ROOT / "public_candidates" / "v48_clear_queue_20260918" / "main.py",
    "v45": ROOT / "variants" / "v45_prefund_10_exported" / "main.py",
    "demand": ROOT / "public_candidates" / "current_20260924" / "demand_timing" / "main.py",
    "marketshock": ROOT / "variants" / "marketshock_callable_fix_20260928" / "main.py",
}


def _offsets(source: str) -> list[int]:
    starts = [0]
    for line in source.splitlines(keepends=True):
        starts.append(starts[-1] + len(line))
    return starts


def _span(source: str, node: ast.AST) -> tuple[int, int]:
    starts = _offsets(source)
    start = starts[node.lineno - 1] + node.col_offset
    end = starts[node.end_lineno - 1] + node.end_col_offset
    return start, end


TARGET_NAMES = ("_R108_DATA", "_V44_ROUTES")


def _payload_value(tree: ast.Module) -> tuple[str, ast.AST] | None:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for name in TARGET_NAMES:
            if any(isinstance(target, ast.Name) and target.id == name
                   for target in node.targets):
                return name, node.value
    return None


def _b85_calls(tree: ast.AST):
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        func = node.func
        if (isinstance(func, ast.Attribute) and func.attr == "b85decode"
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, (str, bytes))):
            yield node, node.args[0]


def _decode_payload(literal: ast.Constant) -> bytes:
    return zlib.decompress(base64.b85decode(literal.value))


def _decode_mapping(value: ast.AST) -> dict:
    for _, literal in _b85_calls(value):
        decoded = _decode_payload(literal)
        routes = json.loads(decoded.decode("utf-8"))
        if not isinstance(routes, dict):
            raise TypeError("portfolio payload is not a mapping")
        return routes
    raise ValueError("portfolio assignment has no literal b85 payload")


def extract_payload(source: str, label: str, depth: int = 0) -> tuple[str, dict]:
    if depth > 12:
        raise ValueError(f"wrapper nesting too deep in {label}")
    tree = ast.parse(source, filename=f"{label}::<{depth}>")
    payload = _payload_value(tree)
    if payload is not None:
        name, value = payload
        return name, _decode_mapping(value)
    for _, literal in _b85_calls(tree):
        try:
            nested = _decode_payload(literal).decode("utf-8")
            ast.parse(nested)
        except (UnicodeDecodeError, ValueError, SyntaxError, zlib.error):
            continue
        try:
            return extract_payload(nested, label, depth + 1)
        except ValueError:
            continue
    raise ValueError(f"portfolio payload not found recursively in {label}")


def _route_expression(routes: dict) -> str:
    raw = json.dumps(routes, separators=(",", ":")).encode("utf-8")
    payload = base64.b85encode(zlib.compress(raw, 9)).decode("ascii")
    return (
        "json.loads(zlib.decompress(base64.b85decode("
        + repr(payload)
        + ")).decode(\"utf-8\"))"
    )


def replace_payload(source: str, target_name: str, data: dict,
                    label: str, depth: int = 0) -> tuple[str, int]:
    if depth > 12:
        raise ValueError(f"wrapper nesting too deep in {label}")
    tree = ast.parse(source, filename=f"{label}::<{depth}>")
    payload = _payload_value(tree)
    if payload is not None:
        name, value = payload
        if name != target_name:
            raise ValueError(f"found {name}, expected {target_name}")
        start, end = _span(source, value)
        return source[:start] + _route_expression(data) + source[end:], depth

    for _, literal in _b85_calls(tree):
        try:
            nested = _decode_payload(literal).decode("utf-8")
            ast.parse(nested)
        except (UnicodeDecodeError, ValueError, SyntaxError, zlib.error):
            continue
        try:
            changed, found_depth = replace_payload(
                nested, target_name, data, label, depth + 1
            )
        except ValueError:
            continue
        packed = base64.b85encode(zlib.compress(changed.encode("utf-8"), 9)).decode("ascii")
        start, end = _span(source, literal)
        return source[:start] + repr(packed) + source[end:], found_depth
    raise ValueError(f"portfolio payload not found recursively in {label}")


def main() -> int:
    base_source = BASE.read_text(encoding="utf-8")
    base_name, base_routes = extract_payload(base_source, str(BASE))
    base_payload = json.dumps(base_routes, separators=(",", ":"), sort_keys=True).encode()
    base_payload_hash = hashlib.sha256(base_payload).hexdigest()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for name, donor in DONORS.items():
        donor_source = donor.read_text(encoding="utf-8")
        donor_name, routes = extract_payload(donor_source, str(donor))
        if donor_name != base_name:
            raise ValueError(f"{name} uses {donor_name}, base uses {base_name}")
        if base_name == "_R108_DATA":
            required = {"actions", "routes", "shops"}
            if not required.issubset(routes) or not required.issubset(base_routes):
                raise ValueError(f"{name} has an incompatible R108 schema")
        elif set(routes) != set(base_routes):
            raise ValueError(
                f"{name} slots differ: base={sorted(base_routes)} donor={sorted(routes)}"
            )
        donor_payload = json.dumps(routes, separators=(",", ":"), sort_keys=True).encode()
        donor_payload_hash = hashlib.sha256(donor_payload).hexdigest()
        if donor_payload_hash == base_payload_hash:
            row = {
                "name": name,
                "base": str(BASE.relative_to(ROOT)),
                "donor": str(donor.relative_to(ROOT)),
                "payload": base_name,
                "payload_sha256": donor_payload_hash,
                "status": "identical_to_base_no_variant_built",
            }
            manifest.append(row)
            print(name, row["status"], donor_payload_hash)
            continue
        candidate, depth = replace_payload(
            base_source, base_name, routes, str(BASE)
        )
        compile(candidate, str(OUTPUT / name / "main.py"), "exec")
        target = OUTPUT / name / "main.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(candidate, encoding="utf-8")
        row = {
            "name": name,
            "base": str(BASE.relative_to(ROOT)),
            "donor": str(donor.relative_to(ROOT)),
            "slots": sorted(routes),
            "payload": base_name,
            "payload_sha256": donor_payload_hash,
            "wrapper_depth": depth,
            "status": "built",
            "sha256": hashlib.sha256(candidate.encode("utf-8")).hexdigest(),
            "path": str(target.relative_to(ROOT)),
        }
        manifest.append(row)
        print(name, "depth", depth, row["sha256"])
    (OUTPUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
