# V48 clear-the-queue evaluation

## Artifact audit

The user-provided notebook embeds a complete single-file agent. The extractor
reconstructed its literal byte chunks, verified SHA-256
`4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96`,
compiled the result, and verified that Kaggle's final function is
`_e335_agent`.

The mechanism leaves farming routes, production decisions, purchases, positive
wheat sales, and positive fertilizer sales unchanged. It removes sale requests
that cannot execute, merges repeated cash-product sales, and fills the freed
sale positions with executable sales without moving purchases.

## Fresh broad panel

Protocol: official engine 1.32.7, seeds 430000–430009, both seats, separate
agent processes, 20 games per family, 180 games total, zero failures.

| Opponent | W-L-T | Mean margin | Minimum margin |
|---|---:|---:|---:|
| submitted 2780 | 20-0-0 | +1,274.60 | +520 |
| corrected prefund | 20-0-0 | +1,346.15 | +181 |
| proactive V45 | 20-0-0 | +1,399.80 | +628 |
| Kaito | 20-0-0 | +42,746.50 | +30,245 |
| pf_all | 20-0-0 | +32,772.10 | +24,816 |
| protected portfolio | 20-0-0 | +9,469.60 | +4,374 |
| Shop0909 tomato | 20-0-0 | +9,432.50 | +4,225 |
| Astra strawberry | 20-0-0 | +22,292.10 | +8,223 |
| Kaito-Gronk | 20-0-0 | +39,892.25 | +30,729 |

Overall: **180-0-0**.

## Independent 2780 confirmation

Seeds 430100–430109, both seats: **19-1-0**. Across both independent direct
sets, V48 is **39-1** against submitted 2780. The sole reversal is seed 430109
in seat 1: V48 loses by 4,744, although it wins the opposite seat by 2,034.
This is a real market-coupling/seat sensitivity, so V48 is not described as
unbeatable.

## Known Shawn diagnostic

Against Shawn404's frozen episode-110040845 tape, V48 loses by 1,105 in both
seat orders. The 2780 controller wins that fixed diagnostic by 18,070. Since the
opponent tape cannot react, this identifies a residual economic mismatch but is
not a ranking between reactive agents.

## Improvement attempt

A narrow wrapper used the V47 un-compacted queue only when V48 was seat 1 and
YARN_STORE was the first unlocked shop. On the exact failure seed it worsened
the margin from -4,744 to -5,147. The wrapper is retained as a rejected probe;
the exact V48 artifact remains the promoted local candidate.

The additional shop-prefix stress set was selected under PASS actions. Actual
shop sequences were not preserved under the tested policies because engine RNG
consumption is action-dependent, so its 17-3 result is not presented as a clean
FM/FM conditional estimate.

## Decision

V48 is the strongest locally tested candidate. No modification was promoted and
no Kaggle submission was made.
