# Latest public code and discussion audit — 2026-09-27

## Decision

Promote the public **Farmer John and the Idle Seller / Step1010** build to the
next submission candidate. It is the only newly published build in this audit
that passed both the current-lineage head-to-head and the historical-family
panel. No Kaggle submission was made during this audit.

Exact candidate:

- `variants/idle_seller_step1010_20260927/main.py`
- SHA-256: `03165654e70bd04479a1db776f58146531c320e622db09b9e59ae0a4353c7b82`
- size: 1,148,715 bytes
- final callable: `step1010_step1009_fixed_point_agent`
- Apache-2.0 license and notice retained beside the candidate

## Sources reviewed

The newest 200 Kaggriculture notebooks were sorted by last run. Five plausible
updates were downloaded and statically extracted without executing notebook
code:

| Notebook | Extracted `main.py` SHA-256 | Result vs exact Cha22, seeds 990001-990003 |
|---|---|---:|
| Farmer John and the Idle Seller | `03165654...` | 4-2 |
| Demand-Preserving Turn Sale Timing | `55be5d5f...` | 4-2 |
| Kaggriculture Harvest Ledger | `63dde9e4...` | 4-2 |
| Top-2 Master Engine V4 | `55be5d5f...` | duplicate of Demand-Preserving |
| V31 Bronze Going Up | `dc5433c...` | 0-6, mean -7,762 |

The first three produced identical banks on these initial worlds despite
different source hashes, showing that they remain very close descendants on
ordinary boards. V31 is rejected.

The current discussion audit found one methodologically useful post,
"What actually predicted the ladder, and 15 things that didn't". Its measured
recommendations match the corrected local protocol already used here: use
engine 1.32.7, strong trading opponents, real ladder boards where possible,
identical seed/opponent/seat triples, both seats, and promote on per-opponent
win rate rather than average margin. It also warns that one-family panels and
uncontested starter/random agents do not predict the ladder. The remaining new
topics contained hypotheses or tooling suggestions, not a released agent with
evidence stronger than Step1010.

## Validation

All games used `kaggle-environments==1.32.7` and fresh child processes for both
agents. There were zero failed games.

### Against exact Cha22

- seeds `991001..991010`, both seats
- **18-2**, mean margin **+943**

### Against exact currently submitted candidate

Opponent: `variants/cha22_slot_schedule_early_20260927/main.py`, the source of
Kaggle submission 56599813.

- seeds `993001..993010`, both seats
- **14-6**, mean margin **+39.5**

The tiny mean and strong win count are desirable for Bradley-Terry: Step1010
flips close outcomes rather than merely increasing already-large wins.

### Historical-family breadth panel

Seeds `992001..992003`, both seats:

| Opponent | W-L-T | mean margin |
|---|---:|---:|
| V48 | 6-0-0 | +3,381 |
| Prefund | 6-0-0 | +4,352 |
| Kaito | 6-0-0 | +35,701 |
| pf_all | 6-0-0 | +31,430 |
| Protected portfolio | 6-0-0 | +7,998 |
| Shop0909 | 6-0-0 | +7,547 |
| **Total** | **36-0-0** | **+15,068** |

## Live context

Submission 56599813 had 70 completed matches when checked: 32 wins, 26 losses,
12 ties, rating 2006, and only 17.6% wins in its latest 17 matches. This confirms
that the submitted close-clone patch did not generalize sufficiently. Step1010
beats that exact source 14-6 locally, but this remains evidence for a candidate,
not a guarantee of top-10 placement.

## Reproduction

```powershell
.\.venv\Scripts\python.exe analysis\run_bucket_policy_panel.py `
  --candidate public_candidates/refresh_20260927/idle-seller/main.py `
  --model cha22 --seed 991001 --seed 991002 --seed 991003 --seed 991004 `
  --seed 991005 --seed 991006 --seed 991007 --seed 991008 --seed 991009 `
  --seed 991010 --out analysis/results/public_refresh_20260927_idle_10.json

.\.venv\Scripts\python.exe analysis\run_w13_isolated.py `
  variants\idle_seller_step1010_20260927\main.py `
  variants\cha22_slot_schedule_early_20260927\main.py `
  --seed 993001 --pairs 10 `
  --output analysis\results\public_refresh_20260927_idle_vs_submitted_10.json
```
