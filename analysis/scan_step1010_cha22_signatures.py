"""Scan real Step1010-vs-Cha22 worlds only through the third shop.

Agents run in isolated child processes exactly as in run_w13_isolated.py.  The
environment stops at observation step 216, avoiding the remaining 480 turns.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import multiprocessing as mp
import os
from pathlib import Path
import sys

# Windows spawn re-imports this module in every policy child.  Silence only
# those children before importing kaggle_environments/OpenSpiel; otherwise its
# unrelated registry diagnostics can exhaust the shared command pipe.
if mp.current_process().name != "MainProcess":
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open(os.devnull, "w")

from kaggle_environments import make

from run_w13_isolated import child


ROOT = Path(__file__).resolve().parents[1]
STEP = ROOT / "variants/idle_seller_step1010_20260927/main.py"
CHA = ROOT / "variants/cha22_slot_schedule_early_20260927/main.py"
TARGETS = {
    ("PET_CAFE",),
    ("BRUNCH_SPOT", "BRUNCH_SPOT"),
    ("BAKERY", "PIZZA_SHOP"),
    ("ICE_CREAM_SHOP", "BRUNCH_SPOT", "YARN_STORE"),
    ("YARN_STORE", "SMOOTHIE_SHOP", "YARN_STORE"),
}


def scan(seed: int) -> dict:
    ctx = mp.get_context("spawn")
    processes = []
    connections = []
    try:
        for path in (STEP, CHA):
            parent, kid = ctx.Pipe()
            process = ctx.Process(target=child, args=(kid, str(path)))
            process.start()
            kid.close()
            processes.append(process)
            connections.append(parent)
        env = make("kaggriculture", configuration={"seed": seed}, debug=False)
        # make() already performs the seeded initialization.  A second reset
        # would run after the engine has deliberately scrubbed configuration.seed.
        while int(env.state[0].observation.step) < 216:
            actions = []
            for seat, connection in enumerate(connections):
                observation = env.state[seat].observation
                # The raw second-seat state omits the shared step field; the
                # stock agent runner supplies it from seat zero before calling.
                observation.step = env.state[0].observation.step
                connection.send((observation, env.configuration))
                if not connection.poll(5):
                    raise TimeoutError(f"seat {seat} timeout at {env.state[0].observation.step}")
                status, value = connection.recv()
                if status != "ok":
                    raise RuntimeError(value)
                actions.append(value)
            env.step(actions)
        shops = tuple(env.state[0].observation.town.unlocked_shops)
        matches = [list(pattern) for pattern in TARGETS if shops[:len(pattern)] == pattern]
        return {"seed": seed, "status": "DONE", "shops": list(shops), "matches": matches}
    except BaseException as exc:
        return {"seed": seed, "status": "FAILED", "error": repr(exc)}
    finally:
        for connection in connections:
            try:
                connection.send(None)
            except (EOFError, BrokenPipeError, OSError):
                pass
            connection.close()
        for process in processes:
            process.join(1)
            if process.is_alive():
                process.terminate()
                process.join()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(scan, seed): seed
                   for seed in range(args.seed, args.seed + args.count)}
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            if row.get("matches"):
                print(json.dumps(row), flush=True)
    rows.sort(key=lambda row: row["seed"])
    output = (ROOT / args.out).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"rows": rows}, indent=2) + "\n", encoding="utf-8")
    matches = [row for row in rows if row.get("matches")]
    print(json.dumps({"completed": sum(r["status"] == "DONE" for r in rows),
                      "failures": sum(r["status"] != "DONE" for r in rows),
                      "matches": len(matches)}, indent=2))
    return 1 if any(row["status"] != "DONE" for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
