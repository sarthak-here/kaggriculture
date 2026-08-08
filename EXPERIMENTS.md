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
