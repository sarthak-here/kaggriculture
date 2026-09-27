"""Find fresh seeds where the guarded missed-pasture recovery activates."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import runpy

from kaggle_environments import make


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "variants/step1010_brunch_pasture33_20260928/main.py"
BASELINE = ROOT / "variants/step1010_cha22_router_step144_brunch_brunch_20260927/main.py"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--count", type=int, default=2)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    candidate = runpy.run_path(str(CANDIDATE))["step1010_brunch_pasture33_agent"]
    baseline = runpy.run_path(str(BASELINE))["step1010_cha22_router_agent"]
    found = []
    for seed in range(args.start, args.start + args.limit):
        env = make("kaggriculture", configuration={"seed": seed}, debug=False)
        env.reset()
        activated = False
        for _ in range(71):
            states = env.steps[-1]
            obs0 = states[0]["observation"]
            obs1 = copy.deepcopy(obs0)
            obs1["player"] = 1
            obs1["private"] = copy.deepcopy(states[1]["observation"]["private"])
            actions = [candidate(obs0, env.configuration), baseline(obs1, env.configuration)]
            if int(obs0["step"]) == 69 and actions[0].get("farmer") == ["BUILD_PASTURE"]:
                activated = True
            env.step(actions)
        if activated:
            found.append(seed)
            print(seed, flush=True)
            if len(found) >= args.count:
                break
    result = {"start": args.start, "limit": args.limit, "seeds": found}
    output = (ROOT / args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return 0 if found else 1


if __name__ == "__main__":
    raise SystemExit(main())
