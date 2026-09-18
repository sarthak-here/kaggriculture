"""Audit a rival step-1 physical signature across a replay corpus."""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import json
from pathlib import Path


def load(path: Path):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return json.loads(raw)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--money", type=float, action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    paths = sorted(args.corpus.glob("episode-*-replay.json.gz"))
    paths += sorted(args.corpus.glob("episode-*-replay.json"))
    counts = Counter()
    hits = []
    for path in paths:
        replay = load(path)
        if len(replay.get("steps", [])) < 2:
            continue
        for seat in (0, 1):
            obs = replay["steps"][1][seat]["observation"]
            rival = obs["farms"][1 - seat]
            signature = (
                float(rival["money"]), len(rival["hands"]),
                len(rival["unlocked_quadrants"]), tuple(rival["farmer"]),
            )
            counts[signature] += 1
            if signature in {(money, 0, 1, (4, 4)) for money in args.money}:
                hits.append({
                    "episode": int(path.name.split("-")[1]), "seat": seat,
                    "teams": replay.get("info", {}).get("TeamNames", []),
                    "path": str(path),
                })
    result = {
        "replays": len(paths), "observed_openings": sum(counts.values()),
        "distinct_signatures": len(counts), "target_money": args.money,
        "hit_count": len(hits), "hits": hits,
        "most_common": [
            {"signature": list(key), "count": value}
            for key, value in counts.most_common(20)
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in result if key != "most_common"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
