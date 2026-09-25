"""Compare fulfilled sale timing across audited replay cohorts.

Uses verified fills rather than requested order quantities.  Submission wins
and losses can optionally be restricted to near-clones by worker agreement.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


PRODUCTS = (
    "WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON",
    "EGG", "MILK", "WOOL", "FERTILIZER",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_dir", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--clone-threshold", type=float, default=.9)
    args = parser.parse_args()

    selected: dict[tuple[int, int], str] = {}
    selected_episodes: dict[int, tuple[int, str]] = {}
    counts: dict[str, int] = defaultdict(int)
    with (args.csv_dir / "episodes.csv").open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            cohort = row["cohorts"]
            if cohort == "top10":
                label = "top10"
            elif cohort in ("submission_loss", "submission_win_control"):
                agreement = float(row["worker_agreement"] or 0)
                if agreement < args.clone_threshold:
                    continue
                label = "near_clone_loss" if cohort == "submission_loss" else "near_clone_win"
            else:
                continue
            key = (int(row["episode_id"]), int(row["seat"]))
            selected[key] = label
            selected_episodes[key[0]] = (key[1], label)
            counts[label] += 1

    stats: dict[str, dict[str, dict]] = defaultdict(
        lambda: defaultdict(lambda: {
            "units": 0, "value": 0.0, "fill_rows": 0,
            "step_units": 0, "day_windows": defaultdict(int),
        })
    )
    paired: dict[str, dict[str, dict[str, dict]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: {
            "units": 0, "value": 0.0, "step_units": 0,
        }))
    )
    with (args.csv_dir / "fills.csv").open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if row["operation"] != "SELL" or row["item"] not in PRODUCTS:
                continue
            episode = int(row["episode_id"]); seat = int(row["seat"])
            label = selected.get((episode, seat))
            pair = selected_episodes.get(episode)
            if pair is not None:
                own_seat, pair_label = pair
                side = "own" if seat == own_seat else "opponent"
                dst = paired[pair_label][row["item"]][side]
                pair_units = int(float(row["units"])); pair_value = float(row["value"])
                dst["units"] += pair_units; dst["value"] += pair_value
                dst["step_units"] += int(row["step"]) * pair_units
            if label is None:
                continue
            units = int(float(row["units"])); value = float(row["value"])
            step = int(row["step"]); day = int(row["day"])
            item = row["item"]; dst = stats[label][item]
            dst["units"] += units; dst["value"] += value; dst["fill_rows"] += 1
            dst["step_units"] += step * units
            start = (day // 5) * 5
            dst["day_windows"][f"{start:02d}-{min(29, start + 4):02d}"] += units

    output = {"clone_threshold": args.clone_threshold, "cohort_games": dict(counts),
              "cohorts": {}, "paired_sale_comparison": {}}
    for label, products in stats.items():
        n = counts[label]
        output["cohorts"][label] = {}
        for item in PRODUCTS:
            src = products[item]
            units = src["units"]
            output["cohorts"][label][item] = {
                "units_per_game": round(units / n, 3),
                "value_per_game": round(src["value"] / n, 3),
                "realized_price": round(src["value"] / units, 3) if units else None,
                "mean_sale_step": round(src["step_units"] / units, 3) if units else None,
                "fill_rows_per_game": round(src["fill_rows"] / n, 3),
                "units_per_game_by_day_window": {
                    key: round(value / n, 3)
                    for key, value in sorted(src["day_windows"].items())
                },
            }
    for label, products in paired.items():
        n = counts[label]
        output["paired_sale_comparison"][label] = {}
        for item in PRODUCTS:
            own = products[item]["own"]; opponent = products[item]["opponent"]
            def summary(src: dict) -> dict:
                units = src["units"]
                return {
                    "units_per_game": round(units / n, 3),
                    "value_per_game": round(src["value"] / n, 3),
                    "realized_price": round(src["value"] / units, 3) if units else None,
                    "mean_sale_step": round(src["step_units"] / units, 3) if units else None,
                }
            own_summary = summary(own); opponent_summary = summary(opponent)
            output["paired_sale_comparison"][label][item] = {
                "own": own_summary, "opponent": opponent_summary,
                "own_minus_opponent_units_per_game": round(
                    own_summary["units_per_game"] - opponent_summary["units_per_game"], 3),
                "own_minus_opponent_value_per_game": round(
                    own_summary["value_per_game"] - opponent_summary["value_per_game"], 3),
            }
    args.out.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
