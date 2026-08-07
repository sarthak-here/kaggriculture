# Kaggriculture — Handoff Document
*Written 2026-08-07. Self-contained — read this instead of re-deriving context.*

## TL;DR

Building an agent for Kaggle's [Kaggriculture](https://www.kaggle.com/competitions/kaggriculture)
simulation competition (turn-based farm economy sim, 720 turns/30 days, head-to-head ladder,
top 10 each win $5,000). Repo: `sarthak-here/kaggriculture` (private GitHub), local at
`C:\Users\sarthak\Desktop\projects\kaggriculture`. Six submissions made so far (v4-v6 successful,
one early one broken). Current live submission (v6) is at ladder rating ~565 (started at 600,
i.e. currently net-negative — see "Where we actually stand" below). **A local uncommitted branch
with several more fixes exists but has NOT been validated as a net improvement — local testing
against the built-in bot has been inconsistent and the debugging session that produced it ran out
of time before reaching a clean conclusion.** That's the main thing to pick back up.

Entry deadline 2026-09-23, final submission 2026-09-30, games continue scoring until ~Oct 15.

---

## 1. Competition rules (condensed)

- Each player manages a `boardSize×boardSize` (default 10×10) farm split into four 5×5 quadrants.
  Only NW is free at start; NE/SW/SE cost $1k/$2k/$4k respectively (`BUY_LAND`, a market order).
- Season = 720 turns = 24 turns/day × 30 days. `actTimeout=1s` per turn, `remainingOverageTime=60s`
  total pool for the whole episode (confirmed from `kaggriculture.json` — this rules out heavy
  per-turn search/MCTS across all 720 turns; only sparse, targeted lookahead could ever fit).
- Each turn: **one action per unit** (main farmer + any hired hands) — movement, plant, water,
  harvest, fertilize, feed, care, collect fertilizer, build, dig, place, pickup, drop. Plus up to
  **`maxMarketOrdersPerTurn=10`** market orders (buy/sell/hire/land) — *extras beyond 10 are
  silently dropped, not queued for later.* This turned out to be a much bigger real constraint
  than it looks (see §5).
- Hired hands cost `fib(n)` where n = hires already made *that day* (1,1,2,3,5,8,13,21,34,55,
  capped there). **Hands vanish at end of day and must be rehired from scratch every morning** —
  hiring only happens meaningfully at hour 0.
- Winner = most money in bank at turn 720. Unsold inventory is worth $0.
- Starting money: **$3000**.

Full mechanical details (watering/feeding deadlines, fertilizer bonus math, town demand growth,
the exact price-curve formula) are in `README.md` inside the installed `kaggle_environments`
package at `.venv/Lib/site-packages/kaggle_environments/envs/kaggriculture/README.md` — read that
directly rather than trusting a second-hand paraphrase for anything subtle.

---

## 2. Full economics reference

All numbers verified from `game_data.py` (which itself was built from the official rules table,
cross-checked against the actual engine source at
`.venv/Lib/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`).

### Crops

| Crop | Kind | Seed cost | Base price | 1st yield | Cycle (max_yield_day) | Yield/tile/day |
|---|---|---|---|---|---|---|
| WHEAT | one-time | $10 | $25 | day 2 | 4 days | 0.80 |
| CARROT | one-time | $20 | $35 | day 2 | 3 days | 0.75 |
| TOMATO | **ongoing** | $50 | $60 | day 8 | repeats every 1d, ×4 max | 0.33 |
| STRAWBERRY | **ongoing** | $100 | $120 | day 10 | repeats every 2d, ×4 max | 0.24 |
| MELON | one-time | $80 | $250 | day 10 | 10 days | 0.55 |

**One-time crops clear their own tile on harvest** (need replanting every cycle). **Ongoing crops
stay on the tile and keep producing on schedule** (just needs watering, no replanting) until they
hit their scheduled-production cap, then decay into a weed.

At the *undiscounted spot price*, profit/tile/day is: WHEAT ~17.5, CARROT ~19.6, TOMATO ~15.3,
STRAWBERRY ~22.5, **MELON ~129.5 — 6-8x every other crop.** This is deliberate on the game
designers' part (see §6, "melon rush").

### Animals

