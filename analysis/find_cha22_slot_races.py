"""Find repeatable same-turn market-slot disadvantages in Cha22 live replays."""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def load_orders(path: Path) -> dict[tuple[int, int, str], int]:
    slots: dict[tuple[int, int, str], int] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                order = json.loads(row["requested_order"])
            except (TypeError, json.JSONDecodeError):
                continue
            if len(order) >= 2 and order[0] == "SELL":
                key = (int(row["seat"]), int(row["step"]), str(order[1]))
                slots[key] = min(slots.get(key, 99), int(row["order_index"]))
    return slots


def load_sales(path: Path) -> dict[tuple[int, int, str], tuple[float, float]]:
    sales: dict[tuple[int, int, str], list[float]] = defaultdict(lambda: [0.0, 0.0])
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["operation"] != "SELL":
                continue
            key = (int(row["seat"]), int(row["step"]), row["item"])
            sales[key][0] += float(row["units"])
            sales[key][1] += float(row["value"])
    return {key: (value[0], value[1]) for key, value in sales.items()}


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
    events = []
    signatures: dict[tuple[int, str, int, int], dict] = {}
    for record in records:
        episode = int(record["episode"])
        own = int(record["seat"]); opp = 1 - own
        base = args.corpus / "csv_audited" / "_parts" / str(episode)
        slots = load_orders(base / "orders.csv")
        sales = load_sales(base / "fills.csv")
        for (seat, step, item), (own_units, own_value) in sales.items():
            if seat != own or (opp, step, item) not in sales:
                continue
            opp_units, opp_value = sales[(opp, step, item)]
            if own_units <= 0 or opp_units <= 0 or abs(own_units - opp_units) > 1e-9:
                continue
            own_price = own_value / own_units
            opp_price = opp_value / opp_units
            if own_price >= opp_price - 1e-9:
                continue
            own_slot = slots.get((own, step, item), 99)
            opp_slot = slots.get((opp, step, item), 99)
            if own_slot <= opp_slot:
                continue
            recoverable = round(opp_value - own_value, 6)
            event = {
                "episode": episode, "result": record["result"],
                "margin": float(record["margin"]), "opponent": record["opponent"],
                "agreement": float(record["agreement"]), "step": step,
                "day": step // 24, "item": item, "units": own_units,
                "own_slot": own_slot, "opp_slot": opp_slot,
                "own_price": own_price, "opp_price": opp_price,
                "recoverable_value": recoverable,
                "would_flip": record["result"] == "L" and recoverable > -float(record["margin"]),
            }
            events.append(event)
            key = (step, item, own_slot, opp_slot)
            bucket = signatures.setdefault(key, {
                "step": step, "day": step // 24, "item": item,
                "own_slot": own_slot, "opp_slot": opp_slot,
                "loss_events": 0, "win_events": 0, "episodes": set(),
                "recoverable_value": 0.0, "losses_flipped": 0,
            })
            bucket["loss_events" if record["result"] == "L" else "win_events"] += 1
            bucket["episodes"].add(episode)
            bucket["recoverable_value"] += recoverable
            bucket["losses_flipped"] += int(event["would_flip"])

    rows = []
    for bucket in signatures.values():
        bucket["episode_count"] = len(bucket.pop("episodes"))
        bucket["recoverable_value"] = round(bucket["recoverable_value"], 3)
        rows.append(bucket)
    rows.sort(key=lambda row: (row["losses_flipped"], row["loss_events"],
                               row["recoverable_value"]), reverse=True)
    events.sort(key=lambda row: (row["would_flip"], row["recoverable_value"]), reverse=True)
    payload = {"agreement": args.agreement, "games": len(records),
               "events": events, "signatures": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"games": len(records), "events": len(events),
                      "signatures": len(rows)}, indent=2))
    for row in rows[:30]:
        print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
