"""Has a submission's ladder rating CONVERGED, or is it still climbing from 600?

Ratings seed at 600 and rise as matches accrue, so a young submission always
reads low. Comparing a fresh submission's score against a mature one is the
single easiest way to draw a wrong conclusion in this competition.

This pulls the real match record for each submission and reports the rating
trajectory, so "worse" can be distinguished from "younger".

Usage: python analysis/submission_progress.py 55622619 55555746
"""

import sys
import time

import requests

LIST_URL = "https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
    "x-requested-with": "XMLHttpRequest",
}


def episodes_for(submission_id, session):
    resp = session.post(LIST_URL, json={"submissionId": submission_id},
                        headers=HEADERS, timeout=90)
    resp.raise_for_status()
    time.sleep(1.0)
    return resp.json()


def report(submission_id, session):
    payload = episodes_for(submission_id, session)
    rows = []
    for ep in payload.get("episodes", []) or []:
        if ep.get("state") != "COMPLETED":
            continue
        agents = ep.get("agents", []) or []
        mine = next((a for a in agents if a.get("submissionId") == submission_id), None)
        if mine is None or mine.get("reward") is None:
            continue
        opp = next((a for a in agents if a is not mine), {})
        rows.append({
            "end": ep.get("endTime") or "",
            "reward": float(mine["reward"]),
            "opp_reward": float(opp.get("reward") or 0),
            "score_before": float(mine.get("initialScore") or 0),
            "score_after": float(mine.get("updatedScore") or 0),
            "opp_score": float(opp.get("updatedScore") or opp.get("initialScore") or 0),
        })
    rows.sort(key=lambda r: r["end"])

    if not rows:
        print("submission %d: no completed episodes" % submission_id)
        return

    wins = sum(1 for r in rows if r["reward"] > r["opp_reward"])
    losses = sum(1 for r in rows if r["reward"] < r["opp_reward"])
    ties = len(rows) - wins - losses

    print("\n=== submission %d ===" % submission_id)
    print("  matches played : %d   (W %d / L %d / T %d)  win rate %.1f%%"
          % (len(rows), wins, losses, ties,
             100.0 * wins / max(1, wins + losses)))
    print("  rating         : %.1f -> %.1f" % (rows[0]["score_before"], rows[-1]["score_after"]))
    print("  mean opponent  : %.1f" % (sum(r["opp_score"] for r in rows) / len(rows)))
    print("  mean reward    : %.0f   (opponents %.0f)"
          % (sum(r["reward"] for r in rows) / len(rows),
             sum(r["opp_reward"] for r in rows) / len(rows)))

    # Is it still climbing? Compare rating gain over the last quarter of matches.
    q = max(2, len(rows) // 4)
    recent = rows[-q:]
    drift = recent[-1]["score_after"] - recent[0]["score_before"]
    print("  last %d matches : rating %+.1f  (%s)"
          % (q, drift,
             "STILL CLIMBING" if drift > 25 else
             "still drifting" if abs(drift) > 10 else "converged"))
    print("  recent win rate: %.1f%%"
          % (100.0 * sum(1 for r in recent if r["reward"] > r["opp_reward"]) / max(1, len(recent))))
    return rows


def main():
    ids = [int(x) for x in sys.argv[1:]] or [55622619, 55555746]
    session = requests.Session()
    for sid in ids:
        report(sid, session)


if __name__ == "__main__":
    main()
