# V48 first genuine external loss — episode 110380424

## Match identification

- Submission: 56325431 (V48 clear-the-queue)
- Opponent: MINGXI LIU, submission 56318693
- Seed: 1213639111
- Seat: V48 seat 1
- Result: 93,561 vs 95,177 (**-1,616**)
- Replay: <https://www.kaggle.com/competitions/kaggriculture/episodes/110380424>

The submission's first listed loss, episode 110369563, is a same-submission
self-match. Episode 110380424 is the first genuine external loss. Only this
external-loss replay was downloaded.

## What did not fail

The replay reconstruction verified all 719 transitions with no cash mismatch.
V48 finished with zero weeds and no crop yield left on tiles. Its gross sales
were **$118,669**, $490 higher than the opponent's $118,179. Therefore this was
not an unharvested-crop, terminal-liquidation, or empty-sale-queue failure.

## Exact accounting

| Component | V48 advantage |
|---|---:|
| Crop economy after crop inputs | -$6,141 |
| Fertilizer trading | +$3,263 |
| Animal products after animal purchases | +$230 |
| Hiring cost | +$1,032 |
| Land | $0 |
| **Final** | **-$1,616** |

V48 sold $490 more but spent $2,106 more, exactly explaining the final margin.

## Root cause

The unlocked shops were:

`SMOOTHIE, SMOOTHIE, BAKERY, FARMERS_MARKET, BAKERY, BAKERY, ICE_CREAM, PIZZA`.

This strongly rewards strawberry and wheat. Carrot has only one supporting shop.
Nevertheless, V48 bought 31 carrot seeds versus the opponent's 6, while buying
163 wheat seeds versus 216. It sold 91 carrots but only 251 strawberries and 404
wheat; the opponent sold 16 carrots, 268 strawberries, and 544 wheat. V48's
generic route diversified into the wrong crop mix instead of adapting production
to the observed shop demand.

The opponent also ran 12 cows and no geese, while V48 ended at 9 cows, 5 sheep,
and 3 geese. However, after animal purchase costs, V48's combined milk/egg/wool
economy was still $230 better. The decisive bug is crop allocation, not herd mix.

## Fixed-tape controls

Against MINGXI LIU's frozen action tape:

| Agent | Margin |
|---|---:|
| V48 | -$1,616 |
| 2780 | -$2,010 |
| proactive V45 | -$1,974 |
| prefund V45 | +$77,330 |
| pf_all | +$5,349 |

The opponent tape cannot react, so the last two wins demonstrate route/economic
compatibility only. They do not establish that those agents beat the live policy.

## Patch direction

The evidence supports a conservative, shop-aware crop-mix gate: reduce carrot
allocation when no PET_CAFE is present and carrot support is limited to a lone
farmers market, reallocating compatible planting capacity toward wheat and
strawberry. This needs state-compatible testing; no patch or Kaggle submission
was made in this analysis.
