# Kaggriculture — current state (2026-08-16)

Snapshot of where the project stands, written at handoff. `EXPERIMENTS.md` is the full
ledger (#1–#59); this is the summary you read first.

---

## Ladder

| submission | score | what it is |
|---|---|---|
| **public agent** | **2,309.7** | **NOT OUR WORK** — see attribution below |
| v33 | 1,012.4 | our line: carrot arm + impact sells + terminal sweep |
| v45 | 992.2 | our line: v33 + adaptive herd (current `main.py`) |
| v27 | 959.1 | carrot arm |
| v26 | 963.2 | sheep-first opening |
| (undescribed 08-13) | 710.0 | **unexplained — not in EXPERIMENTS, find out what it was** |

Only the **latest 2** submissions are scored. Cap is **5/day**.
Ratings **seed at 600** and climb; never read a fresh submission's first score as a result.
Ratings also **drift** — v26 peaked 1,019.2 and later read 963.2. Re-check with the CLI,
never quote from memory.

### Attribution — read before touching the top entry

`submit_pub/main.py` is **Salem Ali's public notebook agent**
(kaggle.com/code/salemali7/3094-score-kaggriculture), decoded from its base64 payload and
reproduced **unmodified**. It is not our logic. Attribution sits in the module docstring
and in the submission message; **keep both if it is ever resubmitted.** It was entered on
explicit user instruction because it runs three quadrants profitably where twelve of our
own configurations could not.

**Our own line is `main.py` (v45)** and is developed separately.

---

## What our agent is (v45, `main.py`)

Two quadrants, 8→adaptive cow/sheep herd, strawberry+melon+wheat program, plus:

- **Carrot arm (#47)** — plants carrot late when the 1.32.7 hinge curve makes it spike.
  Gated on the **projected harvest-day price**, not today's, via `daily_demand()` which
  reads `obs["town"]["unlocked_shops"]` and predicts the market drain *exactly*.
- **Impact-ranked selling (#51)** — ranks SELLs by `qty × (price_now − price_after)`
  rather than gross revenue.
- **Terminal sweep (#51)** — spends every spare order line in the last 4 steps emptying
  the shed, since anything unsold at the buzzer is worth zero.
- **Adaptive herd (#53)** — splits COW/SHEEP by measured MILK/WOOL demand from the shops
  that actually unlocked.

---

## The five facts that explain everything

1. **Demand, not land, is the binding constraint (#52).** The whole town buys ~$186,780 a
   season at base prices, split between both players. We already score ~80,000.
2. **Pricing model (#53):** demand/day governs price *recovery*; the curve's **T** governs
   price *decay per unit sold*. MELON (T=300) holds $128 on 1/day demand; WOOL (T=105)
   collapses to $26 on the same demand. Judge a product by base **and** T, never demand alone.
3. **Seat asymmetry (#55):** byte-identical agents at two paths score **108,192 vs 110,260**
   (~2%). A single unpaired game is worthless as evidence.
4. **Never score by self-play (#50):** a self-play ladder ranked three builds 51k<62k<70k;
   against a fixed opponent the "best" was the **worst**.
5. **Never hold a route cursor back (#59):** in replay agents, withholding cursor
   advancement until a unit is back in position makes it walk forever without executing.

---

## Closed — do not re-open without new information

- **LAND (3rd/4th quadrant): 12 controlled configurations, all negative.** Q3 alone (0/32),
  wheat-rush opening (0/20), wheat-rush+fixes (0/24), full top-30 schedule transcription
  (0/24), Q3 inside the improved build (0/24), conditional-on-demand land (46.4%, 35.7%).
  It also **suppresses the carrot arm** every time. The only 3-quadrant agents that work
  are **replays**, not policies.
- **Carrot floor** — bounded both sides: $40 and $50 lose outright, $85 is noise, **$70 is
  correct**.
- **Crew size** — 9 hands; 12 and 14 both lose, now bounded for 3-quadrant farms too.
- **Melon cut** — 0/28. Melon is fine despite 1/day demand (see fact 2).
- **Pen cap** (5/quadrant) — 8.3%. Frees crop tiles but costs more in milk/wool.
- **Sell-order hoisting for queue position** — 53.6% then 50.0%. The engine really does
  resolve orders by index in lockstep across players, but hoisting pushes seeds past the
  10-line cap and the lost planting cancels the gain.
- **Intra-day sell timing** — no edge ($0.34–1.38 spread across the 4-step cycle).
- **Fertilizer** — keep selling it. 237 units for ~$18,679 despite zero town demand.

---

## Tooling (`analysis/`, all committed)

| script | purpose |
|---|---|
| `duel.py A B [n]` | **the only valid evaluation** — paired seats, ranked by win rate; refuses to run if the two agents' `game_data.py` differ |
| `verify_price_model.py` | asserts our price replica matches the engine. **Run after every kaggle-environments upgrade** |
| `q3_profile.py` / `our_profile.py` | day-by-day build profile from replays / from our agent |
| `market_scarcity.py`, `scarcity_trajectory.py`, `spike_revenue.py` | the 1.32.7 hinge measurement suite |
| `tile_utilization.py`, `seed_pipeline.py`, `carrot_trace.py` | execution and planting diagnostics |

`variants/` is gitignored (derived); regeneration recipes are in EXPERIMENTS.md
"Reproducing".

---

## Open leads, best first

1. **Behaviour cloning from the 36-replay corpus.** Derive a *policy* from expert play
   rather than hand-tuning or replaying. This is the honest route to closing the
   ~1,300-point gap between our line (≈1,000) and a replay agent (2,310).
2. **Tomato arm.** Spikes in 52% of games and is the only untouched new-mechanism play.
   Forecastable: projecting with `daily_demand()` gives **12.7% error at 8 days** vs 56–73%
   naive. Note the market is small (~13/day, ~286 units/season ≈ 7 tiles' worth).
3. **Own replay agent (`replay_agent/`)** — currently 18,587 vs v45's ~111,000. Needs
   action-level guards (projected shed, non-desyncing weed repair). Lower priority than (1).

---

## Environment

- `kaggle-environments >= 1.32.7` (1.32.6 = PR #1394 town demand + shops with replacement;
  1.32.7 = PR #1399 hinge curves on CARROT/TOMATO/EGG).
- Engine source is ground truth:
  `.venv/Lib/site-packages/kaggle_environments/envs/kaggriculture/kaggriculture.py`
- Package submissions as `tar -czf x.tar.gz main.py game_data.py` — **never `main.py`
  alone**, that broke a submission once. Extract and run the tarball before submitting.
- Entry deadline **2026-09-23**.
