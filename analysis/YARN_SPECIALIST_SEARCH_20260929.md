# YARN specialist search — 2026-09-29

## Goal

Repair the severe route''s YARN weakness without making the broad agent weaker
than the established local panel.

## Search

Ten routes were reconstructed from current top-player YARN replays and placed
inside identical Kaito execution guards. Discovery used nine YARN seeds,
balanced across YARN first, second, and third, with both seat orders.

Most routes were immediate regressions. Replay 112946412 scored 18-0 in
discovery but failed independent holdout at 0-12-6, proving seed brittleness.
Replay 114268528 was the only robust specialist: 14-4 discovery and 12-6
holdout, or 26-10 combined, with zero failures. Its mechanism is genuinely
different from the severe carrot route: it plants no carrots and uses an
animal/market economy.

## Unconditional hybrid rejection

The guarded hybrid preserved the severe route outside YARN and inserted replay
114268528 into all five YARN slots. On a third, disjoint ten-seed YARN panel:

| Opponent | W-L |
|---|---:|
| pf_all | 14-6 |
| Step1010 recovery | 4-16 |
| MarketShock | 4-16 |
| Cha22 | 4-16 |

All 80 games completed without harness failures. The specialist is useful
against the pf_all/severe family but is not a broad promotion. The
unconditional hybrid is rejected and must not be submitted.

## Next experiment

The policies diverge at turn 0 only in market purchases; farmer and worker
movement align. Established first-turn signatures are separable: pf_all builds
a pasture and buys wheat/hands/cow/sheep, while Step1010, MarketShock and Cha22
use distinct wheat openings. Test a state-compatible opponent router:

1. issue the severe cow-only opening;
2. observe the opponent after turn 0;
3. select replay 114268528 only for the pf_all/severe signature;
4. prepend missing wheat/sheep purchases at turn 1, within the ten-order cap;
5. retain severe fallback for every unknown or strong-panel signature.

Promotion still requires a non-losing held-out record against every established
family. No Kaggle submission was made.
