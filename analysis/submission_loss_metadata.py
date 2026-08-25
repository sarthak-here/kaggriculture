"""Print compact metadata for every completed loss of a Kaggle submission."""

import json
import sys

import requests


URL = "https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
    "x-requested-with": "XMLHttpRequest",
}


def main():
    submission_id = int(sys.argv[1])
    include_all = "--all" in sys.argv[2:]
    response = requests.post(URL, json={"submissionId": submission_id},
                             headers=HEADERS, timeout=90)
    response.raise_for_status()
    rows = []
    for episode in response.json().get("episodes", []) or []:
        agents = episode.get("agents", []) or []
        mine = next((agent for agent in agents
                     if agent.get("submissionId") == submission_id), None)
        opponent = next((agent for agent in agents if agent is not mine), {})
        if mine is None or mine.get("reward") is None:
            continue
        ours = float(mine.get("reward") or 0)
        theirs = float(opponent.get("reward") or 0)
        if not include_all and ours >= theirs:
            continue
        rows.append({
            "episode": int(episode["id"]),
            "end": episode.get("endTime") or "",
            "seat": int(mine.get("index", 0) or 0),
            "ours": ours,
            "theirs": theirs,
            "margin": ours - theirs,
            "result": "W" if ours > theirs else "L" if ours < theirs else "T",
            "our_before": float(mine.get("initialScore") or 0),
            "our_after": float(mine.get("updatedScore") or 0),
            "opponent": opponent.get("teamName") or opponent.get("name") or "?",
            "opponent_submission": opponent.get("submissionId"),
            "opponent_score": float(opponent.get("updatedScore")
                                    or opponent.get("initialScore") or 0),
        })
    rows.sort(key=lambda row: row["end"])
    if "--recent-wins" in sys.argv:
        count = int(sys.argv[sys.argv.index("--recent-wins") + 1])
        rows = [row for row in rows if row["result"] == "W"][-count:]
    if "--summary" in sys.argv:
        from collections import Counter
        print(json.dumps({"total": len(rows),
                          "by_result": dict(Counter(row["result"] for row in rows)),
                          "by_seat_result": {str(key): value for key, value in
                                             Counter((row["seat"], row["result"])
                                                     for row in rows).items()}}, indent=2))
        return
    print(json.dumps(rows, indent=2))


if __name__ == "__main__":
    main()
