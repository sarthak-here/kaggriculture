"""Patch Cha22 only in shop-pair slots with state-compatible live winners."""
import ast
import base64
import copy
import gzip
import hashlib
import json
import os
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public_candidates/current_20260925/cha22/main.py"
CORPUS = ROOT / "analysis/cha22_live_56556133_20260926"
OUTPUT = ROOT / os.environ.get(
    "CHA22_OUTPUT", "variants/cha22_live_exact_portfolio_20260926/main.py")
_EPISODES_DEFAULT = (113563733, 113586509, 113415764, 113536980, 113506542)
_EPISODES_RAW = os.environ.get("CHA22_EPISODES")
EPISODES = (_EPISODES_DEFAULT if _EPISODES_RAW is None else
            tuple(int(value) for value in _EPISODES_RAW.split(",") if value.strip()))
ACTIVE_GUARD = os.environ.get("CHA22_ACTIVE_GUARD", "1") != "0"


def bundle(source):
    tree = ast.parse(source)
    node = next(node for node in tree.body if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "_R108_DATA"
                        for target in node.targets))
    payload = max((item.value for item in ast.walk(node.value)
                   if isinstance(item, ast.Constant) and isinstance(item.value, str)), key=len)
    data = json.loads(zlib.decompress(base64.b85decode(payload)).decode("utf-8"))
    return node, data


def main():
    source = SOURCE.read_text(encoding="utf-8")
    node, original = bundle(source)
    data = copy.deepcopy(original)
    routes = {int(key): [data["actions"][index] for index in indices]
              for key, indices in data["routes"].items()}
    shop_rows = {tuple(row["shops"]): row for row in data["shops"]}
    index = {int(row["episode"]): row for row in json.loads(
        (CORPUS / "specialists/index.json").read_text(encoding="utf-8"))}
    installed = []
    next_route_id = max(routes) + 1
    for episode in EPISODES:
        row = index[episode]
        pair = tuple(row["shop2"])
        if "YARN_STORE" in pair or row["full_prefix"] < 144:
            raise ValueError(f"unsafe candidate {episode}: {pair} prefix {row['full_prefix']}")
        if pair not in shop_rows:
            raise ValueError(f"shop pair absent from router: {pair}")
        source_route_id = int(shop_rows[pair]["route"])
        route_id = next_route_id
        next_route_id += 1
        with gzip.open(CORPUS / "specialists" / row["route_file"], "rt", encoding="utf-8") as handle:
            replacement = json.load(handle)
        if len(replacement) != 719:
            raise ValueError(f"episode {episode}: incomplete route")
        routes[route_id] = replacement
        # Allocate a fresh route ID and change only this exact shop-pair row.
        # The original IDs are deliberately shared by many pairs, so replacing
        # them in-place causes unrelated openings to inherit the specialist.
        shop_rows[pair]["route"] = route_id
        installed.append({**row, "source_route_id": source_route_id,
                          "route_id": route_id,
                          "affected_shop_pairs": ["/".join(pair)]})

    actions = []
    seen = {}
    encoded_routes = {}
    for route_id, route in routes.items():
        indices = []
        for action in route:
            key = json.dumps(action, separators=(",", ":"), sort_keys=True)
            if key not in seen:
                seen[key] = len(actions); actions.append(action)
            indices.append(seen[key])
        encoded_routes[str(route_id)] = indices
    data["actions"] = actions
    data["routes"] = encoded_routes
    packed = json.dumps(data, separators=(",", ":")).encode()
    payload = base64.b85encode(zlib.compress(packed, 9)).decode("ascii")
    replacement = "_R108_DATA=json.loads(zlib.decompress(base64.b85decode(%r)).decode('utf-8'))" % payload
    lines = source.splitlines(keepends=True)
    newline = "\r\n" if lines[node.lineno - 1].endswith("\r\n") else "\n"
    lines[node.lineno - 1:node.end_lineno] = [replacement + newline]
    candidate = "".join(lines)
    global_guard = "for tape in _IMPL.chassis.routes.values():\n        for a in tape[432:719]:"
    active_guard = "for tape in (_IMPL.chassis.routes[native['route']],):\n        for a in tape[432:719]:"
    if candidate.count(global_guard) != 1:
        raise ValueError("expected exactly one global v219 route guard")
    if ACTIVE_GUARD:
        candidate = candidate.replace(global_guard, active_guard)
    compile(candidate, str(OUTPUT), "exec")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(candidate, encoding="utf-8")
    protocol = {
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "candidate": str(OUTPUT.relative_to(ROOT)),
        "candidate_sha256": hashlib.sha256(candidate.encode()).hexdigest(),
        "active_route_guard": ACTIVE_GUARD,
        "installed": installed,
    }
    (OUTPUT.parent / "protocol.json").write_text(
        json.dumps(protocol, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(protocol, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
