# Shop0909: every loss reviewed through CSV

## Scope and verification

Submission **56159253**, the frozen Shop0909 upload, not pf_all or pf_all2.
Snapshot: **September 11, 2026, 10:43:26 UTC**. External completed record:
**53 wins, 21 losses, 14 ties**. Wins/all = **60.2%**. Decisive wins = **71.6%**.
One self-play calibration game is excluded. Public score checked during this
review: **2162.1**, COMPLETE. No live rank was verified.

All **21 losses** and eight recent wins were downloaded and converted through
the existing official-engine CSV audit. **41,702 cash transitions reconciled,
zero mismatches, zero failed exports**, and every final cash decomposition has
zero residual. Seven exporter tests pass. Both replay seats end DONE in all
29 audited games. The CSV review asserts loss-ID coverage against the frozen
ladder snapshot. Later matches are outside this report.

The eight wins are recent comparison cases, not a random or rating-matched
control sample. They cannot establish population-level risk or causal effects.

## Findings

| Descriptive group | Losses | Main evidence |
| --- | ---: | --- |
| Opening cash/seed shortfall | 5 | Fewer than seven day-0 wheat seeds actually purchased. Two complete hiring collapses, one partially staffed day, two milder shortfalls. |
| Near-clone sale-price/timing | 8 | At least 97% full worker-command agreement and identical milk/wool/egg/carrot/tomato/melon sale quantities. Sale timing, realized prices and smaller secondary flows differ. |
| Different production mix | 8 | Vegetable, wool or egg output differs materially from ours. |

Groups are disjoint descriptive labels, applied in that order by
`review_shop0909_losses.py`. They are **not exclusive causes**: one of the
opening-shortfall games also contains a strong tomato response.

### 1. Protect the opening before optimizing later farming

Two severe defeats account for **161,617 of 254,620 total lost coins (63.5%)**,
but only **2 of 21 losses**. Margin share is not rating impact.

Against bhundreds and グレイラットルーデウス, day-0 wheat-seed purchases stop
at four instead of seven, cash reaches zero, all three step-24 hires fail,
and both initial cows are gone by observation 48. Final milk sales are
**24 vs 242**, wool **66 vs 161**, strawberries **84 vs 249**. The route is
already broken before its step-144 shop decision.

The milder cases matter too:

- infamemconculcemus: four wheat seeds, two coins at dawn, **two rather than
  three day-1 hands**. Milk sales end **212 vs 242**.
- way to you, both games: six wheat seeds, six coins at dawn, all three hires
  succeed, but day-1 wheat purchases are **seven rather than eight**. Milk
  ends **218 vs 245**, strawberries **237 vs 249**.

All eight sampled wins buy seven wheat seeds and hire three hands on day 1.
This contrast supports testing an opening guard, but does not prove the guard
would reverse any complete game.

The earlier saved-state test preserved 13 net wheat and saved 52 coins by
replacing step-0 BUY13/SELL13/BUY13 with BUY13. That was **one transition only**.
A full-game test must check subsequent seeds, feed, hires, worker positions,
herd survival and eventual match results before promotion.

### 2. Several losses require better selling, not more livestock

Eight near-clone losses have matching core sale quantities. Seven also sell
the same strawberry quantity; the other opponent sells fewer strawberries.
Fertilizer and wheat flows are not always equal, so these are not eight
identical economies or pure isolated timing experiments.

Example: ibr mo sal sells the same **245 milk and 161 wool**, but average
realized milk price is **72.73 vs our 65.76**, and wool **158.52 vs 143.58**.
At step 394, the opponent sells 14 wool for **2,591**; we sell 14 at step397
for **2,173**, a 418-coin difference on that pair of fills. Whole-game defeat:
4,653 coins. This is concrete timing evidence, not proof that a universal
three-turn advance is safe.

Near-identical recorded commands do not establish identical source code.
Full worker arguments were compared here, unlike the older truncated
first-two-arguments fingerprint. Eight win controls also show >=90% agreement,
so resemblance alone is not a losing-family detector.

### 3. The default production plan misses valuable demand

- **Tomatoes:** beijijun sells 80 vs our zero; fufufukakaka sells 12 vs zero.
  The latter receives **8,049 coins** from those 12 tomatoes, including 11
  sold at step712 for 7,366. Final loss is only 4,601. No tomato product
  purchases are recorded for that opponent, and reconstructed harvest is 12.
  way to you also harvests/sells 140 in one opening-shortfall game.
- **Carrots:** 加油 sells **176 vs 84**, alongside 119 tomatoes and 158 eggs
  vs our zero tomatoes and 78 eggs. The carrot net-receipts gap alone is
  **17,819 coins**, partially offset by our other advantages.
- **Wool:** tc-al sells **344 vs 273**, Phi **223 vs 161**, mmwstudy
  **281 vs 247**, Wufang Hong **277 vs 272**. This includes both quantity
  deficits and price differences, not one universal need for more sheep.
- **Eggs:** Giord Frank sells **170 vs 78**, sacrificing milk
  (**165 vs our 245**) and still wins by 565.

Eighteen losses use the first-two-shop mapping's default plan0. The other three
map to plans3,1,6. This is loss composition, **not a branch loss rate**.

Phi is especially useful: the first shops are Farmers Market/Ice Cream,
followed by Yarn/Yarn and another Yarn later. We stay with six sheep while
the opponent reaches nine. Our selector observes the first two shops and
does not reconsider this later demand. A state-compatible later adaptation
is a specific hypothesis worth testing; a blind route swap is not validated.

## Every loss

All quantities below are **ours vs opponent**. Cash-component gaps can exceed
the final margin because other components offset them.

