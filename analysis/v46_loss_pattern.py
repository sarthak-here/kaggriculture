"""Compare v46 Kaggle losses with recent rating-matched wins."""

import collections
import glob
import json
import os
import statistics


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUPS = {
    "LOSS": os.path.join(ROOT, "loss_analysis", "v46_submission", "episode-*-replay.json"),
    "WIN": os.path.join(ROOT, "loss_analysis", "v46_controls", "episode-*-replay.json"),
}


def crop_animal_counts(farm):
    crops = collections.Counter()
    animals = collections.Counter()
    weeds = 0
    ready_units = collections.Counter()
    ready_tiles = 0
    for row in farm.get("tiles", []) or []:
        for tile in row:
            if not isinstance(tile, dict):
                continue
            crop = tile.get("crop")
            animal = tile.get("animal")
            if crop:
                crops[str(crop)] += 1
                units = max(0, int(tile.get("yield_units", 0) or 0))
                if units:
                    ready_units[str(crop)] += units
                    ready_tiles += 1
            if animal:
                animals[str(animal)] += 1
            if tile.get("kind") == "WEED":
                weeds += 1
    return crops, animals, weeds, ready_units, ready_tiles


def inventory_total(inventory):
    return sum(max(0, int(value or 0)) for value in (inventory or {}).values())


def shop_bucket(shops):
    first = shops[:3]
    if first[:1] == ["YARN_STORE"]:
        return "YARN-1"
    if len(first) >= 2 and first[1] == "YARN_STORE":
        return "YARN-2"
    if len(first) >= 3 and first[2] == "YARN_STORE":
        return "YARN-3"
    return "NO-YARN-3"


def profile(path):
    replay = json.load(open(path, encoding="utf-8"))
    steps = replay["steps"]
    names = (replay.get("info") or {}).get("TeamNames") or ["seat0", "seat1"]
    me = next((i for i, name in enumerate(names) if "Sarthak" in str(name)), None)
    if me is None:
        raise RuntimeError("Sarthak seat not found in %s" % path)
    opponent = 1 - me
    final_obs = steps[-1][me]["observation"]
    shops = list((final_obs.get("town") or {}).get("unlocked_shops") or [])
    prices = (final_obs.get("market") or {}).get("prices") or {}

    sides = {}
    for seat, label in ((me, "us"), (opponent, "op")):
        final = steps[-1][seat]
        obs = final["observation"]
        farm = obs["farms"][seat]
        crops, animals, weeds, ready, ready_tiles = crop_animal_counts(farm)
        ready_value = sum(amount * int(prices.get(item, 0) or 0)
                          for item, amount in ready.items())
        money = []
        income = spend = 0.0
        harvests = waters = feed_units = 0
        weed_burden = max_weeds = 0
        previous = None
        for state in steps:
            observation = state[seat].get("observation")
            if isinstance(observation, dict):
                current = float(observation["farms"][seat].get("money", 0) or 0)
                money.append(current)
                if previous is not None:
                    delta = current - previous
                    if delta > 0:
                        income += delta
                    else:
                        spend -= delta
                previous = current
                _, _, live_weeds, _, _ = crop_animal_counts(observation["farms"][seat])
                weed_burden += live_weeds
                max_weeds = max(max_weeds, live_weeds)
            action = state[seat].get("action")
            if not isinstance(action, dict):
                continue
            units = [action.get("farmer"), *(action.get("hands") or [])]
            harvests += sum(1 for row in units
                            if isinstance(row, list) and row[:1] == ["HARVEST"])
            waters += sum(1 for row in units
                          if isinstance(row, list) and row[:1] == ["WATER"])
            for order in action.get("market") or []:
                if isinstance(order, list) and len(order) >= 3 and order[0] == "BUY_PRODUCT":
                    feed_units += max(0, int(order[2] or 0))
        day12 = steps[min(12 * 24, len(steps) - 1)][seat]["observation"]["farms"][seat]
        d12_crops, d12_animals, _, _, _ = crop_animal_counts(day12)
        private = obs.get("private") or {}
        sides[label] = {
            "reward": float(final.get("reward") or 0),
            "income": income,
            "spend": spend,
            "quads": len(farm.get("unlocked_quadrants") or []),
            "hands": len(farm.get("hands") or []),
            "animals": sum(animals.values()),
            "animal_mix": dict(animals),
            "crops": sum(crops.values()),
            "crop_mix": dict(crops),
            "weeds": weeds,
            "ready_units": sum(ready.values()),
            "ready_tiles": ready_tiles,
            "ready_value": ready_value,
            "ready_mix": dict(ready),
            "shed_units": inventory_total((private.get("shed") or {})),
            "harvests": harvests,
            "waters": waters,
            "feed_units": feed_units,
            "weed_burden": weed_burden,
            "max_weeds": max_weeds,
            "d12_animals": sum(d12_animals.values()),
            "d12_animal_mix": dict(d12_animals),
            "d12_crops": sum(d12_crops.values()),
            "d12_crop_mix": dict(d12_crops),
            "money": money,
        }

    gaps = [a - b for a, b in zip(sides["us"]["money"], sides["op"]["money"])]
    return {
        "episode": int((replay.get("info") or {}).get("EpisodeId") or 0),
        "seed": (replay.get("info") or {}).get("seed"),
        "seat": me,
        "opponent": str(names[opponent]),
        "shops": shops,
        "prefix": ">".join(shops[:3]),
        "bucket": shop_bucket(shops),
        "margin": sides["us"]["reward"] - sides["op"]["reward"],
        "day12_gap": gaps[min(12 * 24, len(gaps) - 1)],
        "day18_gap": gaps[min(18 * 24, len(gaps) - 1)],
        "max_lead": max(gaps),
        "final_gap": gaps[-1],
        **sides,
    }


