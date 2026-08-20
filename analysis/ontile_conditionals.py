"""What do top agents do when standing on a tile with obvious pending work? (#66)

The BC agent emitted no HARVEST and no DROP in six days, so nothing ever reached
the shed and there was nothing to sell (#65). Before hard-coding "always harvest
a ready tile", measure how often the experts actually do it -- a guard that
forces an action the corpus takes only half the time would be a regression, not
a fix.

Conditional measured, for the target seat only, with the #64 alignment
(obs[i] -> action[i+1]).
"""

import collections
import gzip
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(REPO, "replays_top")
MANIFEST = os.path.join(CORPUS, "manifest.json")
SHED_ACCESS = {(4, 4), (4, 5), (5, 4), (5, 5)}


def load(eid):
    with gzip.open(os.path.join(CORPUS, "episode-%d-replay.json.gz" % eid),
                   "rt", encoding="utf-8") as fh:
        return json.load(fh)


def main():
    manifest = json.load(open(MANIFEST))
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    cond = collections.defaultdict(collections.Counter)

    for row in manifest[:n]:
        data = load(row["episode_id"])
        seat = row["seat"]
        steps = data.get("steps") or []
        for i in range(len(steps) - 1):
            try:
                obs = steps[i][seat]["observation"]
                act = steps[i + 1][seat].get("action")
            except (IndexError, TypeError, KeyError):
                continue
            if not isinstance(obs, dict) or not isinstance(act, dict):
                continue
            farm = (obs.get("farms") or [{}])[seat]
            tiles = farm.get("tiles") or []
            invs = (obs.get("private") or {}).get("inventories") or []
            positions = [farm.get("farmer")] + list(farm.get("hands") or [])
            ops = [act.get("farmer")] + list(act.get("hands") or [])

            for u, (pos, op) in enumerate(zip(positions, ops)):
                if not pos or not op:
                    continue
                x, y = int(pos[0]), int(pos[1])
                verb = str(op[0])
                t = tiles[y][x] if 0 <= y < len(tiles) and 0 <= x < len(tiles[y]) else None
                carried = invs[u] if u < len(invs) else {}
                carrying = sum(int(v) for v in (carried or {}).values())

                if isinstance(t, dict):
                    if float(t.get("yield_units") or 0) > 0:
                        cond["on READY crop (yield>0)"][verb] += 1
                    if t.get("kind") == "PLANT" and not t.get("watered_today"):
                        cond["on THIRSTY crop"][verb] += 1
                    if t.get("animal") and not t.get("fed_today"):
                        cond["on UNFED animal"][verb] += 1
                    if t.get("animal") and not t.get("cared_today"):
                        cond["on UNCARED animal"][verb] += 1
                    if t.get("kind") == "WEED":
                        cond["on WEED"][verb] += 1
                    if t.get("fertilizer_available"):
                        cond["on FERTILIZER"][verb] += 1
                if (x, y) in SHED_ACCESS and carrying > 0:
                    cond["at SHED carrying goods"][verb] += 1
                if (x, y) in SHED_ACCESS and carrying == 0:
                    cond["at SHED empty-handed"][verb] += 1

    for label in ("on READY crop (yield>0)", "on THIRSTY crop", "on UNFED animal",
                  "on UNCARED animal", "on WEED", "on FERTILIZER",
                  "at SHED carrying goods", "at SHED empty-handed"):
        c = cond[label]
        tot = sum(c.values())
        if not tot:
            continue
        top = ", ".join("%s %.0f%%" % (k, 100.0 * v / tot) for k, v in c.most_common(4))
        print("%-26s n=%7d   %s" % (label, tot, top))


if __name__ == "__main__":
    main()
