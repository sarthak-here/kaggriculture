# W13 zero-replay reliability patch

## Root cause

Two severe Wheat-13 losses were reproduced and profiled with successful market
fills, unit positions, nightly animal refreshes and action traces. Against the
latest router (seed 240307, seat order 1), W13 lost by 58,969; against reconstructed
Gronk (seed 240706, order 0), it lost by 26,915. Four cows escaped on day 11 in
both games despite ample wheat and scheduled FEED actions.

The first route divergence was a sparse-controller weed repair. At step 184 a
planned strawberry plant hit a weed, emitted DIG, retried the plant and replayed
eight delayed base actions. A second repair occurred at step 233. The replay tails
shifted workers into collision chains; positions diverged by step 187 and animal
placement first diverged at step 259. Four sheep were not placed, later FEED
actions landed on the wrong cow tiles, and four cows went unfed for two nights.
This is route desynchronization, not a feed-purchase or harvesting shortage.

## Patch

A global aligned-controller ablation removed the catastrophes but discarded useful
weed repairs. The narrower candidate changes only bundled
`PlannerConfig.weed_replay_steps` from 8 to 0: DIG and immediate plant retry remain,
but the controller resumes the current route instead of replaying an eight-action
tail. Candidate SHA-256 is
`e77dea99e4bb085ee4984ab1b2d21727eb49841a544ebe18b7e85ce376beab96`.

It flipped both exact severe failures: -58,969 to +7,889 and -26,915 to +504,
with no animal escapes.

## Fresh paired-seat validation

All games used `kaggle-environments==1.32.7` with separate agent processes.

| opponent | games | result |
|---|---:|---:|
| frozen W13, blocks 241000 and 241900 | 40 | 1-3-36 |
| latest clone/Soil router, 241100 | 20 | 19-1 |
| reconstructed Gronk, 241200 and 241800 | 40 | **38-2 (95%)** |
| original Kaito, 241300 | 20 | **20-0** |
| pf_all, 241400 | 20 | **20-0** |
| Soil, 241500 | 20 | **20-0** |
| Salem, 241600 | 20 | **20-0** |
| Fleong, 241700 | 20 | **20-0** |

All 200 fresh games completed with zero execution failures. Excluding the direct
W13 A/B, the candidate scored 157-3 across seven opponent families. It exceeds
90% against every historical panel opponent and differs from frozen W13 in only
four of forty direct games. The direct changes are one large improvement (+19,667)
and three small regressions (-250, -632, -827), giving a positive aggregate margin
despite the 1-3 decisive count.

## Decision

Preserve `variants/w13_zero_replay/main.py` as the next reliability candidate.
The mechanism and broad panel support promotion, but this is not a claim of
universal dominance. No Kaggle submission was made for this candidate; exact user
approval remains required. `analysis/finalize_w13_zero_replay.py` regenerates the
durable aggregate `analysis/w13_zero_replay_results.json` from the raw local runs.
