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

## Reproducing

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
