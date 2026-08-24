"""Mine downloaded replay seats against any statically decoded v46 base route."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path

from mine_compatible_routes import prefix_length, route_of


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("base_route")
    parser.add_argument("--minimum-prefix", type=int, default=216)
    parser.add_argument("--shop-index", type=int)
    parser.add_argument("--shop", default="YARN_STORE")
    parser.add_argument("--source", type=Path,
                        default=Path("route_mining/active_lineage"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    routes = json.loads(Path("analysis/kaito_v46_routes.json").read_text())
    base = routes[args.base_route]
    args.output.mkdir(parents=True, exist_ok=True)
    unique = {}

    for path in sorted(args.source.glob("episode-*-replay.json")):
        replay = json.loads(path.read_text(encoding="utf-8"))
        episode_id = int(path.name.split("-")[1])
        for seat in (0, 1):
            steps = replay.get("steps") or []
            if not steps or seat >= len(steps[-1]):
                continue
            obs = steps[-1][seat].get("observation") or {}
            shops = list((obs.get("town", {}) or {}).get(
                "unlocked_shops", []) or [])
            if args.shop_index is not None and (
                len(shops) <= args.shop_index
                or shops[args.shop_index] != args.shop
            ):
                continue
            route = route_of(replay, seat)
            prefix = prefix_length(base, route)
            if prefix < args.minimum_prefix or prefix == len(route):
                continue
            packed = json.dumps(route, separators=(",", ":"),
                                sort_keys=True).encode()
            digest = hashlib.sha256(packed).hexdigest()
            target = args.output / ("route-%d-seat%d.json.gz" % (
                episode_id, seat))
            with gzip.open(target, "wt", encoding="utf-8") as handle:
                json.dump(route, handle, separators=(",", ":"))
            row = {
                "name": "ep%d_s%d_p%d" % (episode_id, seat, prefix),
                "episode_id": episode_id,
                "seat": seat,
                "prefix": prefix,
                "shops": shops,
                "route_sha256": digest,
                "route_file": str(target),
            }
            old = unique.get(digest)
            if old is None or prefix > old["prefix"]:
                unique[digest] = row

    rows = sorted(unique.values(), key=lambda row: -row["prefix"])
    target = args.output / "compatible_routes.json"
    target.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    for row in rows:
        print(row["name"], ">".join(row["shops"][:3]))
    print("unique candidates", len(rows), "wrote", target)


if __name__ == "__main__":
    main()
