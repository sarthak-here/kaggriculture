"""Does the AGENT's inference path reproduce the trainer's accuracy? (#67)

Two failures look identical from the outside -- a policy that is genuinely
mis-specialised (covariate shift) and a policy that is wired wrong at play time
(feature drift, label-index mismatch, unit-order mismatch). Both produce a
useless agent while training metrics look fine.

This separates them. It replays held-out corpus states through
`bc_agent/main.py`'s OWN code path -- the same encode, the same weights, the
same legality mask -- and scores the chosen action against what the expert did.

  ~0.85  -> the agent is wired correctly; the deployment failure is covariate
           shift and only DAgger-style correction will move it.
  ~random -> there is a wiring bug, and no amount of guard work will help.
"""

import collections
import gzip
import importlib.util
import json
import os
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "bc_agent"))
sys.path.insert(0, REPO)

import features as F  # noqa: E402

CORPUS = os.path.join(REPO, "replays_top")
MANIFEST = os.path.join(CORPUS, "manifest.json")

spec = importlib.util.spec_from_file_location("bcm", os.path.join(REPO, "bc_agent", "main.py"))
AG = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AG)


def load(eid):
    with gzip.open(os.path.join(CORPUS, "episode-%d-replay.json.gz" % eid),
                   "rt", encoding="utf-8") as fh:
        return json.load(fh)


def main():
    manifest = json.load(open(MANIFEST))
    # take from the END of the manifest: train_bc.py shuffles with seed 0 and
    # takes a 20% val slice, so this is not a clean held-out set, but it is a
    # fair check of the WIRING, which is the question here.
    rows = manifest[-int(sys.argv[1]) if len(sys.argv) > 1 else -6:]

    total = correct = 0
    per_class = collections.defaultdict(lambda: [0, 0])
    confusion = collections.Counter()

    for row in rows:
        data = load(row["episode_id"])
        seat = row["seat"]
        config = data.get("configuration") or {}
        steps = data.get("steps") or []
        for i in range(len(steps) - 1):
            try:
                obs = steps[i][seat]["observation"]
                act = steps[i + 1][seat].get("action")
            except (IndexError, TypeError, KeyError):
                continue
            if not isinstance(obs, dict) or not isinstance(act, dict):
                continue
            obs = dict(obs)
            obs["player"] = seat

            cache = F.encode_step(obs, config)
            private = obs.get("private") or {}
            seeds = private.get("seeds") or {}
            shed = private.get("shed") or {}
            invs = list(private.get("inventories") or [])
            positions = F.unit_positions(cache)

            shared = (cache.glob.astype(np.float32) @ AG._Wg
                      + cache.grid.astype(np.float32) @ AG._Wr + AG._b)

            ops = [act.get("farmer")] + list(act.get("hands") or [])
            for u, op in enumerate(ops):
                if u >= len(positions) or not op:
                    continue
                truth = F.action_label(op)
                if truth is None:
                    continue
                vec = F.encode_unit(cache, u)
                if vec is None:
                    continue
                h = np.maximum(shared + vec.astype(np.float32) @ AG._Wu, 0.0)
                logits = h @ AG._Wo + AG._bo
                x, y = int(positions[u][0]), int(positions[u][1])
                carried = invs[u] if u < len(invs) else {}
                logits = logits + AG._legal_mask(cache, u, x, y, seeds, carried, shed)
                pred = int(np.argmax(logits))

                total += 1
                per_class[truth[0]][1] += 1
                if pred == truth[0]:
                    correct += 1
                    per_class[truth[0]][0] += 1
                else:
                    confusion[(F.UNIT_ACTIONS[truth[0]], F.UNIT_ACTIONS[pred])] += 1

    print("episodes: %d   unit-decisions scored: %d" % (len(rows), total))
    print("ACCURACY THROUGH THE AGENT PATH: %.4f" % (correct / max(1, total)))
    print("  (trainer reported 0.8473 on held-out episodes)\n")

    print("  %-22s %8s %8s" % ("class", "support", "recall"))
    for k, (c, n) in sorted(per_class.items(), key=lambda kv: -kv[1][1])[:12]:
        print("  %-22s %8d %8.3f" % (F.UNIT_ACTIONS[k], n, c / max(1, n)))

    print("\n  most common confusions (truth -> predicted):")
    for (t, p), n in confusion.most_common(10):
        print("    %-22s -> %-22s %6d" % (t, p, n))


if __name__ == "__main__":
    main()
