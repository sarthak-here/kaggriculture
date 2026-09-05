"""Paired-seat A-vs-B evaluation, ranked by WIN RATE.

Two hard-won rules from EXPERIMENTS.md are baked in:

  * Promotion is decided by WIN RATE, never mean margin. On 25,849 real rating
    deltas a win pays +47.92 and a loss -16.33 regardless of size (r = +0.025
    between margin and rating change). Margin is kept only as a mechanism
    diagnostic.
  * Every seed is played in BOTH seat orders, so seat bias cancels.

HARNESS TRAP: `import game_data` caches under a bare module name, so the first
agent loaded in a process poisons every agent loaded after it. Any two agents
compared here MUST ship byte-identical game_data.py; this script refuses to run
otherwise rather than silently producing an inverted result.

Run:  .venv/Scripts/python.exe analysis/duel.py <agent_a> <agent_b> [n_seeds]
"""

import sys
import os
import hashlib
import json
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kaggle_environments import make
from kaggle_environments.envs.kaggriculture.kaggriculture import MARKET_I0, market_price
from portfolio import label_for

TURNS_PER_DAY = 24

# Discovery seeds overstate effects ~2x (EXPERIMENTS method rules), so a result
# found on 2000+ must be re-confirmed on a disjoint set. Override with KAG_SEED_BASE.
SEED_BASE = int(os.environ.get("KAG_SEED_BASE", 2000))
SEEDS_OVERRIDE = [int(value) for value in os.environ.get("KAG_SEEDS", "").split(",")
                  if value.strip()]


def game_data_hash(agent_path):
    gd = os.path.join(os.path.dirname(os.path.abspath(agent_path)), "game_data.py")
    if not os.path.exists(gd):
        return None
    return hashlib.md5(open(gd, "rb").read()).hexdigest()


def carrot_stats(env, player_id):
    """Mechanism counters: did the carrot arm actually do anything?"""
    planted = 0
    sold = 0
    revenue = 0
    for step in env.steps:
        act = step[player_id].get("action")
        if not isinstance(act, dict):
            continue
        for key in ("market", "farmer"):
            v = act.get(key)
            if not v:
                continue
            rows = v if key == "market" else [v]
            for row in rows:
                if not isinstance(row, (list, tuple)) or len(row) < 2:
                    continue
                if row[0] == "PLANT" and row[1] == "CARROT":
                    planted += 1
                elif row[0] == "SELL" and row[1] == "CARROT":
                    sold += int(row[2]) if len(row) > 2 else 1
        for hand in act.get("hands", []) or []:
            if isinstance(hand, (list, tuple)) and len(hand) >= 2 \
                    and hand[0] == "PLANT" and hand[1] == "CARROT":
                planted += 1
    final_inv = env.steps[-1][0]["observation"]["market"]["inventory"]
    return {
        "planted": planted,
        "sold": sold,
        "final_carrot_price": market_price("CARROT", final_inv["CARROT"]),
        "final_carrot_deficit": MARKET_I0 - final_inv["CARROT"],
    }


def play(agent_a, agent_b, seed):
    env = make("kaggriculture", configuration={"seed": seed}, debug=False)
    env.run([agent_a, agent_b])
    rewards = [s["reward"] for s in env.steps[-1]]
    return env, rewards


def result_path(agent_a, agent_b):
    """Use a pairing-specific dump so parallel duels cannot overwrite each other."""
    def slug(path):
        directory = os.path.basename(os.path.dirname(os.path.abspath(path)))
        return directory if directory not in ("", ".") \
            else os.path.splitext(os.path.basename(path))[0]

    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        f"duel_{slug(agent_a)}_vs_{slug(agent_b)}.json")


