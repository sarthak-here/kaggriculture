"""Evaluate agents against action tapes selected by a replay manifest.

This is a causal diagnostic only.  A frozen tape cannot react to the candidate,
so results localize mechanisms but do not rank agents for promotion.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import traceback

from run_w13_isolated import play


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path) -> dict:
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return json.loads(raw)


def execute(job: dict) -> dict:
    result = play(job["agent_path"], job["tape_path"], job["seed"], job["candidate_seat"])
    return {key: value for key, value in job.items() if not key.endswith("_path")} | result


def failed(job: dict, exc: BaseException) -> dict:
    return {
        key: value for key, value in job.items() if not key.endswith("_path")
    } | {
        "status": "HARNESS_ERROR",
        "error": f"{type(exc).__name__}: {exc}",
        "traceback": "".join(traceback.format_exception(exc)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument(
        "--cohort",
        required=True,
        choices=("submission_loss", "submission_win_control", "top10"),
    )
    parser.add_argument("--agent", action="append", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()

    base = args.manifest.resolve().parent
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    agents = [(value, (ROOT / value).resolve()) for value in args.agent]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.out.exists():
        raise FileExistsError(args.out)

    jobs = []
    with tempfile.TemporaryDirectory(prefix="kag-manifest-tapes-") as temporary:
        temporary = Path(temporary)
        for entry in manifest["replays"]:
            labels = [label for label in entry["labels"] if label.get("cohort") == args.cohort]
            if not labels:
                continue
            replay_path = base / entry["path"]
            replay = load(replay_path)
            for label_index, label in enumerate(labels):
                selected_seat = int(label["seat"])
                if args.cohort.startswith("submission_"):
                    tape_seat, candidate_seat = 1 - selected_seat, selected_seat
                    tape_team = label["opponent"]
                else:
                    tape_seat, candidate_seat = selected_seat, 1 - selected_seat
                    tape_team = label["team"]
                folder = temporary / f"{label['episode_id']}-{label_index}"
                folder.mkdir()
                tape_file = folder / "tape.json"
                tape_file.write_text(json.dumps([
                    step[tape_seat]["action"] for step in replay["steps"][1:]
                ]) + "\n", encoding="utf-8")
                policy_file = folder / "main.py"
                policy_file.write_text(
                    "import json\nfrom pathlib import Path\nTAPE=None\n"
                    "def agent(obs,config=None):\n global TAPE\n"
                    " if TAPE is None:TAPE=json.loads((Path(agent.__code__.co_filename).resolve().parent/'tape.json').read_text())\n"
                    " return TAPE[obs['step']]\n", encoding="utf-8")
                for agent_name, agent_path in agents:
                    jobs.append({
                        "episode": int(label["episode_id"]),
                        "cohort": args.cohort,
                        "recorded_team": tape_team,
                        "recorded_result": label["result"],
                        "recorded_margin": label["margin"],
                        "agent": agent_name,
                        "agent_sha256": hashlib.sha256(agent_path.read_bytes()).hexdigest(),
                        "agent_path": str(agent_path),
                        "tape_path": str(policy_file),
                        "seed": int(replay["info"]["seed"]),
                        "candidate_seat": candidate_seat,
                    })

        rows = []

        def record(row: dict) -> None:
            rows.append(row)
            args.out.write_text(
                json.dumps(rows, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(
                row["episode"], Path(row["agent"]).parent.name,
                row["status"], row.get("a"), row.get("b"), flush=True,
            )

        # Each isolated game already launches child processes. On Windows,
        # nesting those launches inside a process pool is fragile, so the
        # reproducible path is deliberately serial.
        if args.workers == 1:
            for job in jobs:
                try:
                    record(execute(job))
                except BaseException as exc:  # preserve every planned row
                    record(failed(job, exc))
        else:
            with ProcessPoolExecutor(max_workers=args.workers) as pool:
                futures = {pool.submit(execute, job): job for job in jobs}
                for future in as_completed(futures):
                    job = futures[future]
                    try:
                        record(future.result())
                    except BaseException as exc:
                        record(failed(job, exc))

    failures = [row for row in rows if row["status"] != "DONE"]
    print(json.dumps({
        "planned": len(jobs), "games": len(rows), "failures": len(failures),
    }, indent=2))
    return 1 if failures or len(rows) != len(jobs) else 0


if __name__ == "__main__":
    raise SystemExit(main())