| Animal | Product | Cost | Base price | 1st yield | Interval | Max held | Structure |
|---|---|---|---|---|---|---|---|
| GOOSE | EGG | $300 | $50 | day 4 | 1 day | 4 | COOP |
| COW | MILK | $400 | $160 | day 8 | 2 days | 6 | PASTURE |
| SHEEP | WOOL | $500 | $200 | day 6 | 3 days | 6 | PASTURE |

`BUILD_COOP`/`BUILD_PASTURE` are **free** — a unit action on an empty tile, no market cost.
Feeding costs 1 WHEAT/day per animal, from the *acting unit's own carried inventory* (not the
shed — see §5's PICKUP mechanic). Animals produce **indefinitely** once running, as long as fed.

### Land

Quadrant 2/3/4 cost $1k / $2k / $4k respectively (cumulative, not per-quadrant-type).

### Market price formula

`price(inv) = base ± amp · f(|inv - I0|)`, where `f` is one of `linear/sq/sqrt/log`, different
functions/targets on the scarcity side vs the glut side. **MELON's glut side is `sq` (quadratic)
with `above_target=3.6` — the steepest glut-sensitivity of any resource** — a deliberate nerf on
the otherwise-dominant crop. Full per-resource params are in `game_data.py`'s `MARKET_PARAMS` and
`predicted_price()` replicates the formula exactly (verified to match reality in testing).

### ROI by time horizon — a genuinely important, non-obvious finding

The crop/animal ranking above is for the **full 30-day season**. It is NOT stable across shorter
horizons — this matters a lot for late-game decisions and was verified with real math (not just
theory):

**At 200 steps (~8.3 days) remaining:**
- WHEAT: **+$140** (2 full cycles) — best
- CARROT: +$118 (2 full cycles, slightly worse than wheat because its 3-day cycle doesn't divide
  8.3 days as cleanly)
- MELON: **$0** — doesn't even reach its first harvest (day 10) in this window. Pure sunk cost.
- STRAWBERRY: $0, same problem.
- TOMATO: barely +$10 (1 harvest, right at the boundary)
- **Every animal is a net LOSS**: GOOSE -$250, COW -$440, SHEEP -$500 (high upfront cost, not
  enough time to produce enough to pay it back even with fast-starting GOOSE)

**At 500 steps (~20.8 days) remaining:**
- **MELON: $2,590** — now completely dominant (2 full cycles now fit)
- CARROT $352, WHEAT $350, STRAWBERRY $380, TOMATO $190 — all modest, roughly flat vs the 200-step
  numbers (steady-rate items don't compound faster with more time)
- COW: **+$220** (now profitable — 7 productions clear the $400 + feed cost)
- GOOSE: +$50 (barely — high production count but thin $50/egg margin)
- SHEEP: $0 (breakeven)

**Animals' actual breakeven point is `days_left ≈ 18-19`, not the `days_left=8` cutoff our code
currently uses** (`DAYS_LEFT_TO_STOP_ANIMAL_INVESTMENT = 8` in `main.py`). This is a **known,
unfixed miscalibration** — see §7.

This is symmetric: the same "days remaining" produces the same economics whether that's early
game or approaching the end. `best_crop_to_plant`/`best_animal_to_get` in `main.py` already key
off `days_left` (not calendar day) for eligibility, which is correct in spirit, but
`best_animal_to_get` **never actually checks for positive profit** — it only excludes animals with
`productive_days <= interval*2`, so it will confidently recommend "the least-bad losing
investment" during the whole days_left 9-18 window. This is very likely part of why animal
investment has tested inconsistently (§8).

---

## 3. Architecture

Two files, submitted as `submission.tar.gz` containing both (**never submit `main.py` alone** —
see §5, this broke the very first submission):

- **`game_data.py`** — static constants (crop/animal tables above) + `predicted_price()` (exact
  replica of the engine's price formula) + `sell_quantity()` (chunks sales against the price curve
  instead of dumping everything) + `land_cost()`.
- **`main.py`** — the actual `agent(obs)` function and all decision logic. **Must always be the
  LAST top-level function defined in the file** — `kaggle_environments`' file-path loader
  (`get_last_callable`) grabs the last callable in the file, not one named `agent` by lookup. A
  helper function accidentally defined after `agent()` once silently became "the agent" and
  crashed instantly; this is a load-bearing structural rule, not a style preference.

### Per-unit decision priority (as of the last committed state; the uncommitted branch has
reordered/added to this — see §8)

