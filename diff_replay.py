"""
Replay diagnostic tool. Not part of the submitted agent -- a standalone
analysis script for reading real ladder match replays.

Usage:
    python diff_replay.py replays/episode-XXXXXXXX-replay.json [--csv out.csv]

Prints a per-day table (money, animal counts, hand count, tile breakdown)
for both players, plus a per-resource market table with an "opp_supply_est"
derived column.

opp_supply_est methodology: market inventory changes each day from four
sources -- both players' SELL orders (+), both players' BUY_PRODUCT orders
(WHEAT/FERTILIZER only, -), and town consumption (-, deterministic given
town.unlocked_shops and turn count, but not computed here for simplicity).
We know OUR OWN sells exactly (read straight from our recorded actions,
not inferred), so:

    opp_supply_est = inventory_delta - our_sells

This is a raw proxy, NOT a fully netted decomposition -- it does not
subtract town consumption or either player's BUY_PRODUCT orders, so it
will systematically UNDERSTATE true opponent supply (town consumption
always drains inventory, biasing the delta negative). Good enough as a
first-pass check of whether the signal exists at all before deciding
whether to build anything more precise on top of it. If opp_supply_est
looks noisy/unclear, that itself is useful information -- don't build a
fancier estimator on a signal that hasn't been shown to be clean first.
"""
import csv
import json
import sys

PRODUCTS = ["WHEAT", "CARROT", "TOMATO", "STRAWBERRY", "MELON", "EGG", "MILK", "WOOL", "FERTILIZER"]
MOVE_OPS = {"NORTH", "SOUTH", "EAST", "WEST"}
IDLE_OPS = {"PASS"}
# everything else (HARVEST, WATER, PLANT, FERTILIZE, DIG, BUILD_COOP,
# BUILD_PASTURE, PLACE, FEED, COLLECT_FERTILIZER, CARE, PICKUP, DROP) counts
# as "working" -- this is a per-unit-per-turn classification of the single
# op each unit takes, not a judgment on whether the op was useful.


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def our_index(data):
    names = data["info"]["TeamNames"]
    return 0 if names[0].strip() == "Sarthak Sharma" else 1


def animal_counts(farm):
    counts = {}
    for row in farm["tiles"]:
        for t in row:
            if isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE") and t.get("animal"):
                counts[t["animal"]] = counts.get(t["animal"], 0) + 1
    return counts


def tile_breakdown(farm):
    """Returns (crops, empty, weeds, structs, idle). idle = empty + weeds --
    tiles that are owned, unlocked, and currently producing nothing --
    the direct "are we over-landed" signal: land sitting idle is land
    that was worth its purchase price but isn't earning it back yet."""
    crops, empty, weeds, structs = 0, 0, 0, 0
    for row in farm["tiles"]:
        for t in row:
            if t is None:
                empty += 1
            elif t == "LOCKED":
                continue
            elif isinstance(t, dict) and t.get("kind") == "PLANT":
                crops += 1
            elif isinstance(t, dict) and t.get("kind") == "WEED":
                weeds += 1
            elif isinstance(t, dict) and t.get("kind") in ("COOP", "PASTURE"):
                structs += 1
    return crops, empty, weeds, structs, empty + weeds


def classify_op(op_list):
    if not op_list:
        return "idle"
    op = op_list[0]
    if op in MOVE_OPS:
        return "walking"
    if op in IDLE_OPS:
        return "idle"
    return "working"


def day_action_breakdown(steps, player, day, turns_per_day):
    """Tally working/walking/idle across every unit-turn (farmer + all
    hands, every hour) for one player on one day. Rough by design -- a
    "working" turn might still be a wasted one (e.g. watering a plant
    that didn't need it), this only tells you whether units had *any*
    on-tile task or were purely in transit."""
    counts = {"working": 0, "walking": 0, "idle": 0}
    for h in range(turns_per_day):
        idx = day * turns_per_day + h
        if idx >= len(steps):
            break
        action = steps[idx][player]["action"]
        counts[classify_op(action.get("farmer"))] += 1
        for hand_op in action.get("hands", []):
            counts[classify_op(hand_op)] += 1
    return counts


def our_sells_this_step(action, item):
    total = 0
    for order in action.get("market", []):
        if order and order[0] == "SELL" and order[1] == item:
            total += order[2]
    return total


