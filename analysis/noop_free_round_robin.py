"""Paired-seat round robin for the six no-op-free current-rule agents."""

from __future__ import annotations

import itertools
import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COHORT = ROOT / "variants" / "noop_free_20260930"
OUT = ROOT / "analysis" / "noop_free_round_robin_20260930.json"
NAMES = (
    "pf_all",
    "v45_prefund",
    "v48_clear_queue",
    "step1010",
    "severe_114720494",
    "flexonafft_repaired",
)
SEEDS = tuple(range(1100500, 1100505))


def play_pair(pair):
    # Import in the worker so Windows processes do not initialize the large
    # environment registry in the parent before spawning.
    from kaggle_environments import make

    name_a, name_b = pair
    path_a = str(COHORT / name_a / "main.py")
    path_b = str(COHORT / name_b / "main.py")
    rows = []
    wins_a = wins_b = ties = failures = 0
    margins = []
    for seed in SEEDS:
        for order in (0, 1):
            first, second = (path_a, path_b) if order == 0 else (path_b, path_a)
            try:
                env = make("kaggriculture", configuration={"seed": seed}, debug=False)
                env.run([first, second])
                final = env.steps[-1]
                rewards = [final[0].get("reward"), final[1].get("reward")]
                statuses = [final[0].get("status"), final[1].get("status")]
                if statuses != ["DONE", "DONE"] or not all(isinstance(v, (int, float)) for v in rewards):
                    raise RuntimeError(f"invalid final state statuses={statuses!r} rewards={rewards!r}")
                seat_a = 0 if order == 0 else 1
                score_a, score_b = rewards[seat_a], rewards[1 - seat_a]
                if score_a > score_b:
                    wins_a += 1
                elif score_b > score_a:
                    wins_b += 1
                else:
                    ties += 1
                margins.append(score_a - score_b)
                obs = final[0].get("observation") or {}
                shops = list(((obs.get("town") or {}).get("unlocked_shops")) or [])
                rows.append({"seed": seed, "order": order, "a": score_a, "b": score_b, "shops": shops})
            except Exception as exc:
                failures += 1
                rows.append({"seed": seed, "order": order, "error": f"{type(exc).__name__}: {exc}"})
    return {
        "a": name_a,
        "b": name_b,
        "wins_a": wins_a,
        "wins_b": wins_b,
        "ties": ties,
        "failures": failures,
        "mean_margin_a": sum(margins) / len(margins) if margins else None,
        "rows": rows,
    }


def main():
    pairs = list(itertools.combinations(NAMES, 2))
    missing = [str(COHORT / name / "main.py") for name in NAMES if not (COHORT / name / "main.py").is_file()]
    if missing:
        raise FileNotFoundError(missing)
    workers = min(4, os.cpu_count() or 1, len(pairs))
    results = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(play_pair, pair): pair for pair in pairs}
        for future in as_completed(futures):
            row = future.result()
            results.append(row)
            print(f"{row['a']} vs {row['b']}: {row['wins_a']}-{row['wins_b']}-{row['ties']} "
                  f"fail={row['failures']} margin={row['mean_margin_a']:+.0f}", flush=True)
    results.sort(key=lambda row: (NAMES.index(row["a"]), NAMES.index(row["b"])))

    table = {name: {"wins": 0, "losses": 0, "ties": 0, "failures": 0, "points": 0.0} for name in NAMES}
    for row in results:
        a, b = row["a"], row["b"]
        table[a]["wins"] += row["wins_a"]
        table[a]["losses"] += row["wins_b"]
        table[a]["ties"] += row["ties"]
        table[b]["wins"] += row["wins_b"]
        table[b]["losses"] += row["wins_a"]
        table[b]["ties"] += row["ties"]
        table[a]["failures"] += row["failures"]
        table[b]["failures"] += row["failures"]
    for row in table.values():
        row["points"] = row["wins"] + 0.5 * row["ties"]
        completed = row["wins"] + row["losses"] + row["ties"]
        row["all_game_win_rate"] = row["wins"] / completed if completed else None
        row["point_rate"] = row["points"] / completed if completed else None
    ranking = sorted(table, key=lambda name: (-table[name]["points"], -table[name]["wins"], name))
    payload = {
        "seeds": list(SEEDS),
        "paired_seats": True,
        "games_per_pair": len(SEEDS) * 2,
        "ranking": ranking,
        "standings": table,
        "pairs": results,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("\nRANKING")
    for position, name in enumerate(ranking, 1):
        row = table[name]
        print(f"{position}. {name}: {row['wins']}-{row['losses']}-{row['ties']} "
              f"points={row['points']:.1f}/50 failures={row['failures']}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
