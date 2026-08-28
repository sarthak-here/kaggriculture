"""Mine winning Kaito-loss routes that exactly match a submitted route prefix."""

import argparse
import ast
import gzip
import hashlib
import json
from pathlib import Path

from extract_kaito_v46 import assignment, decode_json
from mine_compatible_routes import prefix_length, route_of


def selected_slot(shops):
    shops = list(shops or [])
    if shops[:1] == ["YARN_STORE"]:
        return "yarn_first"
    if len(shops) >= 2 and shops[1] == "YARN_STORE":
        return "yarn_second"
    prefix = tuple(shops[:3])
    if prefix == ("FARMERS_MARKET", "PIZZA_SHOP", "YARN_STORE"):
        return "yarn_third_farmers"
    if prefix == ("SMOOTHIE_SHOP", "BAKERY", "YARN_STORE"):
        return "yarn_third_bakery"
    if prefix == ("SMOOTHIE_SHOP", "SMOOTHIE_SHOP", "YARN_STORE"):
        return "yarn_third"
    if shops[:2] == ["BAKERY", "PIZZA_SHOP"]:
        return "bakery_capital"
    return "default"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", type=Path,
                        default=Path("submit_v46_three_suffix/main.py"))
    parser.add_argument("--corpus", type=Path,
                        default=Path("loss_analysis/kaito_current"))
    parser.add_argument("--minimum-prefix", type=int, default=160)
    parser.add_argument("--minimum-clone-streak", type=int, default=24)
    parser.add_argument("--output", type=Path,
                        default=Path("route_mining/kaito_loss_suffixes"))
    args = parser.parse_args()

    tree = ast.parse(args.agent.read_text(encoding="utf-8"),
                     filename=str(args.agent))
    routes = decode_json(assignment(tree, "_V44_ROUTES"))
    profiles = json.load(open(args.corpus / "profiles.json", encoding="utf-8"))
    by_episode = {row["episode"]: row for row in profiles}
    args.output.mkdir(parents=True, exist_ok=True)
    rows = []

    for path in sorted(args.corpus.glob("episode-*-replay.json")):
        episode = int(path.name.split("-")[1])
        profile = by_episode[episode]
        if profile["clone"]["streak2"] < args.minimum_clone_streak:
            continue
        replay = json.load(open(path, encoding="utf-8"))
        ours = int(profile["seat"])
        winner = 1 - ours
        own_route = route_of(replay, ours)
        slot = selected_slot(profile["shops"])
        own_prefix = prefix_length(routes[slot], own_route)
        candidate = route_of(replay, winner)
        prefix = prefix_length(routes[slot], candidate)
        if prefix < args.minimum_prefix or prefix == len(candidate):
            continue
        packed = json.dumps(candidate, separators=(",", ":"),
                            sort_keys=True).encode()
        digest = hashlib.sha256(packed).hexdigest()
        target = args.output / ("route-%d-seat%d.json.gz" %
                                (episode, winner))
        with gzip.open(target, "wt", encoding="utf-8") as handle:
            json.dump(candidate, handle, separators=(",", ":"))
        rows.append({
            "name": "ep%d_s%d_%s_p%d" % (episode, winner, slot, prefix),
            "episode": episode,
            "seat": winner,
            "slot": slot,
            "prefix": prefix,
            "own_prefix": own_prefix,
            "shops": profile["shops"],
            "margin": profile["margin"],
            "opponent": profile["opponent"],
            "op_family": profile["op_family"],
            "clone_streak2": profile["clone"]["streak2"],
            "route_sha256": digest,
            "route_file": str(target),
        })

    unique = {}
    for row in rows:
        key = (row["slot"], row["route_sha256"])
        old = unique.get(key)
        if old is None or row["prefix"] > old["prefix"]:
            unique[key] = row
    result = sorted(unique.values(),
                    key=lambda row: (-row["prefix"], row["slot"]))
    target = args.output / "compatible_routes.json"
    target.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("compatible winners", len(rows), "unique", len(result))
    for row in result:
        print(row["name"], "margin", row["margin"], row["op_family"],
              ">".join(row["shops"][:3]))
    print("wrote", target)


if __name__ == "__main__":
    main()