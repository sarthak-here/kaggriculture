"""Target-screen mined v46 suffixes on the two known YARN-third losses."""

import concurrent.futures
import json
import os
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "variants" / "v46_suffixes" / "index.json"
DUEL = ROOT / "analysis" / "duel.py"
PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
INCUMBENT = ROOT / "submit_pf_all" / "main.py"


def evaluate(row):
    environment = dict(os.environ)
    environment["KAG_SEEDS"] = "93001,93006"
    proc = subprocess.run(
        [str(PYTHON), "-u", str(DUEL), str(ROOT / row["path"]),
         str(INCUMBENT), "2"],
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
    rows = json.loads(INDEX.read_text(encoding="utf-8"))
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(evaluate, row): row for row in rows}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            print("%-20s %d-%d tie%d margin %+d" % (
                result["name"], result["wins"], result["losses"],
                result["ties"], result["margin"]), flush=True)
    results.sort(key=lambda row: (-row["wins"], row["losses"], -row["margin"]))
    target = INDEX.parent / "screen.json"
    target.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("\nTOP")
    for result in results[:8]:
        print("%-20s %d-%d margin %+d source %s" % (
            result["name"], result["wins"], result["losses"],
            result["margin"], ">".join(result["shops"][:3])))
    print("wrote", target)


if __name__ == "__main__":
    main()
