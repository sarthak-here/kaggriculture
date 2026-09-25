"""Matched fresh panel: premium-preempt h4 versus its exact frozen parent."""

from __future__ import annotations

import hashlib
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from run_w13_isolated import play


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/premium_preempt_panel_20260925"
CANDIDATES = {
    "base": "public_candidates/current_20260924/demand_timing/main.py",
    "preempt_h4": "variants/premium_preempt_20260925/h4/main.py",
}
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
SEEDS = range(1020000, 1020003)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def execute(job):
    candidate, family, seed, seat = job
    return {"candidate": candidate, "model": family, **play(
        str(ROOT / CANDIDATES[candidate]), str(ROOT / MODELS[family]), seed, seat
    )}


def summarize(rows):
    result = {}
    for candidate in CANDIDATES:
        result[candidate] = {}
        for model in MODELS:
            subset = [r for r in rows if r["candidate"] == candidate and r["model"] == model]
            done = [r for r in subset if r["status"] == "DONE"]
            wins = sum(r["a"] > r["b"] for r in done)
            losses = sum(r["a"] < r["b"] for r in done)
            result[candidate][model] = {
                "completed": len(done), "expected": len(SEEDS) * 2,
                "wins": wins, "losses": losses, "ties": len(done) - wins - losses,
                "failures": len(subset) - len(done),
                "mean_margin": sum(r["a"] - r["b"] for r in done) / len(done) if done else None,
            }
        families = result[candidate].values()
        result[candidate]["TOTAL"] = {
            key: sum(f[key] for f in families)
            for key in ("completed", "expected", "wins", "losses", "ties", "failures")
        }
    return result


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    OUT.mkdir()
    paths = [*(ROOT / p for p in CANDIDATES.values()), *(ROOT / p for p in MODELS.values())]
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in paths}
    jobs = [(c, m, s, seat) for c in CANDIDATES for m in MODELS for s in SEEDS for seat in (0, 1)]
    (OUT / "protocol.json").write_text(json.dumps({
        "candidates": CANDIDATES, "models": MODELS, "seeds": list(SEEDS),
        "jobs": len(jobs), "engine": "1.32.7", "hashes": hashes,
    }, indent=2) + "\n", encoding="utf-8")
    rows = []
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(execute, job) for job in jobs]
        for future in as_completed(futures):
            row = future.result()
            rows.append(row)
            (OUT / "results.json").write_text(json.dumps(rows) + "\n", encoding="utf-8")
            (OUT / "summary.json").write_text(json.dumps(summarize(rows), indent=2) + "\n", encoding="utf-8")
            print(len(rows), row["candidate"], row["model"], row["seed"], row["order"], row["status"], flush=True)
    assert len(rows) == len(jobs)
    assert all(r["status"] == "DONE" for r in rows)
    assert all(digest(ROOT / rel) == value for rel, value in hashes.items())
    print("COMPLETE", json.dumps(summarize(rows)), flush=True)


if __name__ == "__main__":
    main()
