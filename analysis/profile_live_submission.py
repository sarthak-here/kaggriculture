"""Profile a downloaded Kaggriculture submission corpus by observable families.

Consumes collect_replay_csv_corpus.py + replays_to_csv.py output.  It never
loads opponent code.  Family keys are replay-derived worker/opening hashes and
public farm/economy features.
"""
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def rows(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def number(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    manifest = json.loads((args.corpus / "manifest.json").read_text(encoding="utf-8"))
    csv_dir = args.corpus / "csv_audited"
    episode_rows = rows(csv_dir / "episodes.csv")
    day_rows = rows(csv_dir / "days.csv")
    turn_rows = rows(csv_dir / "turns.csv")

    labels = {int(item["episode_id"]): item for item in manifest["episodes"]}
    episodes = defaultdict(dict)
    for row in episode_rows:
        episodes[int(row["episode_id"])][int(row["seat"])] = row
    days = defaultdict(list)
    for row in day_rows:
        days[(int(row["episode_id"]), int(row["seat"]))].append(row)
    first_turn = {}
    fullest_shops = {}
    for row in turn_rows:
        key = (int(row["episode_id"]), int(row["seat"]))
        if key not in first_turn or int(row["step"]) < int(first_turn[key]["step"]):
            first_turn[key] = row
        current = json.loads(row.get("shops") or "[]")
        if len(current) > len(fullest_shops.get(key, [])):
            fullest_shops[key] = current

    records = []
    for episode_id, label in labels.items():
        if label.get("self_play") or episode_id not in episodes:
            continue
        seat = int(label["seat"]); rival = 1 - seat
        own = episodes[episode_id][seat]; opp = episodes[episode_id][rival]
        own_days = days[(episode_id, seat)]; opp_days = days[(episode_id, rival)]
        shops = fullest_shops.get((episode_id, seat), [])
        totals = {}
        for prefix, source in (("own", own_days), ("opp", opp_days)):
            for field in ("SELL_WHEAT_units", "SELL_CARROT_units", "SELL_TOMATO_units",
                          "SELL_STRAWBERRY_units", "SELL_MELON_units", "SELL_EGG_units",
                          "SELL_MILK_units", "SELL_WOOL_units", "BUY_PRODUCT_WHEAT_units",
                          "BUY_PRODUCT_FERTILIZER_units", "BUY_SEED_CARROT_units"):
                totals[prefix + "_" + field] = sum(number(row.get(field)) for row in source)
        day_gaps = {}
        for day in (0, 3, 7, 14, 21, 29):
            od = next((x for x in own_days if int(x["day"]) == day), None)
            rd = next((x for x in opp_days if int(x["day"]) == day), None)
            if od and rd:
                day_gaps[str(day)] = number(od.get("closing_money")) - number(rd.get("closing_money"))
        records.append({
            "episode": episode_id, "result": label["result"], "margin": number(label["margin"]),
            "seat": seat, "opponent": label["opponent"],
            "opponent_submission": label.get("opponent_submission"),
            "opponent_rating": number(label.get("opponent_rating")),
            "shops": shops, "shop3": "/".join(shops[:3]),
            "own_worker": own["worker_sha256"][:12], "opp_worker": opp["worker_sha256"][:12],
            "opp_opening": opp["opening_sha256"][:12],
            "agreement": number(own["worker_agreement"]),
            "own_reward": number(own["final_reward"]), "opp_reward": number(opp["final_reward"]),
            "opp_hands": int(number(opp["hands"])), "opp_quads": int(number(opp["quadrants"])),
            "opp_cows": int(number(opp["cow"])), "opp_sheep": int(number(opp["sheep"])),
            "opp_geese": int(number(opp["goose"])), "opp_weeds": int(number(opp["weeds"])),
            "opp_build": "%dh-%dq-%dc-%ds-%dg" % (
                int(number(opp["hands"])), int(number(opp["quadrants"])),
                int(number(opp["cow"])), int(number(opp["sheep"])), int(number(opp["goose"]))),
            "day_cash_gap": day_gaps, **totals,
        })

    def grouped(field, minimum=2):
        groups = defaultdict(list)
        for record in records:
            groups[str(record[field])].append(record)
        output = []
        for key, group in groups.items():
            if len(group) < minimum:
                continue
            counts = Counter(row["result"] for row in group)
            output.append({
                "key": key, "games": len(group), "W": counts["W"], "L": counts["L"], "T": counts["T"],
                "mean_margin": sum(row["margin"] for row in group) / len(group),
                "mean_agreement": sum(row["agreement"] for row in group) / len(group),
                "opponents": sorted(set(row["opponent"] for row in group)),
                "episodes": [row["episode"] for row in group],
            })
        return sorted(output, key=lambda row: (-row["L"], row["mean_margin"]))

    counts = Counter(row["result"] for row in records)
    result = {
        "submission": manifest["submission"], "games": len(records), "results": dict(counts),
        "by_seat": {str(seat): dict(Counter(r["result"] for r in records if r["seat"] == seat))
                    for seat in (0, 1)},
        "by_opponent_submission": grouped("opponent_submission"),
        "by_worker_family": grouped("opp_worker"),
        "by_opening_family": grouped("opp_opening"),
        "by_shop3": grouped("shop3"),
        "by_opponent_build": grouped("opp_build"),
        "worst_losses": sorted((r for r in records if r["result"] == "L"),
                                key=lambda row: row["margin"])[:20],
        "records": records,
    }
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(json.dumps({key: result[key] for key in
                      ("submission", "games", "results", "by_seat", "by_opponent_submission",
                       "by_worker_family", "by_opening_family", "by_shop3")},
                     indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
