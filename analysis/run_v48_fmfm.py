"""Targeted V48 versus 2780 comparison on fresh FM/FM shop worlds."""
import gzip
import hashlib
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from run_w13_isolated import play

ROOT = Path(__file__).resolve().parents[1]
A = ROOT / "public_candidates/v48_clear_queue_20260918/main.py"
B = ROOT / "public_candidates/jaxa2780_20260917/main.py"
OUT = ROOT / "analysis/v48_fmfm_20260918"
SEEDS = [440021, 440106, 440262, 440269, 440351, 440396, 440399, 440454, 440549, 440566]


def run(job):
    seed, seat = job
    return play(str(A), str(B), seed, seat)


def main():
    OUT.mkdir(exist_ok=False)
    protocol = {
        "a": str(A.relative_to(ROOT)), "b": str(B.relative_to(ROOT)), "seeds": SEEDS,
        "shop_prefix": ["FARMERS_MARKET", "FARMERS_MARKET"], "paired_seats": True,
        "a_sha256": hashlib.sha256(A.read_bytes()).hexdigest(),
        "b_sha256": hashlib.sha256(B.read_bytes()).hexdigest(), "engine": "1.32.7",
    }
    (OUT / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")
    rows = []
    with ProcessPoolExecutor(max_workers=4) as pool:
        for future in as_completed([pool.submit(run, job) for job in [(s, p) for s in SEEDS for p in (0, 1)]]):
            rows.append(future.result())
            print(len(rows), rows[-1]["seed"], rows[-1]["order"], rows[-1]["status"], rows[-1].get("a"), rows[-1].get("b"), flush=True)
    assert len(rows) == 20 and all(row["status"] == "DONE" for row in rows)
    wins = sum(row["a"] > row["b"] for row in rows)
    losses = sum(row["a"] < row["b"] for row in rows)
    summary = {"wins": wins, "losses": losses, "ties": 20 - wins - losses,
               "mean_margin": sum(row["a"] - row["b"] for row in rows) / 20,
               "min_margin": min(row["a"] - row["b"] for row in rows)}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (OUT / "results.json.gz").write_bytes(gzip.compress(json.dumps(rows).encode(), mtime=0))
    print("COMPLETE", summary)


if __name__ == "__main__":
    main()
