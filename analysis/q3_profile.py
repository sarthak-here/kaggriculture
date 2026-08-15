"""Why does a real top agent make a THIRD quadrant pay when ours cannot?

Our Q3 builds have failed ~35 times on the day 7-15 cash wall (#28d/#36/#37/#46/#48),
yet the agents beating us on the ladder routinely run 3+ quadrants. So the problem is not
Q3 itself -- something upstream lets them afford it. This profiles every player in the
local replay corpus, splits them by how much land they bought, and prints the day-by-day
build of the high scorers so the difference is visible.

Run:  .venv/Scripts/python.exe analysis/q3_profile.py [max_replays]
"""

import sys
import os
import json
import glob
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TURNS_PER_DAY = 24
REPLAY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "replays")


def is_plant(t):
    return isinstance(t, dict) and t.get("kind") == "PLANT"


def is_structure(t):
    return isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE", "SHED", "BARN")


def animal_of(t):
    """An occupied animal tile carries `animal` as a SINGLE string (_new_animal),
    not an `animals` list -- reading it as a list silently reports 0 everywhere."""
    return t.get("animal") if isinstance(t, dict) else None


def profile_player(steps, pid):
    """Day-indexed build profile for one player.

    Hands vanish overnight and are re-hired through the day, so reading
    len(hands) at hour 0 always reports 0. Take the day's PEAK crew instead.
    Money is sampled at end of day, after the day's trading.
    """
    days = []
    for i in range(0, len(steps), TURNS_PER_DAY):
        window = steps[i:i + TURNS_PER_DAY]
        last = window[-1][0]["observation"]["farms"][pid]
        peak_hands = 0
        for st in window:
            f = st[0]["observation"]["farms"][pid]
            peak_hands = max(peak_hands, len(f.get("hands", []) or []))
        crops = Counter()
        herd = Counter()
        animals = 0
        planted = 0
        for row in last["tiles"]:
            for t in row:
                if is_plant(t):
                    crops[t.get("crop")] += 1
                    planted += 1
                elif animal_of(t):
                    herd[animal_of(t)] += 1
                    animals += 1
        days.append({
            "day": i // TURNS_PER_DAY,
            "money": last["money"],
            "quads": len(last["unlocked_quadrants"]),
            "hands": peak_hands,
            "planted": planted,
            "animals": animals,
            "herd": dict(herd),
            "crops": dict(crops),
        })
    return days


