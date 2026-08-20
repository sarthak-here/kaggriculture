"""Where does v45 differ from a 3,100-rated agent? (#69)

BC failed to beat v45 (0-12), so the corpus is more valuable as GROUND TRUTH
than as training data: 373 episodes of agents rating 2,908-3,149 tell us what a
top farm actually looks like, per day, and v45 can be measured against it
directly.

Compares like for like -- same per-day snapshots, target seat only.
"""

import collections
import gzip
import importlib.util
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
CORPUS = os.path.join(REPO, "replays_top")
TURNS = 24


def snap(obs, seat):
    farm = (obs.get("farms") or [{}])[seat]
    tiles = farm.get("tiles") or []
    plant = animal = empty = pasture = 0
    for row in tiles:
        for t in row:
            if t is None:
                empty += 1
            elif isinstance(t, dict):
                if t.get("kind") == "PLANT":
                    plant += 1
                if t.get("kind") == "PASTURE":
                    pasture += 1
                if t.get("animal"):
                    animal += 1
    return {
        "money": float(farm.get("money") or 0),
        "plant": plant, "empty": empty, "animal": animal, "pasture": pasture,
        "quads": len(farm.get("unlocked_quadrants") or []),
        "hands": len(farm.get("hands") or []),
    }


def corpus_profile(n=20):
    man = json.load(open(os.path.join(CORPUS, "manifest.json")))
    rows = sorted(man, key=lambda r: -r["reward"])[:n]
    acc = collections.defaultdict(lambda: collections.defaultdict(list))
    verbs = collections.Counter()
    for r in rows:
        with gzip.open(os.path.join(CORPUS, "episode-%d-replay.json.gz" % r["episode_id"]),
                       "rt", encoding="utf-8") as fh:
            d = json.load(fh)
        seat = r["seat"]
        steps = d.get("steps") or []
        for i in range(0, len(steps) - 1):
            if i % TURNS != 12:
                continue
            obs = steps[i][seat].get("observation")
            if not isinstance(obs, dict):
                continue
            s = snap(obs, seat)
            for k, v in s.items():
                acc[obs.get("day", i // TURNS)][k].append(v)
        for st in steps:
            a = st[seat].get("action")
            if isinstance(a, dict):
                for op in [a.get("farmer")] + list(a.get("hands") or []):
                    if op:
                        verbs[op[0]] += 1
    return acc, verbs, len(rows)


def v45_profile(seeds=(2001, 2002, 2003)):
    from kaggle_environments import make
    spec = importlib.util.spec_from_file_location("v45", os.path.join(REPO, "main.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fn = mod.agent
    nargs = fn.__code__.co_argcount
    acc = collections.defaultdict(lambda: collections.defaultdict(list))
    verbs = collections.Counter()

    def wrapped(obs, config=None):
        a = fn(obs, config) if nargs > 1 else fn(obs)
        if isinstance(a, dict):
            for op in [a.get("farmer")] + list(a.get("hands") or []):
                if op:
                    verbs[op[0]] += 1
        if obs["step"] % TURNS == 12:
            s = snap(obs, obs["player"])
            for k, v in s.items():
                acc[obs["day"]][k].append(v)
        return a

    for sd in seeds:
        env = make("kaggriculture", configuration={"seed": sd}, debug=False)
        env.run([wrapped, os.path.join(REPO, "main.py")])
    return acc, verbs, len(seeds)


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def main():
    print("reading corpus...", flush=True)
    cacc, cverbs, cn = corpus_profile(20)
    print("running v45...", flush=True)
    vacc, vverbs, vn = v45_profile()

    print("\n  day |      TOP-20 CORPUS          |          v45")
    print("      | plant empty anim quad money | plant empty anim quad money")
    for day in range(0, 30, 3):
        c, v = cacc.get(day, {}), vacc.get(day, {})
        if not c or not v:
            continue
        print("  %3d | %5.0f %5.0f %4.0f %4.1f %6.0f | %5.0f %5.0f %4.0f %4.1f %6.0f"
              % (day, mean(c["plant"]), mean(c["empty"]), mean(c["animal"]),
                 mean(c["quads"]), mean(c["money"]),
                 mean(v["plant"]), mean(v["empty"]), mean(v["animal"]),
                 mean(v["quads"]), mean(v["money"])))

    ct, vt = sum(cverbs.values()), sum(vverbs.values())
    print("\n  action mix (%% of unit actions)")
    print("  %-20s %9s %9s" % ("verb", "corpus", "v45"))
    for verb, _ in cverbs.most_common(12):
        print("  %-20s %8.2f%% %8.2f%%"
              % (verb, 100.0 * cverbs[verb] / ct, 100.0 * vverbs.get(verb, 0) / max(1, vt)))
    print("\n  actions per game: corpus %.0f   v45 %.0f" % (ct / cn, vt / vn))


if __name__ == "__main__":
    main()
