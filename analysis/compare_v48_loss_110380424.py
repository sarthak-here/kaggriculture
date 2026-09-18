"""Causal controls against the fixed opponent tape from V48's first external loss."""
import hashlib
import importlib.metadata
import json
from pathlib import Path

from run_w13_isolated import play

ROOT = Path(__file__).resolve().parents[1]
REPLAY = ROOT / "analysis/v48_first_external_loss_110380424/episode-110380424-replay.json"
OUT = ROOT / "analysis/v48_first_external_loss_110380424/controls"
ARMS = {
    "v48": "public_candidates/v48_clear_queue_20260918/main.py",
    "jaxa2780": "public_candidates/jaxa2780_20260917/main.py",
    "v45_prefund": "variants/v45_prefund_10_exported/main.py",
    "v45_proactive": "variants/v45_proactive/main.py",
    "pf_all": "submit_pf_all/main.py",
}


def main():
    assert importlib.metadata.version("kaggle-environments") == "1.32.7"
    replay = json.loads(REPLAY.read_text(encoding="utf-8"))
    seed = int(replay["info"]["seed"])
    OUT.mkdir(exist_ok=False)
    tape = [step[0]["action"] for step in replay["steps"][1:]]
    (OUT / "tape.json").write_text(json.dumps(tape) + "\n", encoding="utf-8")
    opponent = OUT / "main.py"
    opponent.write_text(
        "import json\nfrom pathlib import Path\nTAPE=None\n"
        "def agent(obs,config=None):\n global TAPE\n"
        " if TAPE is None:TAPE=json.loads((Path(agent.__code__.co_filename).resolve().parent/'tape.json').read_text())\n"
        " return TAPE[obs['step']]\n",
        encoding="utf-8",
    )
    hashes = {name: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for name, path in ARMS.items()}
    protocol = {
        "episode": 110380424, "seed": seed, "candidate_seat": 1,
        "opponent": "MINGXI LIU fixed replay actions", "arms": ARMS,
        "hashes": hashes, "replay_sha256": hashlib.sha256(REPLAY.read_bytes()).hexdigest(),
        "limitation": "Opponent actions are fixed; causal diagnostic only, not reactive-policy ranking.",
    }
    (OUT / "protocol.json").write_text(json.dumps(protocol, indent=2) + "\n", encoding="utf-8")
    rows = []
    for name, path in ARMS.items():
        row = dict(arm=name, **play(str(ROOT / path), str(opponent), seed, 1))
        rows.append(row)
        print(name, row["status"], row.get("a"), row.get("b"), flush=True)
    (OUT / "results.json").write_text(json.dumps(rows) + "\n", encoding="utf-8")
    assert all(row["status"] == "DONE" for row in rows)


if __name__ == "__main__":
    main()
