"""Run one Kaggriculture game and print terminal statuses/errors."""
import argparse
from pathlib import Path

from kaggle_environments import make
from kaggle_environments.agent import get_last_callable


def load(path):
    path = Path(path)
    if path.is_dir():
        path = path / "main.py"
    return get_last_callable(path.read_text(encoding="utf-8"), path=str(path))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("first")
    parser.add_argument("second")
    parser.add_argument("--seed", type=int, default=1031040)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    env = make("kaggriculture", configuration={"seed": args.seed}, debug=args.debug)
    env.run([load(args.first), load(args.second)])
    print("steps", len(env.steps))
    for index in range(min(4, len(env.steps))):
        print("step", index, "actions", [state.get("action") for state in env.steps[index]])
    for seat, state in enumerate(env.steps[-1]):
        print("seat", seat, "status", state.get("status"), "reward", state.get("reward"))
        print("info", state.get("info"))


if __name__ == "__main__":
    main()