1. If on an animal tile: harvest ready product → collect fertilizer → feed (if carrying wheat) →
   care
2. Harvest if standing on a ready plant
3. Water if standing on an unwatered plant
4. Shed pickups (wheat for feeding, purchased animals to place) if shed-adjacent
5. Place a carried animal on a matching empty structure
6. Plant / build if standing on an empty tile
7. Dig a weed
8. Otherwise move toward the nearest unclaimed pending task (priority-ordered similarly)

### Per-turn top-level decisions (once per `agent()` call, not per-unit)

- Sell shed inventory (price-curve-chunked, not dumped)
- Land expansion (buy next quadrant once affordable + operating reserve)
- Hiring (fibonacci-cost hands, once/day at hour 0)
- Animal investment (which animal, how many, buy+place)
- Crop selection (ROI-scored `best_crop_to_plant`, buys 1 seed/turn)

### Key mechanical details worth knowing before touching this again

- **`FEED` and `PLACE` consume from the ACTING UNIT'S OWN carried inventory, not the shed** —
  verified directly from engine source. So using an animal or feeding it is a genuine multi-turn
  logistics chain: `PICKUP` from shed → walk → `FEED`/`PLACE`. This is NOT optional — a naive
  "just feed the animal" attempt silently no-ops if the unit isn't carrying wheat.
- Movement has no obstacles — locked (unbought) quadrant tiles are passable, just not actionable.
  So "pathing" is trivial (`step_toward`: reduce whichever of dx/dy is larger), no real routing
  algorithm needed.
- The shed sits at the board's exact center (4 tiles: `(half-1,half-1)`, `(half,half-1)`,
  `(half-1,half)`, `(half,half)` for `half = boardSize//2`); it is never itself in the `tiles`
  array.

---

## 4. Local testing methodology

```bash
# ALWAYS use a fixed seed for before/after comparisons — unseeded runs showed
# 37k-44k swings from RNG alone, making comparisons meaningless without one.
./.venv/Scripts/python.exe -c "
from kaggle_environments import make
env = make('kaggriculture', configuration={'episodeSteps': 720, 'seed': 1}, debug=True)
env.run(['main.py', 'starter'])   # 'starter' is the built-in deterministic baseline bot
final = env.steps[-1]
print([(i, s.reward, s.status) for i, s in enumerate(final)])
"
```

Standard test matrix used throughout: **seeds 1, 2, 3**, always vs `'starter'` (the built-in
non-trivial bot; `'random'` is too weak to be informative once past the earliest iterations).
Always check `status` for errors across the whole episode, not just the final reward.

**Known limitation, discovered late in this session and not fully resolved**: local testing
against `starter` may not be a reliable proxy for whether a change helps against *real* ladder
opponents. Several changes that were well-motivated by real match replay diagnosis (see §6) tested
inconsistently or negatively against `starter` locally. It's unclear whether this means the
changes were actually bad, or whether `starter` just doesn't stress the same things real
competitors do (it doesn't seem to compete aggressively for market share or build large animal
operations, for instance). This tension was never resolved — see §8.

Submitting:
```bash
tar -czf submission.tar.gz main.py game_data.py
kaggle competitions submit kaggriculture -f submission.tar.gz -m "description"
```
**Always ask the user before actually running the submit command** — it's rate-limited (5/day,
only latest 2 tracked for matchmaking) and the user has explicitly asked to be consulted every
time, even mid-session after an earlier approval.

Checking real match results:
```bash
kaggle competitions submissions kaggriculture         # see all submissions + current rating
kaggle competitions episodes <submission_id>           # list real (PUBLIC) vs VALIDATION episodes
kaggle competitions replay <episode_id> -p ./replays    # download full replay JSON
```
Replay JSON structure: `data['info']['TeamNames']` (list of 2 names, figure out which index is us
by matching `'Sarthak Sharma'`), `data['steps']` (720 entries, each a 2-element list of per-player
`{observation, reward, status}` — same shape as local `env.steps`). This is how every real-match
bug in §6 was found: sample `farms[idx]` at `day*24 + 1` or `+2` (not `+0` — hour 0 observations
are *before* that day's hiring/decisions take effect, a sampling trap that wasted real time twice
in this session) across several days and diff our trajectory against the opponent's.

