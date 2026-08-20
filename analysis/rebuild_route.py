"""Rebuild the public agent's route from OUR corpus, keeping its guards (#70).

The public agent = a 719-step route `_ACTIONS` + a large stack of execution
guards. The guards are the valuable, hard part (#58). The route is just data,
and Salem Ali built his by majority-voting **twelve** traces of unknown quality.

We have **373 episodes of the top ten teams**, rated 2,908-3,149, scoring
143k-168k. Same method, far better source -- and #61 showed the reconstruction
loses ~700 rating points to its own sources, so the route is where that loss
lives.

Alignment note: Salem's `_ACTIONS[0]` holds the five opening HIREs, while the
replay's step-0 action is empty and step 1 carries them. So his route already
uses the shifted pairing this ledger verified in #64: route[i] = replay
action[i+1]. We build it the same way.

Two variants, because it is not obvious which wins:
  modal  -- majority action per step across the dominant opening cluster
            (Salem's method, better data)
  best   -- the single highest-scoring episode's route, kept coherent
            (no averaging, so late-game reactivity is not blurred into mush)

Usage: python analysis/rebuild_route.py [n_episodes]
"""

import base64
import collections
import gzip
import json
import os
import re
import sys
import zlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(REPO, "replays_top")
MANIFEST = os.path.join(CORPUS, "manifest.json")
SRC = os.path.join(REPO, "submit_pub", "main.py")
STEPS = 719


def load(eid):
    with gzip.open(os.path.join(CORPUS, "episode-%d-replay.json.gz" % eid),
                   "rt", encoding="utf-8") as fh:
        return json.load(fh)


def route_of(data, seat):
    """route[i] = replay action[i+1], canonicalised to plain lists."""
    steps = data.get("steps") or []
    out = []
    for i in range(STEPS):
        act = None
        if i + 1 < len(steps):
            try:
                act = steps[i + 1][seat].get("action")
            except (IndexError, TypeError):
                act = None
        if not isinstance(act, dict):
            act = {"farmer": ["PASS"], "hands": [], "market": []}
        out.append({
            "farmer": list(act.get("farmer") or ["PASS"]),
            "hands": [list(h) for h in (act.get("hands") or [])],
            "market": [list(m) for m in (act.get("market") or [])],
        })
    return out


def key(a):
    return json.dumps(a, sort_keys=True)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    man = json.load(open(MANIFEST))
    man = sorted(man, key=lambda r: -r["reward"])[:n]

    routes = []
    for r in man:
        try:
            routes.append((r, route_of(load(r["episode_id"]), r["seat"])))
        except Exception as exc:                       # noqa: BLE001
            print("  skip %d: %s" % (r["episode_id"], exc))
    print("loaded %d routes (best reward %.0f)" % (len(routes), routes[0][0]["reward"]))

    # dominant opening cluster: never average two different capital plans
    open_counts = collections.Counter(key(rt[0]) for _, rt in routes)
    modal_open, cnt = open_counts.most_common(1)[0]
    cluster = [(r, rt) for r, rt in routes if key(rt[0]) == modal_open]
    print("dominant opening cluster: %d of %d episodes" % (cnt, len(routes)))
    print("cluster mean reward %.0f, best %.0f"
          % (sum(r["reward"] for r, _ in cluster) / len(cluster),
             max(r["reward"] for r, _ in cluster)))

    # --- variant "modal" ---
    modal = []
    agree = []
    for i in range(STEPS):
        c = collections.Counter(key(rt[i]) for _, rt in cluster)
        best, k = c.most_common(1)[0]
        agree.append(k / len(cluster))
        modal.append(json.loads(best))
    print("mean per-step agreement in cluster: %.3f" % (sum(agree) / len(agree)))

    # --- variant "best" ---
    best_row, best_route = max(cluster, key=lambda rr: rr[0]["reward"])
    print("best single episode: %s reward %.0f"
          % (best_row["team_name"], best_row["reward"]))

    src = open(SRC, encoding="utf-8").read()
    pat = re.compile(r"_ACTIONS = json\.loads\(zlib\.decompress\(base64\.b85decode\('[^']*'\)\)\.decode\('utf-8'\)\)")
    if not pat.search(src):
        print("!! could not locate the _ACTIONS blob")
        return

    for name, route in (("modal", modal), ("best", best_route)):
        blob = base64.b85encode(zlib.compress(
            json.dumps(route, separators=(",", ":")).encode("utf-8"), 9)).decode("ascii")
        new = "_ACTIONS = json.loads(zlib.decompress(base64.b85decode('%s')).decode('utf-8'))" % blob
        out_dir = os.path.join(REPO, "variants", "pub_route_" + name)
        os.makedirs(out_dir, exist_ok=True)
        open(os.path.join(out_dir, "main.py"), "w", encoding="utf-8").write(pat.sub(lambda _m: new, src, count=1))
        print("wrote %s  (route %d steps, blob %d chars)" % (out_dir, len(route), len(blob)))


if __name__ == "__main__":
    main()
