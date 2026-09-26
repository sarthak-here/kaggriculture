"""Build deterministic replay-tape opponents for Cha22's four MILK slot losses."""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
from pathlib import Path
import zlib


ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "analysis/cha22_live_56556133_20260926"
EPISODES = (113418129, 113426386, 113471121, 113593430)


def canonical(action):
    action = action if isinstance(action, dict) else {}
    return {"farmer": list(action.get("farmer") or ["PASS"]),
            "hands": [list(row) for row in (action.get("hands") or [])],
            "market": [list(row) for row in (action.get("market") or [])]}


def main() -> int:
    profile = json.loads((CORPUS / "profile.json").read_text(encoding="utf-8"))
    records = {int(row["episode"]): row for row in profile["records"]}
    rows = []
    for episode in EPISODES:
        record = records[episode]
        own_seat = int(record["seat"]); opponent_seat = 1 - own_seat
        with gzip.open(CORPUS / "replays" / f"episode-{episode}-replay.json.gz",
                       "rt", encoding="utf-8") as handle:
            replay = json.load(handle)
        tape = [canonical(replay["steps"][step + 1][opponent_seat].get("action"))
                for step in range(719)]
        payload = base64.b85encode(zlib.compress(
            json.dumps(tape, separators=(",", ":")).encode(), 9)).decode("ascii")
        source = ("import base64,copy,json,zlib\n"
                  f"_T=json.loads(zlib.decompress(base64.b85decode({payload!r})).decode())\n"
                  "def replay_tape_agent(observation,configuration=None):\n"
                  "    return copy.deepcopy(_T[min(718,int(observation['step']))])\n")
        target = ROOT / f"analysis/cha22_milk_race_tapes/{episode}/main.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        compile(source, str(target), "exec")
        target.write_text(source, encoding="utf-8")
        rows.append({"episode": episode, "seed": int(replay["info"]["seed"]),
                     "own_seat": own_seat, "opponent_seat": opponent_seat,
                     "opponent": record["opponent"], "tape": str(target.relative_to(ROOT)),
                     "sha256": hashlib.sha256(source.encode()).hexdigest()})
    manifest = ROOT / "analysis/cha22_milk_race_tapes/manifest.json"
    manifest.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(rows, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
