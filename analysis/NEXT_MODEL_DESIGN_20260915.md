# Completed tournament and next-model design

360 games: 306 wins, 42 losses, 12 ties, zero execution failures. Ten fresh
seeds per opponent, paired seats, actual submission entrypoints, 18 saved models.
These are not current live leaderboard opponents.

| Opponent | W-L-T | Mean margin |
|---|---:|---:|
| Original pf_all (not pf_all2) |20-0-0|+26604.2|
| Astra strawberry |20-0-0|+13017.1|
| Submitted tomato432 |13-1-6|+939.45|
| Shop0909 h3 |4-16-0|+244.65|
| Unprotected tomato+h3 |0-20-0|-230.5|

Positive mean margin against h3 hides an 80% loss rate. Do not promote on mean
margin or on beating weaker ancestral models. The separate four-family matched
panel had zero outcome gains over baseline.

## Evidence and conflict

30 of 42 losses have identical worker hashes and identical sold quantities.
The remaining 12 need separate state/production diagnosis. Equal commands alone
do not establish equal states. Actual fill values, quantities, and cash matter.
Example seed39163000 vs h3 loses118: milk receipts are117 lower and strawberry
receipts1 lower, with identical transaction quantities and other fill values.

Protected portfolio defers added sales until after432. Unprotected h3 starts144.
But experiment106 already demonstrated that early sales can disable tomato
activation and cause a9702 loss. Globally restoring early h3 is not a solution.

## Design before implementation

Keep the proven base. Separate production-state requirements from market timing,
but only after tracing the exact compatibility differences at288 and432.
Record positions, crops, animals, seeds, inventories, shed, queues and cash for
both versions on the current h3 losses and the earlier39140002 tomato regression.

If differences are solely surplus sale stock, derive and test a resource-aware
sale rule that reserves all future production inputs and accounts for actual
fills. Do not ignore feed, seeds, fertilizer, capacity, queues or worker state;
do not activate a production route using fabricated observations. If critical
state differs, reject that mechanism and restrict sales to verified safe windows.
No new replay swaps or opponent-name detectors are proposed.

Promotion tests must include protected, unprotected h3, submitted tomato and a
distinct-family held-out panel. Report per-family wins/all games, failures, ties,
median and worst margins. Known tomato-production regression must remain fixed.
A finite undefeated test does not prove an unbeatable agent or a top10 result.

Status: diagnosis/design only; no new model built or Kaggle submission made.
Full records: top_models_20260914/summary.json and results.json.gz.
