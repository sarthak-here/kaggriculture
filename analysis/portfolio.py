"""Build a route portfolio keyed on the shop roll, from our top-10 corpus (#73).

#72 found the architecture we were missing: the leading public agents keep
SEVERAL complete routes and pick one at runtime from the unlocked-shop sequence.
prvsiyan's selector is small enough to reuse verbatim:

    shops[:1] == [YARN_STORE]            -> 6c12s_4q_first_yarn
    YARN_STORE in shops[:2]              -> 6c12s_4q_second_yarn
    YARN_STORE in shops[:3]              -> 6c8s_3q
    {PIZZA,ICE_CREAM,SMOOTHIE} & shops[:3] -> 10c4s_3q
    otherwise                            -> 8c6s_3q

Its five routes were hand-built from public replays. We hold 373 episodes of the
top ten plus screening machinery, and #71 showed screened routes beat picked
ones (episode reward is anti-predictive). So: classify every corpus episode into
the same buckets, and screen a better route per bucket.

Two things this needs that a single-route search did not:
  * a seed -> bucket map, because a route for the yarn-first bucket can only be
    evaluated on seeds whose shop roll actually selects it;
  * per-bucket duels, so a route is judged only where it would be used.

Subcommands:
    classify   -- bucket every corpus episode by its shop roll
    seeds N    -- bucket the first N env seeds (needs the engine, ~day 9)
"""

import collections
import gzip
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(REPO, "replays_top")
MANIFEST = os.path.join(CORPUS, "manifest.json")
OUT = os.path.join(REPO, "portfolio")

MILK_SUPPORT = {"PIZZA_SHOP", "ICE_CREAM_SHOP", "SMOOTHIE_SHOP"}


def label_for(shops):
    shops = list(shops or [])
    if shops[:1] == ["YARN_STORE"]:
        return "6c12s_4q_first_yarn"
    if "YARN_STORE" in shops[:2]:
        return "6c12s_4q_second_yarn"
    if "YARN_STORE" in shops[:3]:
        return "6c8s_3q"
    if MILK_SUPPORT.intersection(shops[:3]):
        return "10c4s_3q"
    return "8c6s_3q"


def shops_of_episode(data, seat, upto_step=400):
    """Shop list as it stands once at least 3 have unlocked."""
    steps = data.get("steps") or []
    best = []
    for i in range(0, min(upto_step, len(steps))):
        try:
            obs = steps[i][seat].get("observation")
        except (IndexError, TypeError):
            continue
        if not isinstance(obs, dict):
            continue
        shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
        if len(shops) > len(best):
            best = shops
        if len(best) >= 3:
            break
    return best


def classify():
    man = json.load(open(MANIFEST))
    buckets = collections.defaultdict(list)
    for r in man:
        path = os.path.join(CORPUS, "episode-%d-replay.json.gz" % r["episode_id"])
        try:
            with gzip.open(path, "rt", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:                                # noqa: BLE001
            continue
        shops = shops_of_episode(data, r["seat"])
        lab = label_for(shops)
        buckets[lab].append({**r, "shops": shops[:3], "label": lab})

    os.makedirs(OUT, exist_ok=True)
    json.dump({k: v for k, v in buckets.items()},
              open(os.path.join(OUT, "episode_buckets.json"), "w"), indent=1)

    print("%-24s %8s %10s %10s" % ("bucket", "episodes", "best", "mean"))
    total = sum(len(v) for v in buckets.values())
    for lab, rows in sorted(buckets.items(), key=lambda kv: -len(kv[1])):
        rewards = [r["reward"] for r in rows]
        print("%-24s %8d %10.0f %10.0f"
              % (lab, len(rows), max(rewards), sum(rewards) / len(rewards)))
    print("total %d episodes" % total)
    return buckets


def seeds(n):
    from kaggle_environments import make
    counts = collections.Counter()
    mapping = {}
    for i in range(n):
        seed = 5000 + i
        env = make("kaggriculture", configuration={"seed": seed}, debug=False)
        env.reset()
        shops = []
        # shops unlock every townShopUnlockInterval days; step far enough to see 3
        for _ in range(3):
            pass
        obs = env.steps[-1][0]["observation"]
        shops = list((obs.get("town") or {}).get("unlocked_shops") or [])
        lab = label_for(shops)
        mapping[seed] = {"shops": shops[:3], "label": lab}
        counts[lab] += 1
    os.makedirs(OUT, exist_ok=True)
    json.dump(mapping, open(os.path.join(OUT, "seed_buckets.json"), "w"), indent=1)
    for lab, c in counts.most_common():
        print("%-24s %d" % (lab, c))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "classify"
    if cmd == "classify":
        classify()
    else:
        seeds(int(sys.argv[2]) if len(sys.argv) > 2 else 24)
