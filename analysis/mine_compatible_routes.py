"""Mine public submission replays for continuations compatible with v46.

This never imports an agent.  It compares canonical action prefixes from public
replays against the statically decoded v46 route and records candidates whose
opening is identical through a safe branch boundary.
"""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess

import requests


LIST_URL = "https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes"
HEADERS = {"Content-Type": "application/json"}
STEPS = 719


def canonical(action):
    if not isinstance(action, dict):
        action = {}
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(row) for row in (action.get("hands") or [])],
        "market": [list(row) for row in (action.get("market") or [])],
    }


def route_of(replay, seat):
    steps = replay.get("steps") or []
    route = []
    for index in range(STEPS):
        action = None
        if index + 1 < len(steps):
            action = steps[index + 1][seat].get("action")
        route.append(canonical(action))
    return route


def prefix_length(left, right):
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            return index
    return min(len(left), len(right))


def replay_path(root, episode_id):
    return root / ("episode-%d-replay.json" % episode_id)


def download(root, episode_id):
    path = replay_path(root, episode_id)
    if path.exists():
        return path
    subprocess.run(
        ["kaggle", "competitions", "replay", str(episode_id),
         "-p", str(root), "-q"],
        check=False,
        capture_output=True,
        text=True,
    )
    return path if path.exists() else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("submission_ids", nargs="+", type=int)
    parser.add_argument("--minimum-prefix", type=int, default=160)
    parser.add_argument("--root", type=Path,
                        default=Path("route_mining/active_lineage"))
    args = parser.parse_args()

    routes = json.loads(Path("analysis/kaito_v46_routes.json").read_text())
    default = routes["default"]
    args.root.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    rows = []

    for submission_id in args.submission_ids:
        response = session.post(
            LIST_URL,
            json={"submissionId": submission_id},
            headers=HEADERS,
            timeout=90,
        )
        response.raise_for_status()
        payload = response.json()
        episodes = payload.get("episodes", []) or []
        print("submission", submission_id, "episodes", len(episodes), flush=True)
        for number, episode in enumerate(episodes, 1):
            if episode.get("state") != "COMPLETED":
                continue
            agents = episode.get("agents", []) or []
            actor = next(
                (agent for agent in agents
                 if int(agent.get("submissionId") or -1) == submission_id),
                None,
            )
            if actor is None:
                continue
            episode_id = int(episode["id"])
            path = download(args.root, episode_id)
            if path is None:
                continue
            replay = json.loads(path.read_text(encoding="utf-8"))
            seat = int(actor.get("index", 0) or 0)
            route = route_of(replay, seat)
            prefix = prefix_length(default, route)
            final_obs = replay["steps"][-1][seat]["observation"]
            shops = list((final_obs.get("town", {}) or {}).get(
                "unlocked_shops", []) or [])
            if prefix >= args.minimum_prefix:
                route_file = args.root / ("route-%d-seat%d.json.gz" % (
                    episode_id, seat))
                with gzip.open(route_file, "wt", encoding="utf-8") as handle:
                    json.dump(route, handle, separators=(",", ":"))
                row = {
                    "submission_id": submission_id,
                    "episode_id": episode_id,
                    "seat": seat,
                    "prefix": prefix,
                    "shops": shops,
                    "reward": actor.get("reward"),
                    "opponent_reward": next(
                        (a.get("reward") for a in agents if a is not actor), None),
                    "route_sha256": hashlib.sha256(
                        json.dumps(route, separators=(",", ":"),
                                   sort_keys=True).encode()
                    ).hexdigest(),
                    "route_file": str(route_file),
                }
                rows.append(row)
                print("  candidate", episode_id, "prefix", prefix,
                      "shops", ">".join(shops[:3]), flush=True)
            if number % 20 == 0:
                print("  scanned", number, "of", len(episodes), flush=True)

    unique = {}
    for row in rows:
        key = row["route_sha256"]
        old = unique.get(key)
        if old is None or row["prefix"] > old["prefix"]:
            unique[key] = row
    result = sorted(unique.values(), key=lambda row: (-row["prefix"],
                                                       -float(row["reward"] or 0)))
    target = args.root / "compatible_routes.json"
    target.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("compatible rows", len(rows), "unique routes", len(result))
    print("wrote", target)


if __name__ == "__main__":
    main()
