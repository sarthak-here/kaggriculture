"""Find the earliest state/action divergence between two agents versus one tape.

This is a routing diagnostic: a specialist can only take over after detection
when its own physical state and hidden inventory still match the host policy.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kaggle_environments import make


ROOT = Path(__file__).resolve().parents[1]


def run(agent: Path, tape: Path, seed: int, seat: int):
    players = [str(tape), str(agent)] if seat else [str(agent), str(tape)]
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run(players)
    return env.steps


def own_state(step, seat: int) -> dict:
    obs = step[seat]["observation"]
    farm = obs["farms"][seat]
    return {
        "farm": farm,
        "private": obs.get("private", {}),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("tape", type=Path)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--seat", type=int, choices=(0, 1), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    left = run((ROOT / args.left).resolve(), (ROOT / args.tape).resolve(), args.seed, args.seat)
    right = run((ROOT / args.right).resolve(), (ROOT / args.tape).resolve(), args.seed, args.seat)
    rows = []
    first_state = first_action = None
    for index, (a, b) in enumerate(zip(left, right)):
        state_equal = own_state(a, args.seat) == own_state(b, args.seat)
        action_equal = a[args.seat].get("action") == b[args.seat].get("action")
        if first_state is None and not state_equal:
            first_state = index
        if first_action is None and not action_equal:
            first_action = index
        if index < 30 or (not state_equal and index <= (first_state or index) + 2):
            rows.append({
                "step": index,
                "state_equal": state_equal,
                "action_equal": action_equal,
                "left_action": a[args.seat].get("action"),
                "right_action": b[args.seat].get("action"),
                "left_money": a[args.seat]["observation"]["farms"][args.seat]["money"],
                "right_money": b[args.seat]["observation"]["farms"][args.seat]["money"],
            })
    result = {
        "left": str(args.left), "right": str(args.right), "seed": args.seed,
        "seat": args.seat, "first_state_divergence": first_state,
        "first_action_divergence": first_action,
        "left_reward": left[-1][args.seat]["reward"],
        "right_reward": right[-1][args.seat]["reward"], "rows": rows,
    }
    output = (ROOT / args.out).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in result if key != "rows"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
