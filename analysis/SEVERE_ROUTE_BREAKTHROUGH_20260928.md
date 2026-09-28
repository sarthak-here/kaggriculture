# Severe-loss route breakthrough (2026-09-28)

## Decision

Promote `variants/severe_114720494_route_20260928/main.py` as the strongest
local candidate from the 2026-09-28 search. It is not proven top-10 and has
not been submitted to Kaggle.

The candidate reconstructs the winning worker route from live loss episode
114720494 inside the frozen Kaito execution guards. The same route is placed
in every selector slot, so this is a global structural policy, not a detector
that can silently choose the wrong branch.

Exact artifact:

- SHA-256: `55ba2a4371e1b7552820dbc535cb8b522c0cfb97a9f02b357759492052bcd414`
- Size: 116,740 bytes
- Final callable: `_kaggle_submission_entrypoint`
- Compilation: passed

## Direct paired-seat validation

Every row uses ten fresh seeds, both seat orders, and a disjoint seed range.
There were no failed games.

| Opponent | Seed base | W-L | Win rate | Mean margin |
|---|---:|---:|---:|---:|
| frozen pf_all | 1,043,000 | 20-0 | 100% | +25,662 |
| Step1010 recovery | 1,041,000 | 12-8 | 60% | +1,571 |
| corrected MarketShock | 1,042,000 | 14-6 | 70% | +4,849 |
| Cha22 | 1,044,000 | 10-10 | 50% | +452 |
| demand timing | 1,045,000 | 10-10 | 50% | -544 |
| V48 Mingxi/prefund | 1,046,000 | 12-8 | 60% | -67 |
| protected portfolio | 1,047,000 | 12-8 | 60% | +3,840 |
| Shop0909 opening net | 1,048,000 | 14-6 | 70% | +3,240 |
| Jaxa 2780 | 1,049,000 | 12-8 | 60% | +1,156 |
| Kaito clone/Soil router | 1,050,000 | 20-0 | 100% | +39,843 |
| **Combined** | | **136-64** | **68%** | |

This is broad improvement, not universal dominance. Cha22 and demand timing
remain even matchups, and individual seed families still beat the candidate.

## Real-loss coverage

On all 19 external losses from Step1010 recovery submission 56638257, using
the recorded opponent action tapes:

| Agent | W-L | Mean margin | Worst margin |
|---|---:|---:|---:|
| Step1010 recovery | 0-19 | -1,639 | -14,052 |
| severe route | **12-7** | **+3,738** | -12,302 |

On the five severe losses alone the candidate flips four: episode 114708660,
114714773, 114720754, and source episode 114720494. It slightly improves but
does not flip episode 114699795.

Frozen-tape tests are causal diagnostics only because the opponent cannot
react. They are not included in the 136-64 promotion record.

## Current top-10 diagnostic

Against 30 action tapes sampled from the current top ten, the candidate scores
27-3 with +38,423 mean margin and zero harness failures. The comparable
existing diagnostics were 21-9 for Step1010, 23-7 for corrected MarketShock,
and 22-8 for master-v53. This indicates that the new farm structure covers
more of the observed top-player production families, but does not prove a
27-3 result against reactive versions of those agents.

## Mechanism

Across the direct panel the candidate consistently plants 54 carrot seeds and
sells about 173 carrots per game. Its route finishes as a lean three-quadrant,
eight-cow, four-goose farm; purchased sheep are not retained. This removes
the oversized mixed-farm/feed burden behind Step1010's worst live losses while
keeping enough cattle and fertilizer production to compete in lean-economy
worlds.

This is a structural route change, not another terminal-sale or market-order
patch. That distinction explains why it transfers across several loss
families that rejected the previous local overrides.

## Reproduction

The ten direct result files are named
`analysis/duel_severe_114720494_route_20260928_vs_*.json`. The two diagnostic
panels are:

- `analysis/step1010_recovery_live_20260928/severe_route_vs_step_all_losses.json`
- `analysis/top10_live_20260928_severe_route_tape_panel.json`

The candidate can be rebuilt with `analysis/build_replay_route_agent.py`
using replay `episode-114720494-replay.json`, opponent seat 1, and the output
path above.

No Kaggle submission was made. A new explicit approval is required.
