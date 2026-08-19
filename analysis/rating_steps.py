"""What does a win actually PAY at this point in the submission's life?"""
import sys, time, requests

LIST_URL = "https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes"
H = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0",
     "x-requested-with": "XMLHttpRequest"}


def rows_for(sid, s):
    r = s.post(LIST_URL, json={"submissionId": sid}, headers=H, timeout=90).json()
    time.sleep(1.0)
    out = []
    for ep in r.get("episodes", []) or []:
        if ep.get("state") != "COMPLETED":
            continue
        ags = ep.get("agents", []) or []
        me = next((a for a in ags if a.get("submissionId") == sid), None)
        if me is None or me.get("reward") is None:
            continue
        opp = next((a for a in ags if a is not me), {})
        before = float(me.get("initialScore") or 0)
        after = float(me.get("updatedScore") or 0)
        if not before or not after:
            continue
        out.append({
            "end": ep.get("endTime") or "",
            "d": after - before,
            "before": before, "after": after,
            "win": float(me["reward"]) > float(opp.get("reward") or 0),
            "opp": float(opp.get("updatedScore") or opp.get("initialScore") or 0),
        })
    out.sort(key=lambda x: x["end"])
    return out


def main():
    sid = int(sys.argv[1]) if len(sys.argv) > 1 else 55622619
    s = requests.Session()
    rows = rows_for(sid, s)
    print("submission %d : %d rated matches\n" % (sid, len(rows)))

    n = len(rows)
    print("  segment        matches   mean win pay   mean loss pay   net/match   rating")
    for lo, hi, label in [(0, n // 4, "first 25%"), (n // 4, n // 2, "2nd 25%"),
                          (n // 2, 3 * n // 4, "3rd 25%"), (3 * n // 4, n, "last 25%")]:
        seg = rows[lo:hi]
        if not seg:
            continue
        w = [r["d"] for r in seg if r["win"]]
        l = [r["d"] for r in seg if not r["win"]]
        print("  %-13s %5d     %+8.2f       %+8.2f     %+7.2f    %.1f -> %.1f"
              % (label, len(seg),
                 sum(w) / len(w) if w else 0.0,
                 sum(l) / len(l) if l else 0.0,
                 sum(r["d"] for r in seg) / len(seg),
                 seg[0]["before"], seg[-1]["after"]))

    tail = rows[-20:]
    net = sum(r["d"] for r in tail) / len(tail)
    print("\n  last 20 matches: net %+.2f rating/match, win rate %.0f%%, mean opponent %.0f"
          % (net, 100.0 * sum(1 for r in tail if r["win"]) / len(tail),
             sum(r["opp"] for r in tail) / len(tail)))
    cur = rows[-1]["after"]
    for target in (2292.2,):
        if net > 0:
            print("  at that rate, %.1f -> %.1f needs ~%.0f more matches"
                  % (cur, target, (target - cur) / net))
        else:
            print("  net is NOT positive - it is not climbing toward %.1f" % target)


main()
