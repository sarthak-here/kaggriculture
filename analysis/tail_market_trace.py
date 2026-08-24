"""Trace late-game money, shed, and market actions for two local agents."""

import sys

from kaggle_environments import make


def main():
    a, b, seed = sys.argv[1], sys.argv[2], int(sys.argv[3])
    order = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    entries = [a, b] if order == 0 else [b, a]
    seats = [0, 1] if order == 0 else [1, 0]
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run(entries)
    print("step tag money delta shed market")
    for step in range(648, len(env.steps) - 1):
        for tag, seat in zip(("A", "B"), seats):
            state = env.steps[step][seat]
            next_state = env.steps[step + 1][seat]
            obs = state.get("observation") or {}
            next_obs = next_state.get("observation") or {}
            farm = (obs.get("farms") or [{}, {}])[seat]
            next_farm = (next_obs.get("farms") or [{}, {}])[seat]
            money = float(farm.get("money", 0) or 0)
            delta = float(next_farm.get("money", 0) or 0) - money
            private = obs.get("private", {}) or {}
            shed = {key: value for key, value in
                    (private.get("shed", {}) or {}).items() if value}
            market = (state.get("action") or {}).get("market", []) or []
            if delta or market or shed or step >= 712:
                print(step, tag, int(money), "%+d" % int(delta), shed, market)


if __name__ == "__main__":
    main()
