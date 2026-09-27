"""Build one deterministic opponent tape from a downloaded replay."""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path
import zlib


ROOT = Path(__file__).resolve().parents[1]


def canonical(action):
    action = action if isinstance(action, dict) else {}
    return {
        "farmer": list(action.get("farmer") or ["PASS"]),
        "hands": [list(row) for row in (action.get("hands") or [])],
        "market": [list(row) for row in (action.get("market") or [])],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("replay", type=Path)
    parser.add_argument("--seat", type=int, choices=(0, 1), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    replay_path = (ROOT / args.replay).resolve()
    opener = gzip.open if replay_path.suffix == ".gz" else open
    with opener(replay_path, "rt", encoding="utf-8") as handle:
        replay = json.load(handle)
    tape = [canonical(replay["steps"][step + 1][args.seat].get("action"))
            for step in range(719)]
    payload = base64.b85encode(zlib.compress(
        json.dumps(tape, separators=(",", ":")).encode(), 9)).decode("ascii")
    source = (
        "import base64,copy,json,zlib\n"
        f"_T=json.loads(zlib.decompress(base64.b85decode({payload!r})).decode())\n"
        "def replay_tape_agent(observation,configuration=None):\n"
        "    return copy.deepcopy(_T[min(718,int(observation['step']))])\n"
    )
    output = (ROOT / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    compile(source, str(output), "exec")
    output.write_text(source, encoding="utf-8")
    print(json.dumps({
        "episode": replay["id"], "seed": replay["info"]["seed"],
        "seat": args.seat, "output": str(output.relative_to(ROOT)),
        "sha256": hashlib.sha256(source.encode()).hexdigest(),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
