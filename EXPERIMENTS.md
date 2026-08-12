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