| Episode | Opponent | Deficit | What the CSV shows |
| --- | --- | ---: | --- |
| 107774237 | bhundreds | 85,020 | Opening collapse: zero day-1 hands, cows gone by step48; milk 24/242. |
| 107764291 | グレイラットルーデウス | 76,597 | Same opening collapse; strawberries 84/249 and wool 66/161. |
| 107750404 | 加油 | 13,582 | Carrots 84/176, tomatoes 0/119, eggs 78/158; carrot receipts gap 17,819. |
| 107737091 | tc-al | 13,462 | Bakery/Yarn plan3; wool 273/344, eggs 0/164; wool receipts gap 16,588. |
| 107779199 | way to you | 12,130 | Opening seed/feed shortfall plus tomatoes 0/140; milk 218/245. |
| 107788563 | way to you | 8,856 | Same opening shortfall without tomatoes; milk 218/245, strawberries 237/249. |
| 107784173 | infamemconculcemus | 7,658 | Four initial wheat seeds and two day-1 hands; milk 212/242. |
| 107768272 | beijijun | 7,014 | Core milk/wool/strawberry quantities match; tomatoes 0/80 add 13,998 receipts for opponent, partly offset by its higher spending. |
| 107766205 | 老乡 | 4,943 | Core quantities match; wool average sale price 48.57/62.20; fertilizer sales 342/354. |
| 107749417 | ibr mo sal | 4,653 | Core quantities match; milk and wool sold at worse prices, with explicit later wool fills. |
| 107793153 | fufufukakaka | 4,601 | Tomatoes 0/12, receipts gap 8,049 despite our higher milk, wool and strawberry quantities. |
| 107758332 | Phi | 4,464 | Later Yarn demand; wool 161/223, receipts gap 14,587, partly offset by our other products. |
| 107762301 | Vishal Kishore | 3,425 | Ice Cream/Smoothie; core quantities match; milk receipts gap 1,817. |
| 107771254 | HananFish | 2,697 | Smoothie/Smoothie; strawberries 249/249 but receipts gap 2,305. |
| 107763297 | mmwstudy | 2,091 | Yarn/Farmers plan1; wool 247/281, receipts gap 8,071. |
| 107791164 | Wufang Hong | 1,433 | Yarn/Pizza plan6; wool 272/277 with worse average price, milk 191/210, eggs 0/20. |
| 107761294 | Vishal Kishore | 682 | Ice Cream/Farmers; milk 245/245 but receipts gap 1,873. Opponent sells fewer strawberries, offsetting part of gap. |
| 107762260 | Giord Frank | 565 | Egg-oriented mix: eggs 78/170, milk 245/165; egg receipts gap 5,256. |
| 107730391 | Berat Egemen Gök | 531 | Core quantities match; strawberry receipts gap 609, with smaller offsets elsewhere. |
| 107759663 | Ayaan Ghosh | 141 | All full worker vectors match; strawberry receipts gap 137, fertilizer sales 342/348. |
| 107787165 | DeeSaa | 75 | All nine product sale totals match; wool receipts -240, milk +114 and other small cash differences. |

## What is not supported

- **Terminal harvesting is not the common problem here.** All21 loss endpoints
  show zero private shed/carried product stock and zero crop yield left on
  tiles. The maturity profiler finds no own positive-yield terminal tiles.
  This does not rule out earlier missed harvests, crop expiry or feed failures.
- There are zero pre-action weed-blocked planting/build requests from our side
  in these losses. Generic extra weed clearing is not supported by this audit.
- Feed-without-wheat request flags are scarce and are not independently proven
  failed executions. Early wheat shortages have stronger transaction evidence.
- Loss seats are 11/10. That alone does not measure seat disadvantage without
  all-game seat exposure and paired tests.
- The contemporary top10 was not rescraped for this focused review. Named
  opponents above are observed live opponents, not assumed leaderboard ranks.

## Recommended test order — nothing implemented or submitted

1. **Opening cash resilience:** smallest step-0 purchase change, with full
   opening-state checks and explicit comparison against the unchanged upload.
   Include all five affected live openings, then held-out paired seeds.
2. **Near-clone sale timing:** compare actual fill schedules, shed arrivals,
   quantities and realized prices. Preserve the farm schedule. Do not use
   worker similarity alone to choose a specialist.
3. **Demand-aware vegetables and later Yarn response:** begin with the
   fufufukakaka/beijijun/Phi mechanisms. Plan the complete compatible
   planting/harvesting/return/sale schedule rather than adding isolated orders.

Keep each experiment separate. Evaluate reacting Kaito, pf_all, current
Shop0909 and distinct opponent families on fresh paired seeds. Replayed action
tapes help reproduce mechanisms but do not recover the opponent's live policy.
Report wins/total, ties and failed games. A mechanism fix is not promotion
evidence until held-out results improve without regressions.

## Evidence and reproduction

- `loss_review.csv`: one detailed row for every loss, including actual sales,
  average prices, harvested quantities, early checkpoints and replay URL.
- `control_review.csv`: the same measurements for eight recent wins.
- `match_summary.csv`, `review_details.json`: cash decompositions and exact
  action-difference steps.
- `replay_corpus.zip`: frozen manifest, raw API snapshot and29 compressed
  replays. `csv_tables.zip`: six audited CSV tables and export statuses.
- `archive_index.json`: SHA256 digests and archive sizes.

Extract the two archives into this directory to restore local evidence.
Regenerate CSV into a fresh directory using `replays_to_csv.py --manifest
<manifest> --output <csv_directory> --audit-fills --workers 4`. Run
`summarize_replay_csv.py --directory <root>`, then
`review_shop0909_losses.py --directory <root> --agent <frozen-main.py>`.
The agent argument is parsed as AST literals only, never executed.
The exact frozen main.py is in the tracked Shop0909 panel agent.zip.
