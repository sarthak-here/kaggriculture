"""Profile what an agent does while a unit is standing on a weed tile."""

from __future__ import annotations

import collections
import gzip
import json
import sys
from pathlib import Path


def load(path: Path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    root = Path(sys.argv[1])
    target_name = sys.argv[2] if len(sys.argv) > 2 else None
    verbs = collections.Counter()
    by_actor = collections.Counter()
    by_day = collections.Counter()
    episodes = 0
    for path in sorted(root.glob("*.json*")):
        replay = load(path)
        agents = replay.get("agents") or []
        seat = 0
        if target_name:
            matches = [i for i, row in enumerate(agents)
                       if target_name.lower() in str(row).lower()]
            if not matches:
                continue
            seat = matches[0]
        episodes += 1
        steps = replay.get("steps") or []
        for index in range(len(steps) - 1):
            try:
                obs = steps[index][seat]["observation"]
                action = steps[index + 1][seat].get("action") or {}
                farm = obs["farms"][seat]
            except (IndexError, KeyError, TypeError):
                continue
            positions = [farm.get("farmer"), *(farm.get("hands") or [])]
            actions = [action.get("farmer"), *(action.get("hands") or [])]
            tiles = farm.get("tiles") or []
            for actor, (position, operation) in enumerate(zip(positions, actions)):
                if not position or not operation:
                    continue
                x, y = map(int, position[:2])
                try:
                    tile = tiles[y][x]
                except (IndexError, TypeError):
                    continue
                if isinstance(tile, dict) and tile.get("kind") == "WEED":
                    verb = str(operation[0]) if operation else "MISSING"
                    verbs[verb] += 1
                    by_actor["farmer" if actor == 0 else "hand"] += 1
                    by_day[index // 24] += 1
    print("episodes", episodes)
    print("weed-occupied actor turns", sum(verbs.values()))
    print("verbs", dict(verbs.most_common()))
    print("actors", dict(by_actor.most_common()))
    print("days", dict(sorted(by_day.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
