"""Trace animal buy/pick/place commands for one agent against a replay tape."""
from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path

from kaggle_environments import make


def entrypoint(path: Path):
    namespace = {"__name__": "animal_flow_agent", "__file__": str(path)}
    source = path.read_text(encoding="utf-8")
    exec(compile(source, str(path), "exec"), namespace)
    callables = [value for value in namespace.values() if callable(value)]
    fn = callables[-1]
    positional = [
        p
        for p in inspect.signature(fn).parameters.values()
        if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
    ]
    accepts_config = len(positional) >= 2
    return fn, accepts_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("agent", type=Path)
    parser.add_argument("replay", type=Path)
    parser.add_argument("--candidate-seat", type=int, choices=(0, 1), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    replay = json.loads(args.replay.read_text(encoding="utf-8"))
    tape_seat = 1 - args.candidate_seat
    tape = [step[tape_seat]["action"] for step in replay["steps"][1:]]
    fn, accepts_config = entrypoint(args.agent.resolve())
    trace = []

    def candidate(obs, config):
        action = fn(obs, config) if accepts_config else fn(obs)
        commands = [action.get("farmer", ["PASS"]), *action.get("hands", [])]
        selected = []
        for actor, command in enumerate(commands):
            if (
                isinstance(command, list)
                and command
                and command[0] in ("PICKUP", "PLACE")
                and len(command) >= 2
                and command[1] in ("COW", "SHEEP", "GOOSE")
            ):
                selected.append({"actor": actor, "command": command})
        market = [
            order
            for order in action.get("market", [])
            if isinstance(order, list) and order and order[0] == "BUY_ANIMAL"
        ]
        if selected or market:
            trace.append({"step": int(obs.step), "workers": selected, "market": market})
        return action

    def frozen(obs, _config):
        return tape[int(obs.step)]

    policies = [candidate, frozen] if args.candidate_seat == 0 else [frozen, candidate]
    env = make(
        "kaggriculture",
        configuration={"seed": int(replay["info"]["seed"])},
        debug=False,
    )
    env.run(policies)
    payload = {
        "agent": str(args.agent),
        "episode": int(replay["info"]["EpisodeId"]),
        "candidate_seat": args.candidate_seat,
        "rewards": [state.reward for state in env.state],
        "statuses": [state.status for state in env.state],
        "trace": trace,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
