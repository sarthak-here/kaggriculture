"""Mine replay routes whose opening exactly matches a pf_all portfolio slot."""

import argparse
import ast
import gzip
import hashlib
import json
from pathlib import Path

from extract_kaito_v46 import assignment, decode_json
from mine_compatible_routes import prefix_length, route_of
from portfolio import label_for, shops_of_episode


ROUTE_VARS = {
    "10c4s_3q": "_ACTIONS_10C4S_3Q",
    "8c6s_3q": "_ACTIONS_8C6S_3Q",
    "6c8s_3q": "_ACTIONS_6C8S_3Q",
    "6c12s_4q_first_yarn": "_ACTIONS_6C12S_4Q_FIRST_YARN",
    "6c12s_4q_second_yarn": "_ACTIONS_6C12S_4Q_SECOND_YARN",
}


def load_replay(path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            return json.load(handle)
    return json.loads(path.read_text(encoding="utf-8"))


def episode_id(path):
    return int(path.name.split("-")[1])


def replay_paths(roots):
    seen = set()
    for root in roots:
        for pattern in ("episode-*-replay.json.gz", "episode-*-replay.json"):
            for path in sorted(root.glob(pattern)):
                key = episode_id(path)
                if key not in seen:
                    seen.add(key)
                    yield path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", type=Path, default=Path("submit_pf_all/main.py"))
    parser.add_argument("--source", type=Path, action="append", default=[])
    parser.add_argument("--minimum-prefix", type=int, default=120)
    parser.add_argument("--output", type=Path,
                        default=Path("route_mining/pfall_compatible"))
    args = parser.parse_args()
    roots = args.source or [Path("replays_top"),
                            Path("loss_analysis/pfall_current")]

    tree = ast.parse(args.agent.read_text(encoding="utf-8"),
                     filename=str(args.agent))
    bases = {label: decode_json(assignment(tree, variable))
             for label, variable in ROUTE_VARS.items()}
    args.output.mkdir(parents=True, exist_ok=True)

    rows = []
    scanned = 0
    matching_bucket = 0
    prefix_histogram = {}
    for path in replay_paths(roots):
        replay = load_replay(path)
        scanned += 1
        steps = replay.get("steps") or []
        if not steps:
            continue
        for seat in range(len(steps[-1])):
            shops = shops_of_episode(replay, seat)
            label = label_for(shops)
            base = bases[label]
            route = route_of(replay, seat)
            prefix = prefix_length(base, route)
            prefix_histogram[prefix] = prefix_histogram.get(prefix, 0) + 1
            if prefix > 0:
                matching_bucket += 1
            if prefix < args.minimum_prefix or prefix == len(route):
                continue
            packed = json.dumps(route, separators=(",", ":"),
                                sort_keys=True).encode()
            digest = hashlib.sha256(packed).hexdigest()
            target = args.output / ("route-%d-seat%d.json.gz" %
                                    (episode_id(path), seat))
            with gzip.open(target, "wt", encoding="utf-8") as handle:
                json.dump(route, handle, separators=(",", ":"))
            final = steps[-1][seat]
            rows.append({
                "episode_id": episode_id(path),
                "seat": seat,
                "bucket": label,
                "prefix": prefix,
                "shops": shops,
                "reward": final.get("reward"),
                "route_sha256": digest,
                "route_file": str(target),
            })

    unique = {}
    for row in rows:
        old = unique.get(row["route_sha256"])
        if old is None or row["prefix"] > old["prefix"]:
            unique[row["route_sha256"]] = row
    result = sorted(unique.values(),
                    key=lambda row: (-row["prefix"], row["bucket"]))
    summary = {
        "agent": str(args.agent),
        "minimum_prefix": args.minimum_prefix,
        "replays_scanned": scanned,
        "seats_with_any_matching_prefix": matching_bucket,
        "prefix_histogram": dict(sorted(prefix_histogram.items())),
        "candidates": result,
    }
    target = args.output / "compatible_routes.json"
    target.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("replays", scanned, "matching seats", matching_bucket)
    print("prefix >=", args.minimum_prefix, "unique candidates", len(result))
    for row in result[:30]:
        print(row["bucket"], "ep", row["episode_id"], "seat", row["seat"],
              "prefix", row["prefix"], "reward", row["reward"])
    print("wrote", target)


if __name__ == "__main__":
    main()