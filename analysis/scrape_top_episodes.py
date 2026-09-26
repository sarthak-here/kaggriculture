"""Scrape ladder episodes played by the TOP-N teams, for behaviour cloning (#61).

Why this exists
---------------
Our existing `replays/` corpus is 36 of OUR OWN matches, so the strong seat in it
is whatever opponent we happened to draw. To clone expert play we want episodes
played by the actual top of the leaderboard.

How the API works (verified 2026-08-19, the bundled
`kaggle_environments.api` helper is STALE and 400s):

  * ListEpisodes lives at
        https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes
    and accepts `{"ids": [...]}` or `{"submissionId": N}`.
    It does NOT accept a teamId filter -- that is the whole difficulty here.
  * Its response carries three arrays: `episodes` (each with an `agents` list
    giving teamId / reward / seat index / rating), `submissions`, and `teams`
    (each with `publicLeaderboardSubmissionId`). So one call teaches us the
    leaderboard submission id of every team it mentions.
  * GetEpisodeReplay is GONE from that service (404). Replays come from the
    authenticated CLI instead: `kaggle competitions replay <id> -p <dir>`.

Because there is no teamId filter, reaching the top 10 needs a BFS: seed from a
submission we know, harvest `teams[]`, then expand through the highest-rated
team we have not visited yet. Matchmaking is rating-based, so this climbs the
ladder in a few hops.

Replays are ~31 MB of JSON each and gzip 62x, so they are stored gzipped and the
raw file is deleted immediately. ~0.5 MB per episode on disk.

Usage
-----
    python analysis/scrape_top_episodes.py --dry-run          # plan only
    python analysis/scrape_top_episodes.py --top 10 --max-per-team 40
    python analysis/scrape_top_episodes.py --resume           # safe to re-run

Everything is resumable: already-downloaded episodes are skipped, and the
discovery map is cached in `replays_top/discovery.json`.
"""

import argparse
import csv
import gzip
import io
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile

import requests

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "replays_top")
DISCOVERY = os.path.join(OUT_DIR, "discovery.json")
MANIFEST = os.path.join(OUT_DIR, "manifest.json")

LIST_URL = "https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes"
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
    "x-requested-with": "XMLHttpRequest",
}
COMPETITION = "kaggriculture"

# Be polite: this is an undocumented internal endpoint.
API_DELAY = 1.0


def log(msg):
    print(msg, flush=True)


# --------------------------------------------------------------------------
# leaderboard
# --------------------------------------------------------------------------

def fetch_leaderboard(cache_dir):
    """Download the public leaderboard and return [(rank, teamId, name, score)]."""
    os.makedirs(cache_dir, exist_ok=True)
    zip_path = os.path.join(cache_dir, COMPETITION + ".zip")
    if not os.path.exists(zip_path):
        subprocess.run(
            ["kaggle", "competitions", "leaderboard", COMPETITION, "-d", "-p", cache_dir],
            check=True, capture_output=True,
        )
    zf = zipfile.ZipFile(zip_path)
    name = zf.namelist()[0]
    rows = list(csv.reader(io.TextIOWrapper(zf.open(name), encoding="utf-8")))
    out = []
    for r in rows[1:]:
        # columns: Rank, TeamId, TeamName, LastSubmissionDate, Score, ...
        out.append((int(r[0]), str(r[1]), r[2], float(r[4])))
    return out


# --------------------------------------------------------------------------
# episode service
# --------------------------------------------------------------------------

def list_episodes(body, session, retries=4):
    for attempt in range(retries):
        try:
            resp = session.post(LIST_URL, json=body, headers=HEADERS, timeout=90)
        except requests.RequestException as exc:
            log("    request error: %s" % exc)
            time.sleep(5 * (attempt + 1))
            continue
        if resp.status_code == 200:
            time.sleep(API_DELAY)
            return resp.json()
        if resp.status_code in (429, 500, 502, 503):
            wait = 10 * (attempt + 1)
            log("    HTTP %d, backing off %ds" % (resp.status_code, wait))
            time.sleep(wait)
            continue
        log("    HTTP %d -> giving up on %s" % (resp.status_code, body))
        return None
    return None


