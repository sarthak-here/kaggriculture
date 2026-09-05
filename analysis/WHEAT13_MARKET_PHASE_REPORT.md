# Wheat-13 market-phase investigation

## Accounting correction

Exact action replay against the pinned 1.32.7 engine reproduced the four repeated
optimized-W13 losses. Successful-fill instrumentation showed that the earlier
$2,383 apparent spending disadvantage was a net-cashflow artifact: buys and sells
can occur in the same step. The actual average purchase disadvantage was about $122.

The opponent instead earned $1,689-$2,849 more sales revenue per game, mainly from
better-priced STRAWBERRY sales. Three routes had identical worker actions for all
719 turns; one matched 648/719. Market actions first differed at step 164 and many
opponent sales were exactly two turns later. The mechanism is shared-market sales
phase, not reduced purchasing or extra production.

## Market-phase candidate

Episode 105805980 seat 0 was rebuilt under frozen W13 guards as
`variants/wheat13_market_phase/main.py`.

| opponent | paired-seat result |
|---|---:|
| frozen W13, replay seeds | 8-0 |
| frozen W13, fresh seeds | 20-0 |
| pf_all | 10-0 |
| Soil | 10-0 |
| Salem | 10-0 |
| latest clone/Soil router | 10-0 |
| reconstructed Gronk | 10-0 |
| earlier Kaito/Soil router | 18-2 |
| Fleong | 16-4 |
| frozen Kaito, discovery | 7-3 |
| frozen Kaito, untouched confirmation | 11-9 |

Production remained unchanged in the 28 W13 games: both sides planted nine and
sold fourteen carrots per game. The untouched Kaito result rejects this candidate
as a universal replacement.

## Rejected shop-only hybrid

Kaito's default, first-YARN, and bakery-capital slots were combined with the market
candidate's second/third-YARN slots. Fresh results were 1-9 versus W13, 1-3 with six
ties versus Kaito, and 10-0 versus pf_all. Shop context alone cannot identify the
opponent lineage safely.

## Structural live-loss finding

W13 was 0-8 against sheep-heavy lean opponents from eight distinct submissions.
Five occurred with second-shop YARN. Ordinary W13 mirrors were 4-2 in that bucket
and 41-29 overall. Second-YARN is therefore a field-context proxy for the lean
sheep-heavy family, not an independently broken W13 route.

Preserve the market-phase route as a specialist and mechanism discovery. Do not
submit it or the rejected hybrid without a proven observable opponent-family gate
or state-compatible continuation.
