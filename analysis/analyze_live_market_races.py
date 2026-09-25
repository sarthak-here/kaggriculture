"""Measure market-order races in a downloaded Kaggriculture replay manifest.

Worker equality and market equality are kept separate.  This localizes games
where two agents farm nearly identically but transfer value through a different
ordering of the same market requests.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path


OWN_COHORTS = {"submission_loss", "submission_win_control"}


def load(path: Path) -> dict:
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)


def action(step: list, seat: int) -> dict:
    value = step[seat].get("action") if seat < len(step) else None
    return value if isinstance(value, dict) else {}


def workers(value: dict) -> tuple:
    commands = [value.get("farmer")] + list(value.get("hands") or [])
    return tuple(tuple(command or []) for command in commands)


def market(value: dict) -> tuple:
    return tuple(tuple(order or []) for order in (value.get("market") or []))


def multiset(value: tuple) -> tuple:
    return tuple(sorted(value, key=repr))


def observations(record: list) -> list[dict]:
    shared = record[0].get("observation") or {}
    result = []
    for seat in (0, 1):
        obs = dict(record[seat].get("observation") or {})
        for key in ("farms", "market", "town", "step"):
            if key not in obs and key in shared:
                obs[key] = shared[key]
        result.append(obs)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    base = args.manifest.parent
    matches = []
    position_gaps: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for entry in manifest["replays"]:
        labels = [label for label in entry["labels"] if label["cohort"] in OWN_COHORTS]
        if not labels:
            continue
        replay = load(base / entry["path"])
        steps = replay["steps"]
        for label in labels:
            mine = int(label["seat"])
            opponent = 1 - mine
            counters = Counter()
            first_worker_divergence = None
            first_market_divergence = None
            order_only_cash_advantage = 0.0
            product_position_gap = defaultdict(list)

            for index in range(len(steps) - 1):
                before = observations(steps[index])
                after = observations(steps[index + 1])
                own_action = action(steps[index + 1], mine)
                opp_action = action(steps[index + 1], opponent)
                own_workers, opp_workers = workers(own_action), workers(opp_action)
                own_market, opp_market = market(own_action), market(opp_action)
                counters["turns"] += 1
                counters["worker_equal"] += own_workers == opp_workers
                counters["market_equal"] += own_market == opp_market
                if own_workers != opp_workers and first_worker_divergence is None:
                    first_worker_divergence = index
                if own_market != opp_market and first_market_divergence is None:
                    first_market_divergence = index

                same_multiset = multiset(own_market) == multiset(opp_market)
                counters["market_multiset_equal"] += same_multiset
                if same_multiset and own_market != opp_market:
                    counters["order_only_turns"] += 1
                    own_delta = (after[mine]["farms"][mine]["money"] -
                                 before[mine]["farms"][mine]["money"])
                    opp_delta = (after[opponent]["farms"][opponent]["money"] -
                                 before[opponent]["farms"][opponent]["money"])
                    order_only_cash_advantage += own_delta - opp_delta
                    own_positions = defaultdict(list)
                    opp_positions = defaultdict(list)
                    for pos, order in enumerate(own_market):
                        if len(order) >= 2:
                            own_positions[f"{order[0]}:{order[1]}"].append(pos)
                    for pos, order in enumerate(opp_market):
                        if len(order) >= 2:
                            opp_positions[f"{order[0]}:{order[1]}"].append(pos)
                    for product in own_positions.keys() & opp_positions.keys():
                        if len(own_positions[product]) == len(opp_positions[product]):
                            product_position_gap[product].append(
                                sum(own_positions[product]) / len(own_positions[product]) -
                                sum(opp_positions[product]) / len(opp_positions[product])
                            )

            result = "loss" if label["cohort"] == "submission_loss" else "win"
            for product, values in product_position_gap.items():
                position_gaps[result][product].extend(values)
            turns = counters["turns"] or 1
            matches.append({
                "episode": int(label["episode_id"]),
                "result": result,
                "seat": mine,
                "opponent": label.get("opponent"),
                "margin": float(label["margin"]),
                "worker_agreement": counters["worker_equal"] / turns,
                "market_agreement": counters["market_equal"] / turns,
                "market_multiset_agreement": counters["market_multiset_equal"] / turns,
                "order_only_turns": counters["order_only_turns"],
                "order_only_cash_advantage": order_only_cash_advantage,
                "first_worker_divergence": first_worker_divergence,
                "first_market_divergence": first_market_divergence,
            })

    summary = {}
    for result in ("loss", "win"):
        rows = [row for row in matches if row["result"] == result]
        summary[result] = {
            "matches": len(rows),
            "near_worker_clones": sum(row["worker_agreement"] >= .9 for row in rows),
            "means": {
                key: sum(float(row[key] or 0) for row in rows) / len(rows)
                for key in ("margin", "worker_agreement", "market_agreement",
                            "market_multiset_agreement", "order_only_turns",
                            "order_only_cash_advantage")
            },
            "mean_position_gap_ours_minus_opponent": {
                product: sum(values) / len(values)
                for product, values in sorted(position_gaps[result].items())
                if values
            },
        }
    payload = {"summary": summary, "matches": matches}
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
