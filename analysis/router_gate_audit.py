"""Audit whether the submitted Kaito/Soil opening gate fired in replays."""

import argparse
import json
from pathlib import Path

from pfall_clone_profile import distance


def get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, required=True)
    args = parser.parse_args()

    triggered = []
    for path in sorted(args.corpus.glob("episode-*-replay.json")):
        replay = json.load(open(path, encoding="utf-8"))
        steps = replay.get("steps") or []
        if len(steps) < 2:
            continue
        agents = steps[1]
        our_seat = next(
            (index for index, agent in enumerate(agents)
             if (agent.get("observation") or {}).get("player") == index),
            None,
        )
        # Replay observations identify the observing player.  Submission
        # metadata is more reliable when both observations are present.
        episode = int(path.name.split("-")[1])
        manifest = json.load(open(args.corpus / "manifest.json", encoding="utf-8"))
        meta = next(row for row in manifest if row["episode"] == episode)
        our_seat = int(meta["seat"])
        obs = agents[our_seat].get("observation") or {}
        farms = list(get(obs, "farms", []) or [])
        opponent = farms[1 - our_seat] if len(farms) >= 2 else {}
        hands = len(get(opponent, "hands", []) or [])
        money = float(get(opponent, "money", 0) or 0)
        quads = len(get(opponent, "unlocked_quadrants", []) or [])
        fired = hands == 5 and money <= 10.0 and quads == 1
        streak = current = 0
        for index in range(120, min(244, len(steps))):
            sample = steps[index][our_seat].get("observation") or {}
            current = current + 1 if distance(sample) <= 2 else 0
            streak = max(streak, current)
        if fired:
            triggered.append(episode)
        print(f"{episode} seat={our_seat} gate={fired} "
              f"hands={hands} money={money:.0f} quads={quads} "
              f"pre243_clone_streak={streak}")

    print(f"triggered {len(triggered)}: {triggered}")


if __name__ == "__main__":
    main()
