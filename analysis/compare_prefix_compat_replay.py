"""Compare two candidate prefixes against the opponent tape in one replay."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

from compare_agent_prefix_compat import own_state, run


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("replay", type=Path)
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--candidate-team", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    replay = json.loads((ROOT / args.replay).read_text(encoding="utf-8"))
    teams = replay["info"]["TeamNames"]
    candidate_seat = teams.index(args.candidate_team)
    opponent_seat = 1 - candidate_seat
    with tempfile.TemporaryDirectory(prefix="prefix-tape-") as temp:
        folder = Path(temp)
        (folder / "tape.json").write_text(json.dumps([
            step[opponent_seat]["action"] for step in replay["steps"][1:]
        ]) + "\n", encoding="utf-8")
        tape = folder / "main.py"
        tape.write_text(
            "import json\nfrom pathlib import Path\nTAPE=None\n"
            "def agent(obs,config=None):\n global TAPE\n"
            " if TAPE is None:TAPE=json.loads((Path(agent.__code__.co_filename).resolve().parent/'tape.json').read_text())\n"
            " return TAPE[obs['step']]\n", encoding="utf-8",
        )
        left = run((ROOT / args.left).resolve(), tape, int(replay["info"]["seed"]), candidate_seat)
        right = run((ROOT / args.right).resolve(), tape, int(replay["info"]["seed"]), candidate_seat)
    first_state = next((i for i, pair in enumerate(zip(left, right))
                        if own_state(pair[0], candidate_seat) != own_state(pair[1], candidate_seat)), None)
    first_action = next((i for i, pair in enumerate(zip(left, right))
                         if pair[0][candidate_seat].get("action") != pair[1][candidate_seat].get("action")), None)
    result = {
        "episode": int(replay["info"].get("EpisodeId") or 0),
        "seed": int(replay["info"]["seed"]), "candidate_seat": candidate_seat,
        "left": str(args.left), "right": str(args.right),
        "first_state_divergence": first_state, "first_action_divergence": first_action,
        "left_reward": left[-1][candidate_seat]["reward"],
        "right_reward": right[-1][candidate_seat]["reward"],
    }
    output = (ROOT / args.out).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