def write_rows(agent_a, agent_b, rows):
    out = result_path(agent_a, agent_b)
    with open(out, "w") as handle:
        json.dump(rows, handle, indent=1)
    print(f"\nwrote {out}")

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    agent_a, agent_b = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 20

    ha, hb = game_data_hash(agent_a), game_data_hash(agent_b)
    print(f"A = {agent_a}   game_data md5 {ha}")
    print(f"B = {agent_b}   game_data md5 {hb}")
    if ha != hb:
        print("\nREFUSING TO RUN: game_data.py differs between the two agents.")
        print("The bare-module import cache would poison whichever loads second.")
        return 2
    print("game_data.py identical - safe to mix in one process\n")

    a_wins = b_wins = ties = failures = 0
    margins = []
    mech = {"A": Counter(), "B": Counter()}
    spike_games = 0
    rows = []

    seeds = SEEDS_OVERRIDE or [SEED_BASE + i for i in range(n)]
    for seed in seeds:
        for order in (0, 1):
            # order 0: A in seat 0. order 1: B in seat 0. Same seed both ways.
            first, second = (agent_a, agent_b) if order == 0 else (agent_b, agent_a)
            try:
                env, rewards = play(first, second, seed)
            except Exception as e:
                print(f"  seed {seed} order {order} FAILED: {type(e).__name__}: {e}")
                failures += 1
                rows.append({"seed": seed, "order": order, "status": "FAILED",
                             "error": f"{type(e).__name__}: {e}"})
                continue
            a_seat = 0 if order == 0 else 1
            b_seat = 1 - a_seat
            ra, rb = rewards[a_seat], rewards[b_seat]
            if not isinstance(ra, (int, float)) or not isinstance(rb, (int, float)):
                print(f"  seed {seed} order {order} FAILED: invalid rewards {rewards!r}")
                failures += 1
                rows.append({"seed": seed, "order": order, "status": "FAILED",
                             "error": f"invalid rewards {rewards!r}"})
                continue
            if ra > rb:
                a_wins += 1
            elif rb > ra:
                b_wins += 1
            else:
                ties += 1
            margins.append(ra - rb)

            sa = carrot_stats(env, a_seat)
            sb = carrot_stats(env, b_seat)
            final_obs = env.steps[-1][0]["observation"]
            shops = list((final_obs.get("town") or {}).get("unlocked_shops") or [])
            for k in ("planted", "sold"):
                mech["A"][k] += sa[k]
                mech["B"][k] += sb[k]
            if sa["final_carrot_deficit"] > 450:
                spike_games += 1
            rows.append({"seed": seed, "order": order, "a": ra, "b": rb,
                         "shops": shops, "bucket": label_for(shops),
                         "a_carrot": sa, "b_carrot": sb})
            print(f"  seed {seed} order {order}: A {ra:>9,.0f}  B {rb:>9,.0f}"
                  f"  {'A' if ra>rb else ('B' if rb>ra else '=')}"
                  f"   A planted {sa['planted']:>3} sold {sa['sold']:>3}"
                  f"   carrot ${sa['final_carrot_price']:<5}")

    total = a_wins + b_wins + ties
    expected = len(seeds) * 2
    if not total:
        print(f"\nRESULT over 0/{expected} completed paired-seat games")
        print(f"  failed games: {failures}/{expected}")
        write_rows(agent_a, agent_b, rows)
        return 3 if failures else 1

    print("\n" + "=" * 68)
    print(f"RESULT over {total}/{expected} completed paired-seat games "
          f"({len(seeds)} seeds x 2 orders)")
    print("=" * 68)
    decisive = a_wins + b_wins
    wr = 100 * a_wins / decisive if decisive else float("nan")
    all_wr = 100 * a_wins / total
    print(f"  A wins {a_wins}   B wins {b_wins}   ties {ties}")
    print(f"  A WINS / ALL COMPLETED: {a_wins}/{total} = {all_wr:.1f}%")
    print(f"  A WIN RATE (decisive only): {a_wins}/{decisive} = {wr:.1f}%")
    print(f"  failed games: {failures}/{expected}")
    print(f"  mean margin (diagnostic only): {sum(margins)/len(margins):>+,.0f}")
    print(f"\n  MECHANISM  A: carrot planted {mech['A']['planted']:>4}"
          f"  sold {mech['A']['sold']:>4}")
    print(f"             B: carrot planted {mech['B']['planted']:>4}"
          f"  sold {mech['B']['sold']:>4}")
    print(f"  games ending past the carrot knee: {spike_games}/{total}")

    if mech["A"]["planted"] == mech["B"]["planted"]:
        print("\n  WARNING: both agents planted the same amount of carrot.")
        print("  The lever did not move - do not read anything into the score.")

    write_rows(agent_a, agent_b, rows)
    return 3 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
