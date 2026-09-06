"""Write the durable summary for the fixed W13 zero-replay seed blocks."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "analysis" / "w13_runs"
OUTPUT = ROOT / "analysis" / "w13_zero_replay_results.json"
SPECS = {
    "frozen_w13_241000": "zero_vs_w13_241000.json",
    "latest_router_241100": "zero_vs_latest_241100.json",
    "gronk_241200": "zero_vs_gronk_241200.json",
    "kaito_241300": "zero_vs_kaito_241300.json",
    "pf_all_241400": "zero_vs_pfall_241400.json",
    "soil_241500": "zero_vs_soil_241500.json",
    "salem_241600": "zero_vs_salem_241600.json",
    "fleong_241700": "zero_vs_fleong_241700.json",
    "gronk_241800": "zero_vs_gronk_241800.json",
    "frozen_w13_241900": "zero_vs_w13_241900.json",
}


def summarize(path: Path) -> dict:
    raw = path.read_bytes()
    payload = json.loads(raw)
    rows = payload["rows"]
    done = [row for row in rows if row["status"] == "DONE"]
    margins = [row["a"] - row["b"] for row in done]
    return {
        "file": path.name,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "candidate_sha256": payload["a_sha256"],
        "opponent_sha256": payload["b_sha256"],
        "engine": payload["engine"],
        "games": len(rows),
        "wins": sum(margin > 0 for margin in margins),
        "losses": sum(margin < 0 for margin in margins),
        "ties": sum(margin == 0 for margin in margins),
        "failures": len(rows) - len(done),
        "mean_margin": sum(margins) / len(margins) if margins else None,
        "min_margin": min(margins) if margins else None,
        "max_margin": max(margins) if margins else None,
    }


def main() -> None:
    missing = [name for name in SPECS.values() if not (RUNS / name).exists()]
    if missing:
        raise FileNotFoundError(f"missing result files: {missing}")
    result = {label: summarize(RUNS / name) for label, name in SPECS.items()}
    rendered = json.dumps(result, indent=2) + "\n"
    OUTPUT.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
