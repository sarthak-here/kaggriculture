# Agent registry

Every agent we have built, submitted, or decoded — what it is, where it came from,
what it measured, and how to get it back. Ladder scores drift and ratings seed at
600 (#62), so treat every score here as a snapshot with its date.

Two rules that govern reading anything below:

- **Win rate, not margin**, is the promotion criterion (a ladder win pays +47.92,
  a loss −16.33, margin does nothing).
- **Head-to-head inside one agent family overstates strength.** Always read the
  coupling column: margin against a *neutral* third party is what is real.

---

## Our submissions

| build | file | ladder | what it is |
|---|---|---|---|
| **v46-three-suffix — SUBMITTED EXPERIMENT** | `submit_v46_three_suffix/main.py` | **55751173: 1,594.7 after 13 episodes** | Local **19-1 unseen vs pf_all**, but first ladder loss came at 1,499 against converged 1,614 Corgi-Samoyed. The direct pf_all result is matchup-specific and does not yet prove safer ladder strength (#85). Frozen SHA-256 `5950fdb0032ede297706bb5aaae48461597563b6322de144ec0dee4274388c59`. |
| ~~pf_all2~~ | `submit_pf_all2/main.py` | **REGRESSION — do not use** | 6C12S swap that lowered feed cost but loses 17.9% to pf_all in that bucket (#80) |
| **pf_all — PRODUCTION INCUMBENT** | `submit_pf_all/main.py` | **2,773.2 — RANK 15 of 6,041** | Frontier V113, all five route slots corpus-screened. 10c4s slot verified optimal across 26 of 143 candidates (#80). **Rating CONVERGED: +0.07/match over its last 20, 50% win rate vs mean opponent 2,781.** Remains the submitted model until explicit approval to replace it. |
| pf1 | `submit_pf1/main.py` | not submitted | first single-slot swap (10c4s only) |
| prvsiyan | `submit_prvsiyan/main.py` | 2,547 | Frontier V113 reproduced unmodified |
| pub_v3 | `submit_pub_v3/main.py` | 1,541 | pub base + route ep94493555 + preempt + hinge |
| pub_v2 | `submit_pub_v2/main.py` | 1,904 | pub base + peikopon route + preempt + hinge |
| pub_preempt | `submit_pub_preempt/main.py` | 1,906 | pub base, `_PREEMPT_ENABLED` flipped on |
| pub (base) | `submit_pub/main.py` | 1,821 | Salem Ali's notebook agent, unmodified |

## Decoded public agents (`agents/`)

Kept in-tree because a notebook can be deleted and these are expensive to
re-derive. Each is the agent source decoded from its notebook's base64/b85+zlib
payload.

| file | source notebook | vs neutral v14 |
|---|---|---|
| `agents/prvsiyan.py` | prvsiyan/kaggriculture-frontier-the-moon-counts-melons | **+80,016** |
| `agents/flexonafft.py` | flexonafft/kaggriculture-multi-route-farming-agent | +74,481 |
| `agents/indarkarhana.py` | indarkarhana/rank-top10-read-the-market-choose-the-farm | +73,532 |
| `agents/pub_base.py` | salemali7/3094-score-kaggriculture | +73,532 |
| `agents/boatlee.py` | boatlee/v16-rc5-high-score-8c-4s-premium-market-lead | +70,756 |
| `agents/andrewsokolovsky.py` | andrewsokolovsky/kaggriculture-breaking-the-tie | not measured |

All are forks of the same `BL-MDgogo-10C4S-R0` base.

---

## Head-to-head (pf_all2, fresh seeds 60000+) — kept for the record only

| opponent | record | margin |
|---|---|---|
| churn variant | 12–0 | +22,732 |
| pub_v1 | 12–0 | +10,097 |
| pub_v2 | 12–0 | +9,177 |
| prvsiyan | 12–0 | +2,844 |
| pub_v3 | 9–3 | +3,054 |
| pf_all | 4–2 | +213 ← **six games, inside noise. Misled us.** |

**That last row is why pf_all2 shipped, and it was wrong.** On a proper sample
pf_all2 loses to pf_all **17.9% (5–23)** in the 6c12s bucket where they differ,
and **33.3% (4–8)** overall on fresh seeds (#80). pf_all is the better build.

Coupling for reference: pf_all2 +77,242 vs prvsiyan's +76,826 — only **+416** is
absolute strength; the rest is share capture from base-family opponents.

---

## The live board (2026-08-23) — and what a realistic target looks like

$50,000 pool, final deadline **2026-09-30**. 6,041 teams.

| # | team | score |
|---|---|---|
| 1 | Ryo Hasegawa | 3,134.2 |
| 2 | Subramanya N | 3,037.2 |
| 3 | Arman Tuganbaev | 2,952.4 |
| 4 | MiMi | 2,952.1 |
| 5 | Crop Dusta | 2,951.2 |
| 6 | Izzoudine Mohamed KANTA | 2,906.3 |
| 7 | ActiveMusyoku | 2,894.2 |
| 8 | Kobe BRYANT | 2,875.3 |
| — | *(cliff)* | |
| 9 | shiiin9 | 2,730.7 |
| **15** | **us — pf_all** | **2,773.2** |

**The entire competitive band is ~360 points wide.** Rating goals stated in four figures
are not achievable by anyone — +1,000 would put us 700 clear of the world #1. State targets
in ranks, or in the **+178 to reach top-5**.

**pf_all is converged**, so rank will not improve by waiting: last 20 matches pay
+0.07/match at a 50% win rate against mean opponent 2,781. Only a stronger agent moves it.

### The promotion bar (user's rule, 2026-08-23)

**A new build must beat every previous model >90% of the time before it ships.** Run the
full `submit_*` ladder with `duel.py` on a fresh `KAG_SEED_BASE`, rank on a **panel of real
opponents**, and never promote on the v14 neutral — that is a coupling check only (#81).

### The promotion rule this cost us

A diagnosis explains a loss; it does **not** rank two candidates. When replacing
component X with X′, the test is **X vs X′ directly** — never "X′ fixes the
metric I blamed for the loss", and never "both beat a third party". Feed cost,
dead seed and wheat churn are all *diagnostics*. The only objective is win rate
against the incumbent, on enough games to leave noise behind.

---

## Derived data (gitignored, regenerable)

| what | how to rebuild |
|---|---|
| `replays_top/` — 373 top-10 episodes, 197 MB | `python analysis/scrape_top_episodes.py --top 10 --max-per-team 40` |
| `portfolio/episode_buckets.json` | `python analysis/portfolio.py classify` |
| `portfolio/episode_comp.json` — farm composition per episode | see #73 in EXPERIMENTS.md |
| `portfolio/seed_label.json` — seed → route bucket | `python analysis/portfolio.py seeds N` |
| `variants/` — all A/B builds | `analysis/route_search.py`, `analysis/portfolio_swap.py` |
| `bc_data/`, `bc_model.npz` | `analysis/extract_bc_dataset.py`, `analysis/train_bc.py` |

**The corpus is the one asset no competitor has** and it exists only on this
machine. It is what beat prvsiyan's own hand-built routes (#74). The scraper is
resumable, but only while Kaggle keeps serving those episodes.

---

## Evaluation tools

| script | use |
|---|---|
| `analysis/duel.py A B [n]` | paired-seat, win-rate scored. `KAG_SEED_BASE` for disjoint seeds |
| `analysis/portfolio_duel.py A B [n]` | same, reported PER ROUTE BUCKET. `KAG_BUCKET` targets a bucket |
| `analysis/submission_progress.py <ids>` | distinguishes a *young* rating from a *bad* one |
| `analysis/rating_steps.py <id>` | per-match rating deltas; shows step-size decay |
| `analysis/v45_vs_corpus.py` | profile an agent against top-20 corpus play, day by day |
| `analysis/route_search.py` | build + screen candidate routes |
| `analysis/portfolio_swap.py <bucket> <n>` | swap one route slot |

---

## The ceiling, stated plainly

Everything in the `BL-MDgogo` family converges around **2,500–2,800**. Three
independent probes all hit the same wall:

- **land** (#56) — a third/fourth quadrant is negative across ~35 configurations
- **feed** (#76) — the #1's lean feed profile does not transplant as a route
- **selector** (#78) — biasing toward more land scores 18.8%

Agents above this ceiling differ in what they can **work**, not in which
recording they replay. Passing it needs a different lineage decoded, not more
route tuning.

## Experimental: pf_all + reserve-safe WHEAT market-maker (#82)

- `variants/pf_all_mm/` — 10-unit WHEAT round trip; **36-4 combined** against pf_all
  over two disjoint 10-seed blocks, but only **16-4 on confirmation**, so not promoted.
- `variants/pf_all_mm20/` — 7-3 screen; not promoted.
- `variants/pf_all_mm40/` — 8-2 screen, +1,019 mean margin; not promoted.
- The mechanism is real and leaves all five farm routes unchanged, but remains seed/seat
  sensitive and did not improve the 7-3 win count against prvsiyan on the matched panel.
- Untouched `submit_pf_all/main.py` remains the production incumbent.

## Experimental: reconstructed top-loss routes and WHEAT thresholds (#83)

- `variants/toploss_ep*` preserves five full opponent routes reconstructed from saved losses.
  Only episode 97144518 passed a 4-game screen; it failed confirmation 6-14 and failed its
  matched portfolio bucket 0-10.
- `variants/pf_all_mm_p{5,10,15,25,50,100}` preserves the WHEAT threshold sweep. None
  improves on the $1 experimental setting; thresholds >=10 mostly tie pf_all.
- Production incumbent remains untouched `submit_pf_all/main.py`.

## Best local candidate: v46-three-suffix (#84)

- Frozen artifact: `submit_v46_three_suffix/main.py`.
- It repairs pf_all's recurring third-shop-YARN weakness with separate, prefix-compatible
  suffixes instead of transplanting a whole incompatible route.
- `SMOOTHIE_SHOP / SMOOTHIE_SHOP / YARN_STORE` and
  `SMOOTHIE_SHOP / BAKERY / YARN_STORE` use two mined compatible suffixes.
- `FARMERS_MARKET / PIZZA_SHOP / YARN_STORE` uses the compatible suffix with its late
  CARROT chain changed to TOMATO; replay traces showed TOMATO was pf_all's decisive product.
- Paired-seat result against pf_all: **20-0** on discovery seeds 93000-93009 and
  **19-1** on unseen seeds 94000-94009.
- The remaining observed weakness is Soil (**8-12**), so this is not universal.
- Submitted to Kaggle as **55751173** on 2026-08-25. Snapshot after 13 episodes: **11-1-1, rating 1,594.7**; see the early-ladder correction in #85.

## Experimental: pf_all reliability audit and suffixes (#90)

- 'submit_pf_all_{clone2,cap3,clone2_cap3,recent_gate}' preserves four strict-market-gate
  probes. Best result was only **9-6 with 5 ties** against frozen pf_all; all are rejected.
- 'variants/pfall_suffixes/' preserves 24 exact-prefix-compatible one-slot variants.
  Twenty-three regress. The step-312 6c8s survivor reached **15-5** on ten bucket-matched
  seeds but changed **zero** outcomes on the fresh four-agent panel.
- These artifacts are research memory, not promotion candidates. Production remains the
  byte-identical 'submit_pf_all/main.py'; no submission was made.
## Experimental: Kaito loss suffixes and Soil probes (#92)

- `variants/kaito_loss_suffixes/ep100606696_s0_default_p243/main.py` is a real
  Kaito-family mirror improvement: **33-3 with 4 ties** against the frozen submitted
  Kaito descendant. It is rejected because the fresh panel was only 85% vs pf_all,
  80% vs Salem, and **45% vs Soil**.
- `variants/kaito_feed_guard/` contains four reserve-safe feed-stock probes. All stayed
  0-8 on the selected Soil failure worlds; do not promote or repeat.
- `variants/kaito_soil_preempt/` contains debt-balanced MILK/WHEAT preemption probes.
  All stayed 0-8 on the same worlds; do not promote or repeat.
- Rebuild/profile tools: `analysis/build_kaito_loss_suffixes.py`,
  `analysis/build_kaito_feed_guard.py`, `analysis/build_kaito_soil_preempt.py`, and
  `analysis/kaito_soil_profile.py`.
- Frozen submitted Kaito remains `submit_v46_three_suffix/main.py`, SHA-256
  `5950fdb0032ede297706bb5aaae48461597563b6322de144ec0dee4274388c59`.
## Experimental: Kaito observable Soil router (#93)

- `variants/kaito_soil_router/main.py` keeps frozen Kaito unless the opponent's public
  step-1 state is exactly the Soil-family opening: 5 hands, 1 quadrant, money <= $10.
- The selected lean branch is episode 94498749 seat 0 after Kaito-compatible action 24.
- Combined fresh Soil result: **37-3 (92.5%)** across seeds 119000-120009.
- Fresh panel: **19-1 pf_all, 19-1 Salem, 20-0 Fleong**.
- No-op proof against frozen Kaito: **4-4 with 12 ties and exactly zero paired margin**;
  every non-tie reward swaps with seat order.
- Submitted after explicit approval as **55871991** on 2026-08-29; initial status PENDING.
  Uploaded `main.py` SHA-256:
  `ccee4de0f1efcbb82ffb31672a4984b0811f46fb7c70a78ade913ecb36766262`.
- Frozen Kaito remains byte-identical.


## Candidate: Kaito clone + Soil router (#94)

- `variants/kaito_clone_soil_router/main.py` keeps the submitted Soil detector and
  remembers any 24-turn public close-clone streak before step 243.
- Only confirmed clones receive the episode-100606696 default suffix; non-clones retain
  the submitted policy exactly.
- Mirror validation: **33-3 with 4 ties (91.7% decisive)** over 40 paired games.
- pf_all no-op proof: **9-1 with every reward identical** to the submitted router on the
  same seeds. Soil retention: **10-0**.
- Scope limit: reconstructed Gronk remains **1-11** because its YARN slot is unchanged.
- SHA-256: `0BDEF3B06CA7BAA1F78B4BE714D27B9238F9908DB0D2A3C34C2E0006B83A3066`.
- Submitted with explicit approval as Kaggle submission **55874991**; initial status
  PENDING. Archive SHA-256:
  `883060840941EE321E6E5BD349046EE07658AE8E900C7F257996CA317A3EDA34`.

## Candidate: reconstructed WHEAT-13 base (#96)

- 'variants/panel_wheat13/main.py' is episode 105165498 seat 1's fixed
  9-cow/8-sheep route rebuilt inside frozen Kaito guards.
- Route identity was independently confirmed across eleven recent replays,
  including four first-shop-YARN worlds; most matched all 719 actions.
- Fresh results: **20-0 pf_all**, 12-0 each against Gronk, Soil, Salem and
  Fleong; 16-4 against original Kaito; 16-4 against Kaito+Soil; **35-5** over
  two blocks against the submitted clone/Soil router.
- It is preserved but **not promoted**: 87.5% against the latest router and 80%
  against two earlier Kaito builds fail the >90%-against-every-model rule.
- Its remaining failures concentrate in first-shop-YARN games. A Kaito suffix
  is not state-compatible because the two bases diverge at action 0.
- No Kaggle submission was made.

## Research checkpoint: W13 crop response + demand trading (2026-09-10)

- `variants/w13_crop_demand/main.py`, SHA-256
  `92fc560beab623fe4ad682f8ed2d3088160ee83591120dfb7e818402e6c75beb`.
- Combines price-gated three-day carrot substitutions and reserve-aware wheat
  trading on `variants/w13_zero_replay/main.py`. Separate controls remain saved.
- Ten fresh paired seeds against repaired W13: **20-0**, +1,669 mean coins.
- Six-family matched panel: **zero outcome flips** versus baseline. Kaito stays
  18-2; Suliman reconstruction stays 4-16; original pf_all/Gronk/Soil stay 20-0.
- **Research only; not top-10 validated or promoted.** No Kaggle submission.
- See `analysis/W13_RESPONSE_REPORT.md` and `analysis/w13_response_results.json`.

## Research checkpoint: W13 opening-net repair (#98, 2026-09-10)

- `variants/w13_opening_net/main.py`, SHA-256
  `a6a512cdac1a54ff4941ab410dd3b28a14ec0e88c598be541719dc86aeb0ad9a`.
- Cancels matched opening wheat trades that drain hiring cash against Suliman.
- Two disjoint paired ten-seed blocks: **36–4 Suliman**, versus control **6–34**.
- Matched Kaito and original pf_all remain 18–2, 3정훈 reconstruction 10–10;
  no changed rewards against those three. Direct prior-model mirror: 1–1–18.
- **Submitted experiment: 56139834**, explicitly approved on 2026-09-10 after
  validation; initial status PENDING, no score yet. Not top-10 validated. 220 evaluation
  games, zero failures; sixteen tests pass. Fixed routes are not live policies.
- Full mechanism, evidence and next investigation: `analysis/W13_OPENING_NET_REPORT.md`.

## Separate research baseline: Shop Router 0909 (#100, 2026-09-11)

- Unchanged inspected public snapshot: `public_candidates/shop0909_20260910/main.py`
  with sibling `actions.json`; reproduce via `analysis/build_shop0909_baseline.py`.
- Saved tested bundle: `analysis/shop0909_panel/agent.zip`, SHA-256
  `9fa78bee25ec86381f59c10025b1713bb5f37294320ca009eb3ab91a99851dde`.
- Ten fresh seeds, paired seats: 20–0 vs W13 opening-net (+13,202 mean),
  20–0 Kaito, 20–0 original pf_all, 18–2 Suliman fixed, 14–6 3정훈 fixed.
- Shared panel 72–8 versus incumbent 68–12: four gained wins, no lost wins;
  180 games total including controls, zero ties/failures; five tests pass.
- Not submitted or universally promoted. Remaining wool and milk/strawberry
  allocation losses documented in `analysis/SHOP0909_BASELINE_REPORT.md`.
- W13 submission 56139834 and original pf_all remain byte-identical.
