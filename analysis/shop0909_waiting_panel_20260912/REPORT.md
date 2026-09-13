# Waiting-stock sales: completed validation — September 13, 2026

## Verdict

The h3 candidate reliably beats the submitted opening guard in their direct
matchup, but **does not increase wins on the distinct-opponent panel**. Keep
it as a separate, unsubmitted clone-matchup candidate. Do not call it broadly
dominant or top10-ready.

No games were repeated during finalization. All180 planned games completed
successfully, with zero ties and zero failures. Four focused contract tests pass.
The frozen protocol uses ten fresh seeds39122000–39122009 in both seat orders.
Every source/action-table/runner hash was checked against the protocol.

## Results

| Opponent | Candidate W–L | Guard W–L | Gained/lost wins | Mean margin change |
| --- | ---: | ---: | --- | ---: |
| Submitted opening guard, direct | 20–0 | — | — | Candidate +1,487.50 |
| Kaito (v46-three-suffix) | 20–0 | 20–0 | 0/0 | +191.15 |
| Original pf_all, not pf_all2 | 20–0 | 20–0 | 0/0 | -186.40 |
| Suliman recorded route | 18–2 | 18–2 | 0/0 | +38.45 |
| Historical top2 recorded route | 20–0 | 20–0 | 0/0 | +78.10 |

The distinct-opponent totals are **78–2 for both builds (97.5% wins/all)**.
Across80 matched candidate/control games, the average margin change is only
**+30.33 coins**, compared with +1,487.50 directly against the guard.
The direct minimum winning margin is578 and maximum3,130.
The earlier two-seed discovery result was4–0; it is separate from this held-out
twenty-game direct result.

The reconstructed opponents execute recorded actions; they are not recovered
live policies, and their labels do not assert current leaderboard ranks.

## What actually changed

Market fills are successful engine transactions, not requested order quantities.
Across every one of the80 matched opponent games, our filled-unit totals for
each operation/product are identical to control. There are zero changes in
our worker hashes, opponent worker hashes or shop sequences. Therefore the
measured panel effects are changes in realized trading receipts/costs, not
additional harvest or a newly selected farm plan.

Direct matchup average sales:

| Product | Candidate units | Guard units | Candidate receipts | Guard receipts |
| --- | ---: | ---: | ---: | ---: |
| Milk | 245 | 245 | 20,296.10 | 19,796.50 |
| Wool | 161 | 161 | 16,853.50 | 16,357.90 |
| Strawberry | 249 | 249 | 28,914.60 | 28,422.30 |

The three receipt differences sum to the direct1,487.50-coin advantage.
Worker hashes between the two seats match in18/20 direct games; do not claim
all direct worker traces are identical. The candidate/control comparisons
against the same external opponents are unchanged in all80 games.

The earlier same-observation probe added a14-wool sale request at turn394 where
the recorded route waited until397. Its23 changed market steps and zero worker
changes were activation evidence, not a full-game counterfactual.
The implementation adds eligible held-stock sales and leaves future requests
intact. It is not an exact quantity-conserving shift of the original orders.

## Retained failure

Suliman at seed39122008 loses in both seats:
candidate **-7,198** versus guard **-7,466**.
The268-coin improvement does not flip either outcome. Full actual fill records
for both losses are retained in audit.json.

No tomato or later-Yarn production response was implemented in this experiment.
Those remain separate leads from the21-loss CSV review. The next research
priority should be a compatible demand/production response, with matched
controls, rather than treating another incumbent-only win as broad improvement.

## Reproducibility and disposition

- protocol.json freezes all180 intended game slots and file hashes.
- raw_results.json.gz retains all results, actual fills, checkpoints, worker
  hashes and shop sequences; summary.json retains the runner summary.
- audit.json independently checks coverage, failures, flips, per-game fill
  equality, worker/shop changes and retained losses.
- finalize_shop0909_waiting.py reproduces the audit and package without games.
- candidate.zip contains only main.py,actions.json,LICENSE.txt with fixed ZIP
  timestamps. candidate_manifest.json records its SHA256 and unsubmitted status.

Archive SHA256:
`c6df1ab05cef2a8db5e10a258f1fad021d0892c847a5e5405210cef49ecc3d8e`.

The incumbent and earlier artifacts were not changed. No Kaggle submission
was made in this validation round. This focused scheduled round is complete;
its recurring wakeup is stopped pending the user's next direction.
