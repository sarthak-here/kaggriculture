"""Disjoint paired-seat panel for the demand-timing foundation.

This is intentionally broader than direct incumbent testing.  It contains old
route families, recent queue/market controllers, the hardest close hybrid, and
the exact live incumbent.  Every job is isolated by run_w13_isolated.play.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from run_w13_isolated import play


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/demand_timing_breakthrough_panel_20260924"
CANDIDATE = "public_candidates/current_20260924/demand_timing/main.py"
MODELS = {
    "live_demand350": "variants/panel23_demand_full/main.py",
    "hybrid2965": "variants/panel23_hybrid2965/main.py",
    "thomas2944": "variants/panel23_thomas2944/main.py",
    "latepurchase16": "variants/panel23_latepurchase16/main.py",
    "response_v3": "variants/orderbook_20260923/response_v3/main.py",
    "v48_clear_queue": "public_candidates/v48_clear_queue_20260918/main.py",
    "jaxa2780": "public_candidates/jaxa2780_20260917/main.py",
    "pf_all": "submit_pf_all/main.py",
}
SEEDS = range(980000, 980010)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(job: tuple[str, int, int]) -> dict:
    family, seed, seat = job
    return {"model": family, **play(
        str(ROOT / CANDIDATE), str(ROOT / MODELS[family]), seed, seat
    )}


def summarize(rows: list[dict]) -> dict:
    result = {}
    for model in MODELS:
        planned = len(SEEDS) * 2
        subset = [row for row in rows if row["model"] == model]
        done = [row for row in subset if row["status"] == "DONE"]
        wins = sum(row["a"] > row["b"] for row in done)
        losses = sum(row["a"] < row["b"] for row in done)
        result[model] = {
            "completed": len(done), "expected": planned,
            "wins": wins, "losses": losses,
            "ties": len(done) - wins - losses,
            "failures": len(subset) - len(done),
            "wins_over_total": wins / len(done) if done else None,
            "mean_margin": (
                sum(row["a"] - row["b"] for row in done) / len(done)
                if done else None
            ),
        }
    return result


def main() -> None:
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir()
    paths = [ROOT / CANDIDATE, *(ROOT / path for path in MODELS.values())]
    hashes = {str(path.relative_to(ROOT)): digest(path) for path in paths}
    jobs = [
        (model, seed, seat)
        for seed in SEEDS for model in MODELS for seat in (0, 1)
    ]
    protocol = {
        "candidate": CANDIDATE, "models": MODELS,
        "seeds": list(SEEDS), "jobs": len(jobs), "engine": "1.32.7",
        "hashes": hashes,
        "purpose": "held-out broad-family promotion panel; win rate ranks candidates",
    }
    (OUT / "protocol.json").write_text(
        json.dumps(protocol, indent=2) + "\n", encoding="utf-8"
    )
    rows = []
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(execute, job) for job in jobs]
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            (OUT / "results.json").write_text(
                json.dumps(rows) + "\n", encoding="utf-8"
            )
            (OUT / "summary.json").write_text(
                json.dumps(summarize(rows), indent=2) + "\n", encoding="utf-8"
            )
            print(len(rows), row["model"], row["seed"], row["order"],
                  row["status"], row.get("a"), row.get("b"), flush=True)
    (OUT / "results.json.gz").write_bytes(
        gzip.compress(json.dumps(rows).encode(), mtime=0)
    )
    assert len(rows) == len(jobs)
    assert all(row["status"] == "DONE" for row in rows)
    assert all(digest(ROOT / rel) == value for rel, value in hashes.items())
    print("COMPLETE", json.dumps(summarize(rows)), flush=True)


if __name__ == "__main__":
    main()
