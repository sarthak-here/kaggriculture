"""Fresh paired-seat panel for the hash-verified V48 clear-the-queue agent."""
import ast
import gzip
import hashlib
import importlib.metadata
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from run_w13_isolated import play

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis/v48_panel_20260918"
CANDIDATE = "public_candidates/v48_clear_queue_20260918/main.py"
EXPECTED_SHA = "4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96"
MODELS = {
    "jaxa2780": "public_candidates/jaxa2780_20260917/main.py",
    "current_prefund": "variants/v45_prefund_10_exported/main.py",
    "v45_proactive": "variants/v45_proactive/main.py",
    "kaito": "submit_v46_three_suffix/main.py",
    "pf_all": "submit_pf_all/main.py",
    "protected_portfolio": "variants/protected_portfolio/main.py",
    "shop0909_tomato": "variants/shop0909_tomato432/main.py",
    "astra_strawberry": "variants/w13_add_strawberry/main.py",
    "kaito_gronk": "variants/kaito_gronk_early_router/main.py",
}


def execute(job):
    family, seed, seat = job
    return dict(model=family, **play(str(ROOT / CANDIDATE), str(ROOT / MODELS[family]), seed, seat))


def summarize(rows):
    result = {}
    for model in MODELS:
        subset = [row for row in rows if row["model"] == model]
        done = [row for row in subset if row["status"] == "DONE"]
        wins = sum(row["a"] > row["b"] for row in done)
        losses = sum(row["a"] < row["b"] for row in done)
        result[model] = {
            "completed": len(done), "expected": 20, "wins": wins, "losses": losses,
            "ties": len(done) - wins - losses, "failures": len(subset) - len(done),
            "wins_over_total": wins / len(done) if done else None,
            "mean_margin": sum(row["a"] - row["b"] for row in done) / len(done) if done else None,
        }
    return result


def main():
    assert importlib.metadata.version("kaggle-environments") == "1.32.7"
    candidate = ROOT / CANDIDATE
    assert hashlib.sha256(candidate.read_bytes()).hexdigest() == EXPECTED_SHA
    entrypoints = {}
    paths = {Path(__file__), ROOT / "analysis/run_w13_isolated.py", candidate}
    for rel in MODELS.values():
        path = ROOT / rel
        entrypoints[rel] = [
            node.name for node in ast.parse(path.read_text(encoding="utf-8")).body
            if isinstance(node, ast.FunctionDef)
        ][-1]
        paths.add(path)
    hashes = {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}
    OUT.mkdir(exist_ok=False)
    jobs = [(model, seed, seat) for seed in range(430000, 430010) for model in MODELS for seat in (0, 1)]
    protocol = {
        "candidate": CANDIDATE, "candidate_sha256": EXPECTED_SHA, "models": MODELS,
        "jobs": jobs, "hashes": hashes, "entrypoints": entrypoints, "engine": "1.32.7",
        "caveat": "Fresh 10-seed paired-seat regression panel; not a leaderboard guarantee.",
    }
    (OUT / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")
    rows = []
    with ProcessPoolExecutor(max_workers=4) as pool:
        for future in as_completed([pool.submit(execute, job) for job in jobs]):
            row = future.result(); rows.append(row)
            (OUT / "results.json").write_text(json.dumps(rows) + "\n", encoding="utf-8")
            (OUT / "summary.json").write_text(json.dumps(summarize(rows), indent=2) + "\n", encoding="utf-8")
            print(len(rows), row["model"], row["seed"], row["order"], row["status"], row.get("a"), row.get("b"), flush=True)
    (OUT / "results.json.gz").write_bytes(gzip.compress(json.dumps(rows).encode(), mtime=0))
    assert len(rows) == 180 and all(row["status"] == "DONE" for row in rows)
    assert all(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest for rel, digest in hashes.items())
    print("COMPLETE", json.dumps(summarize(rows)), flush=True)


if __name__ == "__main__":
    main()
