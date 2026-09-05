"""Summarize router branches and opening families in a replay sample."""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

from pfall_clone_profile import distance


def compact_action(action):
    action = action if isinstance(action, dict) else {}
    market = action.get("market") or []
    return ";".join("|".join(map(str, row)) for row in market)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((args.corpus / "manifest.json").read_text(encoding="utf-8-sig"))
    profiles = json.loads((args.corpus / "profiles.json").read_text(encoding="utf-8"))
    metadata = {row["episode"]: row for row in manifest}
    profile_by_id = {row["episode"]: row for row in profiles}
    rows = []

    for path in sorted(args.corpus.glob("episode-*-replay.json")):
        episode = int(path.name.split("-")[1])
        replay = json.loads(path.read_text(encoding="utf-8"))
        meta = metadata[episode]
        profile = profile_by_id[episode]
        seat = int(meta["seat"])
        opponent_seat = 1 - seat
        steps = replay.get("steps") or []
        obs1 = steps[1][seat].get("observation") or {}
        opponent = (obs1.get("farms") or [{}, {}])[opponent_seat]
        hands = len(opponent.get("hands") or [])
        money = float(opponent.get("money") or 0)
        quads = len(opponent.get("unlocked_quadrants") or [])
        soil = hands == 5 and money <= 10 and quads == 1
        streak = best = 0
        for index in range(120, min(244, len(steps))):
            obs = steps[index][seat].get("observation") or {}
            streak = streak + 1 if distance(obs) <= 2 else 0
            best = max(best, streak)
        clone = best >= 24
        behavior_changed = clone and profile["bucket"] == "NO-YARN-3"
        opening = steps[1][opponent_seat].get("action")
        final_obs = steps[-1][seat].get("observation") or {}
        shops = list((final_obs.get("town") or {}).get("unlocked_shops") or [])
        rows.append({
            "episode": episode,
            "result": meta["result"],
            "seat": seat,
            "margin": meta["margin"],
            "bucket": profile["bucket"],
            "op_family": profile["op_family"],
            "soil_branch": soil,
            "clone_latch": clone,
            "clone_changed_route": behavior_changed,
            "op_hands_step1": hands,
            "op_money_step1": money,
            "op_opening_market": compact_action(opening),
            "shops": shops,
        })

    for label, group in (("LOSSES", [r for r in rows if r["result"] == "L"]),
                         ("WINS", [r for r in rows if r["result"] == "W"])):
        print(f"\n{label} {len(group)}")
        for key in ("bucket", "op_family", "soil_branch", "clone_latch",
                    "clone_changed_route", "op_hands_step1", "op_opening_market"):
            print(key, collections.Counter(r[key] for r in group).most_common(12))
    target = args.corpus / "router_sample.json"
    target.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("wrote", target)


if __name__ == "__main__":
    main()
