"""Select stratified near-clone live tapes for fast causal screening."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("races", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    races = json.loads(args.races.read_text(encoding="utf-8"))["matches"]
    clone = [row for row in races if row["worker_agreement"] >= .9]
    losses = sorted((row for row in clone if row["result"] == "loss"),
                    key=lambda row: row["margin"])
    wins = sorted((row for row in clone if row["result"] == "win"),
                  key=lambda row: row["margin"])
    chosen = losses[:6] + losses[-6:] + wins[:4] + wins[-4:]
    ids = {row["episode"] for row in chosen}
    selected = []
    for entry in manifest["replays"]:
        if any(int(label["episode_id"]) in ids for label in entry["labels"]):
            selected.append(entry)
    payload = {
        "retrieved_at": manifest["retrieved_at"],
        "submission": manifest["submission"],
        "selection": {
            "rule": "6 worst + 6 closest near-clone losses; 4 closest + 4 largest near-clone wins",
            "matches": chosen,
        },
        "replays": selected,
    }
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(f"selected {len(selected)} replays")


if __name__ == "__main__":
    main()
