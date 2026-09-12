# Shop0909 opening-net evaluation — September 12, 2026

Only the exact step0 BUY13/SELL13/BUY13 wheat sequence becomes BUY13.
Every later rule, action tape and license is preserved. The base is the exact
Shop0909 submission56159253 archive. Original pf_all is used, never pf_all2.
Ten contract tests pass across baseline and candidate. No Kaggle submission.

## Fresh paired panel

Seeds39119000–39119009, both seats,180 full games. Process-isolated agents.
All planned games completed with zero failures. Ties remain in the denominator.

| Matchup | Wins | Losses | Ties | Games |
| --- | ---: | ---: | ---: | ---: |
| direct | 0 | 0 | 20 | 20 |
| candidate_kaito | 20 | 0 | 0 | 20 |
| base_kaito | 20 | 0 | 0 | 20 |
| candidate_pf_all | 20 | 0 | 0 | 20 |
| base_pf_all | 20 | 0 | 0 | 20 |
| candidate_suliman_fixed | 20 | 0 | 0 | 20 |
| base_suliman_fixed | 20 | 0 | 0 | 20 |
| candidate_top2_fixed | 16 | 4 | 0 | 20 |
| base_top2_fixed | 16 | 4 | 0 | 20 |

| Family | Gained wins | Lost wins | Changed shops | Identical reward pairs | Mean margin delta |
| --- | ---: | ---: | ---: | ---: | ---: |
| kaito | 0 | 0 | 0 | 20/20 | 0.0 |
| pf_all | 0 | 0 | 0 | 20/20 | 0.0 |
| suliman_fixed | 0 | 0 | 0 | 20/20 | 0.0 |
| top2_fixed | 0 | 0 | 0 | 20/20 | 0.0 |

Retained candidate losses against the top2 fixed tape:
| Seed | Seat | Deficit | Milk ours/opponent | Strawberries ours/opponent |
| --- | ---: | ---: | --- | --- |
| 39119003 | 0 | 7973 | 245/261 | 249/315 |
| 39119003 | 1 | 7973 | 245/261 | 249/315 |
| 39119008 | 0 | 10018 | 245/261 | 249/315 |
| 39119008 | 1 | 10018 | 245/261 | 249/315 |

Kaito means the existing submit_v46_three_suffix panel opponent. Suliman
and top2 are recorded-route reconstructions, not their live policies.
Source and runner hashes are frozen in protocol.json. A source hash alone
does not substitute for comparing actual outputs.

## Saved-opening audit and full-game fixed-tape diagnostics

Across29 saved first transitions: five improve cash,24 are unchanged,
none worsen, and all preserve13 net wheat. The maximum saving is52 coins.
These one-turn checks use the original market state and recorded opponent action.

Five affected opponent tapes then run against both builds at seed39120000,
in their original seats. The original live seeds are absent, so these are
new seeded diagnostics, not exact live replay reruns or held-out strength tests.

| Source episode | Arm | Our reward | Opponent reward | Day1 hands | Cows at step48 |
| --- | --- | ---: | ---: | ---: | ---: |
| 107764291 | base | 48927 | 116845 | 0 | 0 |
| 107764291 | candidate | 100948 | 97687 | 3 | 2 |
| 107774237 | base | 48892 | 115777 | 0 | 0 |
| 107774237 | candidate | 101356 | 97378 | 3 | 2 |
| 107779199 | base | 51620 | 57096 | 3 | 2 |
| 107779199 | candidate | 97806 | 101857 | 3 | 2 |
| 107784173 | base | 119610 | 128147 | 2 | 2 |
| 107784173 | candidate | 97546 | 98577 | 3 | 2 |
| 107788563 | base | 52379 | 58313 | 3 | 2 |
| 107788563 | candidate | 97093 | 102125 | 3 | 2 |

Baseline0–5 becomes candidate2–3. Both severe zero-hire/cow-loss cases
reverse. The two way-to-you cases and infamemconculcemus remain losses.
Their fresh seeded shop sequences can change when farming changes weed RNG
consumption; final margin improvements are not isolated price/cash effects.

## Decision

This is a narrowly supported opening-resilience change, not proof of broad
dominance or top10 strength. Direct games against the unchanged upload tie.
Retain the candidate separately. Do not claim that cash savings reverse every
loss or infer leaderboard improvement from fixed-tape counterfactuals.
No further model changes are bundled. No submission without explicit approval.

## Reproduction

Run build_shop0909_opening_net.py to reconstruct from the tracked original archive.
Run test_shop0909_baseline.py and test_shop0909_opening_net.py.
run_shop0909_opening_panel.py freezes a new seed protocol and refuses an existing output.
run_shop0909_opening_diagnostics.py generates tapes from the archived loss corpus.
audit_shop0909_step0.py audits the first transitions. This finalizer checks
all source hashes and packages candidate.zip with deterministic ZIP timestamps.
Raw results are stored as gzip, including checkpoints, fills, worker hashes
and shop sequences. candidate_manifest.json contains exact archive/member hashes.
