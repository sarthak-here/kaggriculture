"""Install coherent live-loss opponent routes into Cha22's guard stack."""
import argparse
import ast
import base64
import gzip
import hashlib
import json
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public_candidates/current_20260925/cha22/main.py"
DEFAULT_EPISODES = (113444951, 113434468, 113638280, 113439196)


def route_bundle(source):
    tree = ast.parse(source)
    node = next(node for node in tree.body if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == "_R108_DATA"
                        for target in node.targets))
    payload = max((item.value for item in ast.walk(node.value)
                   if isinstance(item, ast.Constant) and isinstance(item.value, str)),
                  key=len)
    data = json.loads(zlib.decompress(base64.b85decode(payload)).decode("utf-8"))
    return node, data


def install(source, node, original, route):
    actions = []
    indices = []
    seen = {}
    for action in route:
        key = json.dumps(action, separators=(",", ":"), sort_keys=True)
        if key not in seen:
            seen[key] = len(actions)
            actions.append(action)
        indices.append(seen[key])
    data = dict(original)
    data["actions"] = actions
    data["routes"] = {"999": indices}
    packed = json.dumps(data, separators=(",", ":")).encode()
    blob = base64.b85encode(zlib.compress(packed, 9)).decode("ascii")
    replacement = "_R108_DATA=json.loads(zlib.decompress(base64.b85decode(%r)).decode('utf-8'))" % blob
    lines = source.splitlines(keepends=True)
    newline = "\r\n" if lines[node.lineno - 1].endswith("\r\n") else "\n"
    lines[node.lineno - 1:node.end_lineno] = [replacement + newline]
    patched = "".join(lines)
    marker = "_ROUTES={int(k):[_R108_DATA['actions'][i] for i in ids] for k,ids in _R108_DATA['routes'].items()}"
    keys = tuple(sorted(int(key) for key in original["routes"]))
    graft = marker + "\nfor _live_key in %r:_ROUTES[_live_key]=_ROUTES[999]\ndel _live_key" % (keys,)
    if patched.count(marker) != 1:
        raise RuntimeError("unexpected _ROUTES constructor")
    patched = patched.replace(marker, graft, 1)
    if patched.count("_PIPE_MODE = 'EarlyCycle'") != 1:
        raise RuntimeError("unexpected PIPE mode declaration")
    # PIPE16 mutates exact coordinates in Cha22's native opening and asserts
    # that those cells are idle.  A coherent foreign route must keep its own
    # opening instead of entering that incompatible mutation path.
    patched = patched.replace("_PIPE_MODE = 'EarlyCycle'", "_PIPE_MODE = 'Original'", 1)
    return patched, packed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path,
                        default=ROOT / "analysis/cha22_live_56556133_20260926")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "variants/cha22_live_routes_20260926")
    parser.add_argument("episodes", nargs="*", type=int, default=DEFAULT_EPISODES)
    args = parser.parse_args()
    source = SOURCE.read_text(encoding="utf-8")
    compile(source, str(SOURCE), "exec")
    bundle_node, bundle = route_bundle(source)
    index = json.loads((args.corpus / "specialists/index.json").read_text(encoding="utf-8"))
    by_episode = {int(row["episode"]): row for row in index}
    manifest = []
    for episode in args.episodes:
        row = by_episode[episode]
        route_path = args.corpus / "specialists" / row["route_file"]
        with gzip.open(route_path, "rt", encoding="utf-8") as handle:
            route = json.load(handle)
        if len(route) != 719:
            raise ValueError(f"episode {episode}: expected 719 actions, got {len(route)}")
        candidate, packed = install(source, bundle_node, bundle, route)
        target = args.output / str(episode)
        target.mkdir(parents=True, exist_ok=True)
        path = target / "main.py"
        compile(candidate, str(path), "exec")
        path.write_text(candidate, encoding="utf-8")
        manifest.append({**row, "path": str(path.relative_to(ROOT)),
                         "route_sha256": hashlib.sha256(packed).hexdigest(),
                         "candidate_sha256": hashlib.sha256(candidate.encode()).hexdigest()})
        print(episode, row["opponent"], path)
    (args.output / "index.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
