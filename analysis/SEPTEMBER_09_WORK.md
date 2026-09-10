# September 9, 2026 — research checkpoint index

The work below was saved locally on September 9 and committed the following
morning in **aae39cd** (September 10, 07:26 IST). This index was added on
September 10 to make that work easy to locate. Git commit dates are unchanged.

## Models and code

- `variants/w13_demand_gated/main.py`: demand-aware wheat trading control.
- `variants/w13_demand_ungated/main.py`: ungated comparison.
- `variants/w13_crop_response/main.py`: price-gated carrot substitutions on
  compatible wheat cycles, with replacement wheat requests.
- `variants/w13_crop_demand/main.py`: combined candidate.
- `analysis/build_w13_crop_response.py`: reproducible crop candidate builder.
- `analysis/test_w13_crop_response.py`: crop substitution guard tests.
- `analysis/test_w13_demand_trader.py`: demand/trading guard tests.
- `analysis/audit_top_market_fills.py`: actual-fill and cash-transition audit.

On September 10, all eight source files above were compared with their contents
in aae39cd and matched after normalizing line endings.

## Results and evidence

- Fifteen local match-result JSON files last modified September 9 contain
  **252 games**. Every file was compared with its entry in the already-committed
  `analysis/w13_response_raw.json.gz`; all matched exactly.
- The September 9 `top50_verified_fills.json` likewise matches its entry in
  `analysis/w13_response_audits.json.gz` exactly. It records 47 fully reproduced
  replays and three terminal discrepancies; this is not an all-50 pass claim.
- The preliminary single-replay audit was not separately tracked. It is now
  preserved at `analysis/demand_trader_runs/top_fill_smoke.json`: episode
  106284557, 719 transitions, zero cash mismatches, with the replay/engine hashes.
  It is historical evidence, not a new match or an additional independent result.

The complete checkpoint, including later confirmation, is documented in
`analysis/W13_RESPONSE_REPORT.md` and Experiment #97. It contains 432 evaluation
games; **252 is the September 9 subset, not an additional 252 games**.

Temporary stderr logs and duplicate expanded results remain local. Older
untracked research dated September 7 is outside this September 9 checkpoint.
No agent was changed or submitted as part of this archival follow-up.
