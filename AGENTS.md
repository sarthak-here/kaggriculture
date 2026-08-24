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
| ~~pf_all2~~ | `submit_pf_all2/main.py` | **REGRESSION — do not use** | 6C12S swap that lowered feed cost but loses 17.9% to pf_all in that bucket (#80) |
| **pf_all — BEST** | `submit_pf_all/main.py` | **2,773.2 — RANK 15 of 6,041** | Frontier V113, all five route slots corpus-screened. 10c4s slot verified optimal across 26 of 143 candidates (#80). **Rating CONVERGED: +0.07/match over its last 20, 50% win rate vs mean opponent 2,781.** |
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
