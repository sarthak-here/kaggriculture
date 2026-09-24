"""Install complete rank-1 replay routes inside the modern v350 controller stack."""

from __future__ import annotations

import ast
import base64
import gzip
import hashlib
import json
from pathlib import Path
import re
import zlib

from mine_compatible_routes import route_of


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "variants" / "panel23_demand_full" / "main.py"
REPLAYS = ROOT / "replays_rank1_20260924"
OUTPUT = ROOT / "variants" / "rank1_modern_guard_routes_20260924"


def decode_payload(source):
    tree = ast.parse(source)
    node = next(item for item in tree.body
                if isinstance(item, ast.Assign) and
                any(isinstance(target, ast.Name) and target.id == "_R108_DATA"
                    for target in item.targets))
    payload = max((item.value for item in ast.walk(node.value)
                   if isinstance(item, ast.Constant) and isinstance(item.value, str)),
                  key=len)
    return json.loads(zlib.decompress(base64.b85decode(payload)))


def encode_route(data, route):
    actions = []
    lookup = {}
    indices = []
    for action in route:
        key = json.dumps(action, sort_keys=True, separators=(",", ":"))
        index = lookup.get(key)
        if index is None:
            index = len(actions)
            lookup[key] = index
            actions.append(action)
        indices.append(index)
    return {
        "actions": actions,
        "routes": {key: list(indices) for key in data["routes"]},
        "shops": data["shops"],
    }


def main():
    source = SOURCE.read_text(encoding="utf-8")
    data = decode_payload(source)
    assignment = re.compile(r"^_R108_DATA=.*$", re.MULTILINE)
    if len(assignment.findall(source)) != 1:
        raise RuntimeError("unexpected _R108_DATA assignment count")
    manifest = json.loads((REPLAYS / "manifest.json").read_text(encoding="utf-8"))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    index = []
    for row in manifest:
        episode = int(row["episode_id"])
        seat = int(row["seat"])
        with gzip.open(REPLAYS / f"episode-{episode}-replay.json.gz",
                       "rt", encoding="utf-8") as handle:
            replay = json.load(handle)
        route = route_of(replay, seat)
        revised = encode_route(data, route)
        packed = json.dumps(revised, separators=(",", ":")).encode()
        blob = base64.b85encode(zlib.compress(packed, 9)).decode("ascii")
        replacement = ("_R108_DATA=json.loads(zlib.decompress(base64.b85decode(" +
                       repr(blob) + ")))" )
        candidate = assignment.sub(replacement, source, count=1)
        opening = route[0]
        candidate += f'''\n\n# Preserve the source route's universal step-0 state before modern guards continue.
_R1MG_PARENT=_panel23_submission_entry
_R1MG_OPENING={opening!r}
_R1MG_REPORT={{"opening_overrides":0,"errors":0}}
def rank1_modern_guard_agent(observation,configuration=None):
    action=_R1MG_PARENT(observation,configuration)
    try:
        if int(observation.get("step",0))==0:
            _R1MG_REPORT.update(opening_overrides=1,errors=0)
            return {{"farmer":list(_R1MG_OPENING["farmer"]),
                    "hands":[list(value) for value in _R1MG_OPENING["hands"]],
                    "market":[list(value) for value in _R1MG_OPENING["market"]]}}
    except Exception:
        _R1MG_REPORT["errors"]+=1
    return action
rank1_modern_guard_agent.telemetry=_R1MG_REPORT
'''
        folder = OUTPUT / str(episode)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "main.py"
        path.write_text(candidate, encoding="utf-8")
        compile(candidate, str(path), "exec")
        shops = list(((replay["steps"][-1][seat]["observation"].get("town") or {})
                      .get("unlocked_shops") or []))
        index.append({
            "episode": episode,
            "seat": seat,
            "seed": int((replay.get("info") or {})["seed"]),
            "reward": row.get("reward"),
            "opponent_rating": row.get("rating"),
            "shops": shops,
            "path": str(path.relative_to(ROOT)),
            "sha256": hashlib.sha256(candidate.encode()).hexdigest(),
            "bytes": len(candidate.encode()),
            "unique_actions": len(revised["actions"]),
        })
        print(episode, len(revised["actions"]), len(candidate.encode()))
    (OUTPUT / "index.json").write_text(json.dumps(index, indent=2) + "\n",
                                       encoding="utf-8")
    print("built", len(index), "modern-guard rank-1 routes")


if __name__ == "__main__":
    main()
