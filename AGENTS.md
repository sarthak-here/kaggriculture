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
| **pf_all2** | `submit_pf_all2/main.py` | seeding 2026-08-23 | pf_all with the 6C12S slot fixed (feed 1,312u → 838u) |
| **pf_all** | `submit_pf_all/main.py` | **2,810 (rank ~31)** | Frontier V113, all five route slots corpus-screened |
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

## Head-to-head record of our best (pf_all2, fresh seeds 60000+)

| opponent | record | margin |
|---|---|---|
| churn variant | 12–0 | +22,732 |
| pub_v1 | 12–0 | +10,097 |
| pub_v2 | 12–0 | +9,177 |
| prvsiyan | 12–0 | +2,844 |
| pub_v3 | 9–3 | +3,054 |
| pf_all | 4–2 | +213 |

Coupling: pf_all2 +77,242 vs prvsiyan's +76,826 — only **+416** is absolute
strength; the rest is share capture from base-family opponents.

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
