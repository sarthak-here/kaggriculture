"""Audit the top-10 replay corpus before committing to a feature design (#61).

The question that decides whether behaviour cloning is worth doing at all:
are these 373 episodes played by DIFFERENT policies, or are they 373 replays of
one hard-coded route? EXPERIMENTS notes the claim that 22/30 of the top-30 share
an identical Day-0 signature. If the corpus is one route wearing ten hats, a
cloned policy just relearns that route and inherits the desync problem that
capped path A at 18,587.

Also verifies the manifest's `seat` field really points at the target team, since
every training label depends on it.
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
    if not os.path.exists(path):
        return None
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def signature(steps, seat, n_days=1, turns_per_day=24):
    """Canonical opening: the first day's market orders for one seat."""
    sig = []
    for st in steps[: n_days * turns_per_day]:
        try:
            act = st[seat].get("action")
        except (IndexError, TypeError, AttributeError):
            continue
        if not isinstance(act, dict):
            continue
        for order in act.get("market") or []:
            sig.append(tuple(order))
    return tuple(sig)


def main():
    manifest = json.load(open(MANIFEST))
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else len(manifest)
    manifest = manifest[:limit]

    by_team = collections.defaultdict(list)
    sigs = collections.Counter()
    sig_by_team = collections.defaultdict(set)
    seat_ok = seat_bad = 0
    total_unit = 0
    verbs = collections.Counter()
    missing = 0

    for i, row in enumerate(manifest, 1):
        data = load(row["episode_id"])
        if data is None:
            missing += 1
            continue
        steps = data.get("steps") or []
        seat = row["seat"]
        rewards = data.get("rewards") or []

        # Does the manifest seat actually match the reward we were promised?
        if seat < len(rewards) and rewards[seat] is not None:
            if abs(float(rewards[seat]) - row["reward"]) < 1.0:
                seat_ok += 1
            else:
                seat_bad += 1

        sig = signature(steps, seat)
        sigs[sig] += 1
        sig_by_team[row["team_name"]].add(sig)
        by_team[row["team_name"]].append(row["reward"])

        for st in steps:
            try:
                act = st[seat].get("action")
            except (IndexError, TypeError, AttributeError):
                continue
            if not isinstance(act, dict):
                continue
            hands = act.get("hands") or []
            market = act.get("market") or []
            total_unit += 1 + len(hands) + len(market)
            for op in [act.get("farmer")] + list(hands) + list(market):
                if op:
                    verbs[op[0] if isinstance(op, (list, tuple)) and op else str(op)] += 1

        if i % 50 == 0:
            print("  ...%d/%d" % (i, len(manifest)), flush=True)

    print("\n=== corpus ===")
    print("episodes read      : %d (missing %d)" % (len(manifest) - missing, missing))
    print("target-seat unit-decisions: %d" % total_unit)
    print("seat label verified: %d ok / %d MISMATCH" % (seat_ok, seat_bad))

    print("\n=== policy diversity (day-0 market signature, target seat) ===")
    print("distinct openings  : %d across %d episodes" % (len(sigs), sum(sigs.values())))
    for sig, n in sigs.most_common(5):
        print("  %4d episodes (%4.1f%%)  %s" % (n, 100.0 * n / sum(sigs.values()), str(sig)[:96]))

    print("\n=== per team ===")
    for team, rewards in sorted(by_team.items(), key=lambda kv: -max(kv[1])):
        print("  %-26s %3d eps  best %8.0f  mean %8.0f  distinct openings %d"
              % (team[:26], len(rewards), max(rewards), sum(rewards) / len(rewards),
                 len(sig_by_team[team])))

    shared = [s for s, n in sigs.items() if n > 1]
    cross = sum(1 for s in shared if len({t for t, ss in sig_by_team.items() if s in ss}) > 1)
    print("\nopenings shared by MORE THAN ONE team: %d" % cross)

    print("\n=== verb mix (target seat) ===")
    for verb, n in verbs.most_common(14):
        print("  %-18s %8d  (%.1f%%)" % (verb, n, 100.0 * n / sum(verbs.values())))


if __name__ == "__main__":
    main()