---

## 5. What we tried, roughly chronologically

**v1** (single farmer, ROI-scored crop choice, never misses water/harvest): beat `random` 27447-0,
beat `starter` 27349-3508.

**v2** (multi-unit/hired hands, land expansion, hiring): found and fixed a real bug along the way
— `best_crop_to_plant()` was recomputed fresh every turn, so if the "best" pick flickered between
buying a seed and reaching an empty tile to plant it (prices shift slightly after our own sells),
a *new* seed got bought instead of using the one already held, silently stranding money. Fixed by
always planting whatever's already in inventory before buying anything new. Result: 32456-0 vs
random, 36809-3516 vs starter (up from v1).

**v3** (animals): implemented the full BUY→PICKUP→walk→PLACE / daily PICKUP-wheat→walk→FEED
logistics chain. Found the file-loading-order bug described in §3 while debugging what looked like
a nonsensical crash. Result: 44540-0 vs random, 42430-3499 vs starter.

**Price-aware selling + animal double-buy fix**: replaced "dump the whole shed every turn" with
`sell_quantity()` chunking. Also found the BUY_ANIMAL gate only checked shed count, not an animal
already picked up and mid-transit in a unit's inventory (which takes several turns to walk) — kept
re-buying a fresh one every turn along the way; found 4 unplaced COWs + 1 GOOSE wasted in the shed
at game end before the fix. Switched to fixed-seed testing here after realizing unseeded
comparisons were unreliable. Result: stable ~37300 vs ~3500 across 3 seeds (this dip from v3's
42430 was later understood to be the *real*, non-lucky-RNG baseline — the earlier unseeded numbers
had been outliers).

**Endgame liquidation refinement**: stop feeding/buying wheat for animals that can't produce again
before season end. No measurable local score change (narrow effect window) but strictly no-risk.

**First real submission** (2026-08-07): learned the hard way that `main.py` alone errors — it
imports `game_data.py`, which wasn't bundled. Always use `submission.tar.gz` with both files.

**Real match #1** (v4, episode 90596561): **lost 24763 vs 80682** to a real player. Diagnosed via
replay: opponent bought all 4 land quadrants by ~day 10 despite very little cash margin; we
crawled to 3 quadrants and never bought the 4th (our own `DAYS_LEFT_TO_STOP_EXPANDING` cutoff had
already kicked in by the time we might have been ready, because our `utilization > 0.8` +
2x-cash-buffer gate only ever expanded *reactively*, after already being tile-constrained). **Fix
(v5)**: buy the next quadrant as soon as affordable (1.3x buffer, no utilization requirement).
Local result: 49509/43158/41553 across 3 seeds (up from ~37300), all 4 quadrants bought every
time.

**Real match #2** (v5, episode 90598933): **lost 5617 vs 60895** — a much bigger gap than land
alone explains. Diagnosed: money pinned near $0 for 10+ days straight (day 2 to day 22). Root
cause: the agent plants every affordable empty tile on sight, and melon (best-ROI by far) takes 10
days to first yield — a fast start dumps most of the starting $3000 into ~20 melon seeds within 2
days, and the new aggressive land-buying then competed for the same scarce cash in that same
window, with zero operating cushion left to hire, fertilize, or recover from bad luck. **Fix**:
`MIN_OPERATING_CASH_RESERVE = $400` that `BUY_LAND` must leave untouched on top of the land cost
itself. No local regression.

**Real match #3** (v5, episode 90598134, another loss): opponent finished with 9 SHEEP + 5 COW (14
animals) vs our 3 COW, *despite them holding less land than us*. Diagnosed two compounding causes:
(1) `MIN_CASH_BUFFER_FOR_ANIMALS` was a flat $5000 gate before even considering an animal —
10-15x what one actually costs; (2) `best_animal_to_get()` added a phantom "+200 structure cost"
to every animal's total cost, when `BUILD_COOP`/`BUILD_PASTURE` are actually free (verified from
engine source). Both fixed. Local result: 56397/57804/57001 (up another 14-33%), 2-3 COW
established early. **This is the last cleanly-validated, committed-and-submitted state (v6).**

