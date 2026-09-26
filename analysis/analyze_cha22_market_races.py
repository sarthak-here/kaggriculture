"""Aggregate verified sell fills for Cha22's close-clone live matchups."""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


DAY_BINS = ((0, 5), (6, 8), (9, 11), (12, 14), (15, 17),
            (18, 20), (21, 23), (24, 26), (27, 29))


def day_bin(day: int) -> str:
    for lo, hi in DAY_BINS:
        if lo <= day <= hi:
            return f"{lo:02d}-{hi:02d}"
    return "other"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--agreement", type=float, default=0.9)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    profile = json.loads((args.corpus / "profile.json").read_text(encoding="utf-8"))
    records = [row for row in profile["records"]
               if row["opponent_submission"] != profile["submission"]
               and float(row["agreement"]) >= args.agreement
               and row["result"] in ("W", "L")]
    totals = defaultdict(lambda: {"own_units": 0, "own_value": 0,
                                  "opp_units": 0, "opp_value": 0, "games": set()})
    for record in records:
        episode = int(record["episode"])
        own_seat = int(record["seat"])
        fills = args.corpus / "csv_audited" / "_parts" / str(episode) / "fills.csv"
        with fills.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row["operation"] != "SELL":
                    continue
                seat = int(row["seat"])
                key = (record["result"], row["item"], day_bin(int(row["day"])))
                bucket = totals[key]
                side = "own" if seat == own_seat else "opp"
                bucket[f"{side}_units"] += int(float(row["units"]))
                bucket[f"{side}_value"] += float(row["value"])
                bucket["games"].add(episode)
    rows = []
    for (result, item, period), bucket in sorted(totals.items()):
        own_units = bucket["own_units"]; opp_units = bucket["opp_units"]
        own_price = bucket["own_value"] / own_units if own_units else None
        opp_price = bucket["opp_value"] / opp_units if opp_units else None
        rows.append({"result": result, "item": item, "days": period,
                     "games": len(bucket["games"]),
                     "own_units": own_units, "opp_units": opp_units,
                     "own_value": bucket["own_value"], "opp_value": bucket["opp_value"],
                     "own_price": own_price, "opp_price": opp_price,
                     "price_gap": (own_price - opp_price
                                   if own_price is not None and opp_price is not None else None)})
    payload = {"agreement": args.agreement, "games": len(records),
               "wins": sum(row["result"] == "W" for row in records),
               "losses": sum(row["result"] == "L" for row in records), "rows": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: payload[key] for key in ("games", "wins", "losses")}, indent=2))
    for row in sorted((row for row in rows if row["result"] == "L" and row["price_gap"] is not None),
                      key=lambda row: row["price_gap"])[:25]:
        print(row["days"], row["item"], "price_gap", round(row["price_gap"], 2),
              "units", row["own_units"], row["opp_units"], "games", row["games"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