def main():
    if len(sys.argv) < 2:
        print("usage: python diff_replay.py <replay.json> [--csv out.csv]")
        sys.exit(1)
    path = sys.argv[1]
    csv_path = None
    if "--csv" in sys.argv:
        csv_path = sys.argv[sys.argv.index("--csv") + 1]

    data = load(path)
    us = our_index(data)
    opp = 1 - us
    names = data["info"]["TeamNames"]
    steps = data["steps"]
    turns_per_day = 24

    print(f"Us: {names[us].strip()}  |  Opponent: {names[opp].strip()}  |  seed={data['info'].get('seed')}")
    print()

    csv_rows = []
    prev_inv = None
    our_sells_accum = {p: 0 for p in PRODUCTS}

    num_days = len(steps) // turns_per_day
    for day in range(num_days):
        # accumulate our sells across the whole day (all 24 hours)
        day_our_sells = {p: 0 for p in PRODUCTS}
        for h in range(turns_per_day):
            idx = day * turns_per_day + h
            if idx >= len(steps):
                break
            action = steps[idx][us]["action"]
            for p in PRODUCTS:
                day_our_sells[p] += our_sells_this_step(action, p)

        # sample state at hour 1 (hour 0 is pre-hiring/pre-decision for that day)
        sample_idx = min(day * turns_per_day + 1, len(steps) - 1)
        obs = steps[sample_idx][us]["observation"]
        farms = obs["farms"]
        me, them = farms[us], farms[opp]
        market_inv = obs["market"]["inventory"]
        market_price = obs["market"]["prices"]

        our_animals = animal_counts(me)
        opp_animals = animal_counts(them)
        our_hands = len(me.get("hands", []))
        opp_hands = len(them.get("hands", []))
        our_crops, our_empty, our_weeds, our_structs, our_idle = tile_breakdown(me)
        opp_crops, opp_empty, opp_weeds, opp_structs, opp_idle = tile_breakdown(them)
        our_act = day_action_breakdown(steps, us, day, turns_per_day)
        opp_act = day_action_breakdown(steps, opp, day, turns_per_day)
        our_total_act = sum(our_act.values()) or 1
        opp_total_act = sum(opp_act.values()) or 1
        our_owned = our_crops + our_empty + our_weeds + our_structs

        print(
            f"Day {day:2d} | us: money={me['money']:8.0f} hands={our_hands:2d} "
            f"quad={len(me['unlocked_quadrants'])} crops={our_crops:3d} idle={our_idle:3d}/{our_owned:3d} "
            f"animals={our_animals} act(work/walk/idle)="
            f"{100*our_act['working']/our_total_act:.0f}/{100*our_act['walking']/our_total_act:.0f}/"
            f"{100*our_act['idle']/our_total_act:.0f}% | "
            f"opp: money={them['money']:8.0f} hands={opp_hands:2d} "
            f"quad={len(them['unlocked_quadrants'])} crops={opp_crops:3d} idle={opp_idle:3d} "
            f"animals={opp_animals} act(work/walk/idle)="
            f"{100*opp_act['working']/opp_total_act:.0f}/{100*opp_act['walking']/opp_total_act:.0f}/"
            f"{100*opp_act['idle']/opp_total_act:.0f}%"
        )

        for p in PRODUCTS:
            inv_now = market_inv.get(p, 0)
            row = {
                "day": day,
                "product": p,
                "price": market_price.get(p, 0),
                "market_inventory": inv_now,
                "our_sells_today": day_our_sells[p],
                "our_idle_tiles": our_idle,
                "opp_idle_tiles": opp_idle,
                "our_pct_working": round(100 * our_act["working"] / our_total_act, 1),
                "our_pct_walking": round(100 * our_act["walking"] / our_total_act, 1),
                "opp_pct_working": round(100 * opp_act["working"] / opp_total_act, 1),
                "opp_pct_walking": round(100 * opp_act["walking"] / opp_total_act, 1),
            }
            if prev_inv is not None:
                delta = inv_now - prev_inv.get(p, inv_now)
                row["inventory_delta"] = delta
                row["opp_supply_est"] = delta - day_our_sells[p]
            else:
                row["inventory_delta"] = None
                row["opp_supply_est"] = None
            csv_rows.append(row)

        prev_inv = dict(market_inv)

    # compact per-resource summary: total our_sells vs total opp_supply_est
    print()
    print("=== Season totals per resource ===")
    print(f"{'Product':<12}{'our_sells':>12}{'opp_supply_est':>16}{'end_price':>12}")
    totals = {p: {"our": 0, "opp": 0} for p in PRODUCTS}
    for row in csv_rows:
        totals[row["product"]]["our"] += row["our_sells_today"]
        if row["opp_supply_est"] is not None:
            totals[row["product"]]["opp"] += row["opp_supply_est"]
    last_prices = {row["product"]: row["price"] for row in csv_rows[-len(PRODUCTS):]}
    for p in PRODUCTS:
        print(f"{p:<12}{totals[p]['our']:>12}{totals[p]['opp']:>16}{last_prices.get(p, 0):>12}")

    if csv_path:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"\nWrote {len(csv_rows)} rows to {csv_path}")


if __name__ == "__main__":
    main()
