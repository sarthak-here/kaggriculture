"""Build isolated current-rule variants with ignored market entries removed."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "analysis" / "current_rule_execution_audit_20260930.json"
OUT_ROOT = ROOT / "variants" / "noop_free_20260930"


SUFFIX = r'''

# Current-rule market normalization: remove entries that Kaggriculture 1.32.7
# silently ignores.  Originals are preserved in their own directories.
_NOOP_FREE_ORIGINAL_AGENT = {callable_name}

def _noop_free_market_action(action):
    if not isinstance(action, dict):
        return action
    market = action.get("market")
    if not isinstance(market, list):
        return action
    cleaned = []
    for order in market:
        if not isinstance(order, list) or not order:
            continue
        op = order[0]
        if op == "PASS":
            continue
        if op in ("BUY_SEED", "BUY_PRODUCT", "BUY_ANIMAL", "SELL"):
            if len(order) < 3:
                continue
            try:
                quantity = int(order[2])
            except (TypeError, ValueError):
                continue
            if quantity <= 0:
                continue
        cleaned.append(order)
    if cleaned == market:
        return action
    normalized = dict(action)
    normalized["market"] = cleaned[:10]
    return normalized

def current_rule_noop_free_agent(obs):
    return _noop_free_market_action(_NOOP_FREE_ORIGINAL_AGENT(obs))
'''


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main():
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    manifest = []
    for name, row in audit["agents"].items():
        source_path = ROOT / row["path"]
        source = source_path.read_text(encoding="utf-8")
        callable_name = row["selected_callable"]
        if not callable_name.isidentifier():
            raise ValueError(f"unsafe callable name for {name}: {callable_name!r}")
        output_dir = OUT_ROOT / name
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / "main.py"
        # Preserve code semantics while keeping generated artifacts diff-clean.
        clean_source = "\n".join(line.rstrip() for line in source.splitlines())
        output = clean_source.rstrip() + "\n" + SUFFIX.format(callable_name=callable_name)
        output_path.write_text(output, encoding="utf-8")
        manifest.append({
            "name": name,
            "source": str(source_path.relative_to(ROOT)),
            "source_sha256": sha256(source.encode("utf-8")),
            "source_callable": callable_name,
            "source_noop_count": row["accepted_noop_count"],
            "source_noop_types": row["accepted_noop_types"],
            "output": str(output_path.relative_to(ROOT)),
            "output_sha256": sha256(output.encode("utf-8")),
        })
        print(f"{name}: {row['accepted_noop_count']} observed no-ops -> {output_path}")
    manifest_path = OUT_ROOT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {manifest_path}")


if __name__ == "__main__":
    main()