**Tried and reverted**: discounting crop ROI by predicted future price impact (to avoid a
self-inflicted "melon rush" price crash from planting too much melon). Tested net-negative locally
(melon's price never actually crashed in practice against `starter`, because `sell_quantity`
already throttles real selling pressure and town consumption keeps draining inventory) — the
pre-emptive discount was more pessimistic than reality and left real value on the table by
diversifying away from melon too early. Reverted; documented in `main.py`'s docstring so it isn't
retried blindly.

---

## 6. Real-match diagnostic findings (concrete, evidenced bugs — all confirmed via replay data,
not guessed)

1. **Seed-purchase stranding** (v2) — buy-vs-hold-seed race condition, fixed.
2. **Multi-unit seed collision** — two units both planting the same under-stocked seed type in one
   turn get NONE planted (engine behavior); fixed via a shared per-turn seed budget.
3. **File-loading order bug** (§3) — `agent()` must be the last top-level function.
4. **Animal double-buy waste** — BUY_ANIMAL gate needs to check shed + in-transit inventory, not
   just shed.
5. **Land expansion badly too conservative** — fixed (v5).
6. **Land+melon opening liquidity crisis** — fixed via cash reserve (v5).
7. **Animal investment threshold 10-15x too high + phantom structure cost** — fixed (v6).
8. **Melon rush confirmed as our own agent's default behavior**, not just an organizer anecdote —
   our own ROI formula scores melon 6-8x every other crop at spot price.

---

## 7. Known, confirmed, NOT YET FIXED issues

- **`best_animal_to_get()` never checks for positive profit.** It only excludes animals where
  `productive_days <= interval*2`. Verified via direct calculation (§2) that all three animals are
  net-negative investments until `days_left ≈ 18-19`, yet `DAYS_LEFT_TO_STOP_ANIMAL_INVESTMENT = 8`
  allows investment starting at `days_left=9` — a whole window (9-18 days left) where the function
  confidently recommends a losing investment. This was found in the final minutes of this session
  and not yet fixed. **This is probably the single highest-value next fix** — it's simple, well
  evidenced by real math, and plausibly explains a lot of the inconsistent animal-investment
  results in §8.
- The feed-cost estimate used throughout (`~$25/day` flat) is a rough approximation of wheat's
  market price, not dynamically pulled from `market_prices` in every calculation — worth
  double-checking `best_animal_to_get`'s actual implementation uses the real live price (it does,
  via `market_prices.get("WHEAT", ...)` — the $25 approximation above is only in this document's
  quick recalculation, not in the shipped code).

---

## 8. Unresolved — the messy end-of-session debugging thread

Motivated by real match #3-adjacent data (an opponent who got to 20 animals by day 16 on *minimal*
land and won decisively), attempted to parallelize animal investment (previously only ever pursued
ONE new animal at a time, regardless of cash/workers available — a real, confirmed bottleneck).
This spiraled into a long chain of interacting bugs, each individually real and fixed, but the
*combined* local test result never cleanly beat the v6 baseline:

1. Parallelizing animal investment alone: mixed local results (2 of 3 seeds worse).
2. Found: uncapped new-animal demand recalculates every turn from available cash and never stops
   wanting more, and since one-time crops (melon) free their own tile on harvest, freed tiles got
   routed to animal-building ahead of replanting — **cannibalized the entire crop operation over
   time** (melon count 22→17→8→0 across days 12-24 in one seed). Fixed with a land-fraction cap on
   total animals (`MAX_ANIMAL_LAND_FRACTION = 0.4`) — didn't fully fix it alone.
3. Found: reordering `BUY_SEED` ahead of `BUY_ANIMAL` in the market list had **zero effect** —
   money-order-priority wasn't the mechanism.
4. Found the real mechanism: animal-placement *logistics* (multi-turn PICKUP→walk→PLACE cycles for
   many simultaneously-pending structures) ranked *above* crop-planting in the per-unit priority
   list, so a large backlog of pending structures could keep every unit perpetually busy on animal
   shuttling and never get back to crops — a worker-attention bottleneck, not a cash one. Reordered
   planting above animal-placement.
5. User directly observed two more real issues from watching gameplay: (a) weeds not being cleared
   (they ranked dead last in priority, even behind the animal-care bonus, so in the late game they
   never got attention and permanently ate into usable land); (b) animal structures placed
   "randomly" far from the shed instead of near it, making the *daily* feeding round-trip
   expensive for the rest of the season. Both fixed (weed priority raised; structure-building now
   targets the empty tile nearest the shed, not nearest the acting unit).
