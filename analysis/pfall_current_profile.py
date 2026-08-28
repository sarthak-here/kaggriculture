"""Profile the complete current pf_all loss corpus by route and economy family."""

from __future__ import annotations

import collections
import json
import statistics
from pathlib import Path

from portfolio import label_for

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "loss_analysis" / "pfall_current"


def farm_stats(farm):
    crops = collections.Counter()
    animals = collections.Counter()
    weeds = 0
    ready = 0
    for row in farm.get("tiles", []) or []:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            if tile.get("crop"):
                crops[str(tile["crop"])] += 1
                ready += max(0, int(tile.get("yield_units", 0) or 0))
            if tile.get("animal"):
                animals[str(tile["animal"])] += 1
            weeds += int(tile.get("kind") == "WEED")
    return crops, animals, weeds, ready


def side_profile(steps, seat):
    income = spend = 0.0
    previous = None
    weed_burden = 0
    feed_units = 0
    for state in steps:
        obs = state[seat].get("observation")
        if isinstance(obs, dict):
            farm = obs["farms"][seat]
            money = float(farm.get("money", 0) or 0)
            if previous is not None:
                delta = money - previous
                if delta > 0:
                    income += delta
                else:
                    spend -= delta
            previous = money
            weed_burden += farm_stats(farm)[2]
        action = state[seat].get("action")
        if isinstance(action, dict):
            for order in action.get("market") or []:
                if isinstance(order, list) and len(order) >= 3 and order[0] == "BUY_PRODUCT":
                    feed_units += max(0, int(order[2] or 0))
    snapshots = {}
    for day in (8, 12, 18, 24, 29):
        index = min(day * 24, len(steps) - 1)
        obs = steps[index][seat]["observation"]
        farm = obs["farms"][seat]
        crops, animals, weeds, ready = farm_stats(farm)
        snapshots[day] = {
            "money": float(farm.get("money", 0) or 0),
            "quads": len(farm.get("unlocked_quadrants") or []),
            "hands": len(farm.get("hands") or []),
            "crops": sum(crops.values()),
            "crop_mix": dict(crops),
            "animals": sum(animals.values()),
            "animal_mix": dict(animals),
            "weeds": weeds,
            "ready": ready,
        }
    return {"income": income, "spend": spend, "weed_burden": weed_burden,
            "feed_units": feed_units, "days": snapshots}


def main():
    manifest = json.load(open(CORPUS / "manifest.json", encoding="utf-8"))
    metadata = {row["episode"]: row for row in manifest}
    rows = []
    for path in sorted(CORPUS.glob("episode-*-replay.json")):
        episode_id = int(path.name.split("-")[1])
        replay = json.load(open(path, encoding="utf-8"))
        steps = replay.get("steps") or []
        if not steps:
            continue
        names = (replay.get("info") or {}).get("TeamNames") or ["seat0", "seat1"]
        seat = int(metadata[episode_id]["seat"])
        opponent = 1 - seat
        final_obs = steps[-1][seat]["observation"]
        shops = list((final_obs.get("town") or {}).get("unlocked_shops") or [])
        us = side_profile(steps, seat)
        op = side_profile(steps, opponent)
        final_mix = op["days"][29]["animal_mix"]
        rows.append({
            **metadata[episode_id],
            "opponent": str(names[opponent]),
            "seed": (replay.get("info") or {}).get("seed"),
            "shops": shops,
            "prefix": ">".join(shops[:3]),
            "bucket": label_for(shops),
            "op_family": "%dq-%dc-%ds-%dg" % (
                op["days"][29]["quads"], final_mix.get("COW", 0),
                final_mix.get("SHEEP", 0), final_mix.get("GOOSE", 0)),
            "us": us,
            "op": op,
        })
    json.dump(rows, open(CORPUS / "profiles.json", "w", encoding="utf-8"), indent=2)
    print("losses", len(rows))
    print("seat", dict(collections.Counter(row["seat"] for row in rows)))
    print("bucket", dict(collections.Counter(row["bucket"] for row in rows)))
    print("prefix top", collections.Counter(row["prefix"] for row in rows).most_common(12))
    print("opponent family top", collections.Counter(row["op_family"] for row in rows).most_common(12))
    print("opponent repeated", collections.Counter(row["opponent_submission"] for row in rows).most_common(12))
    close = [row for row in rows if row["margin"] >= -2500]
    severe = [row for row in rows if row["margin"] <= -8000]
    print("close <=2500", len(close), "severe >=8000", len(severe))
    for label, group in (("ALL", rows), ("CLOSE", close), ("SEVERE", severe)):
        print("\n", label, len(group))
        print(" buckets", dict(collections.Counter(row["bucket"] for row in group)))
        print(" seats", dict(collections.Counter(row["seat"] for row in group)))
        for key in ("income", "spend", "feed_units", "weed_burden"):
            ours = statistics.mean(row["us"][key] for row in group)
            theirs = statistics.mean(row["op"][key] for row in group)
            print(" %-11s us %9.0f op %9.0f delta %+9.0f" % (key, ours, theirs, ours - theirs))
        for day in (8, 12, 18, 24, 29):
            gaps = [row["us"]["days"][day]["money"] - row["op"]["days"][day]["money"]
                    for row in group]
            print(" day%-2d gap %+8.0f q %.2f/%.2f animals %.1f/%.1f crops %.1f/%.1f" % (
                day, statistics.mean(gaps),
                statistics.mean(row["us"]["days"][day]["quads"] for row in group),
                statistics.mean(row["op"]["days"][day]["quads"] for row in group),
                statistics.mean(row["us"]["days"][day]["animals"] for row in group),
                statistics.mean(row["op"]["days"][day]["animals"] for row in group),
                statistics.mean(row["us"]["days"][day]["crops"] for row in group),
                statistics.mean(row["op"]["days"][day]["crops"] for row in group)))
    print("\nWORST")
    for row in sorted(rows, key=lambda item: item["margin"])[:20]:
        print("%d s%d %7.0f %-22s %-13s %-24s %s" % (
            row["episode"], row["seat"], row["margin"], row["bucket"],
            row["op_family"], row["opponent"][:24], row["prefix"]))


if __name__ == "__main__":
    main()