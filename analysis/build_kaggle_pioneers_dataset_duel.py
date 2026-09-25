"""Build a private Kaggle dataset plus small isolated duel kernel."""

import gzip
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "analysis/kaggle_pioneers_duel_dataset_20260925"
KERNEL = ROOT / "analysis/kaggle_pioneers_duel_kernel_20260925"
PIONEERS = ROOT / "public_candidates/current_20260925/pioneers2/main.py"
BASE = ROOT / "public_candidates/current_20260924/demand_timing/main.py"
DATASET_ID = "sarthaksharma14/kaggriculture-private-duel-agents"


CODE = r'''import importlib.metadata, json, pathlib, subprocess, sys, time
subprocess.check_call([
    sys.executable, "-m", "pip", "install", "--quiet",
    "kaggle-environments==1.32.7",
])
from kaggle_environments import make
from kaggle_environments.agent import get_last_callable

INPUT = pathlib.Path("/kaggle/input/kaggriculture-private-duel-agents")
WORK = pathlib.Path("/kaggle/working")
PIONEERS = WORK / "pioneers_main.py"
BASE = WORK / "demand_timing_main.py"
# Kaggle automatically expands uploaded .gz files and strips the suffix.
PIONEERS.write_bytes((INPUT / "pioneers_main.py").read_bytes())
BASE.write_bytes((INPUT / "demand_timing_main.py").read_bytes())
PIONEERS_AGENT = get_last_callable(PIONEERS.read_text(), path=str(PIONEERS))
BASE_AGENT = get_last_callable(BASE.read_text(), path=str(BASE))

rows = []
started = time.time()
for seed in range(1021000, 1021005):
    for order in (0, 1):
        first, second = ((PIONEERS_AGENT, BASE_AGENT) if order == 0
                         else (BASE_AGENT, PIONEERS_AGENT))
        row = {"seed": seed, "order": order}
        try:
            env = make("kaggriculture", configuration={"seed": seed}, debug=False)
            env.run([first, second])
            rewards = [step["reward"] for step in env.steps[-1]]
            p_seat = 0 if order == 0 else 1
            farms = env.steps[-1][0]["observation"]["farms"]
            money = [float(farm["money"]) for farm in farms]
            row.update(status="DONE", pioneers=money[p_seat],
                       demand_timing=money[1-p_seat],
                       margin=money[p_seat]-money[1-p_seat],
                       raw_rewards=rewards,
                       steps=len(env.steps),
                       agent_statuses=[step.get("status") for step in env.steps[-1]])
        except Exception as exc:
            row.update(status="FAILED", error=f"{type(exc).__name__}: {exc}")
        rows.append(row)
        print(json.dumps(row), flush=True)

done = [r for r in rows if r["status"] == "DONE"]
summary = {
    "kaggle_environments": importlib.metadata.version("kaggle-environments"),
    "seeds": list(range(1021000, 1021005)),
    "completed": len(done), "failures": len(rows)-len(done),
    "pioneers_wins": sum(r["margin"] > 0 for r in done),
    "demand_timing_wins": sum(r["margin"] < 0 for r in done),
    "ties": sum(r["margin"] == 0 for r in done),
    "mean_margin": sum(r["margin"] for r in done)/len(done) if done else None,
    "elapsed_seconds": time.time()-started,
}
result = {"summary": summary, "rows": rows}
(WORK / "pioneers_duel_results.json").write_text(json.dumps(result, indent=2))
print("FINAL", json.dumps(summary), flush=True)
'''


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    KERNEL.mkdir(parents=True, exist_ok=True)
    (DATA / "pioneers_main.py.gz").write_bytes(gzip.compress(PIONEERS.read_bytes(), mtime=0))
    (DATA / "demand_timing_main.py.gz").write_bytes(gzip.compress(BASE.read_bytes(), mtime=0))
    (DATA / "dataset-metadata.json").write_text(json.dumps({
        "title": "Kaggriculture Private Duel Agents",
        "id": DATASET_ID,
        "licenses": [{"name": "other"}],
        "isPrivate": True,
    }, indent=2) + "\n", encoding="utf-8")
    (KERNEL / "pioneers_duel.py").write_text(CODE, encoding="utf-8")
    (KERNEL / "kernel-metadata.json").write_text(json.dumps({
        "id": "sarthaksharma14/kaggriculture-pioneers-private-duel",
        "title": "Kaggriculture Pioneers Private Duel",
        "code_file": "pioneers_duel.py",
        "language": "python", "kernel_type": "script", "is_private": True,
        "enable_gpu": False, "enable_tpu": False, "enable_internet": True,
        "machine_shape": "None", "dataset_sources": [DATASET_ID],
        "kernel_sources": [], "competition_sources": ["kaggriculture"],
        "model_sources": [],
    }, indent=2) + "\n", encoding="utf-8")
    print(DATA)
    print(KERNEL)


if __name__ == "__main__":
    main()
