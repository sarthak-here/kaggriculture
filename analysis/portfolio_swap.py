"""Swap one bucket's route in the portfolio agent for a corpus route (#73).

The portfolio agent stores each route as its own b85+zlib blob:

    _ACTIONS_10C4S_3Q = json.loads(zlib.decompress(base64.b85decode('...')))

so a bucket can be replaced independently, leaving the selector, the other four
routes and every guard untouched. That makes each swap a clean one-variable A/B.

Routes come from the episodes classified into that same bucket by
`portfolio.py classify`, using the #64 alignment (route[i] = replay action[i+1]),
which is the alignment the base agent itself uses.

Usage:
    python analysis/portfolio_swap.py 10c4s_3q 3     # top 3 candidates for a bucket
"""

import base64
import json
import os
import re
import sys
import zlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "analysis"))

from rebuild_route import load, route_of  # noqa: E402

BASE = os.path.join(REPO, "variants", "pubnew", "prvsiyan", "main.py")
BUCKETS = os.path.join(REPO, "portfolio", "episode_buckets.json")
OUTROOT = os.path.join(REPO, "variants", "pf")

VAR = {
    "10c4s_3q": "_ACTIONS_10C4S_3Q",
    "8c6s_3q": "_ACTIONS_8C6S_3Q",
    "6c8s_3q": "_ACTIONS_6C8S_3Q",
    "6c12s_4q_first_yarn": "_ACTIONS_6C12S_4Q_FIRST_YARN",
    "6c12s_4q_second_yarn": "_ACTIONS_6C12S_4Q_SECOND_YARN",
}


def main():
    bucket = sys.argv[1] if len(sys.argv) > 1 else "10c4s_3q"
    topn = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    var = VAR[bucket]

    src = open(BASE, encoding="utf-8").read()
    pat = re.compile(
        re.escape(var) +
        r" = json\.loads\(zlib\.decompress\(base64\.b85decode\('[^']*'\)\)\.decode\('utf-8'\)\)")
    if not pat.search(src):
        print("!! could not find %s blob in the base agent" % var)
        return

    rows = json.load(open(BUCKETS))[bucket]
    rows = sorted(rows, key=lambda r: -r["reward"])[:topn]
    print("bucket %s -> %s   candidates: %d" % (bucket, var, len(rows)))

    made = []
    for r in rows:
        rt = route_of(load(r["episode_id"]), r["seat"])
        blob = base64.b85encode(zlib.compress(
            json.dumps(rt, separators=(",", ":")).encode(), 9)).decode()
        new = ("%s = json.loads(zlib.decompress(base64.b85decode('%s'))"
               ".decode('utf-8'))" % (var, blob))
        name = "%s_ep%d" % (bucket, r["episode_id"])
        d = os.path.join(OUTROOT, name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "main.py"), "w", encoding="utf-8").write(
            pat.sub(lambda _m: new, src, count=1))
        made.append(name)
        print("  %-34s ep %d  reward %7.0f  shops %s"
              % (name, r["episode_id"], r["reward"], r.get("shops")))
    print("\nwrote %d variants to %s" % (len(made), OUTROOT))


if __name__ == "__main__":
    main()
