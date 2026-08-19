"""Enumerate the REAL per-unit action vocabulary in the top-10 corpus (#61).

Behaviour cloning needs a fixed discrete output space. Rather than guess it from
the engine's verb list, derive it from what top agents actually emit, and check
how much probability mass a truncated vocabulary would lose.

Unit ops and market ops are separated because they are two different models:
a per-unit policy (farmer + each hand) and a market-order policy.
"""

import collections
import gzip
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "replays_top")
MANIFEST = os.path.join(OUT_DIR, "manifest.json")


def load(episode_id):
    path = os.path.join(OUT_DIR, "episode-%d-replay.json.gz" % episode_id)
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def main():
    manifest = json.load(open(MANIFEST))
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    rows = manifest[:n]

    unit_ops = collections.Counter()      # full tuple, e.g. ("PLANT","WHEAT")
    unit_verbs = collections.Counter()
    market_ops = collections.Counter()    # verb+item, quantity stripped
    market_qty = collections.defaultdict(collections.Counter)
    market_lines = collections.Counter()  # how many order lines per step
    pickup_n = collections.Counter()

    for i, row in enumerate(rows, 1):
        data = load(row["episode_id"])
        seat = row["seat"]
        for st in data.get("steps") or []:
            try:
                act = st[seat].get("action")
            except (IndexError, TypeError, AttributeError):
                continue
            if not isinstance(act, dict):
                continue
            for op in [act.get("farmer")] + list(act.get("hands") or []):
                if not op:
                    continue
                t = tuple(op)
                unit_verbs[t[0]] += 1
                if t[0] in ("PICKUP", "DROP") and len(t) >= 3:
                    pickup_n[t[2]] += 1
                    unit_ops[t[:2]] += 1          # drop the count from the class
                else:
                    unit_ops[t] += 1
            market = act.get("market") or []
            market_lines[len(market)] += 1
            for op in market:
                t = tuple(op)
                key = t[:2] if len(t) >= 2 else t[:1]
                market_ops[key] += 1
                if len(t) >= 3:
                    market_qty[key][t[2]] += 1
        if i % 10 == 0:
            print("  ...%d/%d" % (i, len(rows)), flush=True)

    total_unit = sum(unit_ops.values())
    print("\n=== UNIT action classes (farmer + hands) : %d decisions ===" % total_unit)
    print("distinct classes: %d" % len(unit_ops))
    cum = 0
    for k, v in unit_ops.most_common(40):
        cum += v
        print("  %-34s %9d  %5.2f%%   cum %5.2f%%"
              % ("|".join(str(x) for x in k), v, 100.0 * v / total_unit, 100.0 * cum / total_unit))
    for cutoff in (20, 30, 40, 50):
        keep = sum(v for _, v in unit_ops.most_common(cutoff))
        print("  -> top %d classes cover %.3f%% of decisions" % (cutoff, 100.0 * keep / total_unit))

    print("\n  PICKUP/DROP count argument distribution:", pickup_n.most_common(8))

    total_market = sum(market_ops.values())
    print("\n=== MARKET order classes : %d orders ===" % total_market)
    print("distinct verb|item: %d" % len(market_ops))
    for k, v in market_ops.most_common(25):
        qs = market_qty[k]
        top_q = ", ".join("%s x%d" % (q, c) for q, c in qs.most_common(4)) if qs else "-"
        print("  %-26s %8d  %5.2f%%   qty: %s"
              % ("|".join(str(x) for x in k), v, 100.0 * v / total_market, top_q[:60]))

    print("\n=== market order lines per step ===")
    tot = sum(market_lines.values())
    for k in sorted(market_lines):
        print("  %2d lines: %7d (%5.2f%%)" % (k, market_lines[k], 100.0 * market_lines[k] / tot))


if __name__ == "__main__":
    main()
