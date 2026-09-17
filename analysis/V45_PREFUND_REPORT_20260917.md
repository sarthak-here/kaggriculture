# V45 feed-prefunding experiment — 2026-09-17

## Decision

Keep `variants/v45_prefund_10/main.py` as a tested, separate candidate. Do not
replace the frozen submitted model or claim top-10 strength. No Kaggle upload.
Reject `v45_consumption_guard`: it exchanges five repaired losses for five lost
wins and worsens 20/30 diagnostic margins. Do not combine the two changes.

## Mechanism and opening evidence

The submitted V45 buys/sells 70 wheat on turn zero, then buys five feed wheat
on turn one. The candidate buys ten, sells five, and retains five for feed.
On turn one it suppresses the redundant sale/rebuy only if exactly five wheat
remain. Order indices, workers, animal purchases, seed funding and wage guards
are preserved. Unexpected stock or nonstandard configuration uses the parent.

The exact pinned engine was used on 29 distinct recorded two-turn openings,
both seats. Across 101 ordinary quantities and 20 feed-retaining quantities,
7,018 two-turn scenarios were evaluated. These are recorded-opening diagnostics,
not proof against every possible strategy. For quantity ten, all 58 cases keep
five feed and five hired hands, with at least 1,051 cash after setup. The planned
12 melon seeds, seven wheat seeds and next-day three hires require 1,034.
The best ordinary round-trip worst case is 1,026; submitted quantity70 is 960.

Quantity100 superficially has higher cash but leaves ZERO feed after a partially
filled purchase. It is infeasible, not a winner. Frontier reporting now filters
on feed and hands. Quantity10 was selected before its full-game results; no
full-game quantity sweep was used to choose it.

## Full games

| Test | Candidate | Submitted control | Interpretation |
|---|---:|---:|---|
| Fresh seeds 39171000–009, both seats, direct | 20–0 | 0–20 | Mean +142.2 coins; family-specific improvement |
| Original V45, one fresh seed/both seats | 2–0 | 2–0 | Mean margins +175 / +16 |
| Original pf_all, same paired seed | 2–0 | 2–0 | +27,509 / +27,514 |
| Astra strawberry, same paired seed | 2–0 | 2–0 | +17,013 / +15,073 |
| Historical top2 fixed recording, same paired seed | 2–0 | 2–0 | +12,260 / +17,204; not a current reactive leader |

All 36 fresh games completed without failures. The matched panel is small and
changes zero outcomes; it does not demonstrate broad dominance.

On all 20 audited external losses plus ten narrow wins, fixed-opponent replay
diagnostics resolve to 22–8 instead of 10–20: thirteen losses repaired, one win
lost. **20/30 shop sequences change** under the counterfactual. Fixed tapes do
not react to these worlds, so large gains (including +86,554) are not credible
estimates of gains against the live policies. Even unchanged final shop order
does not establish complete environmental equivalence.

KongKongDe improves −511 to +840 with unchanged shop sequence; Roxy improves
−1,211 to −199 with changed shops. Both now buy 12 melon seeds and sell 72 melons,
and both retain three next-day hands. Roxy remains a loss.

One of the original 30 prefund attempts failed at step zero with the harness's
five-second process timeout. A separately recorded serial retry completed.
The original failure remains in results and resolved_summary; it is not erased.
This is NOT a validation of Kaggle's one-second execution limit. Across both
diagnostic arms and fresh validation: 97 attempts, 96 completed, one initial
failure followed by a completed retry. All 21 controller/entrypoint tests pass.

## Remaining weaknesses and next experiment

Rasmus remains −2,930, Justin −1,505, daulettoibazar −540. All three lose another
117 coins versus the prior replay result: this opening sacrifices some earnings
against that opening family. Datatuu and Pablo also remain losses, with changed
shops. CornHub's second loss narrows to −67. Alperen changes +75 to −193.

Do not spend more trials optimizing only the parent mirror. Next priority is a
complete production-and-worker schedule for the goose/carrot-heavy matchup,
starting from the existing replay evidence for Rasmus. Validate seed, feed,
movement, harvest, return and sale together; adding geese or overriding terminal
harvest alone is not justified. Keep this prefund arm separate to measure which
component supplies any improvement. Obtain a broader reactive-family panel
before promotion; do not use fixed replay windfalls as the promotion criterion.

## Evidence and reproduction

Opening matrices: `v45_opening_frontier_20260917.json`,
`v45_prefund_frontier_20260917.json`. Diagnostic directories:
`v45_consumption_guard_screen_20260917`, `v45_prefund_10_screen_20260917`.
Fresh paired protocol, hashes and compressed results: `v45_prefund_fresh_20260917`.
Resolved diagnostic summary explicitly retains the initial failure and retry.
Existing source corpus is archived in `v45_live_20260916/replay_corpus.zip`.

Use `.venv/Scripts/python.exe` (kaggle-environments 1.32.7), UTF-8 mode:

```text
analysis/v45_opening_frontier.py
analysis/v45_opening_frontier.py --prefund-feed
analysis/build_v45_consumption_guard.py
analysis/test_v45_consumption_guard.py
analysis/screen_v45_consumption_guard.py
analysis/build_v45_prefund.py --quantity 10
analysis/test_v45_prefund.py
analysis/screen_v45_prefund.py
analysis/validate_v45_prefund.py
```

Builders and result directories are exclusive: use a clean checkout / new output
directories for reruns; do not overwrite recorded evidence. Restore expanded
replays from the existing archive if absent. Diagnostic opponent tapes are
regenerated by the consumption screen. `retry_v45_prefund_startup.py` reproduces
the specific recorded startup retry, and `summarize_v45_prefund.py` merges evidence
without rewriting the failed original attempt. All upstream source notices remain.