def harvest(payload, team_to_sub, episode_rating):
    """Pull team -> leaderboard-submission and team -> best-seen-rating out of a response."""
    if not payload:
        return
    for team in payload.get("teams", []) or []:
        sub = team.get("publicLeaderboardSubmissionId")
        if sub:
            team_to_sub[str(team["id"])] = {"sub": sub, "name": team.get("teamName", "")}
    for ep in payload.get("episodes", []) or []:
        for ag in ep.get("agents", []) or []:
            tid = str(ag.get("teamId"))
            score = ag.get("updatedScore") or ag.get("initialScore")
            if tid and score:
                episode_rating[tid] = max(episode_rating.get(tid, 0.0), float(score))


def discover(targets, seed_submission, session, budget=40):
    """BFS up the ladder until every target team's LB submission id is known."""
    state = {"team_to_sub": {}, "episode_rating": {}, "visited": []}
    if os.path.exists(DISCOVERY):
        state = json.load(open(DISCOVERY))
        log("resuming discovery (%d teams known, %d visited)"
            % (len(state["team_to_sub"]), len(state["visited"])))

    team_to_sub = state["team_to_sub"]
    episode_rating = state["episode_rating"]
    visited = set(state["visited"])

    def missing():
        return [t for t in targets if t not in team_to_sub]

    if not visited:
        log("seeding discovery from submission %s" % seed_submission)
        harvest(list_episodes({"submissionId": seed_submission}, session),
                team_to_sub, episode_rating)
        visited.add(str(seed_submission))

    for _ in range(budget):
        todo = missing()
        if not todo:
            break
        # Expand through the highest-rated team we know but have not queried.
        frontier = [
            (rating, tid) for tid, rating in episode_rating.items()
            if tid in team_to_sub and str(team_to_sub[tid]["sub"]) not in visited
        ]
        if not frontier:
            log("frontier exhausted with %d target(s) still unresolved" % len(todo))
            break
        frontier.sort(reverse=True)
        rating, tid = frontier[0]
        sub = team_to_sub[tid]["sub"]
        log("  hop -> %-24s rating %7.1f  (missing %d)"
            % (team_to_sub[tid]["name"][:24], rating, len(todo)))
        harvest(list_episodes({"submissionId": sub}, session), team_to_sub, episode_rating)
        visited.add(str(sub))

        state.update(team_to_sub=team_to_sub, episode_rating=episode_rating,
                     visited=sorted(visited))
        os.makedirs(OUT_DIR, exist_ok=True)
        json.dump(state, open(DISCOVERY, "w"), indent=1)

    return team_to_sub, episode_rating


# --------------------------------------------------------------------------
# episode selection + download
# --------------------------------------------------------------------------

def episodes_for_team(team_id, submission_id, session):
    """Every episode that submission played, annotated with OUR target's seat."""
    payload = list_episodes({"submissionId": submission_id}, session)
    if not payload:
        return []
    rows = []
    for ep in payload.get("episodes", []) or []:
        agents = ep.get("agents", []) or []
        mine = next((a for a in agents if str(a.get("teamId")) == str(team_id)), None)
        if mine is None or ep.get("state") != "COMPLETED":
            continue
        others = [a for a in agents if a is not mine]
        opp = others[0] if others else {}
        reward = mine.get("reward")
        if reward is None:
            continue
        rows.append({
            "episode_id": ep["id"],
            "team_id": str(team_id),
            "seat": int(mine.get("index", 0) or 0),
            "reward": float(reward),
            "opp_reward": float(opp.get("reward") or 0),
            "rating": float(mine.get("updatedScore") or 0),
            "won": float(reward) > float(opp.get("reward") or 0),
        })
    return rows


def download_episode(episode_id, session=None):
    """CLI download -> gzip -> delete raw. Returns path or None."""
    gz_path = os.path.join(OUT_DIR, "episode-%d-replay.json.gz" % episode_id)
    if os.path.exists(gz_path):
        return gz_path
    raw_path = os.path.join(OUT_DIR, "episode-%d-replay.json" % episode_id)
    proc = subprocess.run(
        ["kaggle", "competitions", "replay", str(episode_id), "-p", OUT_DIR, "-q"],
        capture_output=True, text=True,
    )
    if not os.path.exists(raw_path):
        log("    download failed for %d: %s" % (episode_id, (proc.stderr or proc.stdout)[:160]))
        return None
    try:
        with open(raw_path, "rb") as src, gzip.open(gz_path, "wb", compresslevel=6) as dst:
            shutil.copyfileobj(src, dst)
    finally:
        os.remove(raw_path)
    return gz_path


