"""Compare pf_all's LOSSES against rating-matched WINS to find a fixable pattern (#81).

Looking only at losses finds patterns that are equally present in wins. The
control group is what makes a difference actionable, so wins are drawn from
opponents rated 2,759-2,843 -- the same band the losses come from.

Everything monetary is per-step money deltas (#77): SELL order quantities are
requests, not sales.
"""

import json
import os
import statistics
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "analysis"))
from portfolio import label_for  # noqa: E402

DIR = os.path.join(REPO, "loss_analysis")


def profile(ep_id):
    path = os.path.join(DIR, "episode-%d-replay.json" % ep_id)
    if not os.path.exists(path):
        return None
    d = json.load(open(path, encoding="utf-8"))
    names = (d.get("info") or {}).get("TeamNames") or ["", ""]
    me = 0 if "Sarthak" in str(names[0]) else 1
    st = d.get("steps") or []
    if not st:
        return None

    out = {}
    for seat, tag in ((me, "us"), (1 - me, "op")):
        inc = sp = 0.0
        prev = None
        feed = 0
        fc = 0.0
        sells = 0
        for i in range(len(st)):
            o = st[i][seat].get("observation")
            if not isinstance(o, dict):
                continue
            m = float(((o.get("farms") or [{}])[seat]).get("money") or 0)
            if prev is not None:
                dm = m - prev
                if dm > 0:
                    inc += dm
                else:
                    sp += -dm
            prev = m
        for i in range(len(st) - 1):
            a = st[i + 1][seat].get("action")
            o = st[i][seat].get("observation")
            if not isinstance(a, dict) or not isinstance(o, dict):
                continue
            pr = (o.get("market") or {}).get("prices") or {}
            for op in a.get("market") or []:
                if not op or len(op) < 3:
                    continue
                if op[0] == "BUY_PRODUCT":
                    feed += int(op[2])
                    fc += int(op[2]) * float(pr.get(op[1], 0) or 0)
                elif op[0] == "SELL":
                    sells += 1
        last = st[-1][seat]["observation"]
        farm = last["farms"][seat]
        tiles = farm.get("tiles") or []
        out[tag] = {
            "reward": st[-1][seat]["reward"],
            "income": inc, "spend": sp,
            "feed_u": feed, "feed_c": fc,
            "sell_orders": sells,
            "quads": len(farm.get("unlocked_quadrants") or []),
            "animals": sum(1 for r in tiles for t in r
                           if isinstance(t, dict) and t.get("animal")),
            "planted": sum(1 for r in tiles for t in r
                           if isinstance(t, dict) and t.get("kind") == "PLANT"),
        }
    obs0 = st[-1][0]["observation"]
    out["bucket"] = label_for(list((obs0.get("town") or {}).get("unlocked_shops") or []))
    return out


def main():
    data = json.load(open(os.path.join(REPO, "portfolio", "pfall_LW.json")))
    groups = {}
    for key, label in (("L", "LOSSES"), ("W", "WINS")):
        rows = []
        for x in data[key]:
            p = profile(x["ep"])
            if p:
                p["margin"] = x["margin"]
                p["opp"] = x["opp"]
                p["oppR"] = x["oppR"]
                rows.append(p)
        groups[label] = rows

    keys = [("income", "us"), ("spend", "us"), ("feed_u", "us"), ("feed_c", "us"),
            ("quads", "us"), ("animals", "us"), ("planted", "us"), ("sell_orders", "us")]
    print("%-14s %14s %14s %12s" % ("metric", "LOSSES (n=%d)" % len(groups["LOSSES"]),
                                    "WINS (n=%d)" % len(groups["WINS"]), "delta"))
    for k, side in keys:
        lv = [r[side][k] for r in groups["LOSSES"]]
        wv = [r[side][k] for r in groups["WINS"]]
        lm, wm = statistics.mean(lv), statistics.mean(wv)
        print("%-14s %14.1f %14.1f %12.1f" % ("our " + k, lm, wm, lm - wm))

    print()
    print("OPPONENT side:")
    for k in ("income", "spend", "feed_u", "quads", "animals", "planted"):
        lv = [r["op"][k] for r in groups["LOSSES"]]
        wv = [r["op"][k] for r in groups["WINS"]]
        print("%-14s %14.1f %14.1f %12.1f"
              % ("opp " + k, statistics.mean(lv), statistics.mean(wv),
                 statistics.mean(lv) - statistics.mean(wv)))

    print()
    print("bucket mix:")
    for label in ("LOSSES", "WINS"):
        c = {}
        for r in groups[label]:
            c[r["bucket"]] = c.get(r["bucket"], 0) + 1
        print("  %-8s %s" % (label, c))

    print()
    print("per-match detail (losses):")
    for r in sorted(groups["LOSSES"], key=lambda z: z["margin"]):
        print("  %-18s m%+7.0f  bucket %-22s us: inc %7.0f sp %6.0f feed %4d q%d | op: inc %7.0f sp %6.0f feed %4d q%d"
              % (r["opp"][:18], r["margin"], r["bucket"],
                 r["us"]["income"], r["us"]["spend"], r["us"]["feed_u"], r["us"]["quads"],
                 r["op"]["income"], r["op"]["spend"], r["op"]["feed_u"], r["op"]["quads"]))


if __name__ == "__main__":
    main()
