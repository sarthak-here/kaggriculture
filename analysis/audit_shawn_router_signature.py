"""Audit whether the narrow Shawn404 detector matches other live replays."""
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "analysis/v45_prefund_exported_live_20260917"
OUTPUT = ROOT / "analysis/shawn404_signature_audit_20260917.json"


def positions_equal(farms, seat):
    own, rival = farms[seat], farms[1 - seat]
    return bool(own.get("hands")) and own.get("hands") == rival.get("hands") and own.get("farmer") == rival.get("farmer")


def main():
    rows = []
    manifest = json.loads((CORPUS / "manifest.json").read_text(encoding="utf-8"))
    seats = {int(row["episode_id"]): row for row in manifest["episodes"]}
    for path in sorted((CORPUS / "replays").glob("episode-*-replay.json.gz")):
        replay = json.loads(gzip.decompress(path.read_bytes()))
        episode = int(path.name.split("-")[1])
        meta = seats[episode]
        for seat in (int(meta["seat"]),):
            obs1 = replay["steps"][1][seat]["observation"]
            obs2 = replay["steps"][2][seat]["observation"]
            obs145 = replay["steps"][145][seat]["observation"]
            rival = 1 - seat
            cash1 = int(obs1["farms"][rival]["money"])
            cash2 = int(obs2["farms"][rival]["money"])
            shops = tuple(obs145["town"].get("unlocked_shops", [])[:2])
            same_positions = positions_equal(obs145["farms"], seat)
            match = cash1 == 2865 and cash2 == 152 and shops == ("FARMERS_MARKET", "FARMERS_MARKET") and same_positions
            rows.append({
                "episode": episode,
                "seat": seat,
                "opponent": meta["opponent"].strip(),
                "cash1": cash1,
                "cash2": cash2,
                "shops": list(shops),
                "same_positions_step145": same_positions,
                "matches": match,
            })
    result = {
        "detector": "opponent cash 2865 at step1, 152 at step2; FM/FM prefix; equal sorted worker positions at step145",
        "rows": rows,
        "matches": [row for row in rows if row["matches"]],
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"audited={len(rows)} matches={len(result['matches'])}")
    for row in result["matches"]:
        print(row["episode"], row["opponent"])


if __name__ == "__main__":
    main()
