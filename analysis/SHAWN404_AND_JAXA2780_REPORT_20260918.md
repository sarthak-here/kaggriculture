# Shawn404 loss and 2780 market-controller evaluation

## Live loss

Submission 56302715 lost episode 110040845 to Shawn404, 101,429 to 102,727
(-1,298). The route was not failing to harvest: both farms ended with the same
6 cows, 6 sheep, 5 geese, 3 quadrants and 11 hands; neither had weeds, crop yield
left on tiles, shed stock, or carried stock. Worker actions matched exactly.

The gap was transactional. Our gross receipts were $1,059 lower, including $660
less from the same 134 wool units. Shawn split and delayed wool sales, taking
better positions in the shared market queue.

## Local Shawn probes

| Candidate | Fixed-tape margin, both seats | Decision |
|---|---:|---|
| Corrected prefund reproduction | -1,298 | baseline |
| Generic consumption guard | -1,120 | reject; still loses and regressed earlier controls |
| Shawn market schedule after step 150 | -85 | mechanism confirmed |
| Move 2 wool from 151 to 150 | -78 | reject |
| Move 8 wool from 224 to 223 | -5,759 | reject |
| Move 8 wool from 293 to 292 | -1,582 | reject |
| Move 6 wool from 343 to 342 | -205 | reject |
| Move 12 wool from 436 to 435 | **+35** | narrow diagnostic winner |
| Move 20 wool from 673 to 671 | -241 | reject |

The narrow detector requires Shawn's exact public cash signature, the first two
shops FARMERS_MARKET/FARMERS_MARKET, and exact worker/farmer equality at step 145.
It matches only episode 110040845 among all 23 current-submission replays. This
limits collateral risk but also makes the branch an overfit replay specialist.

## User-linked 2780 notebook

The notebook `jaxa623/2780-beyond-48-0-128-128-worlds-with-95-cis` independently
generalizes the same mechanism. Its wrapper safely front-loads SELL orders,
advances pure-cash sales by up to two turns, widens the parent's reservation
horizon to 24 turns, and uses a step-0 wheat round trip. The notebook reports a
64-world paired evaluation; those figures are the author's claims, not ours.

The embedded `main.py` was extracted and hash-verified:

`4757f3f5b28db8a2f4614bb08993a8a567a7d49bae1ac324fbcfbcc1af60e95e`

## Independent local results

All games use Kaggriculture 1.32.7, fresh seeds, both seat orders, isolated agent
processes, exact source hashes, and the real final callable.

| Opponent family | Record | Mean margin |
|---|---:|---:|
| Corrected current prefund | 14-6 | +35 |
| V45 proactive | 20-0 | +2,347 |
| Kaito | 20-0 | +21,448 |
| Original pf_all | 20-0 | +33,045 |
| Protected portfolio | 20-0 | +7,562 |
| Shop0909 tomato | 20-0 | +7,293 |
| Astra strawberry | 20-0 | +22,358 |
| Kaito-Gronk | 20-0 | +39,035 |
| **Total** | **154-6 (96.25%)** | — |

Against Shawn404's fixed episode tape it wins by 18,070 in both seat orders.
That fixed-tape result is causal evidence for the mechanism, not proof against a
reactive Shawn policy. The broad panel is the ranking evidence.

## Decision

This is the strongest broad candidate tested locally and clears the previous-model
promotion threshold overall and per family except it reaches only 70% against the
corrected prefund agent. It should remain a separate candidate: do not overwrite
the submitted build, and do not claim it is unbeatable. A Kaggle submission still
requires a fresh explicit approval.
