"""Compare base policies on an explicit shop-bucket seed panel."""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
from pathlib import Path

from run_w13_isolated import play


ROOT = Path(__file__).resolve().parents[1]
MODELS = {
    "cha22": "public_candidates/current_20260925/cha22/main.py",
    "v48": "public_candidates/v48_clear_queue_20260918/main.py",
    "prefund": "variants/v45_prefund_10_exported/main.py",
    "kaito": "submit_v46_three_suffix/main.py",
    "pf_all": "submit_pf_all/main.py",
    "protected": "variants/protected_portfolio/main.py",
    "shop0909": "variants/shop0909_tomato432/main.py",
}


def execute(job):
    candidate, model, seed, seat = job
    result = play(str(ROOT / candidate), str(ROOT / MODELS[model]), seed, seat)
    return {"candidate": candidate, "model": model, **result}


def summarize(rows):
    summary = {}
    for candidate in sorted({row["candidate"] for row in rows}):
        summary[candidate] = {}
        for model in MODELS:
            done = [row for row in rows if row["candidate"] == candidate
                    and row["model"] == model and row["status"] == "DONE"]
            wins = sum(row["a"] > row["b"] for row in done)
            losses = sum(row["a"] < row["b"] for row in done)
            summary[candidate][model] = {
                "completed": len(done), "wins": wins, "losses": losses,
                "ties": len(done) - wins - losses,
                "mean_margin": (sum(row["a"] - row["b"] for row in done) / len(done)
                                if done else None),
            }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", action="append", required=True)
    parser.add_argument("--model", action="append", choices=sorted(MODELS))
    parser.add_argument("--seed", type=int, action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    models = args.model or list(MODELS)
    jobs = [(candidate, model, seed, seat)
            for candidate in args.candidate for model in models
            for seed in args.seed for seat in (0, 1)]
    rows = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(execute, job) for job in jobs]):
            row = future.result()
            rows.append(row)
            print(len(rows), Path(row["candidate"]).parent.name, row["model"],
                  row["seed"], row["order"], row["status"], row.get("a"),
                  row.get("b"), flush=True)
    output = ROOT / args.out
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"seeds": args.seed, "models": models, "rows": rows,
               "summary": summarize(rows)}
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    return 1 if any(row["status"] != "DONE" for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
