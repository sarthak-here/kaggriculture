# W13 sales ablation review

Research only. Based on commit `348901fc8ee65b2a59e00dc81b608cc76856b3a5`.
No Kaggle submission or default-branch replacement is authorized by these results.

## The important code correction

Static decoding establishes that `panel_wheat13` and `wheat13_market_phase`
have identical bundled modules, identical config and identical worker actions
in every one of their seven 719-action route slots. Each slot has the same
60 changed market turns, beginning at route index 250. No baseline order is
removed. The candidate adds SELL requests totaling:

| Product | Additional requested units per route |
|---|---:|
| Strawberry | 92 |
| Fertilizer | 80 |
| Milk | 44 |
| Wool | 6 |

These are requested quantities, not production or successful fills. At runtime,
preemption, stock availability and final liquidation can change the effective
timing and quantities. The report's observed two-turn phase is therefore not a
literal two-turn shift in the committed route arrays. Preserving workers alone
does not distinguish the proposed intervention from the existing candidate.

`w13_sales_static_audit.json` records every changed index. The reproducible
builder asserts identical worker actions/modules/config and retained orders.

## Method

- Official installed engine `kaggle-environments==1.32.7`.
- Separate persistent process per agent prevents bundled `v23`, `v44` and
  `scripts` modules from contaminating the opposing policy. No shared-module
  correctness assumption based only on `game_data.py` hashes.
- Invoke the underlying W13 policy directly in audit mode so exceptions cannot
  disappear inside its catch-all PASS fallback. Normal engine actTimeout remains
  in force; the IPC watchdog is a separate five-second failure safeguard.
- Paired seats, preselected fresh seed blocks; compare baseline and candidate
  against the same opponent on the same seeds.
- Instrument `_commit_unit` for actual successful SELL/BUY fills and prices.
  Do not infer spending from net cash. Per-item unit/value totals and strawberry
  fill timelines are retained in the raw archive.
- Record emitted non-market action hashes. These prove action equality, not
  equality of successful production. Exact fills remain necessary.
- Report failed games explicitly and retain the failed batches. The first two
  Fleong batches failed because this runner initially assumed two-argument
  policies; Fleong takes one. The adapter was fixed and both batches rerun.
  Those 20 harness failures are not agent wins or losses.

## Findings

The result table is generated from the saved JSON in `w13_sales_results.json`.
Small screens are mechanism checks, not promotion evidence.

- Strawberry-only additions: 4-0 discovery (230000-230001), then 10-0 fresh
  confirmation (230200-230204) against W13. This is 14 games over seven seeds,
  not fourteen independent worlds.
- Non-strawberry additions: 4-0 against W13 in the small discovery block.
- Phase vs base with clone preemption disabled on BOTH sides: 4-0. Thus the
  advantage in this screen does not require that preemption controller.
- Full phase and W13 each score 19-1 against Kaito on the same twenty games
  (230100-230104 and 230200-230204), flipping zero outcomes. Phase decreases
  average paired-match margin by about 621 coins across these blocks.
- Strawberry-only additions also score 19-1 on those same twenty Kaito games,
  flipping zero outcomes, with a 488-coin average margin decrease versus baseline.
  Its W13 gain therefore does not establish a general strength increase.
- Full phase and W13 each score 10-0 against Fleong on 230100-230104, flipping
  zero outcomes. Phase decreases average margin by 781 coins.
- In those matched Kaito/Fleong comparisons, emitted worker hashes and shop
  sequences match between baseline and full phase for every game.
- The recovery-gated two-turn delay and the safety-only quiet-window delay each
  score 0 wins, 0 losses, 4 ties, with ZERO delay activations. They are unexercised
  in these worlds; do not interpret the ties as a successful delay mechanism.

The first W13 screen also separates quantity and price effects: strawberry-only
additions sell 262 strawberries per side on average but earn 576 more strawberry
coins. Non-strawberry additions have their own positive effect, so attributing the
entire candidate's gain to strawberries would be incorrect.

## Implemented controls

`build_w13_sales_ablation.py` regenerates standalone variants from committed
sources:

- `w13_add_strawberry`: only candidate's added strawberry SELLs.
- `w13_add_fertilizer`, `w13_add_milk_wool`, `w13_add_non_strawberry`:
  product attribution controls (the individual fertilizer and milk/wool variants
  are built but not yet game-tested).
- `w13_base_no_preempt`, `w13_phase_no_preempt`: matched controller controls.
- `w13_delay_guarded`, `w13_delay_quiet`: actual bounded two-turn postponement.

The delay keeps baseline workers, a single pending batch, zero-quantity
placeholders to preserve other order indices, and final baseline liquidation.
It requires current shed stock, cash/headroom, no upcoming conflicting sales,
no outstanding strawberry preemption debt, and a quiet two-turn obligation
window. The guarded version additionally requires nonincreasing public market
inventory and a positive known-shop consumption forecast. Neither uses private
opponent information or future replay state. Future competitor sales remain
unknown; the forecast is not a guaranteed profit estimate.

Nine synthetic tests exercise actual queue entry/release, no double sale,
purchase/deposit/future-sale vetoes, history gating, reset, and terminal flush.
Live non-activation means these controls are NOT validated as an improvement.

## Decision and next experiments

1. Carry strawberry-only additions forward as the smallest active candidate,
   not a universal or submission-ready replacement.
2. Re-run baseline and this candidate on the ORIGINAL Kaito/Fleong loss seeds
   from the report. Those seeds are not committed in the brief. Do not infer a
   new regression solely from 11-9 without the matched baseline record.
3. Expand to multiple live sheep-heavy opponents and multiple optimized W13
   mirrors, holding out opponent submissions as well as seeds. The current
   local panel cannot establish top-ten strength.
4. Profile which quiet-window veto blocks the delayed sales before loosening
   one. Do not remove cash/stock/deposit guards simply to force activations.
5. If testing a delay where sales fund same-turn purchases, first implement exact
   ordered cash and shed simulation. A generic cash floor is not sufficient.
6. Do not build another shop-only lineage router from these results. The separate
   sheep-heavy production counter remains an unresolved research task.

## Reproduce

```bash
python analysis/build_w13_sales_ablation.py
python analysis/test_w13_sales_delay.py
python analysis/run_w13_isolated.py variants/w13_add_strawberry/main.py variants/panel_wheat13/main.py --seed 230200 --pairs 5 --output analysis/w13_runs/reproduction_strawberry_w13.json
python analysis/summarize_w13_sales.py
```

Runner outputs are exclusive: existing files are never silently overwritten.
Use new, predeclared seeds for further confirmation. Raw evidence is in
`analysis/w13_sales_raw_runs.json.gz`; gunzip and parse the dictionary keyed by
experiment filename. The summary contains its SHA-256.