6. User also flagged a third issue independently: tile selection had a systematic directional bias
   (Python's `min()` breaks Manhattan-distance ties by picking whichever candidate appears first
   in row-major iteration order, favoring low-x/low-y). Fixed by switching to squared Euclidean
   distance as the sort key (ties far less often on a grid).
7. Despite all of the above being individually well-reasoned and evidenced, discovered **hiring
   was structurally starved**: `SELL` orders (one per distinct shed product, often 6-9 with a
   diverse economy) were consuming most of the shared 10-market-orders-per-turn budget before
   `HIRE` was ever reached, capping total hands around 6-8 despite land size wanting far more.
8. Attempted fix #1 (`MAX_NEW_HIRES_PER_TURN = 4`) was itself a bug: hiring only happens once/day
   (hour 0) and hands don't carry over between days, so a flat "per turn" cap is actually a flat
   *per-day* cap on total headcount — this made things measurably worse (confirmed: capped a
   100-tile farm at exactly 5 total units the whole game).
9. Removed that cap, relied on the shared order-budget check alone with land/seed reserving 2
   slots — still capped around 6-7 hands, still not much room.
10. **Realized the actual hard ceiling**: `maxMarketOrdersPerTurn=10` caps hiring at a maximum of
    **10 new hands EVER reachable in a single day**, full stop — i.e. **11 total units (1 farmer +
    10 hands) is the true maximum achievable**, regardless of land size. The formula-based target
    (`num_owned_tiles // 4 - 1` = 24 for a 100-tile farm) was never physically reachable in the
    first place. Recalibrated to try to get as close to the real ~10-hand ceiling as possible by
    minimizing what `SELL` consumes on the hiring turn specifically (deferring low-priority sales
    by one turn costs almost nothing; under-hiring costs the whole rest of the day).
11. Even after all of this, **local score vs `starter` across 3 seeds was still below the v6
    baseline** ($31k/$40k/$43k vs v6's $56k/$58k/$57k) — though seed 3 specifically improved a lot
    (from as low as $28k mid-debugging up to $43k), suggesting real progress mixed with real
    remaining problems, not a uniformly wrong direction.

**This was never resolved.** The uncommitted `main.py` at end of session contains all of steps
1-10's fixes plus the confirmed-good weed/shed-placement/directional-bias fixes, but has NOT been
validated as a net improvement and has NOT been committed or submitted. The last user message
before ending the session was asking about the `best_animal_to_get` profitability-checking gap in
§7, which was never actually implemented.

### Recommended next steps, in priority order

1. **Fix `best_animal_to_get` to require positive profit** (§7) — cheap, well-evidenced, likely
   high-value, and completely independent of the tangled mess in this section. Do this first, in
   isolation, and test it alone against the v6 baseline before touching anything else.
2. **Isolate variables properly.** The debugging session in §8 stacked ~10 changes without testing
   most of them individually. At minimum, test these three in isolation (they're independently
   confirmed correct by direct user observation, not just theory): weed-priority reorder,
   near-shed structure placement, directional-bias fix. Get a clean read on whether *those three
   alone*, on top of the v6 baseline, beat v6 — before reintroducing the animal-parallelization and
   hiring-reallocation changes.
3. **Reconsider whether local testing against `starter` is even the right tool** for validating
   animal-investment strategy specifically. It may be that `starter` doesn't compete for market
   share or build large animal operations the way real ladder opponents do, making it a poor proxy
   for this specific question. If isolated local testing keeps giving ambiguous signal, it may be
   more efficient to submit a well-reasoned (not necessarily locally-dominant) change and read the
   real match replay data instead of continuing to iterate blindly against a weak bot.
4. Only after 1-3 are resolved: revisit animal-count parallelization with the corrected
   profitability gate from step 1 already in place (a lot of §8's inconsistency may partly stem
   from investing during the loss window described in §7, which step 1 would eliminate on its
   own).
5. Task #14 from the original plan (shallow lookahead within the 1s/turn + 60s overage budget) is
   still untouched and lower priority than the above — the ROI-driven core has more low-hanging
   fruit left via real-match diagnosis than search would currently add.
