"""Mine the modal MARKET opening from the top-10 corpus (#67).

#66 left the BC agent alive but at a quarter of expert scale: 12-15 planted
tiles against 40-58, because it never buys enough seed to fill the land. The
capital plan -- hires, seed, stock -- is what sets that scale.

Only MARKET orders are mined, deliberately. They are state-independent (a HIRE
is a HIRE wherever your units happen to stand), so replaying them cannot desync
the way a recorded unit route does (frozen trace = 2,857, #57). Unit actions
stay with the learned policy.

#61 measured where the script ends: day-0 cross-seed agreement is 1.000 and days
1-4 run 0.93-0.85, then it falls off a cliff. So the opening is genuinely a
fixed schedule for roughly five days and a policy thereafter.

Writes `opening_schedule.json`: {step: [[verb, item, qty], ...]}.
"""

import collections
import gzip
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(REPO, "replays_top")
MANIFEST = os.path.join(CORPUS, "manifest.json")
OUT = os.path.join(REPO, "opening_schedule.json")

HORIZON = 120          # 5 days x 24 turns


def load(eid):
    with gzip.open(os.path.join(CORPUS, "episode-%d-replay.json.gz" % eid),
                   "rt", encoding="utf-8") as fh:
        return json.load(fh)


def market_seq(data, seat, horizon):
    """[(step, canonical order tuple list)] under the #64 alignment."""
    steps = data.get("steps") or []
    out = {}
    for i in range(min(horizon, len(steps) - 1)):
        try:
            act = steps[i + 1][seat].get("action")
        except (IndexError, TypeError):
            continue
        if not isinstance(act, dict):
            continue
        orders = []
        for o in act.get("market") or []:
            if not o:
                continue
            orders.append(tuple(str(x) for x in o))
        out[i] = tuple(orders)
    return out


def main():
    manifest = json.load(open(MANIFEST))
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    rows = manifest[:limit]

    seqs = []
    day0 = collections.Counter()
    for row in rows:
        try:
            data = load(row["episode_id"])
        except Exception:                      # noqa: BLE001
            continue
        seq = market_seq(data, row["seat"], HORIZON)
        seqs.append((row, seq))
        day0[seq.get(0, ())] += 1

    if not seqs:
        print("no episodes read")
        return

    # Restrict to the dominant opening cluster -- averaging across two different
    # capital plans would produce a schedule neither team ever played.
    modal_open, n_modal = day0.most_common(1)[0]
    print("dominant day-0 opening: %d of %d episodes (%.0f%%)"
          % (n_modal, len(seqs), 100.0 * n_modal / len(seqs)))
    for o in modal_open:
        print("    %s" % (list(o),))

    cluster = [s for r, s in seqs if s.get(0, ()) == modal_open]
    print("cluster size: %d episodes" % len(cluster))

    schedule = {}
    agree = []
    for step in range(HORIZON):
        counts = collections.Counter(s.get(step, ()) for s in cluster)
        best, n = counts.most_common(1)[0]
        agree.append(n / max(1, len(cluster)))
        if best:
            schedule[str(step)] = [list(o) for o in best]

    json.dump(schedule, open(OUT, "w"), indent=1)
    nz = len(schedule)
    print("\nsteps with a scheduled order: %d of %d" % (nz, HORIZON))
    print("mean cross-episode agreement over the horizon: %.3f"
          % (sum(agree) / len(agree)))
    for d in range(HORIZON // 24):
        w = agree[d * 24:(d + 1) * 24]
        print("  day %d agreement %.3f" % (d, sum(w) / len(w)))

    total = collections.Counter()
    for orders in schedule.values():
        for o in orders:
            key = o[0] if len(o) < 2 else "%s|%s" % (o[0], o[1])
            total[key] += int(o[2]) if len(o) > 2 else 1
    print("\ntotal bought over the opening:")
    for k, v in total.most_common():
        print("  %-24s %d" % (k, v))
    print("\nwrote %s" % OUT)


if __name__ == "__main__":
    main()
