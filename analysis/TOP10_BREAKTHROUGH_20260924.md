# Top-10 breakthrough search — 2026-09-24

## Outcome

The strongest local foundation found in this search is the unmodified current
public `demand_timing` controller:

- file: `public_candidates/current_20260924/demand_timing/main.py`
- SHA-256: `178ae0f727641cf4b618ebb98ade7aa1a1bed7517281aab9849de82a59d8ed3a`
- final Kaggle callable: `_final_sell_block_reorder_entrypoint`
- status: **local candidate, not submitted**

It is a major broad upgrade over the submitted demand350 controller and every
older family tested, but it is not described as proven top 10.  Its direct
matchup against the exact live controller remains seed-sensitive.

## Why static rank-1 cloning was abandoned

Twenty routes reconstructed from current rank-1 Boey wins were placed under the
full modern legality, cash, weed, reservation, and market-response guard stack.
On their own source worlds they went **0-40** against the live demand350 agent,
with mean margin **-49,823.675**.  The rank-1 policy also diverged almost
immediately across all 20 replays and selected different herd compositions from
observable shop support.

Conclusion: the transferable advantage is an observation-conditioned policy,
not a replay tape.  More route-copying is not a credible path through the
current ceiling.

## Current public-controller search

Five September 22-24 notebooks were downloaded and extracted without executing
notebook code.  Literal payloads were hash-verified and compiled:

| controller | initial fresh screen vs live demand350 |
|---|---:|
| demand_timing | 7-3 |
| population_robust | 6-4 |
| rescue7 | 6-4 |
| shepherd_ledger | 6-4 |
| v57_funding | 8-2 |

Disjoint confirmation rejected the tempting v57 result: v57 fell to **10-10**
against the incumbent and lost **2-18** directly to demand_timing.  Demand timing
was **9-11** against the incumbent on that first confirmation block, so direct
incumbent results alone did not establish promotion.

## Matched broad-panel evidence

On seeds 960000-960004, both seats, demand_timing was tested against six distinct
families.  The exact live incumbent was run against the same opponents and
worlds.

| opponent | demand_timing | live demand350 |
|---|---:|---:|
| V48 clear queue | 10-0 | 10-0 |
| Jaxa2780 | 10-0 | 10-0 |
| Thomas2944 | 10-0 | 4-6 |
| hybrid2965 | 4-6 | 2-8 |
| latepurchase16 | 10-0 | 4-6 |
| response_v3 | 10-0 | 5-5 |
| **total** | **54-6** | **35-25** |

The new controller added **19 wins** on a matched 60-game panel.  An earlier
running commentary incorrectly totalled this as 50-10/+15; 54-6/+19 is the
verified arithmetic.

## Disjoint eight-family confirmation

Protocol: engine 1.32.7, seeds 980000-980009, both seats, isolated agent
processes, 20 games per family, 160 games total, zero failures.  Full hashes and
rows are in `analysis/demand_timing_breakthrough_panel_20260924/`.

| opponent | W-L-T | mean margin |
|---|---:|---:|
| exact live demand350 | 10-10-0 | +601.95 |
| hybrid2965 | 17-3-0 | +630.85 |
| Thomas2944 | 20-0-0 | +1,599.60 |
| latepurchase16 | 19-1-0 | +894.50 |
| response_v3 | 19-1-0 | +843.05 |
| V48 clear queue | 20-0-0 | +3,871.50 |
| Jaxa2780 | 20-0-0 | +5,152.80 |
| pf_all | 20-0-0 | +38,066.50 |
| **total** | **145-15-0 (90.625%)** | |

This clears the historical aggregate 90% promotion bar and completely beats
pf_all on this held-out set.  The 10-10 exact-live result is the remaining
warning: nearby market policies can be coupled and seed-sensitive even when the
broad result is excellent.

## Real-loss replay diagnostics

Against the six frozen opponent tapes from live submission 56496586,
demand_timing went **3-3**, mean margin -1,475.7.  The exact submitted controller
went **2-4**, mean -721.3.  The new policy flipped three individual results but
did not dominate the tapes.  These are causal diagnostics only because frozen
opponents cannot react.

## Patches tested and rejected

Four variants changed only the final SELL-block optimizer activation: start at
step 120, 360, or 504, or require the inherited clone gate.  On fresh hybrid
worlds all four produced the same 6-4 record and nearly identical margins.  The
remaining hybrid weakness therefore is not controlled by this final wrapper.

An independent opening-cash variant preserved five net WHEAT while shrinking
the step-0 20/15 round trip to 8/3.  It beat its unmodified parent **19-1** but by
only **8 coins average**.  Matched controls proved it changed zero close-family
outcomes:

| opponent, seeds 990000-990009 | opening8 | unmodified |
|---|---:|---:|
| live demand350 | 6-14 | 6-14 |
| hybrid2965 | 18-2 | 18-2 |

The opening patch is rejected.  The 19-1 direct headline is a coupling artifact,
not a broader strength gain.

## Decision

Freeze the exact unmodified demand_timing controller as the strongest local
candidate and the next research foundation.  Do not layer the tested timing or
opening patches onto it.  It has enough broad evidence to justify considering a
scarce Kaggle submission, but repository rules require a fresh explicit user
approval after seeing these validation results.

