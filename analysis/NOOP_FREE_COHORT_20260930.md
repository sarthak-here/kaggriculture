# No-op-free current-rule cohort — 2026-09-30

## Repair

Six frozen agents were copied into `variants/noop_free_20260930/`.  A final
wrapper removes only market rows that Kaggriculture 1.32.7 silently ignores:
empty rows, market `PASS`, malformed quantity rows, and non-positive quantity
rows.  The source agents remain untouched.  Severe and repaired Flexonafft had
no observed no-ops, but matching wrapped copies are included so the cohort is
reproducible and uniform.

Strict full-game auditing found:

- all six reached `DONE` after 720 steps;
- zero hard action-schema errors;
- zero ignored market entries after repair;
- the intended final callable was selected in all six files;
- all six completed worlds containing repeated shop instances;
- repaired Flexonafft prices still matched the engine at 117/117 points.

## Fresh paired-seat round robin

Seeds 1100500–1100504 were played in both seat orders: ten games for every
pair, 150 games total, with zero failures.

| Rank | Agent | W-L-T | Points / 50 |
|---:|---|---:|---:|
| 1 | Step1010 | 44-6-0 | 44 |
| 2 | Severe 114720494 | 38-12-0 | 38 |
| 3 | V48 clear queue | 34-16-0 | 34 |
| 4 | V45 prefund | 24-26-0 | 24 |
| 5 | pf_all | 9-41-0 | 9 |
| 6 | Flexonafft repaired | 1-49-0 | 1 |

Severe beat Step1010 6-4 directly, but Step1010 had the strongest complete
round-robin record.  Step swept pf_all, V45, V48 and Flexonafft 10-0 each.
Severe swept pf_all and Flexonafft, beat V45 and V48 6-4 each, and beat Step
6-4.  This is a cohort ranking, not proof against the external leaderboard.

## Child-versus-parent safety A/B

Each wrapped child was also played against its exact frozen parent on seeds
1100600–1100604, both seats:

| Child | W-L-T vs parent | Mean margin |
|---|---:|---:|
| pf_all | 3-3-4 | 0 |
| V45 prefund | 0-0-10 | 0 |
| V48 clear queue | 10-0-0 | +43 |
| Step1010 | 4-0-6 | +2 |
| Severe 114720494 | 5-3-2 | +4 |
| Flexonafft repaired | 4-4-2 | 0 |

Removing V48's ignored queue entries produced the only consistent direct gain,
although the margin is small.  No child had a negative direct record.  Seat
and shared-market asymmetry can produce non-ties even for behaviorally equal
wrappers, so the zero-no-op Severe/Flex results are controls, not evidence that
the wrapper changed their policy.

## Decision

Keep all six repaired files as separate artifacts.  Step1010 is the strongest
broad member of this internal cohort; Severe remains the strongest direct
counter to Step1010.  The no-op-free V48 is a valid small monotonic repair of
its parent.  None is automatically approved for Kaggle submission.

Reproduction:

- `analysis/build_noop_free_cohort.py`
- `analysis/audit_current_rule_execution.py` with `KAG_NOOP_FREE=1`
- `analysis/noop_free_round_robin.py`
- `analysis/noop_free_parent_ab.py`
