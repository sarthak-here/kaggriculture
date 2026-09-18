"""Compare agents against frozen action tapes extracted from replay files."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import tempfile

from run_w13_isolated import play


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path):
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return json.loads(raw)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--opponent", required=True)
    parser.add_argument("--agent", action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    paths = sorted(args.corpus.glob("episode-*-replay.json"))
    paths += sorted(args.corpus.glob("episode-*-replay.json.gz"))
    agents = [Path(value) for value in args.agent]
    rows = []
    with tempfile.TemporaryDirectory(prefix="kag-tapes-") as temp:
        folder = Path(temp)
        tape_path = folder / "tape.json"
        policy_path = folder / "main.py"
        policy_path.write_text(
            "import json\nfrom pathlib import Path\nTAPE=None\n"
            "def agent(obs,config=None):\n global TAPE\n"
            " if TAPE is None:TAPE=json.loads((Path(agent.__code__.co_filename).resolve().parent/'tape.json').read_text())\n"
            " return TAPE[obs['step']]\n", encoding="utf-8",
        )
        for path in paths:
            replay = load(path)
            teams = replay.get("info", {}).get("TeamNames", [])
            if teams.count(args.opponent) != 1:
                continue
            opponent_seat = teams.index(args.opponent)
            candidate_seat = 1 - opponent_seat
            tape = [step[opponent_seat]["action"] for step in replay["steps"][1:]]
            tape_path.write_text(json.dumps(tape) + "\n", encoding="utf-8")
            seed = int(replay["info"]["seed"])
            for agent in agents:
                absolute = (ROOT / agent).resolve()
                result = play(str(absolute), str(policy_path), seed, candidate_seat)
                rows.append({
                    "episode": int(path.name.split("-")[1]), "seed": seed,
                    "opponent_seat": opponent_seat, "agent": str(agent),
                    "agent_sha256": hashlib.sha256(absolute.read_bytes()).hexdigest(),
                    **result,
                })
                print(path.name, agent, result.get("status"), result.get("a"), result.get("b"), flush=True)
    output = (ROOT / args.out).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return 1 if any(row["status"] != "DONE" for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
