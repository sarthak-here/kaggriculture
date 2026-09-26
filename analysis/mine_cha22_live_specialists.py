"""Find loss-opponent routes that are state-compatible with Cha22 at day 6."""
import argparse
import gzip
import json
from pathlib import Path


def canonical(action, workers_only=False):
    action = action if isinstance(action, dict) else {}
    out = {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(row) for row in (action.get("hands") or [])],
    }
    if not workers_only:
        out["market"] = [list(row) for row in (action.get("market") or [])]
    return out


def route(replay, seat, workers_only=False):
    steps = replay.get("steps") or []
    return [canonical(steps[index + 1][seat].get("action"), workers_only)
            for index in range(min(719, len(steps) - 1))]


def prefix(left, right):
    for index, pair in enumerate(zip(left, right)):
        if pair[0] != pair[1]:
            return index
    return min(len(left), len(right))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    profile = json.loads((args.corpus / "profile.json").read_text(encoding="utf-8"))
    records = {int(row["episode"]): row for row in profile["records"]}
    candidates = []
    for episode, record in records.items():
        if record["result"] != "L":
            continue
        path = args.corpus / "replays" / f"episode-{episode}-replay.json.gz"
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            replay = json.load(handle)
        own_seat = int(record["seat"]); opponent_seat = 1 - own_seat
        own_full = route(replay, own_seat)
        opp_full = route(replay, opponent_seat)
        own_workers = route(replay, own_seat, True)
        opp_workers = route(replay, opponent_seat, True)
        row = {
            "episode": episode, "opponent": record["opponent"],
            "opponent_submission": record["opponent_submission"],
            "margin": record["margin"], "seat": own_seat,
            "shops": record["shops"], "shop2": record["shops"][:2],
            "opponent_build": record["opp_build"],
            "full_prefix": prefix(own_full, opp_full),
            "worker_prefix": prefix(own_workers, opp_workers),
            "route_file": f"route-{episode}-seat{opponent_seat}.json.gz",
        }
        target = args.output / row["route_file"]
        args.output.mkdir(parents=True, exist_ok=True)
        with gzip.open(target, "wt", encoding="utf-8") as handle:
            json.dump(opp_full, handle, separators=(",", ":"))
        candidates.append(row)
    candidates.sort(key=lambda row: (row["full_prefix"] < 144,
                                     row["worker_prefix"] < 144,
                                     row["margin"]))
    (args.output / "index.json").write_text(
        json.dumps(candidates, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for row in candidates:
        print("%d m%+6.0f full=%3d worker=%3d %-25s %s" % (
            row["episode"], row["margin"], row["full_prefix"], row["worker_prefix"],
            "/".join(row["shop2"]), row["opponent"]))


if __name__ == "__main__":
    main()