def land_days(days):
    """Day each additional quadrant was first observed."""
    out = {}
    prev = days[0]["quads"]
    for d in days:
        if d["quads"] > prev:
            out[d["quads"]] = d["day"]
            prev = d["quads"]
    return out


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 99
    files = sorted(glob.glob(os.path.join(REPLAY_DIR, "*.json")))[:limit]
    if not files:
        print(f"no replays in {REPLAY_DIR}")
        return 1

    players = []
    for path in files:
        try:
            with open(path) as f:
                d = json.load(f)
        except Exception as e:
            print(f"  skip {os.path.basename(path)}: {type(e).__name__}")
            continue
        rewards = d.get("rewards") or []
        steps = d["steps"]
        for pid in range(len(rewards)):
            if rewards[pid] is None:
                continue
            days = profile_player(steps, pid)
            players.append({
                "file": os.path.basename(path),
                "pid": pid,
                "reward": rewards[pid],
                "days": days,
                "final_quads": days[-1]["quads"],
                "land_days": land_days(days),
            })
        print(f"  read {os.path.basename(path)}  rewards={rewards}")

    if not players:
        print("no players parsed")
        return 1

    print("\n" + "=" * 78)
    print(f"SCORE BY FINAL QUADRANT COUNT  ({len(players)} player-games)")
    print("=" * 78)
    by_q = {}
    for p in players:
        by_q.setdefault(p["final_quads"], []).append(p["reward"])
    for q in sorted(by_q):
        rs = sorted(by_q[q])
        print(f"  {q} quadrants: n={len(rs):<3} median {rs[len(rs)//2]:>9,.0f}"
              f"   max {rs[-1]:>9,.0f}   min {rs[0]:>9,.0f}")

    # The comparison that matters: top 3+ quadrant builds, day by day.
    big = sorted([p for p in players if p["final_quads"] >= 3],
                 key=lambda p: -p["reward"])
    if not big:
        print("\nNo 3+ quadrant players in this corpus.")
        return 0

    print("\n" + "=" * 78)
    print(f"TOP 3+ QUADRANT BUILDS (n={len(big)})")
    print("=" * 78)
    for p in big[:6]:
        print(f"  {p['reward']:>9,.0f}  {p['file'][:28]} p{p['pid']}"
              f"  land bought on days {p['land_days']}")

    print("\n" + "=" * 78)
    print("DAY-BY-DAY BUILD OF THE TOP 3 (money / quads / hands / tiles / animals)")
    print("=" * 78)
    for p in big[:3]:
        print(f"\n--- {p['reward']:,.0f}  {p['file'][:28]} p{p['pid']}"
              f"  land {p['land_days']} ---")
        print("day   money  quads  hands  tiles  animals   crop mix")
        for d in p["days"]:
            if d["day"] % 2 and d["day"] > 15:
                continue
            mix = " ".join(f"{k[:4]}:{v}" for k, v in sorted(d["crops"].items()))
            if d["herd"]:
                mix += "  | " + " ".join(f"{k[:5]}:{v}" for k, v in sorted(d["herd"].items()))
            print(f"{d['day']:>3} {d['money']:>7,.0f} {d['quads']:>6} {d['hands']:>6}"
                  f" {d['planted']:>6} {d['animals']:>8}   {mix}")

    # Mean trajectory of 3+ quadrant winners, for a compact comparison target.
    print("\n" + "=" * 78)
    print("MEAN TRAJECTORY: top-half 3+ quadrant builds")
    print("=" * 78)
    top = big[:max(1, len(big) // 2)]
    print("day   money  quads  hands  tiles  animals")
    for di in range(len(top[0]["days"])):
        if di % 2:
            continue
        n = len(top)
        m = sum(p["days"][di]["money"] for p in top) / n
        q = sum(p["days"][di]["quads"] for p in top) / n
        h = sum(p["days"][di]["hands"] for p in top) / n
        t = sum(p["days"][di]["planted"] for p in top) / n
        a = sum(p["days"][di]["animals"] for p in top) / n
        print(f"{di:>3} {m:>7,.0f} {q:>6.1f} {h:>6.1f} {t:>6.1f} {a:>8.1f}")

    # ---- what actually predicts the score? ----
    def corr(xs, ys):
        n = len(xs)
        if n < 3:
            return float("nan")
        mx, my = sum(xs) / n, sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        dx = sum((x - mx) ** 2 for x in xs) ** 0.5
        dy = sum((y - my) ** 2 for y in ys) ** 0.5
        return num / (dx * dy) if dx and dy else float("nan")

    def early(p, key, lo=0, hi=7):
        ds = [d for d in p["days"] if lo <= d["day"] <= hi]
        return sum(d[key] for d in ds) / max(1, len(ds))

    def early_crop(p, crop, lo=0, hi=7):
        ds = [d for d in p["days"] if lo <= d["day"] <= hi]
        return sum(d["crops"].get(crop, 0) for d in ds) / max(1, len(ds))

    print("\n" + "=" * 78)
    print("WHAT PREDICTS THE SCORE?  (Pearson r vs final reward)")
    print("=" * 78)
    rewards = [p["reward"] for p in players]
    q2day = [p["land_days"].get(2, 99) for p in players]
    metrics = [
        ("day Q2 bought (lower=earlier)", q2day),
        ("day Q3 bought", [p["land_days"].get(3, 99) for p in players]),
        ("final quadrants", [p["final_quads"] for p in players]),
        ("mean TILES PLANTED d0-7", [early(p, "planted") for p in players]),
        ("mean tiles planted d8-15", [early(p, "planted", 8, 15) for p in players]),
        ("mean hands d0-7", [early(p, "hands") for p in players]),
        ("mean animals d0-7", [early(p, "animals") for p in players]),
        ("mean animals d8-15", [early(p, "animals", 8, 15) for p in players]),
        ("mean WHEAT tiles d0-7", [early_crop(p, "WHEAT") for p in players]),
        ("mean MELON tiles d0-7", [early_crop(p, "MELON") for p in players]),
        ("mean STRAWBERRY tiles d0-7", [early_crop(p, "STRAWBERRY") for p in players]),
        ("mean STRAWBERRY tiles d8-15", [early_crop(p, "STRAWBERRY", 8, 15) for p in players]),
        ("money at d7", [p["days"][7]["money"] if len(p["days"]) > 7 else 0
                         for p in players]),
    ]
    for name, xs in sorted(metrics, key=lambda m: -abs(corr(m[1], rewards))):
        print(f"  r = {corr(xs, rewards):>+6.2f}   {name}")

    # The land-day correlations above use 99 as "never bought", so they really
    # measure WHETHER a quadrant was bought, not WHEN. Re-run on buyers only.
    print("\n" + "-" * 78)
    print("LAND TIMING, BUYERS ONLY (removes the 'never bought' sentinel)")
    print("-" * 78)
    for q in (2, 3, 4):
        sub = [p for p in players if q in p["land_days"]]
        if len(sub) < 3:
            print(f"  Q{q}: n={len(sub)}, too few")
            continue
        xs = [p["land_days"][q] for p in sub]
        ys = [p["reward"] for p in sub]
        print(f"  Q{q}: n={len(sub):<3} r = {corr(xs, ys):>+5.2f} between day-bought and reward"
              f"   (median day {sorted(xs)[len(xs)//2]})")
        buyers = sum(ys) / len(ys)
        non = [p["reward"] for p in players if q not in p["land_days"]]
        if non:
            print(f"        mean reward: bought {buyers:>9,.0f}   never bought"
                  f" {sum(non)/len(non):>9,.0f}  (n={len(non)})")

    print("\n" + "=" * 78)
    print("TOP QUARTILE vs BOTTOM QUARTILE (mean values)")
    print("=" * 78)
    ranked = sorted(players, key=lambda p: -p["reward"])
    k = max(1, len(ranked) // 4)
    top, bot = ranked[:k], ranked[-k:]
    print(f"{'metric':<32} {'top ' + str(k):>10} {'bottom ' + str(k):>12}")
    for name, _ in metrics:
        pass
    for name, getter in (
        ("reward", lambda p: p["reward"]),
        ("day Q2 bought", lambda p: p["land_days"].get(2, 99)),
        ("day Q3 bought", lambda p: p["land_days"].get(3, 99)),
        ("final quadrants", lambda p: p["final_quads"]),
        ("tiles planted d0-7", lambda p: early(p, "planted")),
        ("WHEAT tiles d0-7", lambda p: early_crop(p, "WHEAT")),
        ("MELON tiles d0-7", lambda p: early_crop(p, "MELON")),
        ("STRAWBERRY tiles d0-7", lambda p: early_crop(p, "STRAWBERRY")),
        ("STRAWBERRY tiles d8-15", lambda p: early_crop(p, "STRAWBERRY", 8, 15)),
        ("animals d0-7", lambda p: early(p, "animals")),
        ("animals d8-15", lambda p: early(p, "animals", 8, 15)),
        ("hands d0-7", lambda p: early(p, "hands")),
    ):
        a = sum(getter(p) for p in top) / len(top)
        b = sum(getter(p) for p in bot) / len(bot)
        print(f"{name:<32} {a:>10,.1f} {b:>12,.1f}")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "q3_profile.json")
    with open(out, "w") as f:
        json.dump([{k: v for k, v in p.items() if k != "days"} for p in players],
                  f, indent=1)
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