# --------------------------------------------------------------------------

def main():
    global OUT_DIR, DISCOVERY, MANIFEST
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=10, help="how many leaderboard teams to target")
    ap.add_argument("--max-per-team", type=int, default=40,
                    help="best-N episodes per team, ranked by that team's reward")
    ap.add_argument("--wins-only", action="store_true",
                    help="keep only episodes the target team won")
    ap.add_argument("--seed-submission", type=int, default=55555746,
                    help="a submission id to start the BFS from (default: ours)")
    ap.add_argument("--out-dir", type=str, default=OUT_DIR,
                    help="independent corpus directory (default: replays_top)")
    ap.add_argument("--dry-run", action="store_true", help="plan only, download nothing")
    args = ap.parse_args()

    OUT_DIR = os.path.abspath(args.out_dir)
    DISCOVERY = os.path.join(OUT_DIR, "discovery.json")
    MANIFEST = os.path.join(OUT_DIR, "manifest.json")

    os.makedirs(OUT_DIR, exist_ok=True)
    session = requests.Session()

    lb = fetch_leaderboard(os.path.join(OUT_DIR, "_lb"))
    top = lb[:args.top]
    targets = [t[1] for t in top]
    log("TARGETS (top %d of %d teams):" % (args.top, len(lb)))
    for rank, tid, name, score in top:
        log("  %3d  %-26s team %s  score %.1f" % (rank, name[:26], tid, score))

    log("\n--- discovery: resolving leaderboard submission ids ---")
    team_to_sub, _ = discover(targets, args.seed_submission, session)
    resolved = [t for t in targets if t in team_to_sub]
    log("resolved %d of %d target teams" % (len(resolved), len(targets)))

    log("\n--- listing episodes ---")
    selected, per_team = [], {}
    for rank, tid, name, score in top:
        if tid not in team_to_sub:
            log("  %-26s UNRESOLVED - skipped" % name[:26])
            continue
        rows = episodes_for_team(tid, team_to_sub[tid]["sub"], session)
        if args.wins_only:
            rows = [r for r in rows if r["won"]]
        rows.sort(key=lambda r: r["reward"], reverse=True)
        rows = rows[:args.max_per_team]
        for r in rows:
            r["team_name"] = name
            r["rank"] = rank
        selected.extend(rows)
        per_team[name] = len(rows)
        best = rows[0]["reward"] if rows else 0
        log("  %-26s %3d episodes kept, best reward %8.0f" % (name[:26], len(rows), best))

    # De-duplicate: top teams play each other, so the same episode can appear twice.
    seen, unique = set(), []
    for r in selected:
        if r["episode_id"] in seen:
            continue
        seen.add(r["episode_id"])
        unique.append(r)

    have = {int(f.split("-")[1]) for f in os.listdir(OUT_DIR) if f.endswith(".json.gz")}
    todo = [r for r in unique if r["episode_id"] not in have]
    log("\n%d unique episodes selected, %d already on disk, %d to download (~%.1f GB transfer, ~%.0f MB stored)"
        % (len(unique), len(unique) - len(todo), len(todo), len(todo) * 0.031, len(todo) * 0.5))

    json.dump(unique, open(MANIFEST, "w"), indent=1)
    log("manifest -> %s" % MANIFEST)

    if args.dry_run:
        log("\n--dry-run: stopping before download.")
        return

    log("\n--- downloading ---")
    ok = 0
    for i, r in enumerate(todo, 1):
        path = download_episode(r["episode_id"])
        if path:
            ok += 1
        if i % 10 == 0 or i == len(todo):
            log("  %d/%d downloaded (%d ok)" % (i, len(todo), ok))
    log("\ndone: %d episodes on disk in %s" % (len(have) + ok, OUT_DIR))


if __name__ == "__main__":
    main()
