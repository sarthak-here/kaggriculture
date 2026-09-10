# Why submission 56139834 is losing

Snapshot: September 10, 2026. This is the submitted **W13 opening-net + crop response + demand trader**, not original pf_all or pf_all2. Frozen source SHA-256: `a6a512cdac1a54ff4941ab410dd3b28a14ec0e88c598be541719dc86aeb0ad9a`.

## Outcome

Submission score at collection: **1665.5**, COMPLETE. External record: **38 wins, 35 losses, zero ties (52.1% wins)**. One self-play episode is excluded. The leaderboard ZIP puts the team at **rank 1760, score 1680.4**; that is the team's better active submission, not this candidate's score.

The central weakness is **production composition**, with a separate smaller near-clone sale-price problem. Execution guards are not the recurring bottleneck in this sample. The local opening-cash improvement was real against its tested opponent, but it did not establish broad ladder strength.

## Data and verification

- All 35 external losses; eight most recent external wins as controls.
- Two recent completed games for each current top-ten team, selected by recency, not high reward. Twenty team/game observations occupy seventeen unique games.
- **60 unique replays, 120 player records, 86,280 turn transitions, 850,868 worker requests, 97,108 market requests, 61,147 aggregated successful transaction rows, 3,600 player-days.** A fill row can contain several executed units.
- Official engine 1.32.7 reconstructed every cash transition: **86,280 matched, zero mismatches**. The final revenue-minus-expense decomposition also has **zero residual for all 63 labeled player/game comparisons**.
- Seven exporter tests pass: action alignment, gzip/plain input equivalence, missing-private handling, formula escaping, explicit corrupt-input failures, complete cash accounting, and oversized requests not being treated as fills.
- Requested actions at record `i+1` are paired with the preceding observation. Successful HIRE and BUY_LAND are audited separately from per-unit market transactions. Engine hooks are restored after every transition.

This is descriptive evidence, not a counterfactual trial. Eight selected controls cannot estimate conditional loss rates by shop bucket. Two top-player replays cannot recover a live policy or establish its general strategy.

## 1. The same farm meets different economies

All **43** analyzed candidate games reach the same maximum herd: **9 cows and 8 sheep**. Every loss sells **195 wool**, and none sells eggs. In **33/35 losses**, the candidate sells just **9 carrots**; the other two sell 27 and 102. Opponents sell more carrots in **31/35 losses**, and sell eggs in **18/35**.

The existing crop controller only considers its prescribed wheat-cycle substitutions after step 300, with a 5,000 cash reserve and conservative instantaneous-price gate. The recorded production shows that this narrow response does not reliably cover the carrot gap. Loosening the gate alone is not a validated remedy: feed replacement, timing, worker positions, production and sale proceeds must be tested together.

Assigning each loss to its **largest negative cash component** gives:

| Component | Losses |
| --- | ---: |
| Carrot net receipts | 11 |
| Egg net receipts | 8 |
| Wool net receipts | 7 |
| Strawberry net receipts | 5 |
| Milk net receipts | 3 |
| Wheat net receipts | 1 |

Net receipts subtract BUY_PRODUCT costs for the same product. Seeds, livestock, hiring and land remain separate expenses. These categories identify the largest accounting deficit, not a unique cause: multiple deficits and compensating advantages coexist.

### Concrete losses

| Opponent / replay | Margin | Evidence |
| --- | ---: | --- |
| Roman Svet / 107444361 | -21,877 | Carrots 27 vs 294; eggs 0 vs 184. Carrot revenue alone is 21,310 lower. Our higher wheat/fertilizer receipts do not compensate. |
| Egor Trushin / 107462916 | -18,610 | Wool 195 vs 251; carrots 9 vs 85. Wool revenue is 13,879 lower. |
| Jane Street Farmers / 107451201 | -14,235 | Carrots 9 vs 84; eggs 0 vs 78. The rival's complete worker-command trace matches one sampled Yusuke Hayashi game, not necessarily its market policy. |
| kta_jpn / 107427634 | -1,835 | Worker operation/target signatures agree on every turn (quantity arguments excluded). Both sell 262 strawberries and 261 milk; strawberry revenue is 24,592 vs 25,895. Sale prices/timing remain relevant in close relatives. |

Roman is not simply ahead from the opening: at the end of day 15 (zero-based), our cash is 24,900 vs 7,789. At day 20 it is 42,790 vs 41,197; by day 25 it is 47,849 vs 58,084. The final reversal is a later-income failure. See `days.csv` for the full progression.

## 2. What is not the dominant explanation

