# Experiment log

Every score below is a **local head-to-head**, fixed `configuration={'seed': N}`,
run with `env.run([agent_a, agent_b])`. Kaggle ladder ratings are noted separately.

## Measurement standard (established 2026-08-08 — read this first)

Earlier versions were compared on 3-5 seeds. **That was not enough to conclude
anything.** Measured noise floor, from 40 matches of v10 against a *byte-identical
copy of itself*:

| statistic | value |
|---|---|
| per-match diff sd | **5,181** |
| single-match range | **-15,870 .. +12,524** |
| mean diff over 40 paired matches | -765 |

So a single seed can swing ±16k on **no difference at all**, but 40 paired matches
resolve a mean to about ±1.6k (2 SE).

**Standard going forward:**
1. 20 seeds x both slot orders = 40 matches, paired across arms.
2. Score by **head-to-head win rate**, not mean money.
3. Prefer **mechanism metrics** (missed feeds, water deaths, PASS turns, harvest
   lag) — under a scheduled agent these are near-deterministic while final money
   is not, so they carry far more statistical power per match.

**Retroactively downgraded by this standard:** `ed8d10c`'s "beat v6 on 2/3 seeds"
was noise, not weak signal. The `MAX_TOTAL_ANIMALS` 12-vs-16 choice was also made
on within-noise margins and is worth re-running.

### Known nondeterminism (unfixed)

The agent is **not deterministic across processes**. Same seed, byte-identical
agents, varying only `PYTHONHASHSEED`:

```
PYTHONHASHSEED=0 -> 85,989    =1 -> 83,884    =2 -> 84,910
```

Cause: `main.py:187` and `main.py:227` iterate `flush_items` / `SELLABLE_PRODUCTS`,
which are **sets of strings**, and `return` on the first match. Python randomizes
string-set iteration order per process, so which product a unit flushes first is a
hash accident. Fixing it (iterate a sorted or explicit priority order) would both
shrink the measured noise floor and make flush order a deliberate choice.

## Version history

| tag | commit | what changed | ladder rating |
|---|---|---|---|
| v1 | `f5e7571` | single-farmer baseline, ROI-scored crops | — |
| v2 | `accc75e` | hired hands, land expansion | — |
| v3 | `10981c2` | animals, feed/care/harvest, fertilizer | — |
| v8 | `a93e7a6` | rebuilt around care-bonus economics | 595.1 -> 625.8 -> 592.8 -> 614.9 |
| v8.1 | `726a9a3` | honest animal ROI, haul-home, land gate | not submitted |
| v8.2 | `2d64c0e` | stop stranding wheat in liquidation | not submitted |
| v9 | `f4a5d92` | premium hold window (**regression**), fert priority | not submitted |
| v10 | `ea4b9aa` | schedule-driven capital plan | **current best, not yet submitted** |

v9 lost to v8 by ~10-30k: the day 16-23 hold window starved payroll (cash hit $3,
hiring broke, animals escaped). v10 deletes the hold window entirely.

## 2026-08-08 experiments

### 1. Two-tier watering priority — FALSIFIED (mechanism worked, score didn't)

Engine facts confirmed at source: `_new_plant` starts `consecutive_unwatered=1`;
rollover increments then kills at `>=2`. So a plant at cu>=1 unwatered at rollover
dies that night, and **a fresh seed must be watered on its planting day**.

Split `needs_water` into a critical tier ranked above harvest.

| metric | patched | v10 baseline |
|---|---|---|
| mid-game (pre-d25) water deaths, 5 seeds | **31** | 55 |
| mean score | 79,711 | 80,897 |

Mid-game water deaths fell 44% — **and score did not improve.** Swept an
`hour >= CRITICAL_WATER_HOUR` gate (6/12/16); all three lost on the mean
(76.2k / 83.4k / 77.6k vs 78.1k / 83.9k / 78.0k). Reverted.

### 2. Weed attribution — the weed thread is closed

Every new weed classified by its predecessor tile state, per game:

| cause | count | verdict |
|---|---|---|
| end-of-life (ongoing crop after final production) | **16-25** | unavoidable by design |
| 2-day unwatered death | 10-17 | real, but not score-relevant at current labour |
| random spawn (`weedSpawnChance=0.005`) | 1-4 | unavoidable |
| one-time crop never harvested | **0** | that path is clean |

Most weeds are the strawberry lifecycle working as intended. Harvesting a one-time
crop clears the tile to `None` (no weed), which is why that row is zero.

### 3. Hand-cap sweep — FALSIFIED, 0 wins in 60 matches

Hypothesis: the 14-hand freeze was an unmeasured eyeball call, and hands 15-18
(fib $610-2584) might pay for themselves. Arms raise `FULL_HANDS_CAP` with
`MAX_MARGINAL_HIRE_COST` raised to match.

| arm | n | win rate | mean diff vs 14 | median | sd |
|---|---|---|---|---|---|
| 14 (control, identical agents) | 40 | 40% | -765 | -340 | 5,181 |
| **16** (cap 1100) | 40 | **0%** | **-26,103** | -26,045 | 5,683 |
| **18** (cap 2600) | 10 | **0%** | **-66,389** | -67,308 | 5,378 |
| **20** (cap 6800) | 10 | **0%** | **-75,158** | -72,800 | 6,635 |

Money milestones (mean, arm vs baseline):

| arm | d15 | d20 | d25 |
|---|---|---|---|
| 16 | **350** vs 6,680 | 9,309 vs 23,412 | 35,869 vs 56,525 |
| 18 | 41 vs 6,630 | 1,553 vs 24,731 | 11,358 vs 60,139 |
| 20 | 40 vs 6,681 | 826 vs 24,390 | 768 vs 57,310 |

**Root cause: the engine wipes `hands` to `[]` on every day rollover, so every hand
is re-hired every morning — the fib hire cost is DAILY RECURRING, not a one-time
purchase.** Hand #18 at $2,584/day is ~$59k across days 7-29. `MAX_MARGINAL_HIRE_COST
= 400` is load-bearing: it marks where the fib curve outruns marginal productivity.
Price any future "buy more labour" idea as `cost x remaining days`.

Mechanism metrics are the interesting part — extra hands **did** improve what they
should (arm 18: missed feeds 26.2 -> 20.2, water deaths 14.6 -> 13.4) but
`pass_turns` **rose** (505 -> 520 at arm 16, 523 -> 544 at arm 18): the marginal
hands idle.

**This retracts the earlier "unit-turns are the binding constraint" conclusion.**
Baseline already idles ~505 unit-turns/game (~5% of ~10,150), and adding units
increases idle time. Labour is not binding at the margin — **cash during the day
7-15 ramp is**, which is exactly when land + herd + seeds must all be funded.

### 4. Fixed-trace replay agent — 100% win rate, PROVENANCE UNRESOLVED

A single-file agent (stdlib only, no `game_data`) that replays a compressed
719-step recorded action sequence, with runtime logic limited to weed repair,
sell-order ranking, and a terminal liquidation overlay.

**Not committed. Not submitted. See the caveat below before touching it.**

| | trace | v10 |
|---|---|---|
| mean | **150,877** | 71,537 |
| mean diff | **+79,339** (sd 5,072) | |
| win rate | **40/40 = 100%** | |
| best game | **176,677** (seed 1024, slot 0) | |

Per-seed (trace / v10, slot 0 and slot 1):

| seed | slot 0 | slot 1 |
|---|---|---|
| 1 | 163,606 / 80,717 | 157,040 / 73,900 |
| 7 | 138,728 / 67,601 | 145,417 / 72,059 |
| 42 | 146,862 / 73,538 | 153,461 / 74,202 |
| 99 | 137,719 / 61,235 | 125,198 / 47,387 |
| 123 | 151,332 / 67,820 | 151,300 / 67,831 |
| 256 | 119,979 / 41,438 | 140,740 / 58,087 |
| 404 | 157,406 / 76,158 | 163,204 / 85,971 |
| 512 | 150,634 / 68,799 | 151,342 / 64,775 |
| 777 | 119,284 / 48,260 | 152,500 / 73,739 |
| 1024 | **176,677** / 84,308 | 156,701 / 82,844 |
| 1337 | 153,097 / 68,463 | 153,594 / 68,979 |
| 2024 | 131,095 / 51,698 | 145,179 / 67,655 |
| 3141 | 152,209 / 72,974 | 150,298 / 66,781 |
| 4242 | 153,250 / 70,341 | 159,346 / 85,151 |
| 5150 | 162,942 / 76,820 | 155,218 / 77,118 |
| 6502 | 163,164 / 94,454 | 161,002 / 87,236 |
| 8080 | 154,141 / 79,474 | 140,060 / 58,845 |
| 9001 | 174,619 / 93,475 | 171,429 / 85,868 |
| 12345 | 142,565 / 58,522 | 145,918 / 66,829 |
| 31337 | 160,084 / 86,058 | 146,728 / 74,082 |

Why a fixed trace survives at all: your farm is private and evolves
deterministically from your own actions. The only things that can derail a replay
are weed RNG (0.5%/day, patched) and market-price drift — and price drift changes
revenue, not whether a farm action lands.

**Two findings about the code itself:**

1. **The route selector is dead code.** It picks `premium_control` when
   `MELON >= 200 or STRAWBERRY >= 150`. The market always starts at equilibrium
   (all inventories 10000 -> MELON exactly 250, STRAWBERRY 120), so the condition
   is true in every episode and `_ROUTE` latches at step 0. The `v22_base` route
   never runs. The "guarded hybrid of two routes" is one route plus ~20KB of dead
   code.
2. A desync metric based on submitted-action PASS-rate is **useless** here — a
   fixed trace submits identical actions every game (0.068 in all 40 matches).
   Measuring desync requires engine-side no-op instrumentation.

> **BLOCKER — do not submit until resolved.** This agent replays a recorded game,
> and 150k exceeds the ~$117-122k the mined reference replays scored. If that trace
> was recorded from another competitor's replay rather than from our own agent,
> submitting it presents their play as our submission. Resolve provenance before
> this goes anywhere near the ladder.

### 5. v11 — four microscope fixes + opening cash reserve (SHIPPED)

Five changes, 30 paired matches (15 seeds x both slot orders) vs pristine v10:

1. **Wheat fill.** The seed block ordered exactly ONE crop per turn, so a
   strawberry/melon wave left every remaining tile bare until the wave finished.
   Added a second `BUY_SEED WHEAT` line for leftover plantable tiles, capped at
   `WHEAT_FILL_RESERVE_TILES = 7`.
2. **Wheat money reserved first.** The fix above did nothing on its own: melon
   spent down to the operating floor, leaving `(308-300)//10 = 0` affordable
   wheat. Now the wheat allowance is held back *before* the premium pick.
3. **Opening cash reserve.** `MIN_OPERATING_CASH_RESERVE = 300` was pricing us
   out of ~4 premium seeds on day 0. Days 0-1 now use
   `OPENING_CASH_RESERVE = 50`, scoped to the seed section only (animal
   investment still stops at $300, which is what frees the cash for seeds).
4. **Planting priority** above weeds and fertilizer while `day <= 13`.
5. **Buildout priority** (build sites) above watering while unhoused animals
   exist and `day <= 13`; **fertilizer** moved above weeds.

| metric | target | v11 | v10 | mean delta | 2SE | improved |
|---|---|---|---|---|---|---|
| wheat_by_d2 | 7 | **7.00** | **0.00** | +7.00 | +-0.00 | 30/30 |
| money_d15 | >=15000 | 7,855 | 6,385 | **+1,470** | +-867 | 21/30 |
| straw_fert_cov | >=0.70 | 0.50 | 0.46 | **+0.05** | +-0.02 | 26/30 |
| animals_d12 | 14 | 12.87 | 12.47 | +0.40 | +-0.29 | 14/30 |
| seed_residence_d | <=1 | 2.02 | 1.99 | +0.04 | — | — |
| **final score** | — | 83,184 | 82,727 | +457 | **+-2,685** | 17/30 (57%) |

**v10 planted literally zero wheat by day 2** — the bug was real and total.
Mechanism metrics improve significantly; **final score remains within noise**,
which is expected at n=30 and is why the gate was mechanism-based.

**A hypothesis that was tested and died.** After the first pass (wheat fill alone,
which measured money_d15 *down* $1,551) the theory was that filling idle tiles
with wheat displaces melon, and since the ramp is cash-constrained, wheat is the
lower-value use of both the tile and the dollar. The counter-evidence was WH's
revealed preference: he buys 12 melon AND 7 wheat on day 0, running down to ~$50,
because his turn-1 feed wheat *is* his operating buffer. Exempting days 0-1 from
the reserve reproduced that, and money_d15 flipped from -1,551 to **+1,470**. It
was never wheat-vs-melon; it was our own reserve protecting against a problem the
opening already solves. **Two knobs looked like one trade-off; they weren't.**

Two metric definitions were also wrong and were corrected: `wheat_d3` ("standing
at end of day 3") is structurally ~0 for any agent, since wheat is `one_time` with
`first_yield_day: 2` and harvest clears the tile — replaced with
cumulative-planted-by-end-of-d2. And `money_d15 >= 15000` is a WH benchmark, not a
bar v10 could clear (v10 sits at 6,385).

### 6. Trace-extraction campaign — 8 rejections, and what they cost to learn

Baseline for all of these is v11 (`a981d69`). 30 paired matches each (15 seeds x
both slot orders) unless noted. **Every one of these was reverted** — the repo is
at v11. Do not re-run them; read the "died at" column first.

| # | change | verdict | died at |
|---|---|---|---|
| 1 | two-tier watering priority | rejected | mechanism worked (-44% water deaths), score flat |
| 2 | `FULL_HANDS_CAP` 16 / 18 / 20 | rejected | **0/60**, `money_d15` collapse |
| 3 | **v11 — 5 fixes** | **SHIPPED** | mechanism +, score within noise |
| 4 | `MELON_LAST_PLANT_DAY` 13->17 | rejected | **inert** — constraint wasn't binding |
| 5 | per-crop seed gate (drip planting) | rejected | 37%, `money_d15` -2,902 (2SE +-524) |
| 6 | premium sell chunk cap ~7 | rejected | **its own mechanism metric** — prices fell |
| 7 | opponent-aware sell ordering | rejected | **the engine has no such mechanism** |
| 8 | feed-buy tightening | rejected | **0/30**, missed feeds 37 -> 71 |
| 8b | liquidation-only feed variant | neutral | real but worth ~$276 (buy/sell round-trip) |
| 9 | week-one fertilizer sell mode | rejected | `money_d15` -1,678 (3.4 SE) |

**#9 detail — the diagnosis was right and the fix still lost.** `FERT_SELL_ONLY_UNTIL_DAY
= 8`: carriers route to the shed, `FERTILIZE` gated off, so collected fertilizer is
sold instead of applied. **Mechanism landed perfectly** — fert units 174 -> 243,
revenue **+$5,839**, hitting the trace's exact 4/day rate from d3. Died at
`money_d15`: **-$1,678 at 3.4 SE**, score -694 (2SE +-2,574).

Root cause: **"week one hands are idle" was the load-bearing assumption and it is
false.** Week one is exactly when buildout happens — structures going up, Q1 being
planted, herd being placed — so diverting fert carriers to the shed spends the very
turns that were building the farm. The constraint law bit in the one window claimed
to be exempt from it. Secondary cost: gating `FERTILIZE` off also stopped
fertilizing **wheat**, a ~600-unit revenue line, not just the melons argued to be
worthless.

**The diagnosis that survives, and it is solid:** the trace's days 2-6 revenue is
**100% fertilizer**, flat at **4 units/day at ~$98** (one per animal per day) —
$396/$392/$389 on d2/d3/d4 against our $99/$98/$97. Wheat is spiky (a 40-unit spike
on d5) and is NOT the mechanism. The fix was aimed at the wrong half twice:
**collection was never the bottleneck** (v11 already collects 4-7/day), and neither
was the shed pickup — the fertilizer goes **animal -> unit inventory -> straight onto
a crop**, never touching the shed at all.

**#4 detail:** `MELON.planted` was 15.0 in both arms — bit-identical. The window
was never the constraint; the seed picker was (see #5).

**#6 detail:** chunks fell 16.2 -> 6.1 as instructed and realized prices went
DOWN. `sell_quantity` already walks the real price curve and stops at the price
floor; a constant cap can only block sales the curve judged safe, and in a shared
market the deferred units get sold later, after the opponent has moved inventory.

**#7 detail — an engine truth worth keeping:** the market is a **per-unit lockstep
loop across both players**, with the engine's own comment `# Both players see the
same pre-commit inventory for this unit.` **There is no within-turn first-mover
advantage, by construction.** Sell-ordering strategies cannot work here at any
gating. Cross-turn timing (selling on turn N vs N+40) IS a real mechanism and
remains untested.

**#8 detail — the most counter-intuitive result:** v11 buys ~782 wheat / $38k over
d10-29 against a real need of ~280 (measured: 39 wheat bought on one day for 14
animals). Tightening it to the exact deficit saved $30.6k of wheat and **lost
$22.8k of score, 0/30 seeds, missed feeds 37 -> 71 (worse in 30/30)**. Surplus
wheat is *insurance that feeds land*; a forfeited care bonus costs ~$1,500. The
trace's low feed spend comes from shed-ring structures and short round trips, not
from smarter buying.

#### Three constants that are load-bearing — treat as correct unless disproven

1. `MAX_MARGINAL_HIRE_COST = 400` — raising it is catastrophic (#2). Hire cost is
   DAILY RECURRING (`hands` is wiped every rollover), so price any hire as
   `cost x remaining days`.
2. `sell_quantity`'s curve walk — beat a hand-written chunk cap (#6).
3. Feed over-buying against the whole herd from shed stock alone — beat exact-
   deficit buying by $22.8k (#8).

**The prior this sets:** seven of eight changes assumed slack that wasn't there,
all in the same direction. The burden of proof on "this constant is obviously
suboptimal" is now high.

#### The reference trace agent is partly dead code

Two of its three closed-loop layers do nothing: the route selector always returns
`premium_control` (the market always opens at equilibrium, so `MELON >= 200` is
always true), and `_front_run_market` targets the non-existent within-turn
ordering advantage. Its ~$150k comes from fewer mechanisms than its file implies.

#### What the gap is NOT (all measured, all ruled out)

Realized price (~$12/unit, not $100) · the hold window (we hold MORE — 100% of
strawberry sold after d20 vs its 86%) · sell ordering (impossible) · feed
purchasing (insurance) · labour supply (idle at the margin) · opening buys (both
farms are broke through d6) · land utilisation (our farm is not emptier — see the
day-29 replay).

### NEXT SESSION STARTS HERE: the days 2-6 revenue divergence

The only organ left, and it sits upstream of the `money_d15` metric that killed
four experiments. From the per-day ledger (6 seeds, trace vs v11):

| day | trace revenue | v11 revenue | trace money@h0 | v11 money@h0 |
|---|---|---|---|---|
| 2 | 396 | 99 | 21 | 11 |
| 3 | 392 | 98 | 85 | 9 |
| 4 | 389 | 97 | 442 | 4 |
| 5 | 1,902 | 192 | 162 | 0 |
| 6 | 1,590 | 350 | 1,024 | 24 |
| 11 | 9,644 | 10,952 | **7,259** | **99** |

Both farms spend near-identically on day 0 and are equally broke d1-6, so **the
divergence is revenue-side, roughly 4x, and it compounds into a 73x cash gap by
d11.** Nothing tested this session touches it.

**The question:** what is the trace selling on days 2-6? Measure per-day, days
0-7: units sold by product, realized price, and what physically produced them.

**Pre-registered candidates:**
1. **Fertilizer collection cadence.** 4 animals from day 0 produce 1
   fertilizer/animal/day, sellable at ~$94 early — potentially ~$375/day from
   day 1 if collected daily. **This is the leading candidate**, and notably it's
   a routing fix in the one window where the constraint law does NOT bite:
   early-game hands have nothing else to do.
2. **Wheat cycle.** It plants ~10 wheat on day 0 vs our 7 and may harvest on a
   tighter cycle (wheat is `first_yield_day: 2`, `one_time`, tile clears on
   harvest).
3. **Wool timing.** Its first wool lands ~day 6, milk ~day 8.

Melon is NOT a candidate — it can't yield before day 10.

### 10-13. Wheat fetching, v13, the engine upgrade, and the Seb package

| # | change | verdict | died at |
|---|---|---|---|
| 10 | wheat fetch before animal visits, unbounded | rejected | feed spend **+$17,147**, 1/30 |
| 10b | + one fetcher per unfed animal | rejected | feed spend +$11,729, 5/30 |
| 10c | **+ `day <= 9` gate** | **SHIPPED as v12** | 20/30, +2,806 |
| 11 | **v13: deterministic value-ordered flush** | **SHIPPED, submitted** | — |
| 12 | land d4/d6/d10 + Q4 | rejected | `money_d15` **-3,076**, 6/40 |
| 13 | inventory-keyed herd sizing | neutral | 20/40, +254 (2SE +-1,820) |

**#10 — the defect was real and the fix needed two bounds, both found by measurement.**
`feed_only` excludes only tiles whose SOLE need is feed, so a **feed+care** tile still
pulled a wheat-less unit: care done, unit leaves, second trip for the feed. Measured
**5,705 animal-tile visits against the reference agent's 3,288** on the same herd. But
**wheat circulation is coupled to wheat spending** through the stateless feed top-up that
#8 proved cannot be tightened, so every extra pickup drains the shed and triggers a
re-buy. Benefit and cost are separated in time — the one-trip gain lands as d15 cash,
the re-buy cost is all d10-29 — so gating to `day <= 9` takes the half that pays.
**Both failed versions IMPROVED every registered guard** (missed feeds down, d15 cash up)
while losing badly; the cost was in a metric neither of us had listed.

**#11 — v13 fixed the measuring instrument.** See the nondeterminism section above; that
bug is now closed. `flush_order()` sorts by value, tie-broken by name. Also: final-day
haul deadline accounts for item types carried (`hour + dist + (types-1) >= 22`), and HIRE
moved ahead of SELL in force-sell mode — **the latter kept as hygiene only, because the
bug it targeted does not exist**: d28-29 markets average 1.8 lines/turn and hit the
10-line cap in 2 of 48 turns, dropping zero hires.

### THE ENGINE MISMATCH — read before trusting anything above

**We were testing on the wrong engine.** Local was `kaggle_environments` 1.32.4; live is
1.32.6, and the kaggriculture file differs by **102 lines**:

| | 1.32.4 | 1.32.6 |
|---|---|---|
| shop draw | without replacement | **with replacement**, `MAX_SHOP_INSTANCES = 8` |
| milk demand | always exactly 3 — **a constant** | varies **1-4** across seeds |
| LOCKED tiles | guard precedes shed ops | shed ops resolve first |

On 1.32.4 every game ended with all 8 distinct shops, so demand was pinned and
shop-adaptive strategy had nothing to adapt to. Absolute scores roughly halved on
1.32.6 (self-play ~101k -> ~40-57k).

**What survived the upgrade** (round-robin, 180 matches on 1.32.6): the ordering is
unchanged — **v13 beats v10 by +3,048 (2SE +-1,991) and v11 by +1,589 (2SE +-1,169)**,
v10 ~ v11. v13's margin is *larger* on the correct engine, so its selection and ladder
submission were not artifacts. **#7 also survives**: 1.32.6 keeps the per-unit lockstep
market and the identical `# Both players see the same pre-commit inventory` comment, so
within-turn sell ordering remains impossible.

**Now suspect, re-test before citing:** #4 melon window, #5 seed gate, #6 chunk cap,
#9 fertilizer sell mode — all four turn on product demand or realized price, and all ran
where every product was guaranteed shop demand. On 1.32.6 a product can draw **zero**
shops and crash. **Improved for free:** our `shed_adjacent_tiles` matches the engine's
`_shed_access_tiles` exactly, and three of those four no longer block on LOCKED.

**#12 — land is a bet financed by milk, not an independent lever.** d4/d6/d10 + Q4 is
what the top player does 5/5, and it still lost 6/40 at -4,527 with `money_d15` -3,076.
The tell: **strawberry plantings fell 5.7 despite owning more land** — we buy tiles we
cannot afford to seed. His week-one dip is survivable because milk at $260 refills the
tank by d15; ours is not.

**#13 — and this is the finding that matters.** Keying cow/sheep ceilings to market
headroom was neutral (+254, 2SE +-1,820) even after correcting the floors to v13 levels
so the cap could only add. Milk revenue rose +$1,983 but `money_d15` fell 978 and milk
price fell 1.7 — the extra cows cannibalise their own price. **Because we are already on
the wrong side of the threshold.** Our own trajectory:

| day | mktinv_MILK | price |
|---|---|---|
| 15 | 9,949 | **$222** |
| 20 | **10,001** | $158 |
| 25 | 10,023 | $112 |

**We cross I0 around day 20 and never come back** — identical to Seb's three 60-93k
games. His 128k/137k advantage was not 13 cows; it was *never crossing I0*, which his
high shop demand did for him for free. More cows on the wrong side just accelerate the
crash. **The lever is sell-side: never push inventory over the line.**

### 14-16. The milk thread, and the complete causal chain

| # | change | verdict | died at |
|---|---|---|---|
| 14 | absolute glut guard (margin 0/50/100) | rejected | **its own mechanism metric** — 3/40 |
| 15 | cow target 5/6/7 vs 8 | conditional | low draw +825, **high draw -8,715** |
| 16 | demand-conditional herd (shop-count) | neutral | 30/60, -103 (2SE +-2,022) |

**#14 — unilateral market control is impossible in BOTH directions.** The guard capped
sells at `(I0 - margin) - mktinv`, i.e. never push a premium product over the glut line.
It failed on the metric it was built for: **crossings were IDENTICAL to baseline at every
margin — 29/40 vs 29/40, 28/40 vs 28/40, 27/40 vs 27/40** — and realized milk price went
DOWN. The market is shared: the opponent supplies the glut whether we participate or not,
so withholding only donates the scarcity-priced units to them. Together with #7 (can't
sell first to advantage) this **retires the entire category**: in a lockstep shared
market you cannot move price by changing your own behaviour, in either direction.

**#15 — the answer is conditional, not a smaller constant.** Fewer cows wins mildly on
low-demand draws (56%, +825) and loses catastrophically on high ones (**1/6 and 1/8**,
-8,715 and -6,039). Note a variant-generation artifact: targets 5 and 6 give identical
results, because the ramp sets `cows = 6` at d9 before the steady-state target applies
and animals are never sold — the herd ratchets.