def mean(rows, side, key):
    return statistics.mean(row[side][key] for row in rows)


def main():
    groups = {label: [profile(path) for path in sorted(glob.glob(pattern))]
              for label, pattern in GROUPS.items()}
    for label, rows in groups.items():
        print("\n%s (%d)" % (label, len(rows)))
        for row in rows:
            print("%d s%d %8.0f %-11s ready $%4d/%4d d12 %+7.0f d18 %+7.0f %-24s %s"
                  % (row["episode"], row["seat"], row["margin"], row["bucket"],
                     row["us"]["ready_value"], row["op"]["ready_value"],
                     row["day12_gap"], row["day18_gap"],
                     row["opponent"][:24], row["prefix"]))

    losses, wins = groups["LOSS"], groups["WIN"]
    print("\nAGGREGATE: loss mean | win mean | difference")
    for side, key in (
        ("us", "income"), ("us", "spend"), ("us", "ready_value"),
        ("us", "ready_units"), ("us", "harvests"), ("us", "feed_units"),
        ("us", "weed_burden"), ("us", "max_weeds"),
        ("us", "quads"), ("us", "animals"), ("us", "crops"),
        ("op", "income"), ("op", "spend"), ("op", "ready_value"),
        ("op", "quads"), ("op", "animals"),
    ):
        left, right = mean(losses, side, key), mean(wins, side, key)
        print("%-18s %10.1f | %10.1f | %+10.1f"
              % (side + "." + key, left, right, left - right))
    for key in ("day12_gap", "day18_gap", "max_lead", "margin"):
        left = statistics.mean(row[key] for row in losses)
        right = statistics.mean(row[key] for row in wins)
        print("%-18s %10.1f | %10.1f | %+10.1f" % (key, left, right, left - right))
    print("\nBUCKETS")
    for label, rows in groups.items():
        print(label, dict(collections.Counter(row["bucket"] for row in rows)))
    print("SEATS")
    for label, rows in groups.items():
        print(label, dict(collections.Counter(row["seat"] for row in rows)))


    print("\nRELATIVE TO OPPONENT")
    for key in ("income", "spend", "ready_value", "weed_burden", "harvests"):
        loss_relative = statistics.mean(row["us"][key] - row["op"][key] for row in losses)
        win_relative = statistics.mean(row["us"][key] - row["op"][key] for row in wins)
        print("%-14s loss %+9.1f | win %+9.1f" % (key, loss_relative, win_relative))
    all_rows = losses + wins
    weed_differences = [row["us"]["weed_burden"] - row["op"]["weed_burden"]
                        for row in all_rows]
    margins = [row["margin"] for row in all_rows]
    mean_weed = statistics.mean(weed_differences)
    mean_margin = statistics.mean(margins)
    numerator = sum((weed - mean_weed) * (margin - mean_margin)
                    for weed, margin in zip(weed_differences, margins))
    denominator = (sum((weed - mean_weed) ** 2 for weed in weed_differences)
                   * sum((margin - mean_margin) ** 2 for margin in margins)) ** 0.5
    print("weed-difference/margin correlation %.3f" % (numerator / denominator))
    print("our weed burden > opponent: losses %d/%d wins %d/%d"
          % (sum(row["us"]["weed_burden"] > row["op"]["weed_burden"] for row in losses),
             len(losses),
             sum(row["us"]["weed_burden"] > row["op"]["weed_burden"] for row in wins),
             len(wins)))
    print("\nLOSS DETAILS")
    for row in losses:
        print("%d margin %+.0f feed %d/%d weeds %d/%d d12 animals %s/%s final %s/%s"
              % (row["episode"], row["margin"], row["us"]["feed_units"],
                 row["op"]["feed_units"], row["us"]["weed_burden"],
                 row["op"]["weed_burden"], row["us"]["d12_animal_mix"],
                 row["op"]["d12_animal_mix"], row["us"]["animal_mix"],
                 row["op"]["animal_mix"]))
if __name__ == "__main__":
    main()