- **Zero weed-blocked PLANT/BUILD requests** by our agent in all 35 losses.
- Only **six FEED requests with no carried wheat at an unfed animal**, across all losses. This is a pre-action risk count, not a counterfactual loss estimate.
- Terminal field audit: each loss ends with **six immature wheat tiles**, planted day 28 with only one day of age, plus **one harvest-ready wool unit**. The six wheat units must not be called missed mature harvests: the official first-yield age is two days.
- Terminal shed/carried products average **8.83 units** in losses versus **9.0** in the eight win controls. Missed inventory has value, but this evidence does not explain the recurring five-figure deficits.
- Gross wheat turnover is misleading. Our wheat net receipts exceed the opposing farm's by **1,766 coins on average in losses**. That is not the trader's causal benefit, because it includes farm wheat and shared-market effects; it does rule out labeling all grain purchases as pure waste.

## 3. The current top ten

Rank and rating are the downloaded snapshot, not a permanent claim. All listed teams have two labeled replay observations in `top10_summary.csv`.

| Rank | Team | Rating |
| --- | --- | ---: |
| 1 | SpaTaro | 3089.4 |
| 2 | Otter Vibe | 3033.1 |
| 3 | feel the agi | 2993.2 |
| 4 | Himanshu Kumar | 2992.1 |
| 5 | binghua | 2982.0 |
| 6 | mtmr_s1 | 2966.8 |
| 7 | Mengfei Li | 2965.0 |
| 8 | Unknown Mother-Goose | 2960.8 |
| 9 | kanno | 2955.0 |
| 10 | Yusuke Hayashi | 2954.5 |

SpaTaro's two observed farms differ markedly: one reaches 15 cows, while another reaches 5 cows/3 sheep and sells 359 carrots. Otter Vibe sells 374 and 208 eggs in its two samples. Several other sampled leaders share the **84-carrot / 78-egg / 161-wool** output pattern found among our losing opponents.

**10/35 loss opponents** have at least 90% exact worker-command agreement with a sampled top-ten trace. Three have 100% agreement: forever young, Jane Street Farmers and Evan Tobias. These comparisons include all worker command arguments, exclude market orders, and do not prove identical source code. Four losses have at least 90% worker-step agreement with our own farm under the exporter's simpler two-argument signature. Therefore we face both distinct production families and close relatives; neither a universal clone counter nor a universal feed repair covers both.

## 4. Public models and discussions checked

Downloaded notebook sources were inspected as data, **not executed**. Sources are archived with this report.

- [Yusuke Hayashi: Shop Router 0909](https://www.kaggle.com/code/yhay81/shop-router-0909): 13 complete plans; selection at step 144 from the ordered first two shops; worker-local same-day weed queues; qualified sale advancement and final liquidation. This is the most directly relevant public baseline to evaluate next. Its author is rank 10 in our snapshot; that does **not** prove the published notebook is their exact ranked submission.
- [Prvsiyan: The Moon Counts Melons](https://www.kaggle.com/code/prvsiyan/kaggriculture-frontier-the-moon-counts-melons): the refreshed notebook describes a bounded livestock substitution that waits for a third shop. Its own fresh comparison reports no gained wins, and unresolved wool/egg production deficits. Useful mechanism to investigate, not evidence of a superior ready-made model.
- [18,144 episodes: local win rate ranks backwards](https://www.kaggle.com/code/dariushafshar/18-144-episodes-local-win-rate-ranks-backwards): its author's two candidates rank oppositely locally and on the ladder. This reinforces reporting distinct opponent families and paired outcome flips, not just incumbent head-to-head wins.
- [Discussion: X-ray your agent](https://www.kaggle.com/competitions/kaggriculture/discussion/738563): describes within-shop-world fingerprints and kinship analysis. Our CSVs now provide the raw material for similar diagnostics. Historical claims about that day's leader were not treated as current facts.
- [Discussion: strongest agents being retired](https://www.kaggle.com/competitions/kaggriculture/discussion/739179): describes changing leader families and near-fixed routers versus adaptive traces. Explanations for retirement in comments are speculation, not established causes.

## Next experiment justified by this evidence

**Evaluate Shop Router 0909 unchanged first**, as a separate baseline, then investigate an early, state-compatible carrot/egg production branch or a shop-specific wool continuation. Preserve the existing W13 and original pf_all. The first question is whether the new production schedule transfers—not how to add another market wrapper.

Use the recorded losses for diagnosis only. Freeze at least ten unused seeds in paired seats for candidate/control comparisons, with distinct reacting public implementations and original pf_all. Deduplicate shared plans, report wins/total, ties, failed games, newly lost wins and changed shop sequences. Replayed top-player tapes are stress controls, not their recovered adaptive agents. No new model test or Kaggle submission was performed in this analysis task.

## Reproduce and inspect

See `REPLAY_CSV_README.md`. `replay_csv_56139834/match_summary.csv` is the concise loss table; `terminal_tiles.csv` records maturity; `opponent_trace_neighbors.csv` records exact worker similarity. The complete six CSV tables and source replays are in verified ZIP archives. The original expanded CSV files also remain locally under `replay_csv_56139834/csv_audited/`.