**#16 — and this is where the project's central question gets answered.** Sizing the herd
to the actual shop draw worked mechanically: on high-demand draws it built **13.9 cows**
(Seb's number) and milk revenue rose **+$8,240**. Feed rose **+$10,297**. Priced per
marginal cow:

| | per extra cow |
|---|---|
| milk revenue | +$1,397 |
| feed cost | **-$1,745** |
| capital | -$400 |
| **net** | **-$749** |

**A cow loses money even on the best draw in the game** — not because milk is cheap, but
because our feed costs more to deliver than the milk is worth.

### THE CAUSAL CHAIN (every link independently measured)

> our feed logistics cost **4x** the reference (~$38-42k vs **$10.6k** for the same ~14
> animals) -> each marginal cow nets **-$749** -> high-demand draws cannot be exploited ->
> milk revenue stays ~$25k against Seb's $74-80k -> the score gap.

And #8 proved the cost cannot simply be cut: buying the exact feed deficit saved $30.6k
of wheat and **cost $22.8k of score**, because the surplus is insurance that makes feeds
land *given our routing*.

**This retroactively explains three separate neutral/negative results in one stroke.**
Seb's herd size (#16), his land schedule (#12), and shop-adaptive sizing (#16) all
presuppose a feed cost we do not have. **We were copying strategies his logistics made
affordable.** The herd is capped by the cost of walking wheat to animals — not by demand,
not by cash, not by labour.

### NEXT: feed delivery cost per animal

Not the purchasing rule (#8 closed that) — the **trip pattern** that makes surplus
necessary. Hypothesis: `PICKUP WHEAT n` takes `min(wheat_pickup_wanted, shed_wheat)`, and
shed wheat is thin because the top-up buys only the deficit and units drain it, so each
unit picks up 1-2 and feeds 1-2 animals per round trip. Fourteen animals then need 7-14
trips instead of 2-3. That would explain both the 4x cost and why the surplus is
load-bearing: **the surplus is what makes a large pickup possible**, and #8 removed the
surplus without changing the trip pattern, so it starved.

Numbers to collect for both agents: wheat carried per PICKUP, animals fed per
shed-departure, shed-departures for feeding per day, shed wheat at hour 0 vs mid-day, and
whether a carrier is diverted to other tasks mid-route (the reference bundles
feed->collect->care on the same tile).

### 17. Feed delivery — the falsified hypothesis, and the win

**Hypothesis (WRONG, and worth recording because we predicted the opposite):**
`PICKUP WHEAT n` takes `min(wheat_pickup_wanted, shed_wheat)`; shed wheat is thin, so
units pick up 1-2 and feed 1-2 animals per trip, needing 7-14 trips for 14 animals.

**Measured — we pick up MORE than the reference, not less:**

| metric | reference trace | v13 |
|---|---|---|
| wheat / PICKUP | 2.59 | **4.94** |
| animals fed / trip | 1.66 | **2.60** |
| total PICKUPs | 209 | 221 |
| total FEEDs | 320 | 315 |
| **moves / trip** | **5.96** | **15.32** |
| unit-turns / feed | 7.21 | **11.88** |
| trips diverted mid-route | 79% | **88%** |
| shed wheat @h12 (d10+) | 29.4 | **11.5** |

Trip counts and total feeding are near-identical. The cost is **movement** — 2.6x the
walking for the same deliveries — and the big pickups **drain the shed** (43 at h0 -> 11.5
by midday), which re-arms the stateless top-up. So the wheat waste was driven by
WITHDRAWAL size, not the purchase rule.

**#17 result — v14, `WHEAT_PICKUP_CAP = 4`: 29/40 = 72%, +1,275 (2SE +-1,177).** Capping
the withdrawal leaves the buy rule untouched, so the surplus stays in the shed as the
insurance #8 proved it must be. The sweep found where the trade-off balances:

| cap | win rate | diff | feed spend | PICKUPs | note |
|---|---|---|---|---|---|
| 2 | 16/40 = 40% | -950 | -18.1k | **345 v 190** | trip explosion eats the saving |
| 3 | 21/40 = 52% | -258 | -14.0k | 335 v 204 | |
| **4** | **29/40 = 72%** | **+1,275** | **-10.7k** | 290 v 185 | missed feeds 7 v 13 |

`moves/trip` fell in every arm (13.26 v 18.74 at cap 4), so pickup size and moves-per-trip
were NOT independent — the interaction ran in our favour.

**Ladder confirmation:** v13 scored **769.5** against v10's **754.3** — same direction as
the local +2,339/60% call. The local method predicts real results.

### THE REFERENCE PLAYERS ARE FIXED SCRIPTS — do not re-derive strategy from them

**Seb's first 30 turns are byte-identical across all five replays** — same buys, same
tiles, same units, same hours, down to `h5(0,3):PLANT-WHEAT at t16`. Money at t1 is
$1,807 in every game. He is a replayed script, exactly like the trace agent (whose route
selector and front-run layer we already found inert).

**This invalidates the adaptation finding.** The cow counts that appeared to track milk
demand (13/11/9/7/7 against demand 4/3/1/1/0) are not decisions — they are one script
meeting different cash trajectories. High milk price -> more revenue -> the scripted
`BUY_ANIMAL` orders clear. Low price -> the same orders fail on insufficient funds.
**Demand did not cause him to buy cows; it caused him to afford the cows the script
always attempts.** His 60k-137k spread on an identical script also means most of that
outcome is the seed, not skill.

**Closed permanently — do not spend runs here:** herd sizing, shop-adaptive sizing,
land-schedule copying. And treat every "technique" mined from a single replay as suspect
until the same script is checked across seeds for identical prefixes.

**What survives:** the reference agents are still useful as *behavioural* comparisons for
mechanical efficiency (feed delivery cost, moves per trip, wasted actions) — properties
of execution that hold regardless of whether the policy was scripted.

### Open defect found while pattern-diffing: wasted CARE

Measured on v14, seed 42: day 18 issues **33 CARE actions for 13 animals — 20 wasted
unit-turns**, consistent across d10-29 (~400 total). The engine's CARE no-ops if
`cared_today` is already set. Cause: every unit evaluates the on-tile animal block against
the START-of-turn observation, so several units standing on the same tile all see
`cared_today == False` and all issue CARE; one succeeds. We have `claimed` to stop two
units walking to the same target but nothing to stop two units ACTING on the same tile.
Likely applies to FEED / COLLECT_FERTILIZER / HARVEST too.

**CLOSED by #18 below — it did apply to all four, and it was the biggest win of the session.**

### 18. On-tile action de-duplication — SHIPPED as v21 (`56761e1`)

The defect above, fixed. `ctx["tile_acted"]` is a per-turn set keyed by `(pos, action)`,
cleared alongside `claimed`. Keyed by *action*, not tile, because two different actions on
one tile both succeed in the engine — only the repeat of a given action is wasted. Applied
to the animal block (HARVEST / COLLECT / FEED / CARE) and to on-tile HARVEST / WATER /
FERTILIZE, which race identically.

Mechanism, 5 seeds, 14 animals over 30 days = 420 animal-days:

| | v20 | v21 |
|---|---|---|
| CARE actions | 535 | **291** |
| duplicate on-tile actions | 1,150 | **330** |
| FEED | 438 | 309 |
| COLLECT_FERTILIZER | 469 | 306 |

v20 issued **more CARE actions than there were animal-days**, which is the tell.

Score vs v20, 20 seeds × both slot orders:

| seed set | record | delta |
|---|---|---|
| original | 40/40 | **+5,977** (2SE 898) |
| fresh (5001-5020) | 40/40 | **+10,444** (2SE 1,888) |

80/80 paired wins. Nothing else this session came close.

**The important part is where the reclaimed turns went**: not to PASS, to PLANT.
Empty tiles @ d20 **9.0 → 3.6**, planted @ d20 **25.6 → 32.0**, seeds bought 83 → 128,
money @ d15 +2,562. Four separate attempts to buy land coverage directly (more seeds,
plant priority, more hands, territory assignment) all failed; the coverage was not
seed- or hand-limited, it was **turn-limited by duplicated work**.

### Trace-agent crew comparison (seed 42, trace 113,328 v v21-lineage 60,917)

| day 21 | trace | v20 |
|---|---|---|
| hands | **14** | 10 |
| distinct tiles worked | **61** | 35 |
| duplicate actions | 11 | 67 |
| CARE (whole game) | 321 | 520 |
| WATER (whole game) | 915 | 694 |
| SOUTH moves (whole game) | **744** | 142 |
| DROP / PLACE | 78 / 25 | 0 / 202 |

The trace agent does not have the duplication defect (321 CARE ≈ one per animal-day).
Two open leads from this table, both unmeasured:
- **SOUTH 744 v 142.** We barely walk into the southern quadrants. Strong suspect for the
  remaining coverage gap.
- **DROP 78 v 0.** It drops goods in the field; we always walk them to a shed and PLACE
  (202 v 25). Possible large movement saving.

### 19. Q3 re-tested on top of v21 — still loses, and the cause is now isolated

v20 dropped the third quadrant, but that verdict was measured while the crew was burning
~800 unit-turns a game on duplicate work (#18). With those turns reclaimed the question
was legitimately open again. It is now closed properly.

vs v21, 20 seeds × both slot orders:

| arm | record | delta | empty@d20 | planted@d20 | seeds | straw rev | money@d15 |
|---|---|---|---|---|---|---|---|
| +Q3 | 16/40 | −4,276 | 19.7 | 40.1 | 111 | 28,738 | −4,706 |
| +Q3, 12 hands | 1/40 | −9,715 | 19.1 | 40.4 | 116 | 29,142 | −10,480 |
| 12 hands only | 0/40 | −8,582 | 0.9 | 34.8 | 128 | 22,173 | −7,453 |
| +Q3, 14 hands | 2/40 | −12,039 | 17.3 | 41.3 | 122 | 31,186 | −7,467 |
| +Q3, seed throttle removed | 19/40 | −3,713 | 17.6 | 40.3 | 117 | 32,637 | −6,059 |

**Q3 is cash-limited, not labour-limited.** Four independent attacks — reclaimed turns,
more hands, unthrottled seed buying, all combined — and it never fills: ~18 of the 25 new
tiles are still bare at day 20 in every arm. The $4,000 purchase lands at day 11 and
`strawberry_target` is keyed to quadrant count, so Q3 also pulls cash into $100 seeds
right inside the binding window. Crop revenue does rise (+$9,351 strawberry in the best
arm) and it is never enough. This is the same `money_d15` wall that has now killed ~20
experiments. **Do not re-open Q3 without first solving day 7-15 cash.**

### 19b. Seed-purchase throughput — no longer a constraint at two quadrants

Two real throttles were found and tested:
- `holding_any_seed`: we refuse to buy any seed while ONE unplanted seed sits in the shed,
  so only one batch is ever in flight.
- the leftover wheat fill is `min(leftover, affordable, WHEAT_FILL_RESERVE_TILES)` = 7
  tiles per order, the same constant that serves as the cash reserve.

Both are genuine design smells, and lifting them does nothing, because after #18 v21
already ends day 20 with **1.9 empty tiles**. There is no land left for extra seed to go on.

| arm | record | delta |
|---|---|---|
| top-up floor 3 (buy while holding <3) | 14/40 | −817 (2SE 747) |
| wheat fill cap 7 → 25 | 15/40 | −1,393 |
| both | 8/40 | −2,427 |

Keep in mind if land ever expands: these caps will bind again the moment empty tiles exist.

### 20. Water the last window day before harvesting — SHIPPED as v22 (`fc45b35`)

Found by watching a replay: the trace agent's wheat goes **4 -> 6 in one step**. That is
the engine's WATER handler (`kaggriculture.py:419-431`):

```python
bonus = 2 if tile["fertilized_until_day"] >= day else 1
tile["yield_units"] = min(crop_data["max_yield"], tile["yield_units"] + bonus)
```

**The yield gain lands on the WATER action itself, not at day rollover.** Fertilizer
doubles it, +1 -> +2. So wheat (starts at 1, window ages 2-4) reaches 4 on watering alone
and 6 only if fertilized — which is exactly the corrected `max_yield: 6` in game_data.py.

We never reached 6 because `worth_harvesting` returns True at `age >= max_yield_day` and
the harvest branch sits ABOVE the water branch. Wheat at age 4 was harvested on the spot,
though the tile survives to the end of that day and had one more watering in it.

Wheat transitions, seed 7, one match:

| | 1→2 | 1→3 | 2→3 | 2→4 | 3→4 | 3→5 | 4→6 | 5→6 |
|---|---|---|---|---|---|---|---|---|
| trace | 40 | 23 | 22 | 9 | 21 | 15 | 3 | 3 |
| v21 | 78 | 0 | 40 | 27 | **0** | **0** | **0** | **0** |

Zero transitions starting from 3/4/5 on our side against 42 on theirs. Mean wheat yield per
harvested tile **2.90 -> 4.49**. Also applies to melon and carrot.

| seed set | record | delta |
|---|---|---|
| original 20 | 35/40 | +3,851 (2SE 959) |
| fresh 20 (5001-5020) | 28/40 | +1,588 (2SE 1,605) |
| fresh 30 (6001-6030) | 38/60 | +1,627 (2SE 1,096) |
| **pooled** | **101/140 (72%)** | **+2,251** |

The first set overstated it by ~2x and its 2SE did not catch that; the second set's band
barely excluded zero. Three sets were needed to get an honest number. **Report the pooled
figure, not the discovery set.**

#### Method note: step alignment in replays

In this environment the observation at step `i` **already includes the effect of the action
recorded at step `i`**. Reading the action from step `i-1` (the natural assumption)
attributes every change to the wrong turn. This burned an earlier harvest-yield audit too.
For "what caused this tile to change between `i-1` and `i`", read the action at step `i`.

### 21. Q3, properly attacked — from −4,276 to ~−1,000, still not shipped

19 arms. The #19 conclusion ("Q3 is cash-limited") was **wrong**, and so were the two
diagnoses after it. Recorded in order, because each was disproven by the next:

| hypothesis | test | verdict |
|---|---|---|
| day 7-15 cash | `EF_d16` buys Q3 after day 15, `money@d15 +0` | **wrong** — still −5,603 |
| cash guard too loose | reserve $300 vs $3,000 | **irrelevant** — money goes $1,244 (d10) → $15,574 (d12), never near the threshold; arms byte-identical |
| premium seed load | strawberry target 42 → 26/19 | helps a little, not the cause |
| seed supply | shed held **24 wheat** beside **22 empty tiles** | **wrong** — supply was never short |
| labour | 11 / 12 / 13 hands | **wrong** — monotonically worse, empty stayed ~21 at 13 hands |

**The actual mechanism**, found by reading the movement chain:

`territory → harvest → animals → wheat fetch → place animal → buildout → needs_water → shed feed → planting`

Watering movement outranks planting movement. With ~39 planted tiles needing water daily,
`needs_water` is never empty, so **a unit that starts the long walk to SW is re-tasked to a
nearer thirsty crop on the very next turn and never arrives.** No amount of cash, seed or
labour can fix that — the units physically never get there. Presence confirmed it: SW drew
39 unit-turns/day against NW's 142, and only 5 of its 25 tiles were ever planted.

A second, independent defect found on the way: the high-priority planting branch is gated on
`day <= LAST_BUILDOUT_DAY` (13), so from day 14 planting is the **lowest-priority action in
the agent**, below fertilizer, weeds and build sites. Q3 is bought day 11+, i.e. always into
that dead zone.

Hoisting planting above watering while land is genuinely empty finally moves it:

| plant-first threshold | record | delta | empty@d20 | straw rev |
|---|---|---|---|---|
| 4 | 2/40 | −6,640 | 10.8 | 23,307 |
| 8 | 0/40 | −8,672 | **9.7** | **16,111** |
| 12 | 0/40 | −13,395 | 13.2 | 16,449 |
| **14** | 17/40 | **−304** | 13.2 | 22,148 |
| 16 | 3/40 | −4,171 | 12.8 | 22,021 |
| 18 | 5/40 | −3,621 | 15.6 | 19,701 |

Empty tiles finally fall (19 → 10-13) and planted reaches ~40. **But filling harder scores
worse** — at threshold 8 the crew abandons watering and strawberry revenue collapses
23,713 → 16,111. Planting and watering compete for the same unit-turns; there is no setting
that buys both.

**The t14 = −304 is not real.** The sweep is non-monotonic (t12 −13,395, t14 −304,
t16 −4,171), which is the VPT signature. Fresh seeds: **−1,138 (2SE 1,193), 14/40**.
Pooled ≈ −700 to −1,100.

**Status: Q3 is now roughly cost-neutral instead of −4,276, but the point estimate is still
negative and the win rate 35%. NOT SHIPPED.** `IC_plantfirst14` in the scratchpad is the
best arm. Also note the no-Q3 control `JD_noq3_t14` is −734, so plant-first does not help
the two-quadrant baseline either — at 3.4 empty tiles it never fires.

**To make Q3 pay, the remaining ~$1,000 has to come from revenue, not from land mechanics.**
Every land-side lever is now exhausted and documented above.

### 21b. Why the 2-quadrant algorithm cannot simply be scaled to 3 — labour economics

The natural objection: our 2-quadrant play works (32 planted, 3.5 empty), we have $22k spare
at day 20, so staff the third plot proportionally (~13 hands for ~48 tiles) and run the same
algorithm. Tested on top of `IC_plantfirst14`, and **it works mechanically and fails
economically**:

| crew | planted@d20 | empty@d20 | record | delta |
|---|---|---|---|---|
| 9 | 38.4 | 12.7 | 14/40 | −1,138 |
| 11 | 43.0 | 11.3 | 0/40 | −8,546 |
| 13 | 45.3 | 10.6 | 0/40 | −14,626 |
| 14 | **50.0** | **7.4** | 0/40 | **−21,791** |

Full land coverage is achievable — 50 planted tiles against the baseline's 31.7. It just
costs far more than it earns.

**HIRE cost is Fibonacci per hand AND recurs daily** (the engine wipes `hands` to `[]` every
rollover, so the whole bill is re-paid each day):

| hand # | 9 | 10 | 11 | 12 | 13 | 14 |
|---|---|---|---|---|---|---|
| cost/day | 34 | 55 | 89 | 144 | 233 | 377 |
| daily wage bill | **88** | 143 | 232 | 376 | 609 | **986** |

9 → 14 hands = **+$19,756 of labour over days 8-29**. Measured score delta **−21,791**.
The labour bill IS the loss. What it bought: wheat +$11,547, strawberry −$2,844 =
**+$8,703**. We pay $19,756 to earn $8,703.

Marginal analysis: hand #14 costs $8,294 over the game and works ~3.6 tiles worth ~$1,400 —
**about 6x its marginal product**. Break-even is a hand worth ~$65/day; Fibonacci crosses
that at hand #11. `FULL_HANDS_CAP = 9` and v18's conditional 11 are sitting exactly on that
cliff, which is why every hand sweep since has come back negative.

**Conclusion: money is not the constraint (we hold $22k at d20); the marginal hand's wage
exceeds its output. Q3 cannot be staffed into profit at current revenue per tile.**

The trace agent runs 13-15 hands, pays the SAME Fibonacci bill, and still scores 85k to our
70k — it affords the crew because it earns more per tile. **The gap is revenue per tile, not
land and not labour.** Next leads: SOUTH movement (744 v 142) and DROP v PLACE (78/25 v
0/202).

### 22. Travel cap — SHIPPED as v23 (`3c408dd`)

The movement chain is task-type first, distance second: a unit would walk eight tiles to a
HARVEST while standing beside a thirsty plant. MOVE was ~42% of all actions.

`TRAVEL_CAP` bounds the global fallback searches. It is a PREFERENCE, not a restriction —
`decide_unit_action` is re-run uncapped when nothing is in range, so far tiles are still
served. The PASS path commits nothing (claims/budgets/tile_acted only mutate on commit), so
the retry is side-effect free.

| cap | original seeds | fresh seeds |
|---|---|---|
| 1 | −5,213 | — |
| **2** | **+2,784 (35/40)** | **+2,954 (33/40)** |
| 3 | +1,378 (30/40) | +1,775 (32/40) |
| 4 | −2,056 | −6,941 |
| 6 | — | −3,446 |

Pooled at cap 2: **68/80 = 85%, +2,870**. Caps 2 and 3 are positive on two independent seed
sets each and cap 4 negative on both, so the cliff between 3 and 4 is real. Land ends up
FULLER (empty@d20 4.3 → 1.5, planted 30.8 → 33.9) because units stop burning turns in transit.

### 22b. Dynamic crew sizing — REJECTED at every threshold

Requested: hire above 9 only when needed, release when idle. Both halves fail.

**Nobody is idle.** PASS is 0-2% of actions from day 8 on, so there is no worker to release.
The engine wipes `hands` nightly anyway, so release is already automatic.

Queue-driven cap raise (trigger on `needs_water + needs_harvest + animals + empties` per hand):

| trigger | record | delta |
|---|---|---|
| queue/hand > 5, cap 12 | 0/40 | −7,381 |
| queue/hand > 8, cap 12 | 1/40 | −5,354 |
| queue/hand > 5, cap 11 | 1/40 | −5,128 |
| queue/hand > 12, cap 12 | 2/40 | −1,998 |

**The loss shrinks monotonically as the trigger gets stricter** — the best version of the
feature is the one that never fires. There is no backlog condition under which hand #10+
earns its Fibonacci wage (see #21b).

### 22c. Weeds are not a cost centre — thread closed for good

| weed cause | per game | note |
|---|---|---|
| lifespan decay | 16.4 | **16.6 of these are STRAWBERRY at natural end of life** — 4 productions done, dies by design |
| | 1.6 | WHEAT, genuinely avoidable |
| unwatered 2 days | 6.6 | |
| random spawn | 0.4 | only fires on empty tiles; v23 runs at 1.5 empties |

Crop value still on the plant when it rotted: **$157/game**. DIG is 22 actions of ~5,900
(0.4%). Wheat loses 4.0 yield-units/game to decay ticks, strawberry 0.2 — because ongoing
crops are already harvested on sight and one-time crops at `age >= max_yield_day`.

A CRITICAL_HARVEST preemption for one-time crops at/after `max_yield_day` was implemented
and tested anyway: **−2,502 (9/40)**. The rule is already in `worth_harvesting`.

### 22d. Critical-water rescue — the FIFTH falsification of watering priority

Thirst kills 6.6 plants/game, forfeiting ~**$2,627** of future production (STRAWBERRY 3.0 →
$1,332; MELON 0.8 → $950; WHEAT 2.8 → $345). Real money, and still not recoverable this way.

| arm | record | delta |
|---|---|---|
| rescue, uncapped | 0/40 | −9,135 |
| rescue, within travel cap 4 | 10/40 | −4,694 |
| rescue, within travel cap 2 | 11/40 | −843 (2SE 749) |
| + CRITICAL_HARVEST | 0/40 | −7,710 |

The uncapped version **backfired mechanically**: thirst deaths rose 7.2 → 13.5 and waterings
fell 878 → 730. Units set off on long walks to one dying plant, watering nothing en route, so
more plants slipped to 1 dry day — **the rule manufactures the emergency it is preventing.**
Capping it fixes the backfire and still loses, because a plant at 1 dry day is already in
`needs_water`; the special case only reorders work.

**Standing law, now 5 for 5: prioritising watering never pays. Do not test a sixth variant.**

### 23. Movement efficiency vs the trace agent — THE GAP DOES NOT EXIST

Two leads were flagged off the v20-vs-trace action mix (#18). **Both were misreadings and are
now closed.** Same-match measurement, v23 vs trace, mean of 4 seeds:

| | total actions | MOVE | move share | work per move | deposits | HARVEST |
|---|---|---|---|---|---|---|
| **v23** | 6,175 | 3,103 | **50%** | **0.95** | 257 | 255 |
| trace | 6,758 | 3,386 | **50%** | 0.86 | 121 | 341 |

**We are slightly MORE step-efficient than the trace agent** (0.95 work per move vs 0.86).
Its larger action count is 13-15 hands, not tighter routing. There is no routing win available.

- **"SOUTH 744 v our 142"** — geography, not technique. It owns three quadrants and walks
  south; we own two northern ones.
- **"DROP 78 v our 0"** — a real engine fact with no value here. `DROP`
  (kaggriculture.py:330) banks the unit's ENTIRE inventory in one action; `PLACE` (:364)
  banks ONE item type. But our units almost always carry a single type, so a DROP rule fires
  only 15x/game (PLACE 257 -> 188) and the deposit gap is trip COUNT, not cost per trip.

| DROP arm | record | delta |
|---|---|---|
| DROP at >=2 types (+ final-day haul) | 20/40 | −407 |
| DROP at >=1 type | 19/40 | −286 |
| DROP at >=3 types | 31/40 | +180 (2SE 291) |
| DROP at >=2, no haul change | 19/40 | −554 |

Best case is +180 against a 2SE of 291 — inside noise, from a rule that fires 4 times a game.
**Not shipped.** Keep `drop_safe()` in mind only if inventories ever carry multiple types
(it is unsafe while carrying feed wheat, fertilizer for a run, or an animal en route).

**Consequence: the deficit vs the trace agent is not execution.** De-dup, water-before-
harvest and the travel cap took every execution win available. What remains is capacity
(13-15 hands) funded by revenue per tile — the same wall as #21b.

### 24. Market coupling — a blind spot in the A-vs-B harness

Both players trade in ONE market, so our selling pattern moves the price curve the opponent
sells into. A paired A-vs-B test cannot see this: it reports our margin against the arm we
changed, not against the field.

Caught on v23. Against the trace agent v23 earns +6,721 more than v22 in absolute terms and
its MARGIN is 4,756 WORSE, because the trace agent gained +11,477 from the same price shift:

| vs trace, 40 matches | our score | trace score | margin | record |
|---|---|---|---|---|
| v23 | 76,936 | 96,086 | −19,150 | 2/40 |
| v22 | 70,215 | 84,609 | −14,394 | 7/40 |

**Resolved by a neutral third party.** v23 and v22 each vs v14, 40 matches:

| | our mean | v14 mean | margin | record |
|---|---|---|---|---|
| v23 | 86,226 | 50,441 | +35,785 (2SE 2,848) | 40/40 |
| v22 | 89,869 | 54,397 | +35,472 (2SE 2,720) | 40/40 |

Identical within noise (+313). Under v23 BOTH scores shift down together, so the coupling
moves both boats and the margin holds. The trace agent is a replayed fixed script whose sell
schedule happens to profit from our altered curve — the least representative opponent we own.

**Method rule: for any change that alters WHAT or WHEN we sell, check the margin against a
neutral third party (v14 snapshot) before shipping, not just the paired A-vs-B.** Ladder
rank is decided by match outcomes, so margin against a varied field is the target metric,
and absolute cash can move without it.

### 25. Boustrophedon sweep (band per worker) — REJECTED, but it solves Q3 coverage

Idea: each worker owns a contiguous band and mows it — out along one row, back along the
next — doing every job on the tiles it passes, instead of greedily jumping to the nearest
task. Implemented generally: serpentine-order every owned tile (even rows L-R, odd rows R-L
so consecutive entries are adjacent), cut the path into one contiguous band per unit, and
target the next tile FORWARD along the band, wrapping at the end. Bands are assigned by each
unit's own path position so nobody crosses anyone; a clear band falls through to the existing
chain. Adding a quadrant just lengthens the path and re-cuts the bands — no per-plot logic.

| arm | record | delta | empty@d20 | planted@d20 | straw rev |
|---|---|---|---|---|---|
| sweep | 1/40 | −9,600 | 2.1 | 32.5 | 19,304 (v 23,668) |
| sweep, planting excluded from band | 2/40 | −7,106 | 1.6 | 33.9 | 23,905 |
| sweep + Q3 | 0/40 | −15,021 | **5.7** | **42.0** | 21,664 |

**Why it cannot win: there is no travel left to reclaim.** work/move 0.94 vs v23's 0.95,
MOVE 3,096 v 3,119, WATER identical at 869. `TRAVEL_CAP = 2` already confines units to a
2-tile radius, so "next along my band" and "nearest task" resolve to nearly the same tile.

**Why it loses: a sweep is route-ordered, not value-ordered.** A unit waters a cheap wheat
because it is next in the band while a ready strawberry waits one band over. Strawberry
revenue 23,668 -> 19,304 is the entire loss.

**Worth keeping:** `QC_sweep_q3` reached **5.7 empty / 42.0 planted**, by far the best Q3
coverage ever measured (every other Q3 arm sat at ~18-19 empty — see #21). The sweep DOES
solve the coverage problem that cash, seed, hands and planting-priority all failed to solve.
It still loses because Q3 is wage-limited, not coverage-limited (#21b). **If revenue per tile
ever makes Q3 viable, `QC_sweep_q3` is how to farm it.**

#### 25b. Two follow-ups: the first sweep was buggy, and the fixed one still loses

**The first implementation was not sweeping at all.** `sweep_bands` re-sorted units by path
position EVERY turn, so as units moved their order flipped and a worker was handed a
different band mid-walk — it abandoned its strip and the motion degenerated to random.
Caught by watching the replay, not by any metric. Fix: worker `i` owns band `i` for the whole
game, no re-sorting.

The fix worked on exactly the thing it should:

| | direction reversals | delta vs v23 | straw rev |
|---|---|---|---|
| v23 (no route structure) | 19% | — | 23,200 |
| stable sweep, free 5-tile slices | **15%** | −7,055 | 22,061 |
| row-pair bands, 10 tiles (out-and-back, per plot) | — | **−10,410** | 18,897 |
| buggy reshuffling sweep | 21% | −9,600 | 19,304 |

**The stable sweep turns around LESS than our shipped agent (15% v 19%) and still loses.**
Row-pair bands — the literal "out along row 1, back along row 2, ~10 tiles" design, verified
tile-by-tile — are worse still.

**Monotonic: the more route structure imposed, the worse the score, and strawberry revenue
tracks it exactly (23,200 -> 22,061 -> 18,897).** A worker sweeping a fixed strip services
tiles in GEOGRAPHIC order, so ripe premium crops wait while it waters whatever is next in the
lane. Since #23 showed we already beat the trace agent on work-per-move (0.95 v 0.86), there
was never travel to reclaim — route discipline can only cost value-ordering, never buy
efficiency.

Crew size was pinned from both sides while testing this (sweep arms, 40 matches each):
6 workers −34,046, 7 −23,780, 8 −11,542, 10 −9,600. Below 9 hands the farm starves; above 9
the Fibonacci wage outruns output (#21b). **9 hands is the optimum, bounded on both sides.**

### 26. COIN MARGIN IS WORTH NOTHING — verified on 25,849 real rating deltas

kaitofukami's v25 notebook claims the official evaluation page says "coin margin does not
matter; only win/loss/tie does". The page is JS-rendered and unreadable by fetch, so this was
tested against real data instead: the public `georgymamarin/kaggriculture-episodes` dataset
carries `rating_after` per (episode, agent). Sorting each submission's episodes
chronologically and diffing `rating_after` gives the per-game rating delta.

| outcome | mean rating delta |
|---|---|
| WIN | **+47.92** |
| LOSS | **-16.33** |

Within wins, controlling for rating gap (±100) and sorting by coin margin:

| margin quartile | mean margin | mean rating delta |
|---|---|---|
| narrowest 25% | 1,009 | +43.31 |
| 2nd | 3,979 | +47.44 |
| 3rd | 8,137 | +44.94 |
| widest 25% | **26,082** | +48.08 |

Widest minus narrowest: **+4.78 against 2SE 6.76**. correlation(margin, delta) = **+0.025**.

**A 26,000-coin thrashing pays exactly what a 1,000-coin squeaker pays.** Reproduce with
`scratchpad/rating_test.py`.

**PROMOTION RULE, effective now: rank by WIN RATE, never by mean margin.** Margin remains
useful only as a mechanism diagnostic (is the change doing what it should), never as the
decision. Note the asymmetry too: a win pays ~3x what a loss costs, so volume of play helps.

### 26b. The paired-seat panel — and a harness bug that inverted it

Built `scratchpad/panel.py`: every agent plays every other, all seeds, BOTH seat orders,
ranked by field win rate plus Bradley-Terry (MM iteration). Motivated by #24 and by the
community notebook "Beating Your Own Best Agent Is The Wrong Test".

**The first run was WRONG and said v22 (81%) beat v23 (70%).** Cause:
`kaggle_environments/agent.py:get_last_callable` appends the agent's directory to `sys.path`
and `exec`s the file — but `import game_data` caches under that BARE NAME in `sys.modules`,
so **the first agent to import it in a worker process fixes that module for every agent
after it**, across matches. The snapshots carried the pre-correction game_data (WHEAT
max_yield 4 not 6, STRAWBERRY max_yield_day 16 not 10) and v22/v23 read those fields in
`fert_worth_it` / `water_before_harvest`, so they played with stale constants.

`tips.py` was immune only by luck — every arm directory got a copy of the CURRENT
game_data.py, so the shared module was always identical. **All shipped decisions stand**;
verified directly: v23 vs v22 = 35/40 = 88%, +2,784, and shipped `main.py` is byte-identical
to the tested arm `LF_cap2_h9`.

`panel.py` now aborts unless every agent carries an identical `game_data.py`. **Any new
harness that mixes agents from different directories must do the same check.**

Corrected panel, 6 agents, 10 seeds, both seats (300 matches):

| agent | field win rate | Bradley-Terry |
|---|---|---|
| trace | 92% | 3.966 |
| **v23** | **78%** | **1.321** |
| v22 | 70% | 0.711 |
| v20 | 40% | 0.003 |
| v14 | 14% | 0.000 |
| v10 | 6% | 0.000 |

Monotone in development order — itself a check the broken run failed. **v23 confirmed best.**

Genuine non-transitivity survives: v23 beats v22 overall yet does WORSE against the trace
agent (10% v v22's 30%). That is exactly why field win rate is the promotion metric.

### 26c. Leaderboard reality (2026-08-10)

We are **rank 1,351 of 3,540** at **922.3** (v22; it drifted up from 893.4). Median 709.9.
1st 3,233.4 | 30th 3,013.3 | 100th 2,851.8. **The gap to top-30 is ~2,090 points and our
shipped wins are worth ~+30 each.** Per kaitofukami (unverified), 22 of the top 30 share an
identical Day-0 signature — the top is largely one copied replay route. Our `premium/` trace
agent is that species and scores 92% on our own panel.

### 26d. v24 SHIPPED (`a9304c9`) — the first version promoted on win rate

`DROP_MIN_TYPES = 3` + `drop_safe()`. DROP banks the unit's ENTIRE inventory in one action
where PLACE banks one item type (engine :330 vs :364); `drop_safe()` vetoes only while
carrying something with a purpose (feed wheat or fertilizer a pickup run wants, an animal
en route to a structure).

**Rejected on 2026-08-09 as "+180, inside noise". That rejection was wrong** — it went
31/40 = 78% on the original seeds AND 31/40 = 78% on fresh seeds, and margin is worth
nothing (#26). Panel (6 agents, 14 seeds, both seats, 420 matches):

| agent | field win rate | Bradley-Terry |
|---|---|---|
| trace | 92% | 4.078 |
| **v24** | **74%** | **1.088** |
| v23 | 64% | 0.608 |
| v22 | 49% | 0.221 |
| v20 | 21% | 0.005 |
| v14 | 0% | 0.000 |

Beats v23 head-to-head 71% on a mean margin of **+142** — the exact case the old criterion
throws away. Also improves against the trace agent (11% v v23's 7%).
Submitted 2026-08-10.

### 26e. Re-audit of margin-judged rejections — only ONE was wrong

Since drop3 proved the old criterion discards real wins, the near-misses were rebuilt on
top of v24 and re-screened on WIN RATE (40 matches each vs v24):

| arm | win rate | margin | old verdict |
|---|---|---|---|
| `XA_drop2` DROP at 2+ types | 42% | −540 | rejected — correctly |
| `XB_drop4` DROP at 4+ types | **22%** | **+30** | untested |
| `XC_cap3` travel cap 3 | 35% | −1,062 | rejected — correctly |
| `XD_cap1` travel cap 1 | 0% | −7,241 | rejected — correctly |
| `XE_topup3` seed top-up floor 3 | 18% | −2,679 | rejected — correctly |

**No further hidden winners. v24's `DROP_MIN_TYPES = 3` and `TRAVEL_CAP = 2` are locally
optimal on the correct metric**, and drop3 was the only rejection the margin criterion
actually got wrong.

`XB_drop4` is the mirror image of the drop3 case: **+30 mean margin, 22% win rate.**
Positive margin, badly losing agent. With drop3 (+180 margin, 78% wins) it demonstrates the
two metrics are decoupled in BOTH directions — neither can be inferred from the other.

### 27. v25 SHIPPED (`4ac3eb5`) — the crop MIX was wrong, not the revenue

Split the trace agent's advantage into volume / price / mix (`scratchpad/revenue_gap.py`,
8 seeds). The surprise: **our total revenue already matches it** — 126,765 v 128,189, within
1%. Final money differs by 13,941. We earn the same money from the wrong crop.

| | v25 lineage | trace |
|---|---|---|
| strawberry tiles @ d18 | **18.5** | **40.0** |
| strawberry revenue | 17,588 | 36,819 |
| wheat revenue | 25,382 | 9,033 |
| **wheat SPEND** | **27,831** | **13,970** |
| cows / sheep | 7.9 / 5.9 | 8.0 / 6.0 |

We churn wheat at near-zero margin (buy 27,831, sell 25,382) on tiles that could carry
strawberry at ~$920/tile. **The cause was a constant, not a capability:**
`strawberry_target` returned 19 for two quadrants and we sat at 18.5 — at the cap with land
to spare.

| target (2 quadrants) | original seeds | fresh seeds | pooled (80) |
|---|---|---|---|
| 24 | 68% | — | — |
| **28** | **70%** | **65%** | **68%** |
| 30 | 75% | 62% | 69% |
| 32 | 65% | 60% | 63% |
| 36 / 40 / 44 | identical to 32 — land saturates at ~35 planted tiles |

Strawberry revenue **+$10,000** in every winning arm. **Funding it by cutting melon FAILED
(32%)** — the trade is wheat -> strawberry, not melon -> strawberry.

Panel (6 agents, 14 seeds, both seats, 420 matches): trace 91% | **straw28 56%** |
straw32 45% | straw30 41% | v24 36% | v22 26%. Beats v24 head-to-head 71%.

**The head-to-head sweep preferred 30; the panel preferred 28.** That disagreement is
exactly why the panel is the promotion test.

**This reframes Q3 (#21, #21b).** Nineteen arms failed because we filled the new quadrant
with cheap wheat — the same zero-margin churn. A quadrant filled with STRAWBERRY at
~$920/tile is a case none of them tested. Retesting now.

### 27b. Q3 CLOSED FOR GOOD — tested with strawberry, the last untested hypothesis

#27 reframed Q3: every earlier arm filled the new quadrant with cheap wheat, so a
strawberry-filled quadrant was never tested. Retested on the v25 base, 40 matches each:

| arm | win rate | strawberry rev | empty@d20 | money@d15 |
|---|---|---|---|---|
| Q3 d11, straw target 42 | 5% | 29,070 | 13.8 | −3,821 |
| Q3 d11, straw target 50 | 0% | 29,240 | 14.6 | −4,415 |
| Q3 d14, straw target 42 | 0% | 23,709 | 17.1 | −2,674 |
| Q3 d9, straw target 42 | 5% | 29,386 | 13.1 | −3,668 |
| **v25 baseline, TWO quadrants** | — | **30,946** | **0.7** | — |

**A third quadrant does not raise strawberry revenue — it slightly LOWERS it.** v25 already
earns ~$30,946 of strawberry on two quadrants; Q3 adds ~14 permanently empty tiles and
drains $3,800 of day-15 cash.

**The trace agent's third quadrant was never the CAUSE of its strawberry advantage.** We
only needed to stop growing wheat on land we already owned. **23 arms across three sessions.
Do not re-open Q3.**

### 27c. NEXT LEAD: feed wheat costs us double for a smaller herd (~$13,845)

Post-v25 revenue split (8 seeds), remaining gap to the trace agent:

| | v25 | trace |
|---|---|---|
| total revenue | 128,466 | 129,460 |
| **final money** | **83,071** | **99,517** |
| **WHEAT SPEND** | **27,862** | **14,018** |
| herd | 7.5 cow + 5.5 sheep = 13 | 8 + 6 = 14 |
| wheat units SOLD | 569 | 208 |

**Revenue is level; the gap is cost, and it is almost entirely feed wheat — $13,845 of the
$16,446 shortfall.** We buy ~670 units for a 13-animal herd and simultaneously sell 569
harvested units: a large buy-and-sell loop that nets about the same as theirs (−4,260 v
−4,706) at twice the gross. Ask: why does a 13-animal herd need double the feed of a
14-animal one?

Also settled here: **melon volume is self-defeating.** Our tiles fell 10.2 -> 2.5 under v25
yet melon revenue barely moved (13,791 v their 14,447 from 12.6 tiles) — we realise
**$166/unit v their $110**. Melon has the steepest price curve in the game (`above: sq`,
target 3.60). Few melons is correct, not a deficiency.

### 27d. Feed wheat is NOT the gap, and sell-throttling makes things worse

**Correction to 27c: that lead was wrong — it compared GROSS wheat spend, not net.**

| | bought | harvested | FEED | sold | shed end | NET cash |
|---|---|---|---|---|---|---|
| v25 | 602 | 259 | **290** | 560 | 7 | **−4,260** |
| trace | 275 | 239 | **323** | 206 | 0 | −4,706 |

The trace agent FEEDS MORE (323 v 290) on less than half the purchased wheat, but our net
wheat cash is actually *better*. We simply run a much larger buy-and-sell loop at the same
net. Wheat is not the leak.

**A real measurement flaw surfaced here.** Engine :583 re-quotes EVERY UNIT at the current
market inventory, so a SELL of n units walks the price down as it executes. Every revenue
figure in this ledger priced whole orders at the pre-order price — overstating revenue, and
overstating it more for whoever sells in bigger chunks. Realized vs nominal
(`scratchpad/realized.py`, 6 seeds):

| product | our slip | their slip | our units/order | their units/order |
|---|---|---|---|---|
| **MELON** | **−3,618** | −845 | **16.3** | 7.7 |
| strawberry | −817 | −1,138 | 10.1 | 7.5 |
| **TOTAL** | **−5,953** | −3,627 | | |

We lose **26% of melon revenue to our own dumping** (nominal 13,894 -> realized 10,276);
they lose 6%. Melon has the steepest curve in the game (`above: sq`, target 3.60).

**But tightening the sell throttle LOSES.** `MIN_SELL_PRICE_RATIO` swept up from 0.70:

| ratio | win rate |
|---|---|
| 0.80 | 8% |
| 0.88 | 5% |
| 0.94 | 5% |
| 0.98 | 25% |

Holding stock to protect the price costs more than the price impact — unsold inventory is
worth $0 at game end and prices recover slowly. Same lesson as v9's hold-window regression.
**The trickle is already near-optimal; do not re-test sell throttling.**

**Caveat for future audits: nominal revenue is not comparable across agents that sell in
different chunk sizes. Use `realized.py`'s price walk.**

### 28. Q3 RE-OPENED — the ladder data says the top runs 3-4 patches, and it is right

**#21/#27b concluded Q3 never pays. That conclusion was drawn entirely from OUR agent and is
not safe.** The field says otherwise. `episode_features.csv` joined to `rating_after`,
33,900 seat-episodes:

| rating band | n | tiles planted | peak crew | strawberry | wheat | money |
|---|---|---|---|---|---|---|
| 0-1000 (us) | 11,662 | 134 | 8.7 | 18.7 | 57.9 | 54,089 |
| 1500-2000 | 5,519 | 154 | 13.6 | 42.2 | 88.0 | 94,787 |
| 2500-2900 | 5,425 | 151 | 13.9 | 41.8 | 85.0 | 107,383 |
| 2900-3100 | 197 | **159** | **14.0** | 41.5 | 92.6 | 102,483 |

**100% of the top 500 rated seats planted >50 tiles.** Median 158. We run crew 10 and ~114
plantings — the 0-1000 profile, which is exactly where we are rated.

**Why 23 arms missed it:** every one moved ONE lever from a small-farm baseline, and each
lever loses alone (land with no crew, crew with no land, seed with nothing to plant on).
Reproduce the package with `scratchpad/bigfarm.py`.

### 28b. The big-farm package: we CAN build it, and it starves the animals

`BF_3q_c14` (3 quadrants, crew 14, seed top-up, wheat fill 25, plant-first, straw target 42)
reproduces the top profile exactly — **58.6 planted tiles, 42.3 strawberry (MORE than the
trace agent's 40), 174 seeds, land full at 1.4 empty.** And it scores 2% on the panel.

| revenue | BF_3q_c14 | v25 | change |
|---|---|---|---|
| **MILK** | 11,983 | 21,949 | **−45%** |
| **WOOL** | 5,467 | 14,769 | **−63%** |
| strawberry | 17,702 | 24,964 | −29% |
| melon | 12,704 | 13,935 | −9% |

Same herd (8 cow / 6 sheep), MORE feeding (308 v 293) — yet animal revenue collapses.
**14 hands over 75 tiles cannot service crops and animals at once, and animals are the
highest-value goods in the game** (milk base 160, wool 200, v wheat 25). We bought 17 extra
strawberry tiles and paid ~$19,000 of milk and wool for them.

**So the blocker is LABOUR ALLOCATION, not land, wages, seed throughput or coverage — all of
which are now individually eliminated.** To run a big farm we need the animal economy held
intact while crops scale: dedicated animal servicing that expansion cannot cannibalise.

### 28c. Corrected cost model — earlier wage figures in #21b were WRONG

`farmHandCostMult = 1`, `_hire_cost = mult * _fib(hires_today)`, and **`hires_today` resets
at every rollover** (line 868) along with the nightly `hands = []` wipe. Actual measured
spend, 3 seeds:

| | hires/game | **wages/game** | max hires in one day |
|---|---|---|---|
| v25 | 239 | **2,288** | 11 |
| trace | 284 | **8,426** | 15 |

The trace agent pays only ~$6,138 more in wages and ~$2,000 more for land. **#21b's claim
that staffing a third quadrant costs ~$19,756 was wrong** — it assumed the full daily ladder
was paid for every hand every day at peak size.

Exact money flow (per-step deltas, 4 seeds) — the reliable accounting:

| | money IN | money OUT | final |
|---|---|---|---|
| v25 | 114,524 | 35,000 | 82,523 |
| trace | **129,190** | 30,521 | 101,669 |

**Income gap −14,666; spend gap +4,479.** Note this contradicts #27/#27d's "revenue is
level" — that used nominal per-order pricing and a per-agent price walk, both of which
ignore that the two agents sell into ONE market in lockstep. **Use per-step money deltas for
any cost or revenue claim; nominal order pricing is not trustworthy.**

Also eliminated as causes: the 10-order-per-turn cap (we hit it 22 turns v their 19 and issue
MORE sell orders, 340 v 229) and buy-side price slippage (+101 v +44, negligible).

### 28d. The big farm fails on PRICE REALIZATION, not production — cause still open

Ring-fenced animal crew (`scratchpad/ringfence.py`, first N units serve animals ahead of all
crop work, falling through when the herd is served): **did not fix it.** Milk stayed at 9,098.

Then the actual mechanism, seed 7:

| | milk units | milk orders | units/order | market MILK inventory at our sell times | quoted price |
|---|---|---|---|---|---|
| BF_3q | **204** | 53 | 3.8 | mean **10,065** | mean **$22.9** (min 1) |
| v25 | **207** | 35 | 5.9 | mean **10,016** | mean **$127.0** |

**The big farm produces the SAME milk and sells it for a quarter of the price.** Milk is
linear above target at ~$2.10/unit, so the ~50 units of extra market inventory at our sell
moments is worth ~$105/unit — the whole $10,000.

Feed/care are fine (no_care 14 v 16 animal-days, no_feed 2 v 4), herd identical (8 cow /
6 sheep), wool units 142 v 148. **Production is not the problem at all.**

Eliminated as causes:
- shed capacity — 14/100 used, never close to full
- 10-order-per-turn cap — BF hits it 24 turns v v25's 22, and issues MORE sells (325 v 290)
- feed/care completion, herd size, animal harvesting
- wages (#28c), buy-side slippage (+101 v +44)

**Open: why does the same volume of milk meet a market carrying ~50 more units?** Milk does
sit in the shed longer on the big farm (mean 0.77 v 0.43, max 24 v 12), which points at sell
TIMING rather than sell sizing — but that is a lead, not a conclusion. Do not build on it
until measured.

**Status: your reading of the ladder is right (#28) and our big-farm build is not yet worth
shipping.** Every production-side explanation is now eliminated; the failure is on the
market side.

### 29. Geese and profitability-based animal buying — sound theory, 15 arms, all lose

**The price curves strongly suggest geese should work.** Revenue from dumping N units into a
fresh market:

| units | MILK price | WOOL price | EGG price | milk revenue | wool revenue | EGG revenue |
|---|---|---|---|---|---|---|
| 50 | 55 | 55 | 43 | 5,430 | 7,655 | 2,244 |
| 100 | **1** | **1** | **42** | 6,205 | 7,969 | 4,371 |
| 200 | 1 | 1 | **41** | 6,305 | 8,069 | **8,510** |

**Milk and wool are LINEAR above target and saturate near $6.3k / $8.1k no matter how much
is produced. EGG is LOGARITHMIC and keeps scaling.** The goose is also the cheapest ($300),
fastest (interval 1, ~2/day) and earliest (day 4) animal, and the reference players never buy
geese, so that market sits unsaturated.

**And it still loses.** Geese at a fixed target (cap cows at 7 when milk < 100, buy geese):

| geese | win rate | delta |
|---|---|---|
| 4 | 2% | −2,075 |
| 6 | 2% | −2,613 |
| 10 | 2% | −4,312 |

Mechanism verified: +$6,249 of egg revenue with milk and wool UNCHANGED — genuinely
additive. But each COOP displaces a crop tile and the birds cost feed and care turns:
planted 34.8 -> 32.1, seeds 114 -> 98. Monotonic in goose count, so the birds are the cost.

**Marginal-profit purchasing** (price each animal at current market prices, net of feed,
purchase and the crop tile it displaces; buy the best while positive) — two models, 11 arms:

*Model 1 — lifetime output priced as one dump.* WRONG: the town consumes daily so production
meets a recovering market. Understated high-volume animals, cut sheep 6 -> 2, and at low tile
cost collapsed crops 35 -> 20 tiles. Best −11,541 (12%).

*Model 2 — priced per DAY against a recovering market.* Correct pricing, still loses:

| crop-tile opportunity value | win rate | delta |
|---|---|---|
| 900 | 12% | −10,112 |
| 1,500 | 32% | −4,099 |
| **2,200** | **40%** | **−2,569** |
| 3,000 | 18% | −8,641 |
| 4,500 | 0% | −45,010 (herd starved) |

Peak at 2,200 and still short of v25, non-monotonic either side. **The transcribed herd curve
is hard to beat**; every profitability variant disturbs the crop economy (strawberry revenue
23,650 v 31,116 at the peak arm).

**Verdict: NOT SHIPPED.** The egg-market insight is real and worth keeping — if a future
build has spare structure tiles that do NOT displace crops (e.g. a genuinely working third
quadrant), geese are the right thing to put on them, because eggs are the only product whose
price survives volume.

### 30. THE LABOUR GAP IS REAL — #23 measured it with the wrong metric

#23 concluded "we out-route the trace agent 0.95 v 0.86 work-per-move, there is no routing
win available". **That was wrong: it counted HAULING as work.** Split productive work from
logistics and the gap is large and consistent (3 seeds, v25 v trace):

| | steps per productive job | **logistics share of work** | PICKUP | PLACE | DROP | PRODUCTIVE actions |
|---|---|---|---|---|---|---|
| **v25** | 1.11 | **25.7%** | **459** | **255** | 5 | 2,197 |
| trace | **1.03** | **14.7%** | 262 | 25 | 96 | **2,485** |

**We burn 760 actions per game on logistics against their 429 — 331 wasted actions — and
they convert a similar total into 288 MORE productive ones.** This is the single clearest
remaining inefficiency, and it is exactly what the user has been pointing at for two
sessions.

Two identified causes:
- **PICKUP 459 v 262.** `WHEAT_PICKUP_CAP = 4` forces a shed trip per ~4 feeds.
- **PLACE 255 v 25.** They bank whole inventories with DROP (96 v our 5). `drop_safe()`
  vetoes DROP whenever a unit carries feed wheat, which is most of the time.

**Raising the pickup cap does NOT work** (win rate, vs v25):

| cap | 6 | 8 | 12 | 20 |
|---|---|---|---|---|
| win rate | 28% | 8% | 0% | 0% |

Wheat spend rises 21,089 -> 32,112: bigger withdrawals drain the shed and the stateless feed
top-up re-buys. **v14's cap of 4 survives even on the corrected metric — do not re-test.**

**Open lead, untested: ROLE SEPARATION.** Our units carry feed wheat and harvested produce at
the same time, so they can never DROP and must PLACE one item type at a time. The trace agent
appears to split the jobs — its haulers carry produce only and bank it in one action. A build
where feed-carriers and produce-carriers are distinct would let DROP actually fire (it
currently fires 4-15 times a game against a possible ~96) and could recover most of the 331
wasted actions. This is the most promising untested idea on the board.

### 31. Role separation and day-dependent crew — both fail, and they complete the picture

**Role separation** (feeders fetch wheat and service animals; producers never touch wheat so
DROP is safe for them by construction) — the #30 fix. **Backfired.** Logistics share rose
24.9% v v25's 18.9%, PICKUP 389 v 310, DROP barely moved (18 v 4). Producers cannot FEED, so
the feeders make MORE trips to cover the herd.

| feed crew | 4 | 5 | 6 | 5 (DROP at 2+) |
|---|---|---|---|---|
| win rate | 0% | 0% | 25% | 0% |

It improves monotonically as it converges back on v25 — the restriction is the damage.

**Day-dependent crew** (the day 7-15 cash squeeze is over by day 18, so raise the cap once
cash is deep) — a good hypothesis, also fails:

| arm | crew 11 from d18 | crew 11 from d20 | crew 12 from d18 | crew 12 from d22 |
|---|---|---|---|---|
| win rate | 0% | 0% | 5% | 0% |

`money@d15` is IDENTICAL (+0) in every arm, so cash genuinely was not the constraint. What
falls is **strawberry revenue** (25,440 v 27,101): the extra late hands harvest and sell more
into a market that is already full.

### THE UNIFYING RESULT: our revenue is MARKET-CAPPED, so extra capacity has negative value

Every capacity-increasing change tested across three sessions loses, and always the same way
— production rises, revenue does not, costs do:

| change | outcome | what happened |
|---|---|---|
| 3rd/4th quadrant (23 arms) | loses | tiles planted, revenue flat |
| crew 11-14 (many arms) | loses | more harvest, prices fall |
| big-farm package (#28b) | 2% | 42 strawberry tiles, revenue flat |
| geese (#29) | loses | +6,249 eggs, crop tiles lost |
| profitability buying (#29) | loses | herd churn, straw revenue down |
| role separation (#31) | loses | logistics UP |
| day-dependent crew (#31) | loses | straw revenue down |

Milk and wool are LINEAR above target and saturate near $6.3k/$8.1k; strawberry is linear at
~$1.92/unit. **More production floods a market that cannot absorb it.** The 2026-08-11 rules
change (town demand halved) makes this STRICTER, not looser.

**So the open question is not how to produce more — it is how to SELL the same production
into a less-saturated market.** #28d is the sharp form: the big farm sold identical milk
units at a QUARTER of the price purely because the market carried ~50 more units at its sell
moments, and the trace agent sells 270 strawberry units to our 172 at the SAME realised
price, which saturation alone cannot explain. **Sell timing and spreading is the last
untested lever, and every production-side lever is now closed.**

### 32. Hungarian (optimal) assignment — implemented and REJECTED

Literature check: greedy nearest-unclaimed is the standard SUB-optimal baseline; minimum-cost
bipartite assignment (Hungarian / Jonker-Volgenant) is the optimality reference in
multi-robot task allocation. Implemented in pure stdlib (submissions cannot import scipy),
O(n^3), run once per turn over units x tasks. `scratchpad/hungarian.py`.

The earlier failed attempt (AA_globalassign) minimised PURE distance and starved the lower
tiers. This version puts priority and distance in one matrix so the solver trades them off:
`cost[u][t] = manhattan(u, t) - VALUE[tier(t)]`.

| arm (harvest/animal/water/plant/weed values) | win rate | delta |
|---|---|---|
| 12/12/8/6/3 | 18% | −3,443 |
| 20/20/10/6/3 | 2% | −5,670 |
| 8/10/6/5/2 | 15% | −4,785 |
| **30/30/15/8/4** | **30%** | −2,490 |

**It improves as the priority weights rise — i.e. as it converges on the greedy priority
chain we already have.** Optimal distance assignment is worse than priority-ordered greedy
here, for two measured reasons:

1. **Steps per productive job is already near-optimal: 1.09-1.13 v the reference's 1.03.**
   There is very little to win in walking-to-task.
2. **The logistics gap is SHED ROUND-TRIPS, which assignment does not touch** — PICKUP 459 v
   262, PLACE 255 v 25 (#30).

(It would also need the sweep's stability fix: the assignment is recomputed every turn, so
targets can swap between units mid-walk.)

**Conclusion: task-routing is a closed problem. The remaining step waste is entirely in shed
logistics.** Constraints already established there: `WHEAT_PICKUP_CAP` cannot be raised
(#30 — 6/8/12/20 give 28%/8%/0%/0% because bigger withdrawals drain the shed and the feed
top-up re-buys), and role separation makes it worse (#31).

**Untested idea that fits all the constraints:** raise the pickup cap AND hold a larger shed
wheat buffer so the bigger withdrawals cannot drain it — the measured failure mode at cap 8+
was shed drain, not the cap itself.

### 33. THE STEP GAP IS FERTILISER LOGISTICS — solved mechanically, not yet profitably

Chasing #30's 331-action logistics gap to its source. It is NOT wheat: wheat pickups are
210 v the reference's 209, and almost nothing is placed back. Broken down by item:

| | PICKUP fert | PLACE fert | total fert logistics |
|---|---|---|---|
| **v25** | **156** | **209** | **365** |
| trace | 39 | **1** | **40** |

**That 325-action difference IS the logistics gap.** And the reason is free money we were
leaving: **the engine auto-banks every carried inventory at the nightly rollover**
(`_drop_inventories_to_shed`). The reference agent simply CARRIES collected fertiliser all
day and lets the rollover bank it. We PLACE it by hand, then PICK IT BACK UP to apply it.

**Fix (`CARRY_FERTILIZER`): drop FERTILIZER from the mid-day flush. It works exactly:**

| | PLACE fert | PICKUP fert | logistics share | productive actions |
|---|---|---|---|---|
| v25 | 150 | 92 | 19.8% | 2,331 |
| **carry** | **13** | **4** | **13.3%** | 2,336 |
| trace | 1 | 39 | 14.7% | 2,485 |

**We become MORE step-efficient than the reference agent.** The long-standing "our labour
takes more steps" complaint is mechanically solved.

**But it loses on score: 15/40 = 38%, −2,588** — because fertiliser revenue halves
(21,972 -> 10,734, −$11,238). Carried fertiliser reaches the shed only at rollover and much
of it never gets sold.

Shed-capacity overflow was the obvious suspect and is **ruled out**: carrying thresholds of
3 / 5 / 8 give byte-identical results, so units never hold more than 3 and the cap never
binds.

**CORRECTED — the fertiliser "revenue collapse" was a MEASUREMENT ARTIFACT.**

Exact per-step money deltas (6 seeds), the only accounting proven reliable:

| | money IN | money OUT | final |
|---|---|---|---|
| carry | 107,614 | 30,518 | 80,096 |
| v25 | 111,081 | 31,736 | 82,344 |
| gap | **−3,466** | **−1,218** | **−2,248** |

The carry fix costs **−$3,466 of income, not −$11,238**, and saves $1,218 of spend. The real
cost is TIMING: carried fertiliser reaches the shed only at rollover, so it sells a day later
into a more saturated market.

**The "we sell 179 units we do not have" anomaly was also the metric, not a defect.** An
order that cannot fill is re-submitted next turn and counted again. The agent is correct.

**METHOD RULE (again, and this one has now bitten three times): never derive revenue from
SUBMITTED market orders.** They over-count re-submissions and ignore the per-unit price walk.
Use per-step money deltas. #27's "revenue is level", #28d's milk-price story and #33's
fertiliser collapse were all distorted by this.

**RESOLVED — the extra steps are a TRADE WE WIN, not waste.**

Every variant that removes the fertiliser round-trip lands on the same result:

| variant | win rate | delta |
|---|---|---|
| full carry (no mid-day fert flush) | 38% | −2,588 |
| carry with threshold 3 / 5 / 8 | 38% | −2,561 / −2,588 / −2,588 |
| bank surplus, keep 1 / 2 / 3 in hand | 38% | −2,767 / −2,742 / −2,769 |

The parameter never matters because units skip banking whenever fertiliser is wanted, which
is most of the time. **v25 spends ~242 extra actions a game on fertiliser round-trips and
earns +$3,466 for them (~$14/action), because shed-banked fertiliser sells a DAY EARLIER
than rollover-banked.** The reference agent takes fewer steps and forgoes that income.

**So "we take more steps than the trace agent" is TRUE and CORRECT.** Steps are not the
objective; money is. Our step count is higher because we run a fertiliser trade the reference
does not. **Do not optimise step count again without pricing what the steps earn.**

Kept for reuse: `CARRY_FERTILIZER` cuts logistics from 19.8% to 13.3% (better than the
reference's 14.7%) if a future build ever needs actions more than it needs the fertiliser
income. The step problem itself IS solved -- 13.3% logistics v the reference's
14.7%. Candidate: bank fertiliser opportunistically when a unit is already standing at the
shed, so it reaches the market same-day at no extra travel. Worth ~$11k, and the
step problem is already solved, so this single question converts a −2,588 arm into a likely
win. Best candidate: the sell path reserves or skips it, or it arrives after the day's sell
orders are already issued.

Also rejected this round: pickup cap + deeper shed buffer (cap 6/8/12 x buffer 2-3x, all
lose, −2,987 to −34,876 — the buffer ties up cash and wheat spend rises to 37,336).

### 34. HOW THE REFERENCE AGENT ACTUALLY WINS — it is the first 10 days

Localising the −14,666 income gap in TIME with per-step money deltas (4 seeds):

| day | our income | trace income | gap | our cash | trace cash |
|---|---|---|---|---|---|
| 6 | 559 | **1,569** | −1,010 | 934 | 2,410 |
| 10 | 2,848 | **4,301** | −1,453 | **383** | **3,792** |
| 14 | 3,227 | **5,978** | −2,751 | 19,276 | 19,960 |
| 16-20 | — | — | **+4,094 (WE lead)** | — | — |
| 22-26 | — | — | −4,984 | 54,225 | 62,245 |

**By day 10 it holds $3,792 and we hold $383 — ten times our cash.** We out-earn it in days
16-20; by then it has already converted the head start into producing assets and pulls away
again from day 22. Early income COMPOUNDS.

**Their opening is nearly identical to ours** (days 0-8, mean of 4 seeds):

| | HIRE | land | wheat/straw/melon seed | cows / sheep | MILK sold | wheat sold | fert sold |
|---|---|---|---|---|---|---|---|
| v25 | 47 | 1 | 23 / 15 / 12 | 6 / **2** | **6** | 68 | 75 |
| trace | 44 | 1 | 24 / 12 / 11 | 5 / **6** | **18** | 43 | 33 |

Same hires, same land, same seed mix. **Two differences: it runs 6 sheep to our 2, and it has
sold 18 milk by day 8 to our 6.** Wool is base $200 and first yields on DAY 6 — the earliest
high-value product in the game. Our early sales are fertiliser (75) and wheat (68), the two
cheapest goods.

### 34b. CORRECTION — the above is WRONG. It counted CASH, not WEALTH.

Cash alone is not the score at day 10; unsold stock is real wealth. Counting cash + shed +
carried + animals + standing crops:

| day | our wealth | trace wealth | gap |
|---|---|---|---|
| 8 | 6,469 | 10,688 | −4,218 |
| **10** | **24,176** | 18,728 | **+5,448 (WE LEAD)** |
| 12 | 27,519 | 26,812 | +707 |
| 14 | 29,936 | 35,696 | −5,760 |
| 18 | 45,708 | 52,510 | −6,802 |
| 24 | 78,126 | 93,388 | −15,263 |
| 28 | 87,096 | 102,348 | −15,252 |

**At day 10 we held $17,648 of shed and carried stock — we were AHEAD on total wealth, not
10x behind.** The opening is fine. The "first 10 days" conclusion above was an artifact of
measuring cash while ignoring inventory.

**The divergence starts at day 12-14 and widens monotonically after.** The column that tracks
it is STANDING CROP VALUE: they hold 4,120 to our 2,808 at d12 and 5,060 to our 2,900 at d18,
and theirs stays productive to the end (2,650 at d26) while ours decays to 310 by d28.

**So they keep a bigger PRODUCING farm alive through days 14-26.** This is the land question
again (#28), but with a much sharper signature than any of the 23 Q3 arms tested: the target
is standing crop value maintained in the second half, not tiles planted at day 20.

**METHOD RULE: measure WEALTH (cash + shed + carried + animals + crops), never cash alone,
for anything mid-game.** Cash-only comparisons mistake asset composition for a deficit.

### 35. The standing-crop gap needs LAND — crop mix is zero-sum on two quadrants

Following 34b: the divergence from day 12-14 tracks standing crop value. Decomposed:

| day | our straw / melon | trace straw / melon |
|---|---|---|
| 12 | 25.0 / **0.2** | 30.0 / **10.0** |
| 16 | 26.8 / **3.5** | 40.0 / **12.8** |
| 20 | 25.8 / **3.2** | 40.0 / **12.8** |

**A v25 regression found here: melon was almost eliminated.** The seed purchase buys ONE crop
per turn, strawberry first. Raising the strawberry target 19 -> 28 (v25) meant `straw_deficit`
never reaches zero, so MELON is never bought — 0.2 tiles standing at d12 against a target of
12. Melon has the highest base price in the game ($250).

Fixed by alternating strawberry/melon on turn parity, and extending
`MELON_LAST_PLANT_DAY`. **All arms still lose:**

| arm | win rate | delta | straw revenue |
|---|---|---|---|
| alternate, last plant d13 | 40% | −1,082 | 22,326 (v 27,377) |
| alternate, last plant d18 | 40% | −1,698 | 22,577 |
| alternate, d18, target 14 | 0% | −9,082 | 18,770 |
| alternate, last plant d22 | 40% | −1,698 | 22,577 |

**Melon displaces strawberry instead of adding to it** — two quadrants hold ~35 tiles, so crop
mix is ZERO-SUM for us. The reference stands ~56 crop tiles (40 straw + 12.8 melon + 3 wheat)
in the same window, which is more than two quadrants physically hold.

**Conclusion: the standing-crop advantage that opens the gap from day 12 REQUIRES the third
quadrant. It cannot be reached by crop mix, target tuning or planting dates.** That makes
#28d — why our three-quadrant builds sell into a crashed market — the single blocking
question for the whole project. Everything else is now measured and closed.

### 36. Third quadrant WITH every learned technique — matches the farm, fails the economics

Fair criticism taken: the techniques had been tested on TWO quadrants (where 35 tiles are
full and everything is zero-sum) while the three-quadrant builds were tested WITHOUT them.
Combined properly: Q3 + melon alternation (#35) + strawberry 42 + seed throughput +
plant-first + crew 11-12. `scratchpad/bigfarm2.py`.

| arm | win rate | planted@d20 | straw revenue | money@d15 |
|---|---|---|---|---|
| Q3 d11, crew 12 | 0/40 | **55.1** | 24,976 | −9,556 |
| Q3 d11, crew 11 | 2/40 | 51.7 | 23,564 | −9,083 |
| Q3 d11, melon to d22 | 0/40 | 54.5 | 19,524 | −10,743 |
| Q3 d14, crew 12 | 0/40 | 52.3 | 19,355 | −7,797 |
| **v25 (two quadrants)** | — | **34.2** | **31,024** | — |

**We finally MATCH the reference's farm size — 55 tiles against their ~56.** No earlier arm
did. And strawberry revenue FALLS versus our own two-quadrant build while holding more
strawberry tiles.

**Diagnosed: the big farm is under-fertilised and under-watered per tile.**

| | tiles @d18 | water per tile | FERTILIZE actions | fert per tile |
|---|---|---|---|---|
| 3 quadrants | 57.7 | 21.3 | **104** | **1.8** |
| 2 quadrants | 32.7 | 25.9 | **115** | **3.5** |

70% more tiles, FEWER fertiliser applications. Strawberry is ongoing: a fertilised checkpoint
yields +2 instead of +1, so half the coverage roughly halves the bonus on our best crop.
Supply is herd-capped — we collect ~290 and buy zero.

**Buying the shortfall makes it far worse:** 0/40, **−61k to −68k**, money@d15 −18,141,
strawberry revenue 15,737. Fertiliser purchases drain the day 7-15 ramp and the farm never
recovers.

**Pattern across EVERY three-quadrant build: money@d15 goes from ~0 to −8k to −18k, and score
tracks it.** The quadrant costs $4,000 plus extra seed plus extra wages inside the one window
where cash is binding. #28's dismissal of the cash explanation was based on the late-buy arm
(d16, money@d15 +0, only −5,603) — that arm avoids the squeeze and loses least. **The cash
window is real after all; it is the least-bad Q3 variant that proves it.**

**Status: Q3 reproduces the reference's FARM but not its ECONOMY.** The remaining question is
unchanged and now very sharp: the reference funds the same farm without the day 7-15 collapse
(#34b shows it is not ahead on wealth at day 10 — it is level, then pulls away from day 12).

### 37. The Day 10-12 inflection, traced to its root

Days 8-14, mean of 4 seeds (v25 | trace):

| day | melon $ | milk $ | harvests | land bought |
|---|---|---|---|---|
| 8 | 0 / 0 | **1,080 / 3,172** | **1.0 / 9.0** | — |
| 10 | 0 / 3,096 | 548 / 1,090 | 13.8 / 8.0 | **— / 1** |
| 11 | **12,028** / 5,968 | 0 / 538 | 5.5 / 7.0 | — |
| 14 | 0 / 801 | 1,689 / 1,066 | 2.8 / **12.0** | — |

**Day 8 is the first milk checkpoint and we bank a third of what they do.** They then buy the
third quadrant on day 10 with that money, and it compounds (#34b). Their harvesting is level
(8-12/day); ours spikes on day 10 catching up. Strawberry earns **$0 for both** through day
14, so our biggest crop plays no part in this inflection. Melon is not a problem either — we
dump 12,028 on day 11 against their spread 3,096+5,968 and still earn more over the window.

**ROOT CAUSE: `first_yield_day` counts from PLACEMENT, not from day 0.** Animal placement:

| | placed on day 0 | producing by day 8 |
|---|---|---|
| **v25 cows** | **1.0** | **1.0** |
| **trace cows** | **3.0** | **3.0** |

A cow must be on the board by day 0 to milk on day 8. They place 3, we place 1 — exactly the
3x day-8 milk gap. `herd_target` already asks for 2 cows before day 7, so the bottleneck is
upstream: PASTURES must be BUILT before an animal can be placed, and each build costs a turn.

**Two fixes tested, both fail:**

*Prioritise ripe livestock above crop harvest* (`scratchpad/ripe.py`): **no effect** — day-8
harvests stay at 1 for both, because we have nothing ripe to collect. Correctly built,
correctly measured, wrong hypothesis.

*Front-load the herd* so cows are placed by day 0:

| early cows / sheep | win rate | delta | money@d15 |
|---|---|---|---|
| 3 / 2 | 0% | −13,124 | −4,482 |
| **4 / 2** | **20%** | −4,737 | −7,294 |
| 3 / 3 | 0% | −13,191 | −11,089 |
| 5 / 2 | 10% | −6,860 | −4,261 |

**The diagnosis is right and the fix still does not pay.** Buying the earlier herd costs more
in the days 0-15 window than the earlier milk returns — the same wall every early-game
investment hits.

**Standing conclusion: our economy cannot fund ANY extra early asset — land, herd, fertiliser,
crew — without losing more than it gains. The reference funds all of them. That is now the
single unexplained fact in the project**, and it is an opening-economics question, not a
farming one.

### 38. Seat-bias audit — diagnostics are sound, and the trace gap is symmetric

Every ad-hoc diagnostic in #27-#37 ran us in seat 0 and the reference in seat 1, and the
engine handles atomic orders (HIRE, BUY_LAND) "in player order". Audited with two identical-
agent controls (`scratchpad/seatcheck.py`, 10 seeds each):

| configuration | seat 0 | seat 1 | diff |
|---|---|---|---|
| v25 v v25 (control) | 75,325 | 75,558 | **−232** |
| trace v trace (control) | 69,591 | 69,550 | **+41** |
| v25 seat0 v trace seat1 | 80,562 | 95,361 | −14,799 |
| trace seat0 v v25 seat1 | 95,312 | 80,572 | **−14,740** |

**Seat-balanced: ours 80,567 v trace 95,336, gap −14,770, we win 1/20.**

**No meaningful seat bias, and the gap is identical in both orders.** Today's diagnostics are
sound as measured.

**One real detail: in v25 self-play seat 0 wins 0/10 despite a margin of only 232.** Tiny but
perfectly consistent, so paired promotion tests MUST keep running both seat orders (tips.py
and panel.py do).

**And the honest framing correction:** we have never run the reference's pattern. Every arm
grafted one or two of its decisions (3 cows on day 0, a third quadrant, melon alternation,
14 hands) onto our own decision engine. Its 719-action replay is internally self-funding --
day-0 purchases pay for day-8 milk which pays for day-10 land. Transplanted fragments arrive
without the chain that paid for them, which is why every arm reproduces the MECHANISM and not
the MONEY. Independent support: kaitofukami reports freezing Seb's observed trace scored
0/50 for them.

**Also worth keeping in proportion: the reference is a top-30-class agent (~3,200 rating) and
we are rank ~1,351 (922).** Losing 1/20 to it is the expected result of a ~2,000-point gap,
not evidence of a defect. Progress is measured against the FIELD (panel win rate), where
v25 > v24 > v22 > v20, and the ladder has confirmed each step.

### 39. v25 is a LOCAL OPTIMUM — and the field's meta is derivative

Herd composition swapped rather than enlarged (day-0 spend in brackets):

| early cows / sheep | day-0 spend | win rate | delta |
|---|---|---|---|
| 3 / 1 | $1,700 | 0% | −8,385 |
| **3 / 0** | **$1,200 (CHEAPER than baseline)** | 18% | −3,595 |
| 2 / 1 | $1,300 | 12% | −4,515 |
| 4 / 1 | $2,100 | 0% | −11,005 |
| v25 baseline 2 / 2 | $1,800 | — | — |

**Even a strictly cheaper opening loses.** The day-8 milk diagnosis (#37) is correct and the
fix still fails, in both the "spend more" and "spend less, differently" directions.

**Every single-parameter move away from v25 now loses**: herd size, herd composition, land
(23 arms), crew (many), crop mix, melon timing, fertiliser buying, sell throttling, routing
(Hungarian), step efficiency, role separation, day-dependent crew, geese, profitability-based
purchasing. v25 sits in a local optimum.

### Field context (GitHub + public logs, 2026-08-12)

20+ public repos. Two useful and non-competitive: `rooklift/krobus` (replay viewer) and
`Beiciccc/Kaggriculture` (a 35-submission public experiment log). From the latter:

- **Independently confirms #26**: "Ranking is based on head-to-head wins, losses, and ties
  rather than final coin margin."
- **Ratings are very noisy**: their BYTE-IDENTICAL resubmissions opened at 681 / 724 / 735 /
  744 and drifted to 808 / 943 / 1046 / 1129. **Our 922 is inside normal variation; never
  read a single submission's rating as a verdict.**
- **Their band is ours** (700-1,130) despite a rigorous derivative programme with
  preregistered promotion gates. The ~3,200 tier is a different population.
- **A submission-killing trap we already guard**: their C17 scored 3000-3000 because
  "redefining an existing callable name did not move its insertion position, while the newly
  named helper became the last callable" -- Kaggle's loader took the wrong entrypoint.
  **Our pre-submission check that `agent()` is the last top-level function is load-bearing.**
- **The meta is derivative**: the top is largely attributed Apache-2.0 forks of a few public
  policies (Kaito, Moon, Rain, Rayk), modified and re-published.

**Strategic consequence: incremental tuning of our own basin is exhausted.** Further gains
need either a different basin (the field's approach: start from a strong public policy and
modify it, with attribution) or a genuinely new mechanism. That is a decision for the user,
not a measurement.

### 40. v26 SHIPPED (`84753ee`) — sheep-first opening, from decoding a public frontier route

#39 concluded v25 was a local optimum. It was — inside a cow-first assumption that had never
been questioned, because `herd_target` opens `cows = 2` and every herd arm varied cows.

Decoded the Apache-2.0 public route in prvsiyan's "The Moon Counts Melons" (a replay tape of
episode 91603791, team chunhu666). Its turn 0:

    HIRE x4, BUY_ANIMAL COW 1, BUY_ANIMAL SHEEP 4,
    BUY_SEED WHEAT 5, BUY_SEED MELON 5, BUY_PRODUCT WHEAT 5

~$2,982 of the $3,000 start, on turn 0, SHEEP-heavy — and only 5 melon seeds to our 12.

**Sheep first-yield on DAY 6, two days before cows, and wool is base $200 v milk's $160.**
The frontier early economy is WOOL-funded. That is precisely the window we were losing
(#37: their $1,569 v our $559 at day 6), and we had misdiagnosed it as a milk/cow-placement
problem.

| early cows / sheep | win rate |
|---|---|
| 3 / 1 | 0% |
| 3 / 0 | 18% |
| 2 / 1 | 12% |
| 4 / 1 | 0% |
| 1 / 4 | 40% |
| 2 / 4 | 60% |
| **0 / 4** | **90%** |

vs v25: original 36/40 = 90% (+5,623), fresh 38/40 = 95% (+5,751), **pooled 74/80 = 92.5%**.
Strawberry revenue rises too (33,175 v 31,938), so the wool-funded opening buys a better crop
economy rather than trading against it. Cows are untouched from day 7 on.

**Method lesson: "local optimum" was true only within an unexamined assumption.** Every herd
experiment varied the cow count because the schedule was written cow-first. Reading what a
stronger agent actually does broke the frame that all our own experiments shared.

**Decoding recipe** (these routes are base85+zlib, not opaque):
```python
b85 = re.search(r"AGENT_B85 = '(.*?)'", src, re.S).group(1)
source = zlib.decompress(base64.b85decode(b85)).decode("utf-8")
mod = types.ModuleType("m"); exec(compile(source, "<m>", "exec"), mod.__dict__)
mod._ACTIONS      # 719 turns of {'farmer':..., 'hands':[...], 'market':[...]}
```
Saved at `scratchpad/pub/moon_main.py`. **This tape is a readable frontier opening and the
rest of it has not yet been mined.**

### 41. v26 panel-confirmed, and the rest of the frontier route mined

**Panel (5 agents, 12 seeds, both seats, 240 matches):**

| agent | field win rate | Bradley-Terry |
|---|---|---|
| trace | 90% | 3.288 |
| **v26** | **72%** | **1.174** |
| v25 | 42% | 0.283 |
| v24 | 30% | 0.168 |
| v22 | 17% | 0.086 |

v26 beats v22 100%, v24 100%, v25 88%. **Field win rate 42% -> 72% is the largest single
jump of the project.** Submitted 2026-08-12.

**The frontier route's full capital plan** (`scratchpad/mine_moon.py`):

| | frontier route | v26 |
|---|---|---|
| early hands d1-6 | **1, 2, 3, 3, 3, 4** | ~5-7 |
| peak hands | **14** | 9 |
| land bought | **days 6 AND 10** (3 quadrants) | day 7 only |
| herd | 1 cow + 4 sheep d0; cows d5-8; 9 cows + 4 sheep total | 4 sheep d0, cows from d7 |
| geese | **zero** | zero |
| strawberry seed | 37 total, wave of **16 on day 10** | — |
| melon seed | **19 total** | ~12 by d8 alone |
| wheat seed | 148 total, incl. **49 on day 20** | — |
| feed wheat bought | 212 | ~600 |

Note it buys **a third of our feed wheat** (212 v ~600) for a comparable herd, and only 19
melon seeds all game.

**Skeleton early crew tested and FAILED:**

| day0 / early cap | win rate | delta | straw revenue |
|---|---|---|---|
| 4 / 3 | 0% | −6,202 | 26,755 (v 33,005) |
| 3 / 3 | 0% | −10,062 | 26,032 |
| 5 / 3 | 0% | −9,548 | 25,945 |
| 4 / 2 | 0% | −14,458 | 24,552 |

A 1-hand day 1 works inside a scripted route that knows exactly where each unit must stand;
our agent needs bodies to plant and water. **Same lesson as every other fragment transplant
(#38): the tape is self-consistent, our engine is not the same engine.**

**Still unmined and cheap to try:** feed wheat at a third of ours, melon seed at 19 total,
the day-20 wheat wave of 49, and the two-quadrant land schedule at days 6/10 (now that the
opening economy is wool-funded, which is the condition none of the 23 Q3 arms had).

### 42. Mining the frontier tape — one big win, four closed leads

The decoded route was read fully: capital plan, unit action mix, and sell rhythm.

**Its unit profile v ours:**

| | frontier | v26 |
|---|---|---|
| WATER | **1,010** | 845 |
| **PASS** | **994 (15%)** | ~113 (2%) |
| PICKUP / PLACE / DROP | **135 / 13 / 57** | 459 / 255 / 5 |
| FERTILIZE | **72** | 115 |
| PLANT | 199 | ~150 |
| MOVE share | 43% | 50% |

**It idles 15% of the time** -- crew deliberately oversized -- and spends the slack on
watering, not hauling. It independently confirms #33: 13 PLACEs to our 255.

**Its sell rhythm:** wheat 455u/39 orders, strawberry 286u/19, milk 241u/32 (7.5 per order),
fertiliser 235u/50, wool 132u/12, melon 114u in 16 orders of 7.1 (we dump melon in 16.3s).

**Leads tested from the tape:**

| lead | result |
|---|---|
| **sheep-first opening (4 sheep, 0 cows early)** | **SHIPPED as v26 — 74/80 = 92.5%** |
| skeleton early crew (1-4 hands to day 6) | 0/40 all arms, straw revenue 33,005 -> 26,755 |
| land at days 6 and 10 | 0-28%, empty@d20 back to 13-15 |
| strawberry last-plant day 15/17/19 | neutral (30-32%, +14 to −242) — target already met, and a strawberry planted after ~d19 cannot yield in time |
| feed from own wheat harvest (sell-reserve 2/3/5x) | 38/35/10%, best −431; wheat revenue 23,089 -> 8,955 |

**The wheat round-trip is genuinely break-even for us** — wheat has the gentlest price curve
in the game, so buying feed and selling harvest costs almost nothing either way. Their 212 v
our 600 feed purchases is a style difference, not an edge.

**Standing lesson: transplanted fragments keep failing (#38) while a transplanted
ASSUMPTION-BREAKER succeeded.** The sheep opening worked not because it was copied but
because it revealed our schedule was cow-first by construction and no experiment of ours had
ever questioned that. Look for what a stronger agent does that our code CANNOT express, not
for parameters to copy.

### 43. Four replay observations, all measured

From watching a downloaded opponent replay (4 quadrants, earlier melon sales, big day-11/12
cash jump, heavy animal spend).

**1. Melon selling — observation correct, fix loses.** They sell melon across days 10 AND 11
(7.1 units/order); we dump 12,028 on day 11 alone (16.3/order) into the steepest curve in the
game (`above: sq`, target 3.60), losing 26% of melon revenue to our own price impact v their
6%. Capping the melon chunk:

| chunk cap | 5 | 7 | 9 |
|---|---|---|---|
| win rate | 22% | 25% | 25% |
| delta | −329 | −261 | −218 |

**This is the FIFTH independent sell-throttle test to lose** (#27d global ratio, #33 fert
carry, melon here). Holding inventory always costs more than the price impact. **Settled --
do not retest.**

**2. Melon cannot be harvested earlier.** It starts at yield 1 and gains +1 per watered day
from age 6, so it caps at `max_yield = 6` by age 10 — exactly when `first_yield_day` first
permits harvest. `fert_worth_it`'s "melon never" rule is CORRECT: fertiliser cannot advance
the harvest, only waste a unit.

**3. Herd size — count confirmed, reduction loses.** 8 cows + 6 sheep = 14 structure tiles,
28% of a 50-tile farm:

| late herd | 5+4 | 6+4 | 6+5 | 7+5 | v26 (8+6) |
|---|---|---|---|---|---|
| win rate | 2% | 2% | 12% | 10% | — |
| planted@d20 | 39.0 | 39.0 | 38.6 | 37.6 | 35.6 |
| straw revenue | 23,678 | 23,678 | 24,121 | 25,379 | 26,502 |

Planted tiles rise and day-15 cash improves (+1,742), but **strawberry revenue falls**: the
freed tiles add strawberry to a saturated market while milk ($160) and wool ($200) sell into
separate curves. **Animal tiles out-earn crop tiles. 28% livestock is correct.**

**4. Wasted planting turns — not happening.** Correctly aligned (action at step i, effect
visible in obs i): 3 failed PLANT and 2 failed WATER per game out of 1,059 such actions --
**0.5% waste**. Structures are already ring-sited near the shed and excluded from
`plantable`.

(A first attempt at #4 reported a 100% waste rate. That was the step-alignment error from
#20 recurring -- action taken from step i-1 against tiles from i-1/i. **The alignment trap is
easy to fall back into; check that the "succeeded" bucket is non-empty before believing any
failure-rate measurement.**)

### 44. Staggered harvest (spread supply at the SOURCE) — three forms, all lose

Idea: instead of throttling SALES (5 previous tests, all lost because held stock costs more
than the price impact), spread supply by harvesting a mass planting in stages -- 25% at
yield 4, 50% at 5, 25% at cap. The crop keeps growing while it waits, so holding is free.
Genuinely different mechanism, and worth testing.

**Form 1 — stage all one-time crops** (25%/50%/25% by tile position, deterministic, no hash):

| split | (2,1) | (1,1) | (3,2) |
|---|---|---|---|
| win rate | 32% | 28% | 12% |
| delta | −157 | −19 | −4,327 |

Strawberry revenue rose (25,420 v 24,281) but **wheat fell** (22,698 v 25,024): wheat has the
gentlest curve in the game and never needed spreading, so staging it just discarded 2 units
a tile.

**Form 2 — stage MELON only.** All splits byte-identical to baseline: **it can never fire.**
Melon starts at yield 1 and gains +1 per watered day from age 6, so it is AT its cap of 6
exactly when `first_yield_day = 10` first permits harvest. There is no window in which melon
is harvestable and below cap.

**Form 3 — stagger melon by DAY instead** (hold ripe tiles 0/1/2 extra days; melon does not
decay until after `max_yield_day = 12`, so holding is free in YIELD terms): **0/40, −5,402.**
Seeds bought 107 v 120, wheat revenue 22,039 v 25,044.

**Why it fails, and the principle it establishes: TILE-DAYS ARE THE SCARCE RESOURCE, NOT THE
MARKET.** A melon taken at age 10 frees its tile for a replant; held to age 12 it costs two
tile-days of production. That cost exceeds the price impact of dumping.

This also explains why all five sell-throttles lost: the binding constraint is never
inventory or price, it is how many productive tile-days we can run. **Any future idea that
buys a better price by occupying a tile or a shed slot for longer starts from behind.**

### 45. Crop-plan and livestock-placement batch — all lose

**Melon-first rotation** (melon owns the land to ~d10, strawberry takes the freed tiles):

| arm | win rate | delta | straw revenue |
|---|---|---|---|
| melon 25 to d3, straw d11-16 | 0/40 | −11,470 | 25,080 (v 35,718) |
| melon 30 to d4, straw d12-16 | 0/40 | −16,924 | 20,112 |

Pushing strawberry to day 11 costs two of its four productions. Three arms returned identical
results, so the melon target was not even binding.

**Second quadrant all melon, wheat bought not grown:**

| melon / straw | wheat fill | win rate | delta | straw revenue |
|---|---|---|---|---|
| 20 / 15 | 0 | 2% | −15,477 | 18,556 (v 37,056) |
| 25 / 12 | 0 | 0% | −20,882 | 14,927 |
| 18 / 20 | 0 | 0% | −12,352 | 22,840 |
| 20 / 15 | 7 | 5% | −11,532 | 15,243 |

**Melon cannot replace strawberry as the primary crop.** Strawberry is ongoing (4 productions
per tile); melon is one-time. Per tile-day strawberry wins even at melon's $250 base.

**Livestock per-quadrant cap** (structures were ring-packed at the shed: measured 7 animals
in EACH of our two quadrants):

| cap | lands | win rate | delta |
|---|---|---|---|
| 5 | 2 | 5% | −10,769 |
| 6 | 2 | 2% | −5,596 |
| 5 | 3 | 5% | −6,049 |
| 4 | 3 | 0% | −7,776 |

On two lands a cap of 5 houses only 10 animals and the rest are bought but never placed. With
a third land it behaves as every other Q3 arm has. Combined with #43's herd-size test
(9/10/11/12 animals, all lost), **livestock count AND placement are both already right.**

**Melon staging is impossible, not merely unhelpful:** melon starts at yield 1 and gains +1
per watered day from age 6, so it is AT its cap of 6 exactly when `first_yield_day = 10`
first permits harvest. The engine never offers a melon below cap. All split settings returned
byte-identical results.

### 46. All tips COMBINED with the third quadrant — still loses, and they subtract

Fair test: each tip lost alone (#43-#45), but #28b showed single-lever tests can miss a basin
needing several levers, and #40 showed our own search misses things. So: third quadrant +
livestock capped per land + staggered harvest + more melon + wheat bought not grown, together.

| arm | config | win rate | delta | empty@d20 | money@d15 |
|---|---|---|---|---|---|
| TIP_a | Q3, 5/land, split (2,1), melon 18 | 2% | −10,748 | 9.6 | −4,405 |
| TIP_b | Q3, 5/land, melon 25, no wheat fill | 0% | −16,523 | 12.1 | −341 |
| TIP_c | TIP_a + crew 12 | 0% | −13,695 | 9.0 | −3,944 |
| **TIP_d** | Q3, 6/land, split (1,1), melon 14 | **12%** | **−4,432** | 12.1 | −3,156 |

**The ordering is the result: the arm closest to tips-OFF does best.** Plain Q3 alone scores
−4,000 to −5,000; TIP_d (tips nearly disabled) lands at −4,432, and the score degrades
monotonically as more tips are applied (−4,432 -> −10,748 -> −13,695 -> −16,523).

**So the tips do not merely fail to rescue Q3 — they subtract from it.** Q3's own signature is
unchanged throughout: 9-12 tiles still empty at day 20 and negative day-15 cash, exactly as in
the previous 30 configurations.

**Q3 status after ~34 configurations: closed unless the day 7-15 economy changes.**

### Ladder confirmation of v26

| version | rating |
|---|---|
| **v26 (sheep-first)** | **1,019.2** |
| v22 | 945.6 |
| v24 | 931.4 |
| v25 | 911.5 |
| v15 | 759.9 |

**First submission over 1,000 and the largest ladder gain of the project (+107.7 over v25).**
It confirms the local measurement (74/80, panel 42% -> 72%) rather than contradicting it.

Note v24 and v25 both scored BELOW v22 on the ladder despite winning locally — ratings are
noisy (a public log shows byte-identical resubmissions spanning 681-1,129), so that ordering
should not be over-read. v26's ~75-point clearance is outside that band.

**Pattern worth keeping: every version built by internal search sits in the 910-945 band. The
one built from reading an external agent (v26) broke past it.**

## 2026-08-15 — the balance patches

### #47. CARROT/TOMATO/EGG became situationally valuable — v27 opportunistic carrot

Two upstream balance patches landed, both announced by Kaggle:

- **1.32.6 / PR #1394** — town-centre demand cut from 2x/day (with a late 2x/4x
  multiplier) to a flat 1x/day, and **shops are now drawn WITH replacement**, so a town
  can roll 4x PET_CAFE and 0x YARN_STORE. Markets are much less resistant to sell
  pressure and per-product demand now varies wildly game to game.
- **1.32.7 / PR #1399** — CARROT, TOMATO and EGG got a **"hinge"** scarcity curve.
  Below I0 the price is now `base + below_target*base*(u + 8*max(0,u-1)^2)` with
  `u = deficit/T`: calm to the knee at T, quadratic past it. CARROT T=450 target **1.00**
  (was log/0.20), TOMATO T=200 target 0.40, EGG T=332 target 0.40.

**First: a live bug.** `game_data.MARKET_PARAMS` still held the pre-1.32.7 curves. That
table backs `sell_quantity()`, so *every* sell decision was being priced against a
fictional market. Fixed, and `analysis/verify_price_model.py` now asserts the replica is
identical to the engine for all 9 products over 6,005 inventory points each.
**Run it after every kaggle-environments upgrade.**

**Measured, 40 games, `analysis/market_scarcity.py`** (our agent grows none of the three,
so this is the untouched market):

| product | ends past knee | median price | max | base |
|---|---|---|---|---|
| TOMATO | **52%** | $91 | $445 | $60 |
| CARROT | **35%** | $63 | **$594** | $35 |
| EGG | 20% | $66 | $167 | $50 |

Kaggle's own announced rates are 50% / 26% / 22%, so the harness agrees with the source.
Spike size tracks the shop draw almost monotonically (carrot demand-weight 8 -> $594
median, weight 2 -> $51), which is the PR #1394 replacement change biting.

**EGG is not worth it** — a goose is $300 and p90 is only $96/unit. Arm dropped.

**Why carrot and not tomato first.** Carrot is $20, 3 days, 4 units, one-time, and in the
endgame it competes with nothing but wheat fill (break-even vs wheat is only ~$40/unit).
Tomato pays far more per tile but needs an 8-day commitment that would displace
strawberry. Carrot is the arm that risks nothing already proven.

**The gate must project, not observe.** Gating on today's price fired two days too late:
price ran $68 -> $101 over the last three days, so the crop went in on day 26-27 and half
of it was still in the ground at the buzzer — 16 tiles planted, **12 units sold**, 13
stranded in the shed. `obs["town"]["unlocked_shops"]` is observable and the consumption
schedule is fixed, so `game_data.daily_demand()` computes the drain exactly:

| day | predicted/day | actual/day |
|---|---|---|
| 25-29 | 49 | 49 |

Projecting the harvest-day price with it, same seed: **33 tiles, 69 units sold**, 6
stranded. `carrot_tiles_wanted()` also walks the price curve down one unit at a time and
subtracts crop already standing (`committed_units`), because the spike is a finite pool —
without that it re-sizes to the whole spike every turn and floods its own market.

**Result — `analysis/duel.py`, 20 seeds x 2 seat orders vs a carrot-disabled baseline
differing by ONE constant:**

| | v27 | baseline |
|---|---|---|
| wins | **23** | 9 (8 ties) |
| **win rate (decisive)** | **71.9%** | — |
| carrot planted / sold | 444 / 1,052 | 0 / 0 |

Attribution is unusually clean:

- In the **11 seeds where the gate never fired, mean margin is exactly +0** — every
  seat-order pair is a perfect mirror. The change is a strict **no-op** when it does not
  fire, so it carries essentially no regression risk.
- In the **9 seeds where it fired, mean margin +2,904**, and 7 of the 9 won *both* seat
  orders. The two that split were marginal 3- and 8-tile fires.
- Seed 2017: carrot at $252, margin **+14,861** — the size of the whole trace-agent gap.

The 71.9% understates the effect: non-firing seeds are exact mirrors that contribute one
win to each side by construction, pulling the rate toward 50%.

**Market-coupling check (the ledger rule for anything that changes what/when we sell).**
Both builds played the same 12 seeds x 2 orders against a neutral third party, the v14
snapshot, with all three sharing one `game_data.py` (v14 reads only `seed_cost` and
`first_yield_day`, so the shared table is behaviourally inert for it):

| | margin vs neutral v14 |
|---|---|
| v27 | **+48,601** |
| v26 baseline | +47,542 |
| **v27 edge** | **+1,059** |

Both win 24/24 against v14, so win rate saturates and only margin discriminates. The edge
against a neutral opponent (+1,059) is slightly **smaller** than the head-to-head margin
(+1,307), which is the reassuring direction — the paired test was not being flattered by
coupling. Carrot revenue is genuinely new money, not money taken from the opponent.

**Follow-ups, in order.** (a) TOMATO, worth ~$8k/tile against carrot's ~$680 and spiking
in 52% of games — the 8-day forecast is viable, since projecting with `daily_demand()`
gives **12.7% mean error at an 8-day horizon** against 56-73% for naive extrapolation,
and it errs low, which is the safe direction for a commit gate. (b) Sweep
`CARROT_MIN_MARGINAL_PRICE`; $70 is conservative against a ~$40 break-even.

### #48. Third quadrant re-enabled by request — loses 0/32, and it eats v27's carrot gain

Q3 turned back on at `LAND_SCHEDULE = {2: 7, 3: 10}` (day 10 is when the frontier agents
buy it, #34b). Requested explicitly with consequences accepted; recorded here for the
ledger, not as a promotion argument.

Mechanism fires: quadrants go 1 -> 2 (day 9) -> 3 (**day 12**, not 10 — cash gates it two
days; money sits at $69/$373/$341 across days 9-11).

**16 seeds x 2 seat orders vs v27, one line different:**

| | Q3 build | v27 |
|---|---|---|
| wins | **0** | **32** |
| mean margin | **−5,621** | — |

It loses in **both seat orders on all 16 seeds** — worst −13,138, best −1,161, never a
single win. This is the same day 7-15 cash wall as the previous ~34 configurations
(#28d, #36, #37): buying $2,000 of land at day 10-12 strands the ramp.

**New and worth keeping: Q3 actively suppresses the carrot arm.** Carrot planted/sold
collapses because Q3 eats the cash and the tiles that carrot would have used:

| seed | Q3 build | v27 |
|---|---|---|
| 2008 | 18 planted / **25 sold** | 33 planted / **104 sold** |
| 2006 | 12 / 18 | 14 / 37 |
| 2014 | 1 / 0 | 9 / 12 |

So Q3 does not merely fail on its own, it subtracts from the one arm that is working —
the same interaction #46 saw with the day-0 tips. **Any future Q3 attempt has to be
measured against a carrot-enabled baseline, or it will look better than it is.**

### #49. Why do real agents make 3 quadrants pay? Mined the 36-replay corpus

`analysis/q3_profile.py` profiles all 72 player-games in `replays/` day by day and
correlates the build against final reward.

**Two measurement bugs found and fixed first** — both would have inverted the reading:
- Hands vanish overnight and are re-hired during the day, so `len(hands)` at hour 0 is
  always 0. Use the day's PEAK crew.
- An occupied animal tile carries `animal` as a **single string** (`_new_animal`), not an
  `animals` list. Reading it as a list reported **0 animals for every player in every
  game**, which briefly looked like the headline finding ("the top agents keep no
  livestock"). It was entirely an artifact.

**Land is NOT the win condition.**

| metric | r vs reward |
|---|---|
| final quadrant count | **+0.02** |
| mean animals d8-15 | **+0.64** |
| mean animals d0-7 | +0.59 |
| mean STRAWBERRY tiles d8-15 | +0.43 |
| mean MELON tiles d0-7 | **−0.41** |
| mean hands d0-7 | +0.35 |

The day-bought correlations in the first pass (Q3 r=−0.50) were an artifact of using 99 as
a "never bought" sentinel — they measured *whether*, not *when*. **Among buyers only,
timing is worthless: Q2 r=−0.06, Q3 r=−0.02, Q4 r=+0.03.**

What the buy/don't-buy split does say:

| | bought | never bought |
|---|---|---|
| Q3 | **50,497** | 27,943 |
| Q4 | 32,599 | **41,903** |

So **three quadrants is the sweet spot and a fourth is negative** — which is why the raw
correlation with quadrant *count* is ~0. But this is observational and confounded: agents
that can afford Q3 are the ones whose economy already works. Our #48 result is the
controlled version of the same question (one line changed, 0/32), and it says buying Q3
does not create the economy that pays for it.

**We are not short of the things that correlate.** Our d8-15 animals (~11) and strawberry
(~28 tiles) both exceed the corpus top quartile (6.3 and 8.7).

**The one real lead is the single best build, 110,596 (`episode-90598134` p0), decoded:**

```
d0 h1:  HIRE x4
d0 h2:  BUY_LAND            <- Q2 on DAY 0, not day 7
        BUY_SEED WHEAT 44   <- 44 wheat in one order
        (~$1,447 of the $3,000 opening: $1,000 land + $440 seed + $7 fib hires)
d0-d2:  plant/water wheat with all 5 units -> 43 tiles standing by day 1
d3-d11: herd ramps 3 -> 14 (COW:5 SHEEP:9), wheat held at 33-43 tiles
d11:    Q3 + MELON 22 planted in one wave, cash $167 -> $3,236 -> $10,882 by d13
```

It **never plants a single strawberry**, and runs wheat->melon only. Against our build:
43 producing tiles in week one versus our ~18, because wheat is $10 with a 2-day yield
while strawberry is $100 with a 10-day one — the capital lockup lands exactly on the day
7-15 cash wall that has killed all ~35 Q3 attempts.

n=1, so this is a lead and not a law — but v26, the only version that ever broke the
910-945 band, also came from decoding one external agent rather than from internal search.

### #50. v28 wheat-rush: transcribing the 110,596 opening — FAILS, 0/20 and 0/24

Built the #49 lead as `variants/v28_wheatrush`: Q2 on **day 0**, 44 wheat in one order,
**no animal before day 3**, no strawberry ever, melon held to a single 22-tile wave at
day 11. A faithful transcription of `episode-90598134` p0.

**The opening reproduces exactly.** Day 0 ends 2 quadrants / 37-44 wheat tiles / 0 animals
/ **$1,488**, against the reference's $1,533.

**Then it starves.** Money pins at $0-17 from day 7, so the day-11 melon wave is never
affordable, and land goes bare (5-9 tiles on some days against the reference's steady
33-43). **0 wins in 20 paired games, mean margin −60,890.**

**Wheat is not the revenue for either build** — v28 sold 1,065 wheat and bought back 853;
the reference sold 554 and bought 570. Wheat is feed infrastructure that roughly pays for
itself. The reference's actual engine is **114 MELON** (base $250) plus milk 156 / wool
187. Strip the melon wave and there is no high-value crop left, which is exactly what
happened to v28.

**METHOD ERROR, recorded so it is not repeated.** Two ablations were run and scored by
SELF-PLAY reward on one seed:

| build | self-play reward (seed 2001) | vs v27, paired |
|---|---|---|
| v28 | 51,274 | −60,890 (0/20) |
| v28b (hands 9->12) | 61,723 | not run |
| v28c (herd held to day 12) | **70,345** | **−77,747 (0/24)** |

The self-play ladder said v28c was the big winner. Against a common opponent it is the
**worst** of the three. **Self-play absolute reward is not a strength measure** — both
seats change together and they share one market, so the number moves with the equilibrium,
not with strength. This is the market-coupling trap from #24/#28d in a new disguise.
**Always score a variant against a FIXED opponent.**

**Verdict: the wheat-rush direction is closed.** Its one portable-looking by-product
(hands 9->12, since the reference runs 12 to work 55 tiles while our cap was tuned on a
2-quadrant farm) was retested properly — `v27_hands12` vs `v27`, one constant apart —
and **loses 0/24, mean margin −8,930**. `FULL_HANDS_CAP = 9` stands, now bounded on both
sides for a THREE-quadrant farm as well. The self-play "+10k" was pure artifact.

**Everything the corpus offered has now been tested and none of it transfers.** #49's
correlations were observational; both controlled tests built from them (#48 Q3, #50
wheat-rush) lost decisively. The pattern from #39 holds: **v27 is a local optimum and
single levers moved off it lose**, whether the lever comes from internal search or from
copying a stronger agent's build. What actually worked this cycle (v26 sheep-first, v27
carrot) came from a NEW mechanism, not from re-weighting the existing one.

### #51. The public 3,094 agent decoded — land closed for the 4th time, sell-ranking wins

Pulled the highest-scoring public notebook, `salemali7/3094-score-kaggriculture`
("HarvestForge-X" / `BL-MDgogo-10C4S-R0`). Its agent is a base64+zlib blob: a **719-action
replay** plus generic execution guards, self-described as a behavioural reconstruction
from twelve public traces. Decoded to `public/salemali7_agent.py`; route extracted with
`importlib` (it is `_ACTIONS`).

**As a benchmark it beats v27 80% (16-4), mean margin +17,524.** That is now our target,
and a far better yardstick than the v14 snapshot.

**Its capital schedule, decoded:**

| | route | v27 |
|---|---|---|
| BUY_LAND days | **6 and 11 -> exactly 3 quadrants, never a 4th** | day 7 -> 2 |
| herd | **10 COW / 4 SHEEP** | 8 COW / 6 SHEEP |
| hands | **11-12 from day 8** | 9 |
| melon | 12 on d0, 20 by d6 | 12 |
| strawberry | 11 while small, then a **23-seed wave the day Q3 lands** (34 total) | 28 |
| carrot | **days 21-25** | our v27 arm, independently |
| wheat | bought constantly for feed (91 units on d23 alone) | same idea |

Two things worth noting: it stops at THREE quadrants, confirming #49's buy/don't-buy split
from the other direction; and it plants late carrot, which is the v27 arm arrived at
independently by a top-30 agent.

**v29 = that whole schedule transcribed onto our execution layer. LOSES 0/24, −21,242.**
(One real bug found and fixed on the way: with 2C+2S standing from turn 0 and
`OPENING_CASH_RESERVE = 50`, there was no money left for day-0 feed wheat and the entire
opening herd escaped on day 2. Raised to 260 and gave melon a ramp so it is not all bought
on day 0. The herd then survives — and it still loses.)

**LAND IS NOW CLOSED ON FOUR INDEPENDENT CONTROLLED TESTS:**

| test | what was added | result |
|---|---|---|
| #48 | Q3 alone at day 10 | 0/32, −5,621 |
| #50 | wheat-rush opening + Q3 | 0/20, −60,890 |
| #50 | ...plus hands and herd fixes | 0/24, −77,747 |
| **#51** | **full top-30 schedule, 3 quads, 10C4S, 12 hands** | **0/24, −21,242** |

**The reason is that the top agents are REPLAYS.** Their per-step execution is recorded
expert play; the capital schedule is only the visible part. Transcribing the schedule onto
a hand-written policy does not transfer the execution, and the extra land makes us *worse*
because our policy cannot work the tiles it adds. **Do not attempt a third quadrant again
without first improving per-tile execution.**

**What DID transfer: sell ORDERING.** The route ranks its sell orders by *price impact* --
`qty * (price_now - price_after_this_order)`, times a small urgency term from
`_demand_per_day` -- so the order with the most to lose from waiting goes out first. We
ranked by gross revenue, which puts big cheap orders ahead of small ones sitting on a steep
part of the curve. It matters because both players' orders interleave in one market and the
`sq`-glut goods (melon, wool) collapse fastest.

**v30 = impact-ranked sells. WINS 89.3% (25-3), +2,461 over 14 seeds x 2 orders**, and
sells *more* carrot through the same planting (642 v 618). One helper, no schedule change.
(`duel.py`'s "lever did not move" warning fires here because it watches carrot *planting*,
which is identical by design; the lever is the sell order.)

**v31 = v30 + terminal sweep.** Their `_terminal_liquidation` spends every spare order line
on the last 4 steps emptying the shed, since anything unsold at the buzzer is worth zero.
Ours reserved feed wheat and hit the 10-line cap, stranding late arrivals (6 carrots
measured, #47). **WINS 78.6% (22-6) over v30**, carrot sold 844 v 786. Margin is only +278
but promotion is by win rate.

**Q3 RETESTED INSIDE THE IMPROVED BUILD — still 0/24, −6,036 (fifth strike).** And it
suppresses the carrot arm again exactly as in #48: 74 planted / 118 sold with Q3 against
114 / 318 without. Land does not become affordable by making the rest of the agent better.

**HONEST LIMIT: none of this closes the benchmark gap.** v31 against the public 3,094 agent
is 20% / −18,340; v27 was 20% / −17,524. Statistically indistinguishable. v30/v31 are real
improvements *within our lineage* (which is what the ladder rewards, since most opponents
are mid-field) but they do **not** make us competitive with a top-30 replay. Beating that
needs better per-tile execution, not better book-keeping.

**SHIPPED as v33 = v27 + impact-ranked sells + terminal sweep, Q3 reverted.
Direct against v27: 96.4% (27-1), +2,682 over 14 seeds x 2 orders.**

### #52. THE MARKET CEILING — why land cannot pay, with the number

Ten controlled land configurations have now lost (#48 x1, #50 x2, #51 x1, #52 x6 below).
This entry explains the mechanism, and it is not about land at all.

**Measured total town demand, full 8-shop town, per season, at BASE prices:**

| product | demand/day | season units | value at base |
|---|---|---|---|
| STRAWBERRY | 25 | 550 | $66,000 |
| CARROT | 49 | 1,078 | $37,730 |
| MILK | 7 | 154 | $24,640 |
| WHEAT | 31 | 682 | $17,050 |
| TOMATO | 13 | 286 | $17,160 |
| EGG | 13 | 286 | $14,300 |
| MELON | 1 | 22 | $5,500 |
| WOOL | 1 | 22 | $4,400 |
| **TOTAL** | | | **$186,780, split between BOTH players** |

That is ~$93k each. **v33 already scores 80,008.** We are at the ceiling.

**Kaggriculture is a zero-sum race for a fixed demand pool, not a production game.**
The town buys a bounded number of units per day; anything produced beyond that drives the
price to the floor. Land, labour and crop tiles all scale SUPPLY, and supply is not the
binding constraint. This single fact explains every negative result in this ledger:

- adding a 3rd quadrant loses (supply up, demand flat)
- adding hands loses (wages up, sellable output flat)
- removing fertiliser logistics freed ~15% of labour and PLANT went 130 -> 129, because
  planting was never labour-bound
- filling new land with TOMATO also fails: total tomato demand is only ~13/day, so the
  whole season's tomato market absorbs ~286 units — about 7 tiles' worth, not a quadrant

**Supporting measurement — labour is spent on travel, and extra land does not add work:**

| | v33 (2 quadrants) | v33+Q3 (3 quadrants) | pub3094 (top-30, 3 quads) |
|---|---|---|---|
| total unit-actions | 6,177 | 6,302 (+2%) | 6,894 |
| MOVE | **49%** | **49%** | **50%** |
| PLANT | 130 | 138 | **187** |
| HARVEST | 291 | 303 | **394** |

Everyone spends half their labour walking. The benchmark does slightly LESS total work than
us and scores 60,004 to our 37,395 — it is not out-producing us, it is out-SELLING us.

**Configurations tested and rejected this round** (all vs v33, paired seats):

| variant | change | result |
|---|---|---|
| v34 | Q3 + hands 9->14 | 0/24, −23,243 |
| v35 | Q3 + hands 14 + 5-pen cap | 0/24, −26,138 |
| v36 | 5-pen-per-quadrant cap alone | 8.3%, −9,211 |
| v37 | meta herd 10C/4S from day 0 | 37.5%, −7,622 |
| v38 | stop hauling fertiliser to crops | loses |
| v39 | Q3 + tomato arm on the new land | loses |

The pen cap is worth a note: capping pens at 5/quadrant frees crop tiles but cuts the herd
from 14 to ~9, and milk+wool are $29k of the $186k pool. The freed tiles grow crops we
cannot sell. Net negative.

**CONSEQUENCE — the only way up is SHARE, not output.** Beating the field means taking a
larger slice of a fixed pool: selling before the opponent does, at better moments, into
products they are not supplying. That is why v30's impact-ranked sell ordering won (+2,461)
while every supply-side change lost, and it is why the public 3,094 agent ships a
`_PREEMPT_ENABLED` clone-preemption path (disabled in the published notebook) that front-runs
the opponent's sells. **Next work belongs there, and in the under-supplied hinge products,
not in more land.**

### #53. Share-capture round: adaptive herd WINS, order-slot and crop-mix arms fail

Following #52's conclusion that only SHARE of a fixed pool can grow, six arms were tried.

**Revenue audit first (seed 2001, v33) — where our money actually comes from:**

| product | units | revenue | $/unit | town demand/day |
|---|---|---|---|---|
| STRAWBERRY | 199 | $40,951 | **$206** | 25 |
| WHEAT | 554 | $22,911 | $41 | 31 |
| FERTILIZER | 265 | $19,788 | $75 | **0** |
| MILK | 189 | $12,980 | $69 | 7 |
| MELON | 72 | $9,216 | $128 | **1** |
| CARROT | 77 | $5,674 | $74 | **49** |
| WOOL | 174 | $4,498 | **$26** | **1** |

Strawberry sells ABOVE base ($206 v $120), so the town is still short of it.

**WINNER — v45 adaptive herd, 60.7% (17-11), +936.** PR #1394 draws shops WITH
replacement, so a town can roll no YARN_STORE at all; wool demand is then 1/day and wool
trades at $2.00 while strawberry sits at $212. We were still running a fixed 8C/6S herd.
`adaptive_herd()` keeps herd SIZE and moves only the split, weighting COW/SHEEP by measured
MILK/WOOL demand from the unlocked shops, engaging from day 7 once ~3 shops are known.
**v26's sheep-first opening was tuned before that patch** — this is the patch catching up
with it.

**THE REAL PRICING MODEL, corrected.** "Low town demand" does NOT mean "worthless":
demand/day governs price RECOVERY, but the curve's `T` governs price DECAY PER UNIT SOLD.

| product | base | glut curve | T | outcome |
|---|---|---|---|---|
| MELON | 250 | sq 3.60 | **300** | holds **$128** on 1/day demand |
| WOOL | 200 | sq 3.20 | **105** | collapses to **$26** on 1/day demand |

Same demand, opposite verdicts — which is why cutting sheep WON and cutting melon LOST.

**FAILED ARMS:**

| arm | idea | result |
|---|---|---|
| v40 | hoist ALL sells ahead of buys for queue position | 53.6%, −358 |
| v41 | hoist only the top-2 sells | 50.0%, +340 |
| v43 | size carrot by cumulative demand | no-op (the $70 floor still gates it) |
| v44 | melon 12->4, strawberry 28->40 | **0/28, −16,069** |

On v40/v41: the engine really does resolve market orders by INDEX in lockstep across both
players (`for i in range(max_len)`), so an earlier slot quotes against better inventory --
but hoisting sells pushes seed orders past the 10-line cap and the lost planting cancels
the price gain exactly. Queue position is real and worth ~0 net.

**Also measured and rejected:** intra-day timing. Price by position in the 4-step town
consumption cycle varies by only $0.34-1.38 on prices of $60-213. There is no
sell-on-the-right-turn edge.

**Also confirmed:** fertiliser is worth selling despite ZERO town demand — 237 units for
~$18,679 ($79/unit average) as the price walks $100 -> $43. Do not cut it.

### #54. CARROT_MIN_MARGINAL_PRICE sweep — the $70 floor is right, lower is worse

#53's revenue audit showed carrot demand at 49/day (~1,078 units a season) against our 77
units sold, which looked like the most under-exploited number in the agent. The obvious
read was that the $70 floor (2x base) was far too conservative, since carrot beats a wheat
tile at roughly $40. **That read was wrong.**

Swept against master (v45), 12 seeds x 2 seat orders each:

| floor | carrot planted | carrot sold | win rate | margin |
|---|---|---|---|---|
| **$40** | 632 | **1,608** | **29.2%** | −859 |
| **$50** | 404 | 952 | **33.3%** | −892 |
| **$70 (shipped)** | ~180 | ~400 | baseline | — |

Monotonic: the more carrot we plant, the worse we do. Selling 1,608 carrots instead of 400
LOSES. Carrot at $46-74/unit is worth less per tile-DAY than the strawberry and wheat it
displaces (strawberry ~$412/tile/day, carrot ~$99), so chasing the raw demand number spends
good tile-days on a cheap crop.

Raising the floor was then tried in the other direction and shows why the method rule
about fresh seeds exists:

| floor $85 | win rate | margin |
|---|---|---|
| 12 seeds (discovery) | 60.0% (12-8-4) | +79 |
| **22 seeds (confirmation)** | **47.1% (16-18-10)** | **−85** |

The 60% evaporated on a larger sample. **$70 stands, unchanged.**

**Carrot is a late-game filler for tiles that have nothing better to do, not a main crop.**
The high floor is what keeps it in that role. The 49/day demand is real but it is not
OURS to take profitably — supplying it costs more than it pays.

### #55. SEAT ASYMMETRY — identical agents score ~2% apart. Never read an unpaired game.

While debugging an apparent divergence in the conditional-land build, a null test settled a
question that has been contaminating every single-seed comparison in this project:

```
variants/null_copy/main.py  vs  main.py     (byte-identical files, different paths)
seed 2000 -> steps differing: 445 of 720
             rewards: 108,192 vs 110,260     (a 2,068 / ~2% gap)
```

**The two seats are not symmetric.** Seat 0 and seat 1 start in different board positions,
so identical code takes different routes from day 2 onward and scores ~2% apart. The gap is
larger than most of the effects we have been trying to measure.

Consequences, and they are retroactive:

- **Any single unpaired game is worthless as evidence**, including every "vs v33 on seed
  2001" number quoted while iterating. Only `analysis/duel.py` results (both seat orders,
  every seed) count. This is why it plays both orders.
- It also explains the mirror-pair rows in #47: seeds where the arm did not fire showed
  margins like [1978, −1978] — that is pure seat advantage cancelling exactly, which is
  the design working.
- A divergence between two builds is NOT evidence that a code change did something. Diff
  the actions against a null copy first.

### #56. CONDITIONAL third quadrant — buy land only in rich towns. Also fails.

Every prior land test bought Q3 unconditionally. Since PR #1394 draws shops WITH
replacement, town demand varies a lot between games (measured across seeds: crop demand
$2,650-$7,210/day at base, 2.7x spread), so land could be a bad average bet and still be a
good conditional one. `land_worth_it()` gates the third quadrant on demand projected to a
full 8-shop town, since only ~4 shops are known at the day-11 decision.

| build | gate | result vs v45 |
|---|---|---|
| v47 | all crop demand >= $6,200/day projected | 46.4% (13-15-8), −433 |
| v48 | fillable crops only, carrot-rich towns blocked | **35.7% (10-18-8), −1,072** |

v47's per-seed breakdown was genuinely informative — the gate DID win where it fired on
seeds 2003 [1061, 855] and 2016 [875, 1865], both orders positive. But seed 2017, the
+14,861 carrot-spike seed of #47, lost **11,702 and 8,885**. Counting carrot demand as
"rich town" made the gate fire hardest in PET_CAFE towns, which is exactly where the third
quadrant starves the carrot arm — the signal was self-defeating.

v48 removed carrot/tomato from the signal and blocked carrot-rich towns outright. It got
WORSE (35.7%), which says the remaining fillable-crop demand does not predict where land
pays either.

**LAND IS NOW 12 CONTROLLED CONFIGURATIONS, ALL NEGATIVE** (#48 x1, #50 x2, #51 x1,
#52 x6, #56 x2). Conditional purchase was the last structurally different idea available
to a computed policy and it did not work.

**The one approach not yet tried, and the only one with public evidence of working:
replay a route instead of computing one.** Every 3-quadrant agent we can actually verify
(the 110,596 corpus build, the public 3,094 agent) is a hard-coded action sequence, not a
policy. #52 explains why that matters: with ~50% of unit actions spent walking and a fixed
demand pool, the margin is in per-step execution quality, which a recorded expert route has
and a written policy does not. That path is derivative and the source notebooks ask forks
to retain attribution, so it is the user's call, not ours.

### #57. Replay backbone (v50) — WIP, 18,587 of the ~110,000 it needs

Per #56, the only 3-quadrant agents with public evidence of working are recorded routes,
not policies. Built one: `replay_agent/` embeds the player-0 action sequence of public
episode 90598134 (reward 110,596, three quadrants) from Kaggle's published episodes
dataset, with our own market layer on top (impact-ranked sells + terminal sweep, #51).
**Attribution is in the module docstring — the route is another competitor's play.**

Progress on seed 2001 against v45:

| build | reward | standing tiles at end |
|---|---|---|
| raw frozen trace | 2,857 | 2 |
| + cash floor $260 | 2,029 | — |
| + cash floor $100 | 5,027 | 8 |
| **+ farmer position resync** | **18,587** | 18 |
| + hand position resync | 18,587 (no change) | 18 |
| v45 for reference | ~111,000 | — |

**What was learned, and it is the useful part:**

- **A frozen trace really does collapse** (2,857), confirming the public claim that freezing
  an adaptive trace scores ~0. Days 0-2 track the source EXACTLY (31/43/43 tiles, money
  1,533/1,506/1,499), then weeds -- which spawn on different tiles every seed -- block a
  scheduled PLANT and knock the units off the route. Every later position-relative action
  then lands on the wrong tile.
- **Position resync is the single biggest guard: 5,027 -> 18,587 (3.7x).** If a unit is not
  standing where the recording stood, walking back beats firing a misaligned action.
- **Cash floor must be SMALL.** The route deliberately runs to ~$75 to buy seed; a $260
  floor starved its own seed buying and halved standing tiles. But zero is fatal too --
  hands vanish nightly, so $0 at end of day means no crew tomorrow, and the raw trace lost
  its whole crew on days 6 and 9 that way. $100 is about right (a 9-hand crew costs ~$88).
- **Hand position resync changed nothing**, so hand positions were already aligned. The
  remaining failure is action-level, not positional: BUY_SEED/HARVEST steps that the live
  state cannot satisfy.

**Still missing** is what the public 3,094 agent spends most of its code on: weed repair
with shift/repay bookkeeping (dig the blocking weed, then catch the route back up), and
projected-shed tracking so recorded sells match real stock. That is the remaining work if
this path is continued.

### #58. Both replay paths measured — the public agent wins, ours does not work

Built both routes to a 3-quadrant agent and measured them against v45.

| path | what it is | result vs v45 |
|---|---|---|
| **A: our own replay backbone** (`replay_agent/`) | episode 90598134's route + our guards | **18,587 vs ~111,000** (seed 2001) |
| **B: public 3,094 agent** (`variants/pub3094`) | salemali7's published notebook agent | **70.8% (17-7), +18,904** |

**Path B is the only thing that delivers what was asked**: three quadrants AND a decisive
win over our own line. It is a decoded copy of `salemali7/3094-score-kaggriculture`, itself
described as a behavioural reconstruction from twelve public traces.

**Path A stalled, and the failure is instructive.** Adding weed repair with a shift/repay
counter made it strictly WORSE — reward 0.0, two standing tiles, status DONE with no crash.
Holding the route index back for ALL units whenever any ONE unit digs deadlocks against the
position resync: the units are pinned to the held-back recorded positions and never advance,
so the farm buys seed forever and harvests nothing. **A correct implementation needs
PER-UNIT shift tracking**, not one global counter -- which is presumably why the public
agent carries separate `_SHIFT_STATE` and `_WEED_STATE` dicts per seat with due/repay
bookkeeping. Reverted to farmer-resync-only (18,587).

Honest position: reproducing a working replay agent is a real engineering project, not a
patch. The measured gap is 18,587 against ~111,000.

**DECISION POINT, and it is the user's, not ours.** Submitting path B means entering
substantially another competitor's agent under our own name. The source notebook is public
and published for forking with attribution retained, so it is permitted; whether to do it
is a call about the user's own entry. Nothing from path B has been submitted.

### #59. Path A drift guards — three designs, all worse than doing nothing

Continued the own-replay agent. Three ways to handle a unit knocked off the recorded
route, all measured on seed 2001 against v45 (~111,000-152,000 depending on coupling):

| guard design | reward |
|---|---|
| **step-locked cursor + position resync (kept)** | **18,587** |
| global shift/repay counter | 0 |
| per-unit cursors with daily re-sync | 920 |

**The rule: never hold a route cursor back.** The recorded positions change every single
step, so once a unit has drifted at all, "am I where the recording stood?" is true almost
every turn. Any design that withholds cursor advancement until the unit is back in position
makes it walk forever and never execute -- globally (reward 0) or per-unit (920). What works
is the opposite: advance the cursor with wall-clock step ALWAYS, and treat position
correction as a best-effort overlay that simply costs that unit its turn.

So path A's ceiling is not cursor bookkeeping. Getting a replay agent to work needs the
action-level guards the public agent carries (projected shed so recorded sells match real
stock, weed repair that does not desync, market-state tracking), or a different approach
entirely -- deriving a POLICY from the replay corpus rather than replaying actions.

**Path B was submitted** with attribution in both the module docstring and the submission
message: it is Salem Ali's public notebook agent, reproduced unmodified, entered because it
runs three quadrants profitably where twelve of our own configurations could not. Our own
line remains v45.

### #60. The ladder entry ships its share-capture path DISABLED — flipping it wins 95.8%

Our leaderboard rank is currently carried entirely by the public agent (rank **372 of
5,290**, score **2,344.5**, verified via the kaggle CLI 2026-08-19). Our own line, v45,
reads 973.6. So the question "how do we rank better" is really "what is wrong with the
entry that holds our rank", and there are two answers.

**Finding 1 (the lever). `_PREEMPT_ENABLED = False` in the submitted file.** The author
ships a complete clone-preemption path — `_preempt_shift` pulls tomorrow's scheduled sells
of the four premium goods (STRAWBERRY/MELON/MILK/WOOL) forward one step, with a
`_repay_shift` due-counter so nothing is sold twice — and then turns it off, with the
docstring noting "clone preemption is disabled in this experiment." This is exactly the
mechanism #52 says is the only lever left: **share, not output.** Front-run the opponent's
sell into a shared market.

Flipping that one constant, measured with `duel.py` (paired seats, win rate):

| test | opponent | result |
|---|---|---|
| **preempt ON vs the shipped OFF build** | itself (clone) | **95.8% (23-1), +891 over 12 seeds x 2 orders** |
| gate behaviour vs a non-clone | v45 | **fires 0 times, 3/3 seeds — strict no-op** |

Mechanism verified before reading the score, per the standing rule: on seed 2001 it fired
**11 times** and shifted **90 units** (WOOL 44, MILK 46) forward, reproducing that duel's
98,831-97,516 exactly. (`duel.py`'s built-in mechanism counter is the *carrot* one and is
meaningless for this lever — its "the lever did not move" warning is a false alarm here.)

**The gate is `_clone_distance(obs) <= 6`,** a public-signature distance between the two
farms. In a mirror it is 0 at every step; against v45 it is 10-44 and never once dips to 6.
So the win is **conditional on facing a route-clone** — pure upside where it fires, byte
-identical behaviour where it does not. That condition is common in our rating band
precisely because this notebook is public and 22/30 of the top-30 share a Day-0 signature,
but the ladder's actual clone share cannot be measured locally. Treat +891 as the
best case, not the expected case.

**Finding 2 (a real defect, small blast radius). The public agent still prices on the
pre-1.32.7 curves.** Its `_MARKET_PARAMS` hardcodes `log` for CARROT and `linear` for
TOMATO/EGG, while the engine gives all three the `hinge` curve (#47); `_market_price` has
no hinge branch at all. Measured error against `game_data.predicted_price`:

| item | at the knee (T) | at 1.5x T | at 2x T |
|---|---|---|---|
| CARROT | $42 vs $70 (-40%) | $42 vs $158 (-73%) | $43 vs $385 (**-89%**) |
| TOMATO | exact | $96 vs $144 (-33%) | $108 vs $300 (-64%) |
| EGG | exact | $80 vs $120 (-33%) | $90 vs $250 (-64%) |

It also corrupts `_impact_score`, which takes `current_quote` from the real market but
`later_quote` from this model: past the knee it scores a 20-unit carrot sell at 2,320 when
the true impact is 280, an 8x overestimate.

**But do not overrate this.** The route buys 14 CARROT seed and sells 15 CARROT, plants no
TOMATO, and keeps no geese, so the mispricing touches ~15 of the ~3,830 units it sells a
game. It is worth fixing on principle, not for points. **Not shipped and not measured** —
recorded so the next session does not rediscover it and assume it is the big win.

**Nothing submitted.** Two constraints govern that call and both are the user's:
- **Only the latest 2 submissions score.** They are currently pub (2,344.5) and v45
  (973.6), so exactly **one** slot can be spent without risk; a second new submission
  evicts the pub entry and the rank goes with it.
- Flipping the flag means submitting a **modified** version of another competitor's agent.
  The attribution block must stay and the modification must be disclosed in it.

### #61. The top-10 corpus — and the finding that "the top are replays" is WRONG

Scraped **373 episodes played by the top 10 teams** (`analysis/scrape_top_episodes.py`),
to test whether a cloned policy is worth building. It is, and the audit overturned a
belief this ledger has carried since #48.

**Getting the data.** Kaggle's episode API has **no team filter** — `ListEpisodes` accepts
only `{"ids": [...]}` or `{"submissionId": N}`. Two traps: the bundled
`kaggle_environments.api` helper is **stale** (its `/requests/EpisodeService/` base URL
400s; the live one is `/api/i/competitions.EpisodeService/`), and `GetEpisodeReplay` is
**404 / gone** — replays now come from the authenticated CLI, `kaggle competitions replay
<id> -p <dir>`. The way to a specific team is that every `ListEpisodes` response also
returns a `teams[]` array carrying each team's `publicLeaderboardSubmissionId`. So the
scraper seeds from our own submission and BFS-walks up the ladder, always expanding through
the highest-rated team not yet queried. Matchmaking is rating-based, so it took **7 hops**
from us (2,344) to all ten targets (2,908-3,149). Replays are ~31 MB each and gzip **62x**,
so they are stored gzipped and the raw file deleted: 11.6 GB of transfer, **197 MB on disk**.

**Corpus: 373 episodes, 2,925,126 target-seat unit-decisions, 373/373 seat labels verified**
against the replay's own reward array. Best rewards **143,984-168,259**, versus 110,596 for
the best thing in our own 36-episode `replays/` set and ~111,000 for v45. 7x the data and a
markedly stronger teacher.

**First audit looked like a death sentence.** Only **6 distinct day-0 openings across 373
episodes**, and 9 of the 10 teams open *identically in every game they play* — one opening
covers 57.6% of the corpus and is shared across teams. That is the #48/#56 "the top are
hard-coded replays" story, apparently confirmed.

**It is wrong.** Measuring modal-action agreement across seeds per team
(`analysis/corpus_determinism.py`) shows the scripted part is only the opening:

| team | rank | overall agreement | steps identical in ALL seeds |
|---|---|---|---|
| tetsuya | 1 | **0.282** | 10.8% |
| Ryo Hasegawa | 2 | **0.305** | 8.9% |
| Galaxantic | 10 | 0.775 | 27.5% |
| ReCurSiON | 6 | **0.945** | 70.7% |

For Ryo Hasegawa the day-by-day profile is a cliff: day 0 agreement **1.000**, days 1-4
0.93-0.85, day 7 0.43, and from day 15 to the end **0.05** — which with 20 episodes is the
floor, i.e. every episode does something different. **85.7% of all steps have <90%
agreement.** These are not replays. They are policies with a scripted ~4-day capital
opening (the modal 5-hire/2-cow/2-sheep queue we already decoded) and ~25 days of genuinely
reactive play.

**Two consequences that matter.**

1. **This explains the public agent's ceiling.** `salemali7`'s notebook builds its route by
   taking the *majority action across twelve traces*. That method **destroys exactly the
   state-conditional behaviour measured above** — it collapses a reactive policy into a
   fixed 719-step route. Which is why the reconstruction scores ~2,344 while the agents it
   was reconstructed from score 2,908-3,149. The missing ~700 points is the reactivity that
   majority-voting averaged away. **Cloning real episodes preserves what majority-voting
   throws out**, so BC is strictly better than another reconstruction.
2. **Reactivity tracks rank at the top.** The two most reactive agents are ranks 1 and 2;
   the near-pure replay (ReCurSiON, 0.945) sits at rank 6. So **curate the training set**:
   train on tetsuya and Ryo Hasegawa, and exclude or downweight ReCurSiON, which would
   mostly teach a fixed route.

**Caveat, stated honestly:** low agreement proves actions *differ* across seeds, not that
they differ *usefully* — some divergence is position drift rather than deliberate
conditioning. But a drifted replay would still show correlated actions, and 0.05 across
the whole back half is near-total divergence. Either way the actions are state-dependent
in effect, which is what BC needs.

**Verb mix on the target seat** (2.93M decisions): moves 44.3%, WATER 12.1%, PASS 8.5%,
HARVEST 5.1%, SELL 4.8%, FEED 4.1%, CARE 4.1%, COLLECT_FERTILIZER 4.0%, PLANT 2.4%. The
corpus is dominated by routing and tending — which is precisely the per-step execution #52
identified as the margin, and the one thing our hand-written policy cannot express.

Next: feature design, then a held-out-episode BC baseline. Note the deployment constraint —
do not assume torch exists in the submission sandbox; train in torch, export to numpy, and
embed the weights base64 in `main.py` the way the public agent embeds its route.

### #62. Ladder ratings INFLATE early then decay — a peak score is not a result

Reading the two live submissions' per-match rating deltas (`analysis/submission_progress.py`,
and the deltas are in the `ListEpisodes` payload as `initialScore`/`updatedScore`) shows the
rating system is TrueSkill-shaped: the step size collapses as a submission's uncertainty
shrinks, so **almost all of a submission's rating is earned in its first ~45 matches**.

| segment | pub 55555746 win pay | net/match | rating |
|---|---|---|---|
| first 25% (46) | **+64.08** | +40.42 | 600 -> **2441.3** |
| 2nd 25% | +5.99 | -0.35 | 2441.3 -> 2425.0 |
| 3rd 25% | +4.75 | -0.51 | 2425.0 -> 2401.6 |
| last 25% | +4.12 | **-2.23** | 2401.6 -> **2296.6** |

Same shape on the preempt build (68 matches): win pay **+98.29 -> +19.10 -> +8.32 -> +5.38**,
net/match +65.56 -> +11.22 -> +2.98 -> **+2.29**.

**Consequences, both of which we got wrong before measuring:**

1. **A submission cannot grind its way up once the step decays.** At +5.38 a win and +2.79
   net per match, climbing 1,995 -> 2,292 needs ~107 more matches *and the step keeps
   shrinking the whole time*, so the true asymptote is well below a linear projection.
   **Do not read "still climbing" off a positive trend** — check the step size first. This
   corrects the previous session's reading of the preempt build as merely "young".
2. **The peak rating is inflated and the converged one is the real one.** pub banked 2,441
   during its high-uncertainty phase against a weaker pool, and has been corrected DOWNWARD
   ever since: **-145 over its last 47 matches, with a 15% win rate against a mean opponent
   of 2,326.** Its "2,344 / rank 372" was never its strength; it was its uncertainty.

**And this independently confirms #61 on the live ladder.** The public reconstruction wins
**15%** of its matches at the 2,326 level. That is exactly the predicted failure: majority
-voting twelve traces collapses a reactive policy into a fixed route, and against the real
reactive agents at the top of the ladder the route loses. The ladder is telling us the same
thing the corpus audit did.

**Practical:** rank is set by the BEST of the latest 2 submissions, and both slots are ours
(preempt + pub), so nothing is at risk right now. But **pub is the older of the two — one
more submission evicts it.** Both are converging toward roughly 2,050-2,200 from opposite
directions.

### #63. BC feature design — and a unit policy at 79.8% on held-out episodes

Built the cloning pipeline and validated that the features carry signal.

**The encoder (`analysis/features.py`) is shared by training and inference.** Any drift
between how features are built at train time and play time silently destroys the policy and
is invisible in training metrics, so there is exactly one code path. For the same reason its
constants come from `game_data` rather than a local copy — that is precisely the bug that
left the public agent pricing carrot 89% wrong after 1.32.7 (#60).

**Everything is shaped by one constraint: `actTimeout` is 1 second per step** for a farm of
up to ~15 units. So the encoder splits into what is shared per step and what is per unit:

| piece | dim | computed |
|---|---|---|
| `global` | 82 | once per step |
| `grid` (22 channels x 10x10) | 2,200 | once per step |
| `unit` (position, carry, tile-under, nearest-work vectors, 5x5 egocentric patch) | 325 | per unit |

Measured **2.3 ms per step for all 12 units** — 400x inside the budget. The network mirrors
the split (`relu(Wg@glob + Wr@grid + Wu@unit)`), so the expensive half is projected once per
step and only a small matmul runs per unit.

**Action space is small and clean** (`analysis/action_space.py`): the corpus emits **27
distinct unit classes, top 20 covering 99.74%**. Completed to **35 classes** so every legal
op has a slot — a never-predicted class costs one logit, a missing one silently mislabels
data. PICKUP counts (1-6) go to a separate head instead of multiplying the vocabulary.
Market orders are a **separate model**: 19 verb|item classes, and **80.35% of steps emit no
market order at all**.

**Extraction** (`analysis/extract_bc_dataset.py`) stores relationally — per-step features
once, unit rows pointing at them — because storing the 2.2k-float grid per unit would
duplicate it ~12x. 80 episodes (tetsuya + Ryo Hasegawa, the reactive pair #61 identified)
gave **576,592 unit-decisions in 32 s, 27 MB**. Both seats' observations were verified
complete in the replays first.

**Baseline (`analysis/train_bc.py`, numpy, ~15 s/epoch): val accuracy 0.7984 vs a 0.1427
majority-class baseline — a 5.6x lift.** Split is **BY EPISODE**, never by row: units in one
game share a board and market, so a random row split leaks across the boundary.

Per-class recall says something useful about *what* it learned:

| learned nearly perfectly | learned poorly |
|---|---|
| FEED 0.977, PICKUP\|WHEAT 0.935, PLANT\|WHEAT 0.923, CARE 0.918, COLLECT_FERTILIZER 0.919, WATER 0.915, PASS 0.907, HARVEST 0.889 | WEST 0.679, EAST 0.698, SOUTH 0.702, NORTH 0.754, FERTILIZE 0.577, **DROP 0.286** |

**Task selection — what to do on arrival — is essentially solved. Movement is the weak
half**, which is expected: several routes to the same tile are equally good, so top-1
accuracy understates movement quality. DROP at 0.286 is a real gap worth a look.

**Train loss 0.536 vs val loss 0.551 means this is UNDERfit, not overfit** — capacity,
epochs and the remaining 293 episodes are all still on the table.

**What this does NOT prove.** 79.8% action agreement is not 79.8% of the skill. BC suffers
compounding covariate shift: a 20% per-decision error rate walks the agent into states the
expert never visited, and this environment punishes exactly that (a frozen trace scores
2,857 — #57). **The only verdict that counts is `duel.py` against v45.** Do not read the
accuracy as a result.

### #64. The BC label was leaking — obs[i] contains the effect of action[i]

The first playable BC agent scored **0** against v45's 123,483. The diagnosis is worth
recording in full because the bug was invisible in every training metric and this ledger
had already warned about it.

**Symptom.** The agent never hired — 0 hands for the whole game — spent its 3,000 on 34
animals with no pasture to put them on, was broke by step 120, and emitted PASS 639 times.
Live and training step-0 features were verified **byte-identical**, so it was not feature
drift.

**Cause.** In a replay, the observation stored at index `i` ALREADY contains the effect of
the action stored at index `i`:

- step 0: `money 3000, hands 0`, action `PASS` / no orders
- step 1: **`money 25, hands 5`** — and the five `HIRE` orders are in *that same entry*
- of 365 WATER actions sampled, **365 had `watered_today` already true** on the unit's own
  tile; under the shifted pairing, **0** did.

So the decision that produced `action[i+1]` was made at `obs[i]`. Training `obs[i] -> action[i]`
teaches "`watered_today` is set, therefore emit WATER" — a rule that is unlearnable at play
time because the live agent sees the tile *before* it acts.

**This inflated #63's headline number.** The 0.7984 val accuracy was partly the model reading
the answer off the observation, which is exactly why the suspiciously strong classes were the
ones whose effects are visible in the tile they act on: WATER .915, FEED .977, CARE .918,
COLLECT_FERTILIZER .919, HARVEST .889. **Treat #63's per-class recalls as void.**

**Fix** in `extract_bc_dataset.py`: iterate `range(len(steps) - 1)` and pair
`steps[i].observation` with `steps[i+1].action`. Step 0 now correctly carries the modal
opening — `HIRE x5, BUY_SEED WHEAT 7, BUY_SEED MELON 12, BUY_ANIMAL COW 2, SHEEP 2,
BUY_PRODUCT WHEAT 6` — which matches the opening decoded independently in #48.

**The lesson is the meta one.** "Observation at replay step i already includes the action
recorded at step i" was ALREADY in this ledger's method rules, written down from an earlier
session, and it was not applied when building the extractor. A high validation number was
taken as evidence the pipeline was right. **A BC pipeline's first check should be an
adversarial one — verify the label is not visible in the input — before reading any
accuracy at all.**

**Market model note.** A single 0.5 threshold left the rare-but-essential classes at ~0
recall (SELL|WOOL 0.000, BUY_ANIMAL|COW 0.000, BUY_PRODUCT feed 0.010) — an agent that
never buys feed is not playable. Per-class thresholds calibrated for F1 on held-out episodes
lifted overall F1 **0.484 -> 0.604** and brought every essential class alive (HIRE .880,
SELL|WHEAT .793, feed .574, COW .572).

### #65. BC agent v1 plays badly — 84.7% per-decision accuracy, ~1 reward

**Result: the cloned agent does NOT work yet.** Against v45 it scores **1 vs 97,325**
(seed 2001) and **1 vs 160,558** (seed 2002). Recorded in full because the failure is
informative and the pipeline underneath it is sound.

**Offline the models are fine** — unit policy **0.8473** held-out (35 classes, majority
0.1463), market policy **F1 0.685** after per-class threshold calibration. Inference runs
at **6 ms/step** against a 1,000 ms budget.

**Three real bugs were found and fixed on the way**, each of which moved it:

1. **Label leakage** (#64) — `obs[i]` contains the effect of `action[i]`. Score 0.
2. **Hire slot starvation** — the crew-rebuild guard claimed all 10 market order lines, so
   `BUY_SEED` could never be emitted and the farm planted **nothing for 30 days**. The
   corpus opening spends exactly 5 lines on HIRE and 5 on seed/stock. Capped at 5.
3. `gd.CROPS[c]["seed"]` is spelled **`seed_cost`** in `game_data` — a silent KeyError that
   killed the agent at day 0 and looked like a strategy failure in the trace.

**The remaining failure is economic, and the trace is unambiguous** (seed 2001, day/money/
hands/planted/seeds/shed):

```
  0    239   9   3  15   0
  2     63   9   8   8   0
  3      9   8   9   5   1
  4      2   4   9   5   1
  6      1   0   0   5   1
```

The opening works — 9 hands, 9 tiles planted, seeds bought. Then **money bleeds to zero by
day 4 and never recovers**, the crew (wiped nightly by the engine) cannot be rebuilt, and
the farm is dead for 24 of 30 days.

**Cause: it never closes the produce -> sell loop.** Over days 0-5, with 9 tiles planted,
it emitted **WATER only 26 times** — roughly 4/day for 9 thirsty tiles — so crops never
reached yield, the shed stayed at 0-2 units, and there was nothing to sell. Meanwhile
**PICKUP fired 166 times** (1.88% of the corpus, ~15% here) and **PASS 408**.

**So the deployment action distribution is badly skewed versus the training distribution,
even though per-decision accuracy is 84.7%.** That is textbook BC covariate shift: small
per-step errors move the farm into states the top-10 corpus never contains (broke, 3 hands,
2 planted tiles), and inside those states every prediction is extrapolation. This
environment punishes it hard — the same reason a frozen trace scores 2,857 (#57).

**Contributing design error**: the legality mask deliberately left `PICKUP` unmasked to
avoid over-constraining, and `PICKUP` promptly became the second-most-common action. Masking
too little is as harmful as masking too much; the wasted turns compound into the cash bleed.

**Next, in order of expected value:**
1. **Execution-guard layer.** Mask `PICKUP` unless the unit is on the shed or a tile holding
   produce, and force the obvious on-tile work (WATER a thirsty tile, HARVEST a ready one)
   rather than letting a soft argmax skip it. This is precisely the action-level guard code
   the public 3,094 agent spends most of its lines on (#58) — the guards are not a detail,
   they are the product.
2. **DAgger-style correction** — roll the policy out, collect the states it actually visits,
   and label them from the nearest corpus behaviour. Straight BC cannot fix its own drift.
3. Only then revisit capacity/epochs. The model is still underfit (train .402 / val .439),
   but underfitting is NOT the binding constraint — the deployment gap is.

**Do not read the 0.8473 as progress toward a score.** It measures agreement on states the
expert visited, and the agent's problem is the states the expert never visited.

### #66. Execution guards — the farm survives now, but still loses decisively

Added the guard layer #65 called for. **It fixed the collapse and did not fix the score.**

**First, a measurement that changed the design.** Before hard-coding "always harvest a ready
tile", `analysis/ontile_conditionals.py` measured what the top-10 agents actually do while
standing on obvious work (target seat, #64 alignment):

| standing on | what experts do |
|---|---|
| READY crop (yield>0) | WATER 20%, **HARVEST 18%**, WEST 15%, EAST 13% |
| THIRSTY crop | **WATER 45%**, WEST 14%, EAST 10% |
| UNFED animal | FEED 23%, NORTH 23%, PASS 17% |
| at SHED carrying goods | **DROP 18%**, NORTH 16%, WEST 12% |

**So forcing is wrong.** Experts harvest a ready tile under one time in five and drop at the
shed under one time in five — they walk *through* tiles constantly, and the local tile does
not determine the action. A "force the obvious work" guard would have driven the policy
*away* from expert behaviour while looking like a fix. Guards are therefore **hard legality
only**, from the engine's own preconditions:

- `PICKUP` requires shed adjacency (tiles `(4,4) (4,5) (5,4) (5,5)`) AND stock of that item.
- `DROP` requires shed adjacency AND something carried.

**Effect on stability is large.** Before/after on seed 2001:

| | v1 (#65) | with guards |
|---|---|---|
| crew at day 9 | **0** (dead since day 6) | **9** |
| tiles planted | 9 peak, 0 by day 6 | 12-15 sustained |
| tiles reaching yield | ~0 | **all planted tiles** |
| wasted PICKUP | 166 in 6 days | 0 |

**Effect on score is nil.** BC 1 / 1 / 5,381 against v45 128,159 / 129,658 / 167,252.

**The remaining gap is production, and it is quantified.** With the farm alive, units stand
on a ready tile **567 times** and harvest on ~4% of them against the expert's 18% — roughly
a 4.5x under-harvest — and the farm carries 12-15 planted tiles against the expert's 40-58.
It also over-waters (92% on a thirsty tile vs the expert's 45%). Production never reaches
the level where sales can fund the next round.

**This is the covariate-shift wall, not a missing guard.** Every state the agent occupies
(12 tiles, ~$200, 9 hands) is one the top-10 corpus never contains, and inside those states
the policy's action distribution drifts from what it scored 0.8473 on. Legality masking
removes wasted turns; it cannot move the policy back into the training distribution.

**What is actually needed next — and it is not more guards:**
1. **DAgger-style relabelling.** Roll the policy out, collect the states it actually visits,
   label them from the nearest corpus behaviour, retrain. This is the only step that
   addresses the distribution mismatch directly.
2. Failing that, seed the early game from the known modal opening (#48) so the farm reaches
   expert scale before the learned policy takes over — a hybrid, but an honest one.

**Do not add more legality guards expecting a score change.** The legal-action space is now
correct; the problem is which legal action gets chosen, in states the expert never visited.

### #67. Scripted opening + deterministic navigation — still ~6k against ~143k

Option 2 from #66: hand the learned policy a farm at expert scale instead of asking it to
build one. **It did not work either**, and the reason is now pinned down precisely.

**First, the decisive control.** `analysis/verify_agent_path.py` replays corpus states
through `bc_agent/main.py`'s OWN code path — same encoder, same weights, same legality mask —
and scores the chosen action against the expert's:

```
ACCURACY THROUGH THE AGENT PATH: 0.9162     (trainer reported 0.8473)
  HARVEST 0.984   FEED 0.997   CARE 1.000   WATER 0.973   PLANT|WHEAT 0.962
  top confusions:  WEST->SOUTH 450,  EAST->SOUTH 443,  NORTH->WEST 322
```

**So the agent is wired correctly** — features, weights, label indices, unit ordering and
mask all agree with training. Every remaining failure is distributional, not a bug. Run this
control FIRST next time; it separates "mis-specialised policy" from "broken plumbing", which
look identical from the outside and had cost two rounds of guessing.

**Two interventions, both grounded, both ineffective:**

1. **Scripted market opening** (`analysis/extract_opening.py`, `opening_schedule.json`).
   Mined the dominant day-0 cluster (40 episodes): agreement **1.000 on days 0-2, 0.951 on
   day 4**, 21 scheduled steps over 5 days. Only MARKET orders are replayed — they are
   state-independent, so unlike a unit route they cannot desync. Result: **no change** (1/1/1).
   The opening only buys ~20 seeds; scale was never set there.
2. **Deterministic navigation.** Since the confusions are almost entirely MOVE-vs-MOVE, keep
   the learned choice of WHAT to do on a tile and compute WHERE TO WALK by priority
   (harvest > thirsty > plantable > animals), with claim-marking so the crew does not
   converge on one tile. Result: **606 / 1 / 6,310** against v45's 172,645 / 158,441 /
   142,974.

**The best case is now legible, and it fails in a new place.** On seed 2003 the crew holds 9
all game and **money recovers to ~6,000 by day 18** — the economy finally works. But planted
tiles fall to **1-5**, and **82% of unit actions are moves** (corpus: ~44%), with WATER 222,
HARVEST 97, PLANT 111 across a whole game.

**The farm stops replanting while holding 6,000 in cash.** Experts run near zero because they
reinvest continuously, so "6,000 in hand, 2 tiles planted" is a state the corpus never
contains — and the market head, asked to extrapolate there, does not buy seed. Fixing the
crew exposed the cash bug; fixing cash exposed the replanting bug. **Every intervention has
fixed one failure and revealed another of exactly the same kind.**

**Conclusion: stop patching.** Three rounds of guards (#66, #67 x2) each corrected a real
defect and none moved the score, because the defect is never the mechanism — it is that the
policy is being queried outside its support. The only remaining honest options are
**DAgger-style relabelling** (roll out, collect visited states, label from nearest corpus
behaviour, retrain — a real project, not a patch) or **abandoning BC** and keeping v45 as
our line. Given the 2026-09-23 deadline, that is a call about how to spend the remaining
weeks, not a technical question.

**Kept regardless**: the corpus (373 episodes, 2.6M decisions), the encoder, both models, the
scrape/audit tooling and `verify_agent_path.py` are all reusable and committed. The BC agent
is NOT submitted and must not be — v45 remains our line.

### #68. BC pushed 1 -> ~21k, still loses 0-12 to v45 — and the corpus finds a v45 bug

**The BC agent went from ~1 to ~21,000 in one session.** The lever was not the policy:

| change | seeds 2001/2002/2003 |
|---|---|
| #67 baseline | 606 / 1 / 6,310 |
| **+ keep the land full** | **13,888 / 15,426 / 10,181** |
| + cash-aware crop plan (wheat while poor, melon/strawberry when rich) + seed batch cap | **16,651 / 21,158 / 21,222** |

Ryo Hasegawa (168,259) runs `empty` tiles at ZERO from day 3 — every seed bought is
planted at once. Our agent sat on 25 idle tiles. That one capital rule was the whole 4x
production gap, and it is a rule, not a policy subtlety.

**Controlled A/Bs run against that baseline, all negative — record them so they are not
retried:**

| arm | result |
|---|---|
| buy land on the expert clock (Q2 day 6, Q3 day 10) | 4,632 / 7,704 / 5,205 — **worse, twice** |
| drop livestock entirely | 15,482 / 12,172 / 18,029 — worse |
| feed-first navigation priority | 14,986 / 10,506 / 4,401 — worse |
| CREW_TARGET 12 / 14 | ~3k / ~1k — Fibonacci wages |
| CASH_FLOOR 100/200/300/600 | 11k/11k/16k/7k vs 150's 21k — **non-monotonic = noise** |

All six top episodes buy quadrant 2 on day 6-7 and quadrant 3 on day 10-11, without
exception, and it STILL loses for us: we cannot afford it when they can. **#56 now holds
for the BC agent as well as the hand-written one.**

**Verdict on BC: `analysis/duel.py bc_agent/main.py main.py 6` gives 0-12, mean margin
-116,820.** It does not beat our own line and will not in the time left. Parked, with the
corpus, encoder, models and tooling all kept.

### #69. The corpus as GROUND TRUTH — v45 stops replanting after day 12

Since BC lost, the 373 episodes are worth more as a measuring stick than as training data.
`analysis/v45_vs_corpus.py` profiles v45 against the top-20 episodes, day by day:

| day | corpus plant | v45 plant | corpus quad | v45 quad | corpus money | v45 money |
|---|---|---|---|---|---|---|
| 3 | 17 | 18 | 1.0 | 1.0 | 157 | 94 |
| 9 | 37 | 35 | 2.0 | 2.0 | 2,121 | 326 |
| 12 | **56** | **33** | **3.0** | 2.0 | 11,702 | 13,308 |
| 18 | **58** | **33** | 3.0 | 2.0 | 43,524 | 28,669 |
| 24 | **53** | **24** | 3.0 | 2.0 | 105,197 | 60,051 |
| 27 | **51** | **21** | 3.0 | 2.0 | 130,635 | 72,419 |

**v45 tracks a 3,100-rated agent EXACTLY to day 9** (35 planted vs 37, both on 2 quadrants).
Everything diverges after that, in two separate ways:

1. **The corpus takes quadrant 3 at day 10-12 and jumps to 56 planted.** Known, and closed
   for us on ~35 configurations (#48/#56, re-confirmed above).
2. **NEW, and not explained by land: v45's planted count DECAYS from 33 at day 12 to 21 at
   day 27, while the corpus holds 51-58 flat.** Animals only account for 3 of those tiles
   (15 -> 18). v45 is letting roughly a dozen tiles fall out of production for the back half
   of the game — on land it already owns and already paid for.

**This is a gap the ledger has looked straight past.** #? measured weed ROT loss at
$157/game and concluded weeds were not worth chasing. That accounted for the produce lost on
the tile, and never for the OPPORTUNITY COST of the tile sitting fallow: ~12 tiles idle for
~15 days, on a farm whose whole output is ~30 tiles. The rot is trivial; the vacancy is not.

**Next, and it is on our REAL line, not the BC branch:** make v45 keep replanting through the
back half — clear dead tiles and re-seed them instead of letting the farm shrink. Corpus
says the target is flat 51-58 planted; v45 should at minimum hold its day-12 33 rather than
sliding to 21. Measure with `duel.py` against current v45, promote on win rate.

### #72. The meta moved to ROUTE PORTFOLIOS and we were optimising a single route

We were stuck at ~1,900 while the top sits at ~3,136. The reason is architectural, and three
independent public notebooks found it before we did.

**Pulled and decoded five current public agents** (`kaggle kernels list --competition
kaggriculture --sort-by voteCount`; each embeds its agent as a base64/b85+zlib payload, so
decode with the same trick used on salemali7). All five are forks of the SAME
`BL-MDgogo-10C4S-R0` base as our pub line.

**Absolute strength -- margin vs a NEUTRAL third party (v14), 6 seeds, base 5000.** This is
the measure that coupling cannot fake:

| agent | vs neutral v14 |
|---|---|
| **prvsiyan (Frontier V113)** | **+80,016** |
| flexonafft (multi-route) | +74,481 |
| our pub_v3 | +74,348 |
| indarkarhana ("Rank Top10") | +73,532 |
| pub_v1 (base) | +73,532 |
| pub_v2 | +73,440 |
| boatlee (V16-RC5) | +70,756 |

**pub_v2 is level with pub_v1 here (+73,440 vs +73,532), which independently confirms the
#70 coupling warning: its ladder gain was share capture, not strength.** pub_v3 is +816 over
base -- a real but small gain.

**Head-to-head, 8 games each, seeds 5000+:**

| | indarkarhana | flexonafft | prvsiyan | boatlee |
|---|---|---|---|---|
| pub_v1 | 50% | **0%** | **0%** | 100% |
| pub_v2 | 100% | **0%** | **0%** | 100% |
| pub_v3 | 100% | 75% | 50% | 75% |

Our route-swap work was real -- 0% -> 75% against flexonafft -- but it caps there.

**THE ARCHITECTURE WE ARE MISSING.** prvsiyan's V113 carries **five route tables** --
`_ACTIONS_10C4S_3Q`, `_ACTIONS_6C12S_4Q_FIRST_YARN`, `_ACTIONS_6C12S_4Q_SECOND_YARN`,
`_ACTIONS_6C8S_3Q`, `_ACTIONS_8C6S_3Q` -- and selects one at RUNTIME from the unlocked-shop
sequence (`_kawa_route_label`), then layers reactive carrot/tomato arms, a late plan, and
post-weed replant repair on top. flexonafft ("yarn-led, milk-supported, or balanced") and
indarkarhana ("read the market, choose the farm") do the same thing.

**We have been tuning ONE fixed route. The meta is portfolios keyed on the shop roll.** That
is why the shop sequence matters so much: #53 showed demand composition decides which
products pay, and PR #1394 draws shops WITH REPLACEMENT, so the right farm plan genuinely
differs game to game. A single route cannot express that.

**Both of our edges are already in prvsiyan** -- `_PREEMPT_ENABLED = True` and CARROT/TOMATO/
EGG on the `hinge` curves. There is nothing of ours left to bolt on; it is ahead, not
adjacent. (flexonafft, by contrast, has preempt but **zero** occurrences of "hinge" -- it
still carries the carrot mispricing from #60.)

**Where our unique asset still applies:** prvsiyan hand-built its five routes from public
replays. We hold **373 episodes of the top ten** plus proven screening machinery
(`analysis/route_search.py`), and #71 showed screened routes beat hand-picked ones and that
episode reward is anti-predictive. The open move is to screen a better route PER
SHOP-CONDITION CLUSTER and swap them into a portfolio agent -- the v1->v3 trick applied to an
architecture that starts ~6,000 stronger.

### #73. Portfolio build: the route slot is a FARM COMPOSITION, not a shop condition

Started swapping our corpus routes into the portfolio agent (#72). The first attempt failed
in a way that identifies the real constraint.

**Setup.** The portfolio agent stores each route as its own b85+zlib blob
(`_ACTIONS_10C4S_3Q`, `_ACTIONS_6C12S_4Q_FIRST_YARN`, ...), so one bucket can be replaced
with the selector, the other four routes and every guard untouched -- a clean one-variable
A/B. Tooling: `analysis/portfolio.py` (classify), `portfolio_swap.py` (swap),
`portfolio_duel.py` (duel reporting win rate PER BUCKET).

**A measurement design note worth keeping:** the shop roll is NOT a pure function of the
seed. `_end_of_day` draws weed spawns from the same RNG *before* it picks a shop, so what the
agents do changes which shops unlock. Pre-mapping seeds to buckets is therefore invalid;
`portfolio_duel.py` records the bucket each game actually landed in and groups afterwards.

**First attempt: classify corpus episodes by the shop roll they FACED.** All three swaps lost
0-14, but the margins split sharply:

| swapped route | source | margin in the 10c4s bucket |
|---|---|---|
| ep92777801 | ReCurSiON, 166,656 | **-103,473** |
| ep94439800 | tetsuya, 165,467 | **-99,799** |
| ep93819271 | peikopon, 160,658 | **-3,908** |

**A -100k collapse is not a weak route, it is a broken agent.** The cause: `10c4s_3q` names a
FARM COMPOSITION -- 10 cows, 4 sheep, 3 quadrants -- and the guards (feed guard, room guard,
pen logic) act on the farm that route builds. Drop in a route that buys a different herd and
the guards operate on a farm that does not exist.

**Re-classified all 373 episodes by what the route actually BUILDS** (BUY_ANIMAL totals + max
quadrants) rather than the shops it saw:

| composition | episodes | best reward |
|---|---|---|
| **10C4S_3Q** | **143** | 160,658 |
| 6C12S_4Q | 49 | 154,540 |
| 9C4S_3Q | 37 | 166,656 |
| 6C8S_3Q | 15 | 150,653 |
| 8C6S_3Q | 12 | 124,324 |

The two that collapsed were **9C4S_3Q** and **12C3S_3Q** -- wrong composition for the slot.
The near-parity one was the best **10C4S_3Q** episode in the corpus. That is the whole
explanation, and it maps our compositions onto four of the five slots directly.

**Rule for any future route swap: match the slot's composition first. A route is not a
portable recording; it is the thing the guards are written against.**

**Open question the screen is answering:** prvsiyan's hand-built 10c4s route still beat the
BEST composition-matched episode we have (-3,908). Its routes are evidently cleaned rather
than raw recordings. Since #71 showed episode reward is anti-predictive, the screen now
samples 12 candidates ACROSS the 143-episode reward range rather than taking the top.

### #74. Portfolio swap WORKS: our screened route beats the leading agent's own

Composition-matched screening (#73) against prvsiyan's hand-built `_ACTIONS_10C4S_3Q`,
scored per route bucket so the other four slots do not dilute the signal. 12 candidates
sampled ACROSS the 143-episode reward range:

| route | episode reward | in-bucket, discovery seeds |
|---|---|---|
| **ep94469751** | 135,608 | **10-0, +3,150** |
| ep94397452 | 142,764 | 10-0, +2,022 |
| ep93949700 | 131,799 | 10-0, +1,901 |
| ep93491727 | 117,695 | 4-2, +1,455 |
| **ep93819271** | **160,658 (corpus best)** | **0-4, -5,166** |
| ep92772579 | 125,960 | 0-6, -14,705 |

**Episode reward is anti-predictive AGAIN, and this time decisively: the highest-reward
10C4S_3Q episode in the entire corpus LOSES, while three mid-reward ones beat the base
10-0.** That is now three independent confirmations (#71 route search, #72 route ranking,
this). Never pick a route by its episode score; screen it.

**Winner confirmed on disjoint seeds:**

| | in-bucket | overall |
|---|---|---|
| discovery 5000+ | 10-0, +3,150 | 17-1 (94.4%), +1,824 |
| **FRESH 9000+** | **9-3 (75.0%), +1,183** | 15-5 (75.0%), +763 |

The usual discovery shrinkage, and still a clear win. **This is the first time we have beaten
the strongest available agent using something only we have** -- the 373-episode top-10 corpus
plus screening. prvsiyan hand-built its five routes from public replays; one of ours is
better than its best in the bucket that covers most games.

Packaged as `submit_pf1/` -- base agent with exactly one route blob replaced, selector and
guards untouched.

**Remaining headroom:** the other three slots (6C12S_4Q with 49 corpus episodes, 6C8S_3Q with
15, 8C6S_3Q with 12) are untouched, and 18 candidates are built. Screening them needs a
seed -> bucket map, because those buckets almost never come up on arbitrary seeds -- 10c4s
dominates. Each slot is independent, so the wins should stack.

### #75. RANK 31 -- and the #1/#2 replays show a structural gap: the wheat churn

**Ladder, 2026-08-23: rank 31 of ~5,900, score 2,693.3.** `pf_all` (Frontier V113 with all
five route slots corpus-screened) is 32-3 (**91.4%**) in 35 matches and still climbing;
prvsiyan unmodified sits at 2,540.9 (76 matches, 75.7%). The corpus-screened routes are what
took us past the top-100 target.

**A real regression found from a ladder loss, and fixed.** Losing to "Vibe Farmer" (rated
2,625) by 889 looked like bad luck; the replay showed it was not. Vibe Farmer is the SAME
agent family -- identical 4 quadrants, 6C/12S herd, 12 melon, 42 strawberry. We out-SOLD it
on nearly everything and our sell revenue was **+15,938 higher**, yet we lost, because:

| category | us | Vibe Farmer |
|---|---|---|
| HIRE | $5,977 | $5,977 (identical) |
| ANIMAL | $8,400 | $8,400 (identical) |
| **FEED (BUY_PRODUCT)** | **$56,741** | **$28,611** |

Our 6c12s route pick (ep94369942) bought **1,312 feed units** against the base's 800-987 --
a fixed count baked into that recording. Rebuilt the slot with ep93867727 (838 feed):
mean feed cost **$57,436 -> $37,181**, now BELOW the base's $39,711, and the stack improved
from 78.6%/85.0% to **87.5% (21-3) on fresh seeds 47000+**.

**Note the trap: lowest feed is NOT best.** ep93783010 uses the fewest feed units in the
corpus (673, exactly matching Vibe Farmer) and collapsed **0-12, -36,172**. Feed volume is a
symptom to check, never an objective to minimise.

**THE STRUCTURAL GAP (from 5 head-to-head #1 vs #2 replays, episodes 96622153/96651842/
96816183/96870933/96925730):**

| | feed units | feed cost | wheat sold | quads | herd |
|---|---|---|---|---|---|
| **Ryo Hasegawa (#1, 3,132)** | **86-143** | **$3.0-5.8k** | 247-417 | 3 | 12C2S, 8C6S, 12C5S, 11C3S, 7C9S |
| Subramanya N (#2, 3,055) | 166-300 | $6.4-11.9k | 217-383 | 3 | 9C10S, 4C8S, 11C2S, 8C7S |
| **our pf_all2 (2,693)** | **837** | **$37,181** | **1,817** | 3-4 | fixed per slot |

Two differences, both structural rather than route-quality:

1. **We run a WHEAT CHURN and they do not.** We grow ~1,800 wheat, sell all of it, then buy
   ~840 units back as feed. They grow modestly, sell 250-400, and barely buy feed. Every
   churn cycle pays the market spread AND, at T=400, drives the wheat price down against our
   own remaining sales. #52 said the game is a zero-sum race for a fixed demand pool; this is
   us paying twice to move the same wheat through the market.
2. **Their herd composition varies EVERY GAME** -- 12C2S, 4C8S, 9C10S, 11C3S, 7C9S. That is
   adaptive, chosen on something finer than our five fixed compositions keyed on the shop
   roll. Our portfolio commits to one of five recorded herds; theirs is computed.

That is the first difference we have found that is not "a better recording", and it is the
most plausible explanation of the 2,693 -> 3,132 gap. Attacking the churn is the next move:
stop selling wheat that will be repurchased as feed.

### #76. The wheat churn is NOT fixable inside this agent family

#75 found the structural gap: the #1 agent buys 86-143 feed units a game, we buy 837, because
we grow ~1,800 wheat, sell it all, then buy ~840 units back to feed the herd. Two attacks,
both negative, and together they close the question.

**1. A sell-side guard reproduces the profile and loses.** `_wheat_churn_guard` keeps a
rolling feed reserve (shed capacity is 100, so stockpiling is impossible) and skips a feed
purchase while it is covered. It works mechanically -- feed **435 -> 222 units**, wheat sold
**683 -> 317**, squarely in the top-2 band -- and then loses badly: 87,658 vs 120,163 and
109,104 vs 143,207.

The reason is instructive. Suppressing SELLs does not stop the route PLANTING ~1,800 wheat.
With a 100-slot shed the unsold surplus simply goes nowhere. **The churn is a property of the
route's crop mix, not of the sell logic.**

**2. Low-churn routes do exist in our corpus -- and they do not transplant.** Scanning all 373
episodes for feed volume (range 77 to 1,314, median 487) turns up the top-2 profile, and it
belongs almost entirely to **Ryo Hasegawa, the current #1**:

| episode | reward | feed | wheat sold | composition |
|---|---|---|---|---|
| 94406847 | 107,086 | 77 | 556 | 6C10S_3Q |
| **94401941** | 97,451 | **84** | 385 | **10C4S_3Q** |
| 94442170 | 147,301 | 83 | 227 | 7C4S_3Q |

Dropped into our 10c4s slot -- including ep94401941, which matches the slot composition
exactly, the condition that mattered in #73 -- all three collapse:

| route | vs pf_all2 |
|---|---|
| ep94401941 (composition-matched) | **0-12, -146,033** |
| ep94405973 | 0-12, -134,853 |
| ep94461751 | 0-12, -134,787 |

**Conclusion: the lean feed profile is a property of Ryo Hasegawa's WHOLE AGENT, not of a
transplantable route.** Composition matching was necessary (#73) but is not sufficient; a
route also depends on the guard stack it was recorded under. Within the BL-MDgogo family the
churn is structural, and closing the 2,693 -> 3,132 gap needs that family replaced, not
retuned.

**Do not retry**: sell-side churn guards, or importing low-feed routes into BL-MDgogo slots.

### #77. Fertilizer "gap" was a measurement error -- SELL orders are requests, not sales

Chasing why mandgeee (2,774) beat pf_all by 3,913, the SELL totals showed them moving 2,198
fertilizer to our 1,624 and it looked like a real extraction gap worth ~$21k.

**It is not real.** `COLLECT_FERTILIZER` yields exactly 1 unit
(`_inv_add(inv, "FERTILIZER", 1)`), and both sides collected almost identically -- **352 vs
346**. Fertilizer cannot exceed collections, so the 574-unit "gap" was impossible on its
face.

**Cause: I counted SELL ORDER QUANTITIES as units sold.** The engine fulfils a SELL only up
to what is in the shed, so a 1,624-unit order total can sit on top of ~350 real units. This
ledger already carries the rule -- "use per-step money deltas for cost/revenue claims;
nominal per-order pricing lies" (#21b) -- and it was not applied.

**Corrected with per-step money deltas:**

| | us (pf_all) | mandgeee |
|---|---|---|
| income | **$163,882** | $142,493 |
| spend | **$56,159** | $30,857 |
| net | 107,723 | **111,636** |

We earn **+$21,389** more and spend **+$25,302** more; net -3,913, matching the reported
margin exactly. The verdict from #75 survives -- we lose on SPEND, dominated by feed -- but
every revenue/units figure quoted in #75 and the Vibe Farmer analysis was inflated by this
same error and should be re-derived from money deltas before being reused.

**The feed finding itself is safe**, because it was counted from `BUY_PRODUCT` orders and
buys ARE fulfilled when affordable -- and it is independently confirmed by simulation:
pf_all 1,312 units, base 800-987, pf_all2 838.

**Standing rule, restated because it keeps costing us: SELL order quantities are requests.
Only per-step money deltas measure revenue. BUY orders are safe to count; SELL orders are
not.**

### #78. Three ladder losses, two causes -- and the selector is NOT one of them

All measured with per-step money deltas (#77), not order quantities.

**Kaan Dinız (2,820), -2,840 -- the feed defect again.** Same family, same 4 quadrants and
6C9S herd.

| | us (pf_all) | Kaan |
|---|---|---|
| income | $138,827 | $132,894 |
| spend | $57,528 | $48,755 |
| feed | **1,312u / $56,550** | 970u / $42,076 |

+$5,933 more earned, +$8,773 more spent, net -2,840 exactly. Already fixed in pf_all2 (838
feed units). This is now the THIRD loss traced to the same 1,312-unit route: Vibe Farmer,
mandgeee, Kaan.

**MiMi (2,725), -10,254 -- a different cause entirely.**

| | us | MiMi |
|---|---|---|
| **quadrants** | **3** | **4** |
| herd | 10C2S | 8C3S |
| income | $110,269 | **$119,599** |
| spend | $27,820 | $26,896 |
| feed | 433u | 150u |

**MiMi out-EARNED us by $9,330 on effectively the same spend**, running four quadrants where
our selector chose a three-quadrant plan.

**Tested whether the selector is at fault: it is not.** Rerouting the milk-support branch
(`_KAWA_MILK_SUPPORT` -> `10c4s_3q`) to a 4-quadrant plan instead scored **3-13 (18.8%),
-11,799** against pf_all2. Three quadrants is the right choice FOR OUR AGENT; MiMi's edge is
that it can work a fourth profitably and we cannot.

That is the same wall as #56 (land negative across ~35 of our configurations) and #76 (the
lean-feed profile is a property of the #1's whole agent, not a transplantable route). Three
independent probes -- land, feed, selector -- all land on the same conclusion: **the
BL-MDgogo family has an architectural ceiling around 2,500-2,800, and the agents above it
differ in what they can WORK, not in which recording they replay.**

**Do not retry**: biasing the route selector toward more land.

### #79. Five ladder losses dissected -- feed is architectural, and the corpus is bimodal

All figures from per-step money deltas (#77).

| opponent | rating | margin | cause |
|---|---|---|---|
| Vibe Farmer | 2,625 | -889 | 6c12s route buying 1,312 feed units -- **FIXED in pf_all2** |
| mandgeee | 2,774 | -3,913 | same | 
| Kaan Dinız | 2,820 | -2,840 | same |
| MiMi | 2,725 | -10,254 | architectural: 4 quadrants worked profitably, we cannot (#78) |
| fufufukakaka | 2,751 | -11,877 | **10c4s route feed floor -- NOT fixable** |

**fufufukakaka is the informative one** because it is not the bug we fixed. Both farms ran 3
quadrants and 3 planted tiles; income was near-identical ($81,449 vs $83,719). They ran MORE
animals (15 v 12) on HALF the feed:

| | us | fufufukakaka |
|---|---|---|
| spend | $27,925 | $18,318 |
| feed | **433u / $18,570** | 229u / $8,780 |

The $9,790 feed gap is essentially the whole 11,877 margin.

**And it cannot be fixed by swapping routes.** Feed volume across the 143 corpus 10C4S_3Q
routes is **bimodal with nothing in between**: one route at **84** units (Ryo Hasegawa's,
which collapses at -146,033 when transplanted, #76) and everything else at **431-741**, with
a large cluster at **exactly 434** -- every peikopon episode, identical regardless of seed.

**Feed volume is a fixed property of the agent that recorded the route, not a situational
choice.** Our current 10c4s route (ep94469751, 434) already sits at the floor of the
workable cluster. There is no moderate-feed option to screen.

**Also checked and rejected as a different lineage:** `nagatakengo/kaggriculture` decodes to
a genuinely non-BL-MDgogo agent (13.7k chars, plain source) and loses **0%, -155,427**.
`ameythakur20` decodes to a byte-size match for prvsiyan (same family).
`kaitofukami/22-24-unseen-lineages-v41-sparse-closed-loop` (gzip payload) and
`stevenleehans/kaggriculture-e284` (SOURCE_B85) did NOT extract with the current decoder and
remain the two most promising unexplored candidates -- kaitofukami's title claims 22/24
against unseen lineages, and "closed loop" implies reactive rather than replayed.

**Do not retry**: screening 10c4s routes for lower feed.

### #80. pf_all2 was a REGRESSION -- I optimised a proxy instead of the outcome

**pf_all remains our best build. pf_all2 is worse and should not be used.**

| test | result |
|---|---|
| pf_all2 vs pf_all, **6c12s bucket** (the only slot they differ in) | **17.9% (5-23), -4,757** |
| pf_all2 vs pf_all, all buckets, fresh seeds 77000+ | **33.3% (4-8), -857** |

**How the error happened, because the shape of it will recur.** Three ladder losses (#75,
#78) traced to pf_all's 6c12s route buying 1,312 feed units against opponents' 464-970. I
formed the causal story "feed overspend loses games", found a 838-unit replacement, verified
the feed cost fell ($57,436 -> $37,181), and shipped it.

**I never A/B'd the two candidates against each other.** Both beat the prvsiyan base in the
yarn bucket (ep94369942 9-1, ep93867727 12-0), which I read as interchangeable. Head to head
inside pf_all, ep94369942 wins **23-5**. The high-feed route spends more and produces more
than enough to cover it.

An early pf_all2-vs-pf_all run showed 4-2 (+213) and I treated that as confirmation; it was
six games and inside noise. The user spotted the regression from the ladder before the local
tests did.

**The rule this violates, stated so it is checkable:** a diagnosis explains a loss, it does
not rank two candidates. **When replacing component X with X', the promotion test is X vs X'
directly -- never "X' fixes the metric I blamed" and never "both beat a third party".**
Feed cost, dead seed, wheat churn are all DIAGNOSTICS. The only objective is win rate against
the incumbent.

**Also settled: pf_all's 10c4s route is optimal for our corpus.** A widened screen of 14 more
candidates (26 of 143 now tested) found nothing better -- best was 50.0% at -340. That slot
covers ~45% of games and is maxed.

### #81. pf_all's loss pattern found and localised -- but no patch exists in our toolkit

**pf_all's ladder record: 89 matches, 64-25 (71.9%).** Profiled its 12 worst losses against
12 RATING-MATCHED wins (win opponents 2,759-2,843) so any pattern found is not just "we lose
to strong agents". Everything from per-step money deltas (#77).

**The pattern is the route bucket:**

| bucket | losses | wins |
|---|---|---|
| 10c4s_3q | 4 | **8** |
| **6c12s yarn (both)** | **6** | 3 |
| 8c6s_3q | 2 | 1 |

Losses skew hard to the yarn buckets, wins to 10c4s. Every yarn loss shows `feed 1312` --
our spend $54-57k against opponents' $12-49k. Six losses, -41,777 total. Loss opponents
average **2,672** rating, wins **2,301**. Nine of 25 losses are under 2,200 margin, so
flipping the bucket would move 71.9% toward ~82%.

**Three patches tried, all negative:**

1. **Lower-feed yarn routes.** Against v14_neutral in the yarn bucket the low-feed routes
   looked better (ep93867727 **+74,493** vs current **+73,232**). Against a PANEL of real
   opponents they are clearly worse:

   | 6c12s route | prvsiyan | flexonafft | indarkarhana | total |
   |---|---|---|---|---|
   | **current (1,312 feed)** | 60% | 60% | 80% | **66.7% (20-10)** |
   | ep93867727 (838) | 40% | 40% | 70% | 50.0% (15-15) |

2. **Reroute yarn rolls to the strong 10c4s slot**: **0-10 against all three opponents,
   ~-21,000.** Composition beats route quality (#73) -- a 10C4S route cannot run a 6C12S_4Q
   farm, whatever its quality.

3. Biasing the selector toward more land was already 18.8% (#78).

**A METHOD CORRECTION THAT MATTERS MORE THAN THE RESULT.** The neutral-opponent check and the
panel DISAGREED, and the panel is right. `v14_neutral` is a weak, structurally different
agent: it is the correct tool for detecting share-capture inflation (its whole purpose in
#70/#72), but it is the WRONG tool for RANKING two candidates, because both beat it so
decisively that the margin difference is noise about play we will never face.

**Rank candidates on a PANEL of realistic opponents. Use the neutral only to ask "is this
gain real or coupling?"** This also retroactively vindicates #80: pf_all2 lost the panel-like
head-to-head, and the neutral test that seemed to contradict it was measuring the wrong thing.

**Where this leaves pf_all: optimal for our approach.** Every lever is now exhausted --
10c4s slot (26 of 143 candidates), 6c12s slot (6 candidates + panel), the selector (2
modifications), feed guards, land, churn. We know precisely where it is weak (yarn buckets
against 2,700+ opponents) and that our corpus contains no route that fixes it.

## Reproducing

```bash
# Rebuild the eval opponents (variants/ is gitignored - these are derived).
# A/B baseline: same file, ONE constant flipped, so the arm is the only difference.
mkdir -p variants/v26_nocarrot && cp game_data.py variants/v26_nocarrot/
sed 's/CARROT_MAX_TILES = 16/CARROT_MAX_TILES = 0/' main.py > variants/v26_nocarrot/main.py

# Neutral third party. v14 reads only seed_cost/first_yield_day from game_data,
# so sharing the CURRENT game_data.py is behaviourally inert for it -- and it is
# required, because `import game_data` caches under a bare module name and two
# different copies in one process poison each other.
mkdir -p variants/v14_neutral && git show v14:main.py > variants/v14_neutral/main.py
cp game_data.py variants/v14_neutral/

# Promotion decision: paired seats, ranked by win rate.
.venv/Scripts/python.exe -u analysis/duel.py main.py variants/v26_nocarrot/main.py 20

# Coupling check: BOTH builds vs the same neutral opponent, compare margins.
.venv/Scripts/python.exe -u analysis/duel.py main.py variants/v14_neutral/main.py 12
.venv/Scripts/python.exe -u analysis/duel.py variants/v26_nocarrot/main.py variants/v14_neutral/main.py 12

# After ANY kaggle-environments upgrade, before trusting a single sell decision:
.venv/Scripts/python.exe analysis/verify_price_model.py
```

```bash
# head-to-head, fixed seed
.venv/Scripts/python.exe -c "
from kaggle_environments import make
env = make('kaggriculture', configuration={'seed': 42}, debug=False)
env.run(['main.py', 'other/main.py'])
print([s['reward'] for s in env.steps[-1]])"

# the real Kaggle visualizer, locally
#   env.render(mode='html') -> file, then serve it:
#   python -m http.server 8765   ->   http://127.0.0.1:8765/<file>.html
#   (direct file:// is blocked by the browser extension)
```

Engine source is ground truth for all mechanics:
`.venv/Lib/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`

### #82. Reserve-safe WHEAT churn is real, but seed-sensitive -- keep separate from pf_all

Decoded a genuinely distinct sparse closed-loop agent and isolated its one-tick WHEAT
market-maker with the route held constant. The mechanism itself won **18-2 (90.0%)**
on seeds 81000-81009, +108 mean margin. Ported only that wrapper onto the untouched
five-route pf_all portfolio.

**Direct promotion tests, paired seats:**

| candidate vs untouched pf_all | seeds | record | mean margin |
|---|---:|---:|---:|
| pf_all + 10-unit WHEAT | 83000-83009 | **20-0 (100%)** | +468 |
| pf_all + 10-unit WHEAT, disjoint confirmation | 86000-86009 | **16-4 (80%)** | +92 |
| pf_all + 20-unit WHEAT | 85000-85004 | 7-3 (70%) | +555 |
| pf_all + 40-unit WHEAT | 85000-85004 | 8-2 (80%) | +1,019 |

Combined 10-unit evidence is **36-4 (90%) over 20 seeds**, but the disjoint block misses
the required >=90% promotion bar. Larger batches raise mean margin but worsen seat-sensitive
market coupling. Against prvsiyan on matched seeds 84000-84004, both patched and untouched
pf_all scored **7-3**; the patch did not flip a game and changed mean margin from -2,160 to
-2,428. Therefore this is an **experimental incremental candidate, not a pf_all replacement**.

The saved MiMi replay was rendered to `loss_analysis/episode-97108196-replay.html`. Its exact
step data confirms the larger ceiling remains architectural: pf_all's fixed compositions,
especially the feed-heavy yarn buckets, lose to strong policies that profitably operate more
quadrants/animals. WHEAT churn captures deterministic town demand but does not repair that gap.

No Kaggle submission was made. Untouched `submit_pf_all/main.py` remains unchanged.

### #83. Top-loss architecture and WHEAT-threshold follow-up -- no promotion

Profiled five representative pf_all losses to MiMi, Arman, Crop Dusta and
fufufukakaka day by day. The winners do not share one scalar patch:

- MiMi reaches Q4 on day 12 and runs 9 cows / 3 sheep.
- Crop Dusta reaches Q3 on day 8 (pf_all day 11) with cows, sheep and geese.
- Arman wins at Q3 with a lean 6-cow / 10-sheep economy.
- fufufukakaka uses 12 hands and mixed 15-animal herds while pf_all's matching
  losses use 9-12 hands and 14-18 animals.

Rebuilt each opponent's complete 719-step route and screened it directly against
pf_all. MiMi scored 1-3; Arman 0-4; Crop Dusta 0-4; fufufukakaka episode 97395540
0-4. Episode 97144518 screened 4-0 but collapsed to **6-14 (30%, -76,411)** on
ten fresh seeds. Restricting that route to pf_all's matching `10c4s_3q` bucket
still scored **0-10 (-98,071)**. The route depends on finer seed state/reactivity,
not merely shop bucket or farm composition.

Tried to stabilize #82's 10-unit WHEAT expert by raising minimum predicted profit:

| threshold | screen result |
|---:|---:|
| $5 | 6-4, -11 |
| $10 | 2-2, 6 ties |
| $15 | 2-2, 6 ties |
| $25 | 1-1, 8 ties |
| $50 | 2-2, 6 ties |
| $100 | 2-2, 6 ties |

Higher thresholds remove the profitable arm and expose pure seat symmetry. The original
$1 threshold remains best, but its disjoint 16-4 confirmation still misses the >=90%
promotion rule. `submit_pf_all/main.py` remains untouched and incumbent. No Kaggle
submission was made.

### #84. Compatible suffix routing breaks pf_all: 19-1 unseen

The breakthrough came from replacing pf_all's replay-table architecture, not from another
scalar guard. The current sparse closed-loop v46 agent first scored **16-4** against pf_all
on seeds 93000-93009. All four losses were third-shop-YARN (`6c8`) starts. Widening v46's
built-in third-YARN rule made it worse (15-5 overall, 0-5 in that bucket), proving that a
suffix only works when its pre-branch farm state matches.

Decoded v46 statically with `analysis/extract_kaito_v46.py`, then mined 208 public episodes
for routes matching v46's default action prefix through step 216. Nineteen compatible
suffixes were screened in both seats. No single suffix repaired both loss prefixes, but two
routes were complementary:

| exact first-three-shop prefix | suffix |
|---|---|
| `SMOOTHIE_SHOP / SMOOTHIE_SHOP / YARN_STORE` | episode 98451967 |
| `SMOOTHIE_SHOP / BAKERY / YARN_STORE` | episode 98276177 |

The first two-prefix router flipped all four original losses and scored **20-0** against
pf_all on seeds 93000-93009. On the unseen 94000-94009 block it scored 18-2. Replay/day and
late-market traces localized one new loss to
`FARMERS_MARKET / PIZZA_SHOP / YARN_STORE`: the compatible route grew CARROT while pf_all's
late 26-unit TOMATO sale decided the game. Changing only that suffix's post-216 CARROT
seed/plant/sell operations to TOMATO flipped the prefix in both seats.

**Frozen candidate:** `submit_v46_three_suffix/main.py`, SHA-256
`5950fdb0032ede297706bb5aaae48461597563b6322de144ec0dee4274388c59`.

| paired-seat test | seeds | record | mean margin |
|---|---:|---:|---:|
| candidate vs pf_all, discovery | 93000-93009 | **20-0 (100%)** | +8,434 |
| candidate vs pf_all, unseen | 94000-94009 | **19-1 (95%)** | +8,016 |
| candidate vs Fleong 2830 artifact | 95000-95009 | **18-2 (90%)** | +17,229 |
| candidate vs Salem 3094 artifact | 95000-95009 | **16-4 (80%)** | +5,301 |
| candidate vs Kaito v46 parent | 95000-95009 | 3-3, 14 ties | 0 |
| candidate vs Soil Rain artifact | 95000-95009 | **8-12 (40%)** | +1,413 |

The Kaito-parent tie is expected: the agent is unchanged unless one of the three exact
prefixes activates. Soil remains the main matchup weakness. Four compatible yarn-second
suffixes, terminal-rule variants, full TOMATO/WHEAT/STRAWBERRY/MELON substitutions, and
partial 2-12-plot WHEAT substitutions all failed to flip the final second-YARN loss; those
changes were rejected rather than overfit.

This is the first candidate to clear the >90% unseen promotion bar against pf_all. It is
kept separate; `submit_pf_all/main.py` is untouched. Submitted to Kaggle as **55751173**
on 2026-08-25 with message `v46 three-suffix router 19-1 unseen`. Validation completed at the standard 600.0 initial rating; its first assigned episode was a tie at 64,149.

### #85. Early ladder falsifies “categorically better than pf_all”

Submission 55751173 reached **11-1-1 and 1,594.7** after 13 episodes, but its first real
loss came after nine wins, at rating **1,499.0**. Episode 98663380 was a 65,317-69,168
loss to Corgi-Samoyed submission 55743618, then rated 1,611.2. Corgi is not a hidden top
agent: its 61-match record is 38-23 (62.3%) and its rating is converged near 1,614.

The user's comparison was correct. Normalizing timestamps and excluding the one-agent
seeding episode, pf_all won **27 consecutive duels** and first lost at rating **2,648.7**.
Therefore the new agent's 19-1 paired-seat result against pf_all cannot be interpreted as
general ladder dominance. It is a strong direct matchup, with family/market coupling, but
pf_all had substantially better early-ladder coverage.

Replay 98663380 localizes the loss. Our agent led by 8,471 on day 18, then lost the late
game by 3,851. It ran 11 cows / 4 sheep against Corgi's leaner 7 cows / 4 sheep. Across
money deltas, Corgi earned about 2,812 more and spent about 1,039 less, with much heavier
late WHEAT turnover. On replay seed 1201036856, the submitted agent and pf_all split 1-1
when directly paired, so the episode does not prove pf_all would beat Corgi on that exact
world; it proves the new architecture has a seat-sensitive late-game matchup hole.

**Method correction:** beating the incumbent is necessary but not sufficient. Promotion
also needs dissimilar-opponent coverage and an early-ladder surrogate panel. Keep
submission 55751173 as an experiment, not a proven universal replacement. No additional
Kaggle submission was made.

### #86. Food is sold; pf_all transplant and Kaito counter probes

The apparent terminal inventory in the v46 replay was not unsold food. On the Corgi seed,
the agent sold all sellable products during steps 718-719; the only remaining shed item was
one SHEEP, which the engine does not allow as a `SELL` product. The real weakness was late
liquidation: v46 held 74 WHEAT at step 696 and trickled it out, whereas pf_all sold 69 WHEAT
at step 697 and already has a full terminal controller from step 708.

Three state-compatible pf_all transplants were isolated:

| variant | exact-loss seeds vs pf_all | fresh 106000-106009 vs pf_all |
|---|---:|---:|
| terminal takeover at 704 | 1-3 | rejected before confirmation |
| v46 collision-ranked terminal sells at 708 | 3-1 | **13-5, 2 ties** |
| both changes | 1-3 | rejected before confirmation |

The collision result was coupling, not a field improvement. On identical 107000-107009
panel seeds, collision-pf_all and untouched pf_all had exactly the same records: Fleong
20-0, Salem 20-0, Kaito 4-16, Soil 20-0. It flipped **zero** panel outcomes and changed only
small terminal dollar amounts. It is retained as a rejected variant, not promoted.

The Kaito replay exposes pf_all's actual structural weakness. In the first-shop-YARN world
at seed 107000, pf_all expands to four quadrants and 6 cows / 12 sheep; Kaito stops at three
quadrants and 6 cows / 10 sheep, uses a lean strawberry/wheat farm, and leads by about
$12,000 from day 17. This is not repairable by terminal ordering.

The policies are incompatible from turn zero: pf_all opens with pasture + five hires + cow
+ two sheep, while Kaito opens with two hires + seven MELON seed + five WHEAT seed + four
sheep. Corrected one-turn crossover probes both scored **0-6** against Kaito and produced
almost no farm output, confirming immediate state divergence. A valid next architecture
must optimize a new common opening that can branch later; frozen-policy switching is not a
safe shortcut. `submit_pf_all/main.py` remains untouched. No Kaggle submission was made.
### #87. “Unsold food” correction: terminal crops were never harvested

The user correctly clarified that the visible food was not shed inventory; it was mature
food left standing in the fields. `analysis/unharvested_profile.py` now measures terminal
`yield_units`, ready tiles, final-price value, and last-day HARVEST actions.

Both real v46 ladder losses show the same mechanism:

| episode/opponent | our terminal ready crop | value | opponent ready crop |
|---|---:|---:|---:|
| 98663380 / Corgi | 27 WHEAT on 12 tiles | $1,188 | $0 |
| 98683942 / John Stupid | 20 WHEAT + 4 CARROT on 11 tiles | $1,252 | $0 |

On the same local worlds, v46 leaves roughly $948-$1,252 harvestable while pf_all leaves
only $28-$70. Therefore this is a genuine v46 terminal-worker weakness and one reason the
new submission underperformed pf_all.

Six isolated repairs were tested against frozen `submit_v46_three_suffix` on both seeds
in paired seats. Full terminal controllers beginning at 708, 704, 696, and 684 all scored
**1-3**. A final-day surgical overlay and a WHEAT-only feasible-return overlay also scored
**1-3**. Earlier takeovers recover more crop but abandon profitable animal work and alter
market timing. The surgical versions still disturb validated worker paths and later CARROT
collection. Engine inspection also corrected an assumption: WATER immediately increases
non-ongoing crop yield, so replacing final-day WATER indiscriminately can create a larger
terminal backlog.

Conclusion: the diagnosis is valid, but a generic worker override is negative. The safe
repair requires rebuilding the route's final-day movement schedule with joint assignments
for harvest, animal work, shed return, and sale. pf_all already has effective terminal
worker routing and does not need this transplant. No Kaggle submission was made.
### #88. Full v46 ladder loss pattern: two failure families, not one shop bucket

Pulled submission 55751173's complete current record: **88 matches, 72-12-4
(85.7% decisive win rate), rating 2,286.8**. The recent 22-match win rate is 63.6%.
Downloaded all twelve loss replays and compared them with twelve recent wins against
rating-matched opponents (roughly 2,188-2,345).

There is no dominant shop bucket:

| first-three-shop bucket | losses | matched wins |
|---|---:|---:|
| no YARN | 7 | 8 |
| YARN first | 2 | 2 |
| YARN second | 2 | 1 |
| YARN third | 1 | 1 |

Terminal unharvested crop is a real v46 weakness but does not discriminate losses: our
mean terminal ready value is $1,258 in losses and $1,143 in wins; relative to the opponent
it is +$556 in losses and +$571 in wins. It should be repaired eventually, but it is not
why a particular match becomes a loss.

The economic mechanism is consistent. In losses we earn $6,688 less than the opponent but
spend $4,353 less, netting the observed -$2,335 mean margin. In matched wins we earn only
$924 less while spending $7,111 less, netting +$6,187. The model is a cost-saving policy;
it loses when an opponent creates enough extra output to exceed those savings.

The twelve losses divide into two practical families:

1. **Clone/near-clone execution losses (six).** Boredom, AI After Hours, Akhil Chinta,
   Kaipeng Zheng, Arda Ceylan, and CroDoc use the same or nearly the same herd/composition.
   Most are close market/seat races. AI After Hours is the large exception (-$6,186): both
   finish with 11 cows / 4 sheep, but our weed burden was 1,134 observation-turns versus
   315 and we carried roughly four fewer strawberry plots from day 11 onward.
2. **Different/leaner economy losses (six).** Corgi, John Stupid, Controlvector, Sebastien
   Mametz, sana slama, and Lord Momo use different herd mixes. The strongest examples are
   Corgi's 7 cows / 4 sheep and Lord Momo's 6 cows / 8 sheep against our 11 cows / 4 sheep.
   Their late crop throughput overcomes our lower spending. Lord Momo wins by $8,897.

Weed burden is a secondary but measurable signal: ours averages 996 observation-turns in
losses versus 684 in matched wins; opponent-relative weed burden correlates -0.457 with
margin across the 24-replay sample. It is not universal—several opponents carry more weeds
and still lose—but it is actionable in clone matchups.

Seat order also matters: the full record has 36 wins in each seat, but losses split 8 in
seat 0 versus 4 in seat 1 (decisive win rates 81.8% vs 90.0%). Eight of twelve losses are
under $2,000, consistent with market ordering and small execution differences deciding
most failures.

Next repair priorities are therefore (a) state-safe weed clearing for clone-like openings
and (b) a separately validated lean-economy route/opening. Shop-prefix routing and generic
terminal harvesting do not address the observed loss split. No Kaggle submission was made.

### #89. On-tile weed repair does not improve v46's win rate

Replay profiling refined the weed signal from #88. Across the twelve v46 ladder losses,
our units spent 902 actor-turns standing on weeds. Besides 239 existing DIG actions, the
fixed routes attempted 114 WATER, 68 HARVEST, 29 FERTILIZE, and 21 PASS actions while on
a weed. The existing sparse repair only catches PLANT/BUILD collisions, so these failed
on-tile operations were a plausible closed-loop gap.

Three isolated variants were built on frozen `submit_v46_three_suffix`, preserving every
route, movement action, market action, selector, and the opening through step 159:

| variant | extra on-weed DIG gate |
|---|---|
| `submit_v46_weed_core` | HARVEST/WATER/FERTILIZE/CARE/FEED |
| `submit_v46_weed_idle` | PASS only |
| `submit_v46_weed_broad` | union of core and idle |

Against frozen v46 on seeds 109000-109009 in both seat orders, every variant finished
**3-3 with 14 ties**. Against exact frozen `submit_pf_all` on independent seeds
110000-110009, the unchanged v46 baseline and all three repairs each finished **15-5**.
No repair converted a single outcome. Diagnostic mean margins were +$3,397 baseline,
+$3,272 core, +$3,172 idle, and +$3,272 broad.

Conclusion: failed operations on weed tiles are real, but replacing them with DIG does
not improve match wins and slightly reduces mean margin. Persistent weed burden is a
symptom of fixed-route state drift, not a locally repairable cause. All three variants
remain separate rejected artifacts; the frozen models are unchanged. No Kaggle
submission was made.

### #90. Full pf_all loss audit and recent-method transplants do not clear the reliability bar

Pulled submission 55697862's complete record: **137 matches, 79 wins and 58 losses**.
One loss was an ambiguous pf_all self-match, leaving **57 real opponent losses**. All 57
replays were downloaded and profiled rather than extrapolating from the old 12-loss sample.

The losses are two different failure families:

| family | count | identifying evidence |
|---|---:|---|
| close losses (margin <= $2,500) | 21 | 17 in seat 0; 15 have a persistent 24-turn clone-distance <=2 streak |
| severe losses (margin >= $8,000) | 18 | zero persistent clone-distance <=2 streaks; day-12 lead becomes a day-29 deficit |

Across all losses, pf_all leads by $3,311 at day 12 but trails by $5,534 at day 29.
In the severe family it earns $9,873 more than the opponent but spends $21,047 more,
buys 643 more feed units, carries 1,148 more weed observation-turns, and moves from
+$5,265 on day 12 to -$11,321 on day 29. It finishes with 14.3 standing crops against
33.9. The severe failures are leaner, structurally different economies, not mirror races.

Four state-compatible versions of the recent strict clone gate were tested directly
against frozen pf_all on seeds 111000-111009 in both seats:

| variant | record | decisive win rate |
|---|---:|---:|
| clone distance 2 | 6-6, 8 ties | 50.0% |
| adaptive horizon capped at 3 | 6-8, 6 ties | 42.9% |
| both changes | 6-8, 6 ties | 42.9% |
| full recent gate (distance 2, start 160, batch 10, horizon 3) | 9-6, 5 ties | 60.0% |

The strongest recent gate is still far below the >90% reliability requirement.

The top-player corpus plus all pf_all losses yielded **24 exact-prefix-compatible
suffixes** across four route buckets (longest branch points: 312 for 6c8s, 262 for
second-YARN, and 256 for 10c4s). Every suffix was built as an isolated pf_all variant
and bucket-screened. Twenty-three were regressions. The sole survivor,
'ep94415941_s0_p312_6c8s_3q', initially scored 4-0 with 6 ties, then 15-5 on ten disjoint
bucket-matched seeds. Its five raw losses all canceled in the opposite seat and the
paired mean margin was only +$5: non-inferior, but not dominant.

On fresh seeds 113000-113009, the survivor and frozen pf_all produced **identical rewards
in every panel game**: Fleong 20-0, Salem 20-0, Kaito 4-16, and Soil 20-0. It flipped zero
field outcomes. Therefore it does not repair pf_all's real Kaito/lean-economy weakness.

Conclusion: pf_all loses close mirror races through market/seat ordering and loses severe
matches to lean architectures that are incompatible before a safe suffix branch. The
recent strict market gate and compatible-suffix techniques cannot fill that structural
gap on top of pf_all. Frozen 'submit_pf_all/main.py' remains byte-identical at SHA-256
'9F9718CFA6E3FF822FAFAF12414CC34EF6BDBF67BFDBAD92662A42D0CCFDC0BF'. No Kaggle
submission was made.
### #91. pf_all rerun first genuine loss reproduces the severe lean-economy failure

Frozen pf_all was resubmitted as Kaggle submission 55847309 after explicit approval.
The initial recorded loss was a self-match and was excluded. The first external run went
5-0 before losing episode 101790539 to ikevayansky by $16,099 at rating 1,158.7.

This is not a clone race. Clone distance never reached 6 after turn 120. It is the severe
structural family from #90:

| metric | pf_all | opponent | delta |
|---|---:|---:|---:|
| route/farm | second-YARN, 4 quadrants | 3 quadrants, 6 cows / 10 sheep | |
| total income | $115,786 | $86,075 | +$29,711 |
| total spending | $61,760 | $15,950 | **+$45,810** |
| feed units | 1,312 | 135 | **+1,177** |
| weed observation-turns | 3,685 | 1,256 | **+2,429** |
| day-12 money gap | | | +$2,966 |
| day-18 money gap | | | -$10,688 |
| day-29 money gap | | | -$12,618 |
| day-29 standing crops | 23 | 35 | -12 |

pf_all again earns more but destroys the advantage by expanding to quadrant four and
funding its 1,312-feed second-YARN route. The opponent stays on three quadrants with a
lean 6-cow/10-sheep herd and converts lower spending into a late crop-throughput lead.
This independently confirms that the current ladder weakness is the Kaito-like lean
architecture identified in #90, not a new bug and not fixable by the rejected strict
clone gate. No additional Kaggle submission was made.

### #92. Kaito loss audit: a compatible suffix wins the mirror but does not solve Soil

Pulled all **193** current matches for submitted Kaito descendant 55751173: **111 wins,
64 losses, 18 ties**. All 64 losses were downloaded and profiled. Forty-five are
NO-YARN/default-route games and 45 show a persistent close-clone streak. The complete
loss sample earns $10,213 less than its opponent while spending $4,709 less. In the 26
close losses, Kaito is level through day 18 and loses by only $861 on average; in the 19
severe losses, income trails by $25,253 and the final deficit is $12,266. This confirms
two families: late execution races against Kaito-like clones and structural losses to
different lean routes.

Mining the 64 winning opponents found only two suffixes with an exact Kaito-route prefix
of at least 160 actions. The default-route continuation from episode 100606696 branches
at step 243 and beat frozen submitted Kaito **33-3 with 4 ties (91.7% decisive)** over two
fresh 10-seed blocks. The YARN-first continuation reached only **7-3 with 10 ties (70%)**
and was rejected.

The default suffix failed the required real-opponent panel on seeds 116000-116009:

| opponent | default suffix | frozen submitted Kaito on identical seeds |
|---|---:|---:|
| pf_all | 17-3 (85%) | 17-3 (85%) |
| raw Kaito | 15-5 | 7-7, 6 ties |
| Salem | 16-4 (80%) | 16-4 (80%) |
| Soil | **9-11 (45%)** | **10-10 (50%)** |
| Fleong | 20-0 | not rerun |

Thus the suffix is a genuine Kaito-family share-capture improvement, not a broad strength
improvement. It changed no pf_all or Salem outcomes and made Soil one game worse. It is
rejected despite clearing 90% against the submitted descendant.

Full trajectories on the six Soil failure seeds localized the matchup. Frozen Kaito is
ahead by **$1,715 at day 12 and $8,751 at day 18**, then finishes **$4,783 behind**: a
roughly $13,500 late swing. Kaito harvests more (420 vs 390) and carries fewer weed
observation-turns (385 vs 532), so neither generic harvesting nor weed repair explains
the loss. It finishes with 11 cows / 4 sheep against Soil's lean 7-cow farm, but buys only
105 wheat versus Soil's 189. Kaito's route schedules 234 FEED actions, indicating wheat
availability can make planned work no-op.

Two narrowly scoped repairs were tested on the known Soil failures:

1. Four reserve-safe wheat top-up guards (start 160/240, batch 4/8, threshold 2/4) added
   wheat only with livestock present, cash above a floor, and a free market slot. All
   remained **0-8**; margins moved only slightly.
2. Kaito's dormant debt-balanced non-clone preemption was activated for MILK and WHEAT
   across four horizons/batches each. It only moves a real future sell earlier and removes
   the same quantity from its original slot. Every variant remained **0-8**. The best
   margin change was only about +$240.

Static decoding explains why a direct Soil continuation cannot be transplanted: Soil and
every Kaito route diverge at **action 0**. Soil's modal route is a different opening and
late economy, not a compatible suffix. The immediate-feed and single-product queue-timing
hypotheses are therefore closed. A future Soil repair needs a separately executable
day-0 branch or a stronger opponent-family policy, not another global Kaito suffix.

Frozen `submit_v46_three_suffix/main.py` remains byte-identical at SHA-256
`5950FDB0032EDE297706BB5AAAE48461597563B6322DE144EC0DEE4274388C59`. No Kaggle submission
was made.

### #93. Observable day-0 routing closes Kaito's Soil failure without a global regression

Mining 1,426 replay seats for routes compatible with Kaito's exact opening found 20
lean branches. The strongest, episode 94498749 seat 0, matches Kaito through action 24
and then runs a 3-quadrant 7-cow/4-sheep economy. It beat Soil 20-0 in discovery and
19-1 on fresh seeds 119000-119009, but as a global replacement it lost 13-7 to Kaito
and 20-0 to both pf_all and Salem. It is a specialist, not a replacement.

Soil exposes a unique public opening signature at observation step 1: five hands, one
quadrant, and at most $10 remaining. In the measured panel, pf_all also has five hands
but $1,452, Salem has five hands but $20, and Kaito/Fleong have two hands. A router was
built that emits frozen Kaito's identical step-0 action, latches the lean policy only on
that observable signature at step 1, and otherwise remains on frozen Kaito. No team name,
submission identity, or private information is used.

Validation on paired seats:

| opponent / check | seeds | result |
|---|---:|---:|
| Soil block 1 | 119000-119009 | 19-1, +$6,873 |
| Soil block 2 | 120000-120009 | 18-2, +$4,115 |
| pf_all | 120000-120009 | 19-1, +$8,573 |
| Salem | 120000-120009 | 19-1, +$8,085 |
| Fleong | 120000-120009 | 20-0, +$21,112 |
| frozen Kaito no-op check | 119000-119009 | 4-4, 12 ties, exactly $0 paired margin |

Router and lean specialist produced identical final rewards on all 20 Soil block-1 games,
proving the branch fired in both seat orders. Against Kaito, every non-tie reward exactly
swapped with seat order and the paired margin was zero, proving the detector-off path
retains Kaito behavior. Combined Soil result is **37-3 (92.5%)**.

This is the first Kaito patch to close a documented structural loss family while passing
the broad real-opponent panel. After explicit user approval, the router was submitted to
Kaggle as **55871991** on 2026-08-29. The uploaded archive was 141,459 bytes with a
top-level `main.py`; that file's SHA-256 is
`CCEE4DE0F1EFCBB82FFB31672A4984B0811F46FB7C70A78ADE913ECB36766262` and its last function
is `_kaggle_submission_entrypoint(obs, configuration)`. Initial status: PENDING. Frozen
Kaito remains unchanged at SHA-256
`5950FDB0032EDE297706BB5AAAE48461597563B6322DE144EC0DEE4274388C59`.


### #94. Live Kaito rerun losses are mostly seat-1 clone races; a clone-only suffix clears the mirror bar

Downloaded and profiled all 16 losses then visible for submitted Kaito/Soil router
55871991. The Soil opening detector fired in **0/16**, so these are frozen-Kaito
losses rather than router false positives. Thirteen losses are from seat 1, twelve are
NO-YARN/default openings, and eleven contain a persistent farm-distance-at-most-two
clone streak. Eight of those clone streaks occur in NO-YARN games. The full sample earns
$10,838 less than its opponent while spending $4,541 less; close losses are mostly level
through day 12 and severe losses already trail by $3,129 at day 12. This reproduces #92's
two families: late default-route clone races and unrelated lean structural losses.

The default suffix from episode 100606696 was first stacked globally with the Soil
router. It was rejected after two pf_all blocks disagreed: 10-0 followed by 5-5, only
15-5 combined. A second router therefore advances the suffix policy silently through
step 243 and latches it only after any 24 consecutive public observations with farm
distance at most two. Soil retains priority at step 1; non-clones remain on the submitted
policy. The first implementation incorrectly required the clone streak to end exactly at
step 243; the corrected latch remembers an earlier confirmed streak.

Paired-seat validation of `variants/kaito_clone_soil_router/main.py`:

| opponent / check | seeds | result |
|---|---:|---:|
| submitted Kaito/Soil router | 125000-125004 | 9-1 |
| submitted Kaito/Soil router | 126000-126009 | 19-1 |
| submitted Kaito/Soil router | 127000-127004 | 5-1, 4 ties |
| pf_all no-op check | 125100-125104 | 9-1, every reward identical to incumbent |
| Soil specialist retention | 125200-125204 | 10-0 |
| reconstructed Gronk | six replay-derived seeds | 1-11, unchanged |

The mirror total is **33-3 with 4 ties (91.7% decisive)**, clearing the historical 90%
bar. The exact pf_all reward match proves the clone branch stayed off there. Gronk remains
unfixed because its YARN-2 slot does not use the default suffix; this candidate addresses
the dominant NO-YARN clone family, not YARN or non-clone structural losses. Candidate
SHA-256 is `0BDEF3B06CA7BAA1F78B4BE714D27B9238F9908DB0D2A3C34C2E0006B83A3066`.
No Kaggle submission was made.


### #95. Clone-targeted Kaito router submission

After explicit approval, `variants/kaito_clone_soil_router/main.py` was packaged as
`submission_kaito_clone_soil_router.tar.gz` with a top-level `main.py` and submitted to
Kaggriculture as **55874991**. Source SHA-256:
`0BDEF3B06CA7BAA1F78B4BE714D27B9238F9908DB0D2A3C34C2E0006B83A3066`; archive SHA-256:
`883060840941EE321E6E5BD349046EE07658AE8E900C7F257996CA317A3EDA34`. Initial status:
PENDING. Three submissions remained for the day after upload.

### #96. Submission 55874991 regression audit and Wheat-13 base reconstruction

The submitted clone/Soil router completed 319 visible matches at **131 wins, 184
losses, 4 ties**, public score **1546.2**. Its all-game win rate is 41.1% (41.6%
of decisive games), and its recent 80-match sample is 23-56-1. This live result
rejects the earlier mirror-only promotion evidence.

A stratified replay sample (eight recent severe losses, six recent close losses,
six recent wins) localized the current failure distribution. Ten of fourteen
sampled losses had an opponent with zero hands after step 0 and only a WHEAT
reserve purchase; four used 'BUY_PRODUCT WHEAT 13'. Five losses ended against a
3-quadrant 9-cow/8-sheep farm. In the eight severe losses the opponent earned
$25,506 more, spent $8,578 more, bought 430 more feed units, and led by $11,887
at day 18. The Soil detector fired in 0/20 samples; the clone latch fired in six,
but changed the selected route in only three. The live regression is therefore
mostly a different-lineage structural failure, not detector false positives.

Four WHEAT-13 opponent routes were extracted. Two from different submissions and
different shop rolls matched for 717/719 actions; twelve additional recent
replays from submission 55983621 included four YARN-first rolls and eleven routes
that matched the selected route for all 719 actions. This is a fixed, repeatable
9-cow/8-sheep policy rather than replay noise. Episode 105165498 seat 1 was rebuilt
inside the frozen Kaito execution guards as 'variants/panel_wheat13/main.py'.

Paired-seat results, with failed games counted explicitly:

| opponent | result |
|---|---:|
| pf_all, fresh 10 seeds | **20-0** |
| reconstructed Gronk | **12-0** |
| Soil | **12-0** |
| Salem | **12-0** |
| Fleong | **12-0** |
| original Kaito | 16-4 |
| Kaito + Soil | 16-4 |
| submitted clone/Soil router, two 10-seed blocks | **35-5 (87.5%)** |

An alternate WHEAT-13 trace with a step-2 divergence regressed to 4-16; two
near-identical traces reproduced 17-3. The remaining Kaito-family losses are
concentrated in first-shop-YARN worlds: 10 of 13 reproduced losses. WHEAT-13
plants nine and sells fourteen carrots per game, while Kaito's winning YARN-first
schedule buys twelve late carrot seeds and sells roughly twenty-seven. A direct
transplant is unsafe: the policies differ at action 0, and Kaito's 'align_hands'
only truncates/extends the worker action list; it does not remap workers or farm
state. The source submission itself converged near 2285, another warning that
the 20-0 pf_all result may include interaction effects.

Conclusion: this is the strongest broad different-lineage base found so far and
closes the reconstructed Gronk hole, but it does **not** clear the user's >90%
bar against every previous model. Preserve it as a candidate, do not submit it.
The next valid patch must be a state-aware WHEAT-13 YARN-first continuation, not
a Kaito suffix splice. No Kaggle submission was made.

Evaluation harness correction: 'analysis/duel.py' now records exceptions and
invalid rewards as failures, writes failure rows even when zero games complete,
returns non-zero on partial failure, reports wins over all completed games beside
decisive-only win rate, and stores each game's shop roll and route bucket.

### #97. W13 demand trading and price-gated crop cycles (2026-09-10)

`variants/w13_crop_demand/main.py` combines gated wheat trading with 61 eligible
three-day crop cycles that switch from wheat to carrots when observed prices
justify the extra seed and replacement feed. On ten fresh paired seeds it beats
repaired W13 20-0 (+1,669 mean). Crop-only is 6-0-14 on the same block. Direct
execution audit verifies 24 successful plants and harvests, 71 carrots, and all
770 late wheat purchases filled in both seats of the representative +9,754 game.

Do not promote on that mirror result. Matched baseline/candidate records are
identical across six opponents: Kaito 18-2, original pf_all 20-0, Gronk 20-0,
Soil 20-0, Suliman fixed reconstruction 4-16, and the 3정훈 fixed reconstruction
16-4. All six have improved average margins but **zero outcome flips**. No live
top-10 claim is justified. Replacement feed is still tracked at order issuance;
the successful representative audit does not prove universal settlement safety.

There are 432 evaluation games and four audit repeats, zero execution failures.
Nine controller tests pass and four candidates rebuild byte-identically. Full
results, limitations and reproduction: `analysis/W13_RESPONSE_REPORT.md`.
The original incumbents are unchanged; no Kaggle submission was made.

The top-50 cash audit reproduces 47 complete games and flags three terminal-step
discrepancies. It also disproves a prior inference: SpaTaro's requested purchases
of products other than WHEAT/FERTILIZER are not legal fills in the official engine.

### #98. Opening wheat netting repairs Suliman's capital trap (2026-09-10)

`variants/w13_opening_net/main.py` cancels matched WHEAT sell/buy requests only
at steps 2–23 on top of frozen `w13_crop_demand`. The diagnostic at 317002 shows
eight round trips actually losing 21 coins. Day-1 cash falls to 3, only two of
four hands are hired, and an unfed cow escapes. Netting retains 24 coins, hires
four hands, keeps the cow and raises day-12 strawberry plants from 28 to 33.
No day-zero worker actions change. The diagnostic flips −20,902 to +10,699,
but its shop sequence changes too; do not attribute the full margin to output.

Fresh Suliman blocks: **18–2 vs control 2–18** on 318100–318109, and independent
**18–2 vs control 4–16** on 319000–319009, each in both seats. Combined **36–4
versus 6–34**, thirty favorable outcome flips and zero unfavorable ones. Every
Suliman shop sequence changes. Kaito and original pf_all remain 18–2 each,
3정훈 reconstruction remains 10–10; their matched rewards are exactly unchanged.
Direct combined-model mirror is 1–1–18 with zero paired mean margin.

This is a confirmed matchup repair, **not top-10 validation or promotion**.
220 evaluation games plus three diagnostic repeats, zero failures. Sixteen
controller/reporting tests pass; candidate rebuild is byte-identical, SHA-256
`a6a512cdac1a54ff4941ab410dd3b28a14ec0e88c598be541719dc86aeb0ad9a`.
See `analysis/W13_OPENING_NET_REPORT.md`, archived paired results and production
profiles. Incumbents remain unchanged and no Kaggle submission was made.

Next lead: the second top-route's close losses have a carrot-sales gap; examine
state-compatible short crop cycles without sacrificing feed or sale timing.
Wool-heavy towns remain another weakness. Do not repeat generic herd/harvest
patches without a distinct, tested mechanism. Five-hour continuation is updated.

Submission follow-up, 2026-09-10: after reviewing #98, the user explicitly
approved uploading the exact candidate. Submitted **56139834** at 07:24:55 UTC,
initial status PENDING with no score. SHA-256 remains
`a6a512cdac1a54ff4941ab410dd3b28a14ec0e88c598be541719dc86aeb0ad9a`.
Validation commit `27a22f6`; receipt in
`analysis/submission_w13_opening_net_56139834.json`. This is an approved experiment,
not a claim that the historical promotion bar or top-10 target has been met.

## #99 — Current live losses and top-ten replay CSV audit (2026-09-10)

User requested replay-to-CSV code, current loss diagnosis and top-ten/public-model
research. Submission 56139834 snapshot: COMPLETE, 1665.5, **38–35 external**;
one self-play excluded. Team rank 1760/1680.4 belongs to its better active score.
Collected all 35 losses, eight recent wins and two observations per top-ten team:
60 unique replays. Exporter produces six CSV tables; official engine reproduces
all **86,280 cash transitions**, zero mismatches. Includes successful atomic
HIRE/BUY_LAND; complete cash decomposition residual zero. Seven tests pass.

All 43 candidate games reach 9 cows/8 sheep. In 33/35 losses we sell 9 carrots;
all losses sell zero eggs and 195 wool. Largest net-receipt shortfalls: carrots
11, eggs 8, wool 7, strawberries 5, milk 3, wheat 1. Accounting categories are not
causal ablations. Roman Svet loss -21,877 includes carrots 27 vs 294, eggs 0 vs
184. Egor Trushin loss -18,610 includes wool 195 vs 251. Near-clone sale-price
losses also remain. Ten loss opponents match a sampled top-ten worker trace at
>=90%, three exactly; market policies/source identity are not inferred.

No own weed-blocked work in losses; six no-wheat FEED requests total. Each loss
ends with six **immature** wheat tiles and one harvest-ready wool unit, not six
missed mature harvests. Terminal stocks are similar in win controls. Gross
trading turnover must be netted before diagnosing costs.

Refreshed public Shop0909, Moon and local-rank-inversion notebooks plus relevant
discussions. Most relevant next baseline: Shop Router 0909's shop-specific
production, kept separate and evaluated unchanged before adapting. Published
notebook not verified identical to author's top-ten submission. No new agent
changes, duels or Kaggle submission. Full report: `analysis/REPLAY_CSV_LOSS_REPORT_56139834.md`;
data dictionary: `analysis/REPLAY_CSV_README.md`; verified archives and CSV summaries
under `analysis/replay_csv_56139834/`. Preserve all incumbents.

## #100 — Unchanged Shop0909 baseline, fresh matched panel (2026-09-11)

Following #99 and user approval to proceed, extracted the inspected public
Shop Router 0909 without executing notebook cells. Main/data/license hashes
match the publication exactly. Kept separate from W13 and original pf_all.
Five source/behavior contract tests pass. Protocol checkpoint pushed before
completion as `2d43b82`; seeds 39117000–39117009, both seats, 180 full games.

Direct vs submitted W13 opening-net: **20–0**, +13,202 mean, +3,340 minimum.
Shared panel: Shop0909 **72–8** vs W13 **68–12**; four favorable outcome flips,
zero lost incumbent wins. Kaito 20–0 vs 18–2; original pf_all 20–0 vs 20–0;
Suliman fixed 18–2 vs 18–2; 3정훈 fixed 14–6 vs 12–8. Zero ties/failures.
Changed candidate/control shops: Kaito 16/20, pf_all 0, Suliman 2, 3정훈 0.
Do not interpret fixed-route opponents as recovered live top-player policies.

Direct sales average 83.1 carrots/54.6 eggs vs W13 9/0, while milk/strawberry
volumes are slightly lower. This supports a broader production baseline, not
an isolated proof of any one crop. Six routing IDs exercised, not all plans.

Retained losses: Suliman 39117007 with third-shop Yarn, wool 161 vs 242;
3정훈 39117001/004/009, with higher opponent carrot/milk/strawberry output.
Worst 3정훈 deficit remains -15,088. Therefore this is a promising separate
baseline, not top-ten validation or universal promotion. The next mechanism
must address allocation and safe state-compatible branching, not blindly
switch between unrelated tapes. No new crop controller implemented this round.

Report: `analysis/SHOP0909_BASELINE_REPORT.md`. Rebuild, tests, protocol and
verified raw archive under `analysis/shop0909_panel/`; `agent.zip` contains
the exact unchanged tested files. No Kaggle submission; fresh exact-artifact
approval remains mandatory. All incumbents remain unchanged.

Submission follow-up (2026-09-11): user approved the exact validated Shop0909
archive after the report. Submitted **56159253**, 05:31:13 UTC, initially PENDING.
Archive SHA-256 `9fa78bee25ec86381f59c10025b1713bb5f37294320ca009eb3ab91a99851dde`
matches validation commit `ff85c47`; ZIP members and final agent callable checked.
CLI reported four submissions remaining today. Receipt:
`analysis/submission_shop0909_56159253.json`. No further submission authorized.

## #101 — Shop0909 live capital-collapse diagnosis (2026-09-11)

Scheduled checkpoint inspected latest state before launching old W13 work.
Shop0909 56159253 COMPLETE at 2162.3 vs W13 1591.9. External record 52–20–13.
Two severe losses, 107774237 (-85,020) and 107764291 (-76,597), share a pre-shop
capital collapse: cash zero by step17, zero day1 hires, both cows gone by step48,
only one quadrant/213 coins at step144. This is not the late crop-mix mechanism.

Official-engine saved-state step0 counterfactual replacing BUY13/SELL13/BUY13
WHEAT with BUY13 preserves 13 net wheat and saves 52 coins in both cases.
**One transition only, not a full-game improvement or validated patch.**
The W13 opening-net wrapper excludes step0, so cannot simply be transferred.
No model changed, no full games rerun, no submission. Diagnosis and compressed
replays: `analysis/shop0909_live_56159253/REPORT.md`. Older scheduled W13 crop
implementation remains unperformed; latest submitted baseline is Shop0909.

## #102 — Shop0909 all-loss CSV review (2026-09-11)

Frozen 10:43 UTC record for 56159253: 53W/21L/14T, excluding self-play.
Every loss plus eight recent wins audited: 41,702 cash transitions, zero
mismatches or failed exports; seven exporter tests pass. No model changes.

Disjoint descriptive groups: five opening cash/seed shortfalls, eight
near-clone sale-price/timing losses, eight different-production-mix losses.
Two severe openings explain 161,617 lost coins, but only two of 21 losses.
All 21 own terminal states have zero stock and zero crop yield left on tiles.
No support for a blanket endgame harvest patch from this cohort.

Specific leads: opening purchase resilience; actual clone sell timing;
fufufukakaka's 12 tomatoes earn 8,049 while ours earns zero; Phi exploits
three later Yarn shops after the first-two-shop selector stays on plan0.
All are hypotheses for paired held-out tests, not validated agent fixes.
Full 21-match report and archived CSV/replays:
`analysis/shop0909_all_losses_20260911/REPORT.md`.

## #103 — Shop0909 exact step0 net purchase: defensive candidate (2026-09-12)

Built separately from the exact submitted56159253 ZIP. Only the exact initial
BUY13/SELL13/BUY13 wheat sequence becomes BUY13. All action tapes, licenses,
later rules and the frozen incumbent remain unchanged. Ten policy tests pass.

Across29 saved opening observations, the net wheat remains13 in every case:
five improve cash (26–52 coins),24 are unchanged, none worsen. Full-game
diagnostics using the five affected opponent action tapes at new seed39120000
give baseline0–5 vs candidate2–3. Both zero-hire/cow-collapse cases reverse,
with three day1 hands and both cows alive at step48. Original live seeds are
unknown: these are fixed-tape diagnostics, not exact live reruns or held-out
matchup-strength estimates. Three losses remain.

Fresh paired panel: ten unused seeds39119000–39119009,180 games, zero failures.
Direct candidate vs unchanged Shop0909:0W/0L/20T. Each arm scores20–0 vs Kaito,
20–0 vs original pf_all,20–0 vs Suliman fixed,16–4 vs top2 fixed:76–4 each.
All80 matched opponent games have identical reward pairs, worker hashes and
shop sequences. No broad strength gain, no lost wins and no promotion claim.

Total190 full games plus29 one-turn audits. Candidate ZIP SHA256:
`a63d56e478203b281b9560df3224abef322f34fcb81dee812f707720593758fb`.
Report/protocol/raw results/package:
`analysis/shop0909_opening_panel_20260912/REPORT.md`.
Saved opening diagnostics:
`analysis/shop0909_opening_diagnostics_20260912/`.
No Kaggle submission. Retain as a narrow defensive option; the vegetable,
late-Yarn and near-clone sale-timing deficits remain unresolved.

### #103 submission receipt — explicit approval received

User approved the exact frozen opening guard after seeing validation. Uploaded
once: submission56182426,2026-09-12T09:02:16.353Z, PENDING at verification.
Archive SHA remains a63d56e478203b281b9560df3224abef322f34fcb81dee812f707720593758fb.
Four daily submissions remain. No sale-timing or production experiment is
included in this upload. Receipt: analysis/submission_shop0909_opening_56182426.json.

## #104 — Waiting-stock sale timing discovery (2026-09-12; held-out panel pending)

Separate Shop0909_h3 candidate adds held-stock sales scheduled2–3 turns later,
with no worker changes. Four tests pass. Same-observation probe on107749417
changes23 market steps, including a14-wool request at394 instead of waiting
until397; this is activation evidence, not a full-game counterfactual.
Discovery seeds39121000/001, paired seats:4–0, mean margin2537, no failures.
Only two seeds, so not a promotion result. A180-game held-out panel on ten
unused seeds39122000–009 is running in analysis/shop0909_waiting_panel_20260912.
No new submission. Checkpoint: analysis/SHOP0909_WAITING_SALES_CHECKPOINT.md.
The five-hour resume automation now tracks this panel instead of stale W13 work.

### #104 completed held-out validation — September 13, 2026

All180 games completed, zero failures or ties. Ten fresh seeds39122000–009,
paired seats. h3 vs submitted guard20–0 (mean+1487.50,min+578,max+3130).
Distinct-opponent panel: both78–2 (Kaito20–0,pf_all20–0,Suliman18–2,top2 20–0).
No outcome flips. Mean margin changes:+191.15,-186.40,+38.45,+78.10 respectively.
Every matched game's own successful filled-unit totals, own/opponent worker
hashes and shops are unchanged. Average panel margin improvement only+30.33.
Direct gains come from milk/wool/strawberry receipts at equal sold quantities.
Suliman39122008 remains a loss in both seats (-7198 vs control-7466).
Verdict: demonstrated clone-matchup edge, no broad win-rate improvement. Keep
separate and unsubmitted. Four tests pass. Completed evidence and frozen ZIP:
analysis/shop0909_waiting_panel_20260912/REPORT.md. No games duplicated.
Focused scheduled round complete; recurring wakeup stopped. Tomato and later
Yarn production gaps remain for a separately chosen research round.

## #105 — Full latest-submission audit and compatible tomato continuation (2026-09-13)

Downloaded all170 available episodes of56182426 plus five recent rank-one
Majkel1337 games. External record54W/68L/47T; one self-play tie excluded.
All175 exports succeed:251650 cash transitions, zero mismatches. Loss groups:
40 different-production,27 near-clone pricing/timing,1 seed shortfall, and no
day-one staffing collapses. All68 losses end with zero crop yield and no stock.
Full evidence: analysis/shop0909_full_20260913/REPORT.md and two verified archives.

Correction: replay info.seed is available even when configuration.seed is null.
Replayed rank-one108381189 exactly (all720 farm/market/town/private states),
then reproduced both rewards for ten actual own-loss scenarios using the frozen
submitted policy and recorded opponent actions. Opponent adaptation remains
unmodeled in candidate counterfactuals.

Five coherent rank-one route probes lose all20 new-seed discovery games. They
are recorded-route proxies, not the live rank-one policy. Reject those probes.

Skyspace108145550 has identical non-cash farm/private state to ours at432.
Its continuation buys land and10 tomato seeds and eventually sells80 tomatoes.
Built separate tomato432 candidate with exact state/queue/plan guards, cash
threshold10000 and >=2 Farmer/Pizza shops. Eight tests pass. Ten actual losses:
baseline0-10,tomato2-8,h3 sales2-8; all30games valid. Skyspace gap-37042 becomes
-460, JAZ COLD HORN-17597 becomes+2120, ansheng jhang-4209 becomes+700.

Fresh seed39131000-009 paired panel is running. Direct5W/1L/14T; Kaito20-0
for both arms so far. No promotion and no Kaggle upload. Builders and diagnostic
results are saved separately; original submitted artifact remains unchanged.

### #105 held-out panel completed

180games, zero failures. Direct5W/1L/14T, mean+1908.6; tomatoes produced in4/20.
The +/-160 non-tomato seat pair nets zero and is not a tomato-branch result.
Both arms score78-2 on the four-opponent panel, zero outcome flips. Margin
deltas: Kaito+1516.1,pf_all+1289,Suliman+1083.1,top2-408.3. Candidate changes
later shops in4/20 per family because environment randomness is coupled to
farm actions; this is not a fixed-shop price-only comparison.
Activation on169 saved external games:69 eligible (25W/16T/28L), zero
pre-432 action mismatches. Additional fresh Skyspace-recording checks running.
Frozen tomato ZIP SHA2566675155bf551cdeb547028cd226ed7d6c935c6bfeda636dec7c202495cf08195.
Report: analysis/tomato_panel_20260913/REPORT.md. No submission or rank claim.

### #105 completed independent Skyspace check

Ten further fresh seeds39133000-009, both seats,40games/0failures. Against the
fixed Skyspace action recording, tomato9-11 vs submitted baseline8-12: one
gained win, no lost wins, mean margin improvement2243.7. Shops change8/20.
This is a modest targeted improvement, not the live opponent or top10 proof.
Total250 candidate/control games plus20 rejected rank-one route probes and
one exact full-replay seed verification. Eight guard tests pass; all169 saved
external prefixes match the submitted model until432. Frozen package root
main.py/actions.json/tomato.json/LICENSE.txt matches the tested files, last
top-level def is agent. Retain separate; no Kaggle submission. All work for
this replay-comparison/build round is complete, and no evaluation is pending.

## #106 — Authorized tomato submission and two complementary probes (2026-09-14)

Submitted approved frozen tomato432 ZIP once:56226432, COMPLETE, initial600.
Receipt: analysis/submission_tomato432_56226432.json. No further upload approved.

Combined h3/tomato discovery seeds39140000-009, paired seats:19-1/20validgames.
The loss is material (-9702): candidate loses tomato activation and sells0 vs80.
Do not promote. Next ablation should preserve the pre432 prefix before enabling
h3 on fallback branches, but that ablation is not yet implemented/tested.

Built two exact-state-gated day12 sheep continuations from108358878/108143468,
requiring two Yarn shops and10000cash. Six guard tests plus two prefix checks
pass. Six original-seed diagnostics valid; original baseline rewards reproduce.
Deficits change -15313 -> -39 (tomato baseline -10902) and -13768 -> -5.
Neither is a win, and the opponents are fixed recordings. Fresh panel required.
Research details: analysis/RESEARCH_20260914.md. Both experiments stay separate.

## #107 — Current tomato losses and protected portfolio (2026-09-14)

Submission56226432 score1960.3; snapshot40W/33L/2T. Downloaded all33 losses
and8 recent wins. JSON engine audit:58958 verified cash transitions,0mismatches.
15 near-clone losses,18 other cases. Yusuke Hayashi108886864 reveals residual
opening collapse: cash0 at24, no hands, final-70665. Prior netting is insufficient.

Built separate day1_recovery and protected_portfolio variants. Recovery prepends
SELL WHEAT1 before exact threeHIRE orders only with cash<4 and projectedstock>=2.
Portfolio adds exact-state sheep continuations and delays h3 until after432 on
fallback branches only. Seven guard tests pass. All33losses/8controls paired
against recorded opponents at original seeds are running (83games with recovery
ablation); ten fresh paired seeds39151000-009 also running. No new submission.
Evidence: analysis/tomato_losses_20260914/REPORT.md and audited replay archive.

### #107 completed diagnostics and next matched panel

All83 diagnostic games completed, zero failures; all41 baseline reward pairs
exactly reproduce. Four of33 losses become wins and all8 winning controls remain
wins. Worst Yusuke deficit -70665 becomes -15596, still a loss; recovery alone
reaches -15760. Fresh direct10seeds39151000-009:14W/0L/6T, zero failures.
Seven guard tests pass. Evidence: analysis/PROTECTED_PORTFOLIO_REPORT.md.

Standalone crop-only adaptive_agent was a mistaken direction and is parked:
0W/4L in smoke testing. The proven public base remains the development foundation.
Matched four-family held-out panel is running on39162000-009, paired seats,
both baseline/candidate (160games). No submission or broad-strength claim.

### #107 completed four-family panel and expanded tournament

The160-game matched panel completed with zero failures. Both arms78W/2L;
Kaito20-0, original pf_all20-0, Suliman fixed20-0, historical top2 fixed18-2.
Zero gained/lost wins. Results do not support a broad-strength improvement.

User requested all our top models. Added an18-checkpoint tournament on fresh
seeds39163000-009, both seats,360games. Includes original pf_all, Kaito routers,
Astra strawberry, full-market W13, repaired/opening/crop W13, Shop0909 variants,
late Yarn, prvsiyan and pub_v3. Excludes rejected pf_all2 and crop-only prototype.
Status: running. Protocol/source/asset hashes: analysis/top_models_20260914.

Harness correction before this expanded run: selecting _V44_POLICY bypassed
outer router logic in newer Kaito wrappers. Now calls the last top-level def.
Three selector tests pass. Prior four-family panel used original Kaito, not the
newer router wrappers. No agent files changed; no Kaggle submission.

## #108 — Completed 18-model tournament and design checkpoint (2026-09-15)

360 completed games,306W/42L/12T,0failures. Original pf_all20-0 (+26604mean),
Astra strawberry20-0 (+13017); submitted tomato13-1-6; h3 only4-16 despite
positive244.65 mean margin; unprotected tomato+h3 beats candidate20-0.
30 losses have identical worker hashes and sold quantities. This local candidate
is not a universal improvement. Early sales versus production compatibility is
the central conflict; prior early-sales tomato regression remains a veto case.
Design and evidence: analysis/NEXT_MODEL_DESIGN_20260915.md. No model changes
or submission; trace production compatibility before implementation.
