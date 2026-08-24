"""Parallel paired-seat screen for an index of local agent variants."""

import concurrent.futures
import json
import os
from pathlib import Path
import re
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DUEL = ROOT / "analysis" / "duel.py"
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
INCUMBENT = ROOT / "submit_pf_all" / "main.py"


def evaluate(row, seeds):
    environment = dict(os.environ)
    environment["KAG_SEEDS"] = seeds
    proc = subprocess.run(
        [str(PYTHON), "-u", str(DUEL), str(ROOT / row["path"]),
         str(INCUMBENT), str(len(seeds.split(",")))],
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=900,
    )
    output = proc.stdout + "\n" + proc.stderr
    wins = re.search(r"A wins (\d+)\s+B wins (\d+)\s+ties (\d+)", output)
    margin = re.search(r"mean margin \(diagnostic only\): ([+\-0-9,]+)", output)
    result = dict(row)
    result.update(
        returncode=proc.returncode,
        wins=int(wins.group(1)) if wins else -1,
        losses=int(wins.group(2)) if wins else -1,
        ties=int(wins.group(3)) if wins else -1,
        margin=int(margin.group(1).replace(",", "")) if margin else 0,
    )
    if not wins:
        result["tail"] = output[-1000:]
    return result


def main():
    index = (ROOT / sys.argv[1]).resolve()
    seeds = sys.argv[2]
    workers = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    rows = json.loads(index.read_text(encoding="utf-8"))
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(evaluate, row, seeds) for row in rows]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print("%-22s %d-%d tie%d margin %+d" % (
                result["name"], result["wins"], result["losses"],
                result["ties"], result["margin"]), flush=True)
    results.sort(key=lambda row: (-row["wins"], row["losses"], -row["margin"]))
    target = index.with_name("screen_%s.json" % seeds.replace(",", "_"))
    target.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("TOP")
    for result in results[:8]:
        print("%-22s %d-%d margin %+d" % (
            result["name"], result["wins"], result["losses"], result["margin"]))
    print("wrote", target)


if __name__ == "__main__":
    main()
