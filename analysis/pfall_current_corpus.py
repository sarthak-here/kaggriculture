"""Download and manifest every completed loss for one Kaggle submission."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

import requests

URL = "https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
    "x-requested-with": "XMLHttpRequest",
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("submission_id", type=int)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--reuse", type=Path, action="append", default=[])
    args = parser.parse_args()
    response = requests.post(URL, json={"submissionId": args.submission_id},
                             headers=HEADERS, timeout=90)
    response.raise_for_status()
    rows = []
    for episode in response.json().get("episodes", []) or []:
        agents = episode.get("agents", []) or []
        mine_rows = [agent for agent in agents
                     if agent.get("submissionId") == args.submission_id]
        if len(mine_rows) != 1:
            continue
        mine = mine_rows[0]
        opponents = [agent for agent in agents if agent is not mine]
        if not opponents or mine.get("reward") is None:
            continue
        opponent = opponents[0]
        ours = float(mine.get("reward") or 0)
        theirs = float(opponent.get("reward") or 0)
        if ours >= theirs:
            continue
        rows.append({
            "episode": int(episode["id"]),
            "end": episode.get("endTime") or "",
            "seat": int(mine.get("index", 0) or 0),
            "ours": ours,
            "theirs": theirs,
            "margin": ours - theirs,
            "our_score": float(mine.get("updatedScore") or mine.get("initialScore") or 0),
            "opponent_submission": opponent.get("submissionId"),
            "opponent_score": float(opponent.get("updatedScore") or opponent.get("initialScore") or 0),
        })
    rows.sort(key=lambda row: row["end"])
    args.out.mkdir(parents=True, exist_ok=True)
    json.dump(rows, open(args.out / "manifest.json", "w", encoding="utf-8"), indent=2)
    reused = downloaded = failed = 0
    for index, row in enumerate(rows, 1):
        episode_id = row["episode"]
        target = args.out / f"episode-{episode_id}-replay.json"
        if target.exists():
            reused += 1
            continue
        source = next((root / target.name for root in args.reuse
                       if (root / target.name).exists()), None)
        if source:
            shutil.copy2(source, target)
            reused += 1
        else:
            proc = subprocess.run([
                "kaggle", "competitions", "replay", str(episode_id),
                "-p", str(args.out), "-q",
            ], capture_output=True, text=True)
            if target.exists():
                downloaded += 1
            else:
                failed += 1
                print("failed", episode_id, (proc.stderr or proc.stdout)[:160], flush=True)
        if index % 10 == 0 or index == len(rows):
            print(f"{index}/{len(rows)} reused={reused} downloaded={downloaded} failed={failed}", flush=True)
    print(f"losses={len(rows)} reused={reused} downloaded={downloaded} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())