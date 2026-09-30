"""Paired-seat A/B of each no-op-free child against its frozen parent."""

from __future__ import annotations

import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "variants" / "noop_free_20260930" / "manifest.json"
OUT = ROOT / "analysis" / "noop_free_parent_ab_20260930.json"
SEEDS = tuple(range(1100600, 1100605))


def play(entry):
    from kaggle_environments import make

    child = str(ROOT / entry["output"])
    parent = str(ROOT / entry["source"])
    wins = losses = ties = failures = 0
    margins = []
    rows = []
    for seed in SEEDS:
        for order in (0, 1):
            first, second = (child, parent) if order == 0 else (parent, child)
            try:
                env = make("kaggriculture", configuration={"seed": seed}, debug=False)
                env.run([first, second])
                final = env.steps[-1]
                rewards = [final[0].get("reward"), final[1].get("reward")]
                statuses = [final[0].get("status"), final[1].get("status")]
                if statuses != ["DONE", "DONE"] or not all(isinstance(v, (int, float)) for v in rewards):
                    raise RuntimeError(f"statuses={statuses!r} rewards={rewards!r}")
                child_seat = 0 if order == 0 else 1
                child_score, parent_score = rewards[child_seat], rewards[1 - child_seat]
                wins += child_score > parent_score
                losses += parent_score > child_score
                ties += child_score == parent_score
                margins.append(child_score - parent_score)
                rows.append({"seed": seed, "order": order, "child": child_score, "parent": parent_score})
            except Exception as exc:
                failures += 1
                rows.append({"seed": seed, "order": order, "error": f"{type(exc).__name__}: {exc}"})
    return {
        "name": entry["name"],
        "parent_noops": entry["source_noop_count"],
        "wins": wins,
        "losses": losses,
        "ties": ties,
        "failures": failures,
        "mean_margin": sum(margins) / len(margins) if margins else None,
        "rows": rows,
    }


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    results = []
    with ProcessPoolExecutor(max_workers=min(4, os.cpu_count() or 1)) as pool:
        futures = [pool.submit(play, entry) for entry in manifest]
        for future in as_completed(futures):
            row = future.result()
            results.append(row)
            print(f"{row['name']}: child {row['wins']}-{row['losses']}-{row['ties']} parent "
                  f"fail={row['failures']} margin={row['mean_margin']:+.0f}", flush=True)
    order = {entry["name"]: i for i, entry in enumerate(manifest)}
    results.sort(key=lambda row: order[row["name"]])
    OUT.write_text(json.dumps({"seeds": list(SEEDS), "paired_seats": True, "results": results}, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
