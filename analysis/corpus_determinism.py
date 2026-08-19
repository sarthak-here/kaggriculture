"""How much of top-agent play is REPLAY vs STATE-CONDITIONAL? (#61)

`corpus_audit.py` found only 6 distinct day-0 openings across 373 episodes, and
9 of 10 top teams open identically in every game they play. That is a replay
signature, not a policy.

But the opening being fixed does not mean the whole game is. A frozen trace
scores ~2,857 (EXPERIMENTS #57), so these agents MUST be correcting against live
state somewhere. This script finds where.

Method: for ONE team, take all its episodes (different seeds) and measure the
fraction that emit the identical action at step t. Agreement ~1.0 means the
route is fired blind; agreement well below 1.0 means behaviour is being derived
from state, and that is the part worth cloning.
"""

import collections
import gzip
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "replays_top")
MANIFEST = os.path.join(OUT_DIR, "manifest.json")
TURNS_PER_DAY = 24


def load(episode_id):
    path = os.path.join(OUT_DIR, "episode-%d-replay.json.gz" % episode_id)
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return json.load(fh)


def canon(action):
    """Hashable form of one seat's action at one step."""
    if not isinstance(action, dict):
        return None
    return (
        tuple(action.get("farmer") or []),
        tuple(tuple(h) for h in (action.get("hands") or [])),
        tuple(tuple(m) for m in (action.get("market") or [])),
    )


def main():
    manifest = json.load(open(MANIFEST))
    by_team = collections.defaultdict(list)
    for row in manifest:
        by_team[row["team_name"]].append(row)

    team = sys.argv[1] if len(sys.argv) > 1 else max(
        by_team, key=lambda t: max(r["reward"] for r in by_team[t]))
    rows = by_team[team][: int(sys.argv[2]) if len(sys.argv) > 2 else 20]
    print("team: %s   episodes: %d\n" % (team, len(rows)))

    seqs = []
    for row in rows:
        data = load(row["episode_id"])
        seat = row["seat"]
        seq = []
        for st in data.get("steps") or []:
            try:
                seq.append(canon(st[seat].get("action")))
            except (IndexError, TypeError, AttributeError):
                seq.append(None)
        seqs.append(seq)

    n_steps = min(len(s) for s in seqs)
    agree_by_step = []
    for t in range(n_steps):
        counts = collections.Counter(s[t] for s in seqs if s[t] is not None)
        if not counts:
            agree_by_step.append(0.0)
            continue
        agree_by_step.append(counts.most_common(1)[0][1] / sum(counts.values()))

    print("modal-action agreement across seeds, by game day")
    print("(1.00 = every episode emits the identical action = blind replay)\n")
    print("  day   steps      agreement")
    for day in range(0, n_steps // TURNS_PER_DAY):
        lo, hi = day * TURNS_PER_DAY, (day + 1) * TURNS_PER_DAY
        window = agree_by_step[lo:hi]
        if not window:
            continue
        mean = sum(window) / len(window)
        bar = "#" * int(round(mean * 40))
        print("  %3d   %3d-%3d   %.3f  %s" % (day, lo, hi, mean, bar))

    overall = sum(agree_by_step) / len(agree_by_step)
    identical = sum(1 for a in agree_by_step if a >= 0.999)
    print("\noverall agreement      : %.3f" % overall)
    print("steps identical in ALL : %d of %d (%.1f%%)"
          % (identical, n_steps, 100.0 * identical / n_steps))
    print("steps with <90%% agreement: %d (%.1f%%)"
          % (sum(1 for a in agree_by_step if a < 0.9),
             100.0 * sum(1 for a in agree_by_step if a < 0.9) / n_steps))


if __name__ == "__main__":
    main()
