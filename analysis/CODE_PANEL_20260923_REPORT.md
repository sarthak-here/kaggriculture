# Kaggriculture current Code panel campaign — 2026-09-23

## Outcome

The September 23 Code snapshot produced four distinct executable agents and
four controlled branches around the strongest broad candidate. The selected
branch is `variants/panel23_demand_full/main.py`.

It completed every game and achieved:

| Opponent | Seeds | Paired games | W-L-T | Mean margin | Worst margin |
|---|---:|---:|---:|---:|---:|
| frozen V48 | 621000-621004 | 10 | 10-0-0 | +6,659.6 | +623 |
| pf_all | 623000-623004 | 10 | 10-0-0 | +36,540.6 | +25,855 |
| Jaxa2780 | 623000-623004 | 10 | 10-0-0 | +3,525.0 | +2,346 |
| submitted V48+MINGXI router | 623000-623004 | 10 | 10-0-0 | +3,157.8 | +1,012 |

No failures occurred in these 40 broad-panel games.

## Current Code snapshot

The candidate pool was pulled from the live competition Code listing. Hashes
were checked before execution. Two differently titled notebooks, Master Engine
V3 and Population-Robust Economy, generated the exact same 1,006,888-byte
`main.py` (`98df1455...fdf5`) and were counted as one algorithm.

The four distinct retained artifacts were:

| Local model | Main mechanism | SHA-256 prefix |
|---|---|---|
| `panel23_thomas2944` | Thomas opening, herd-safe policy after step 336 | `2714b6eb...` |
| `panel23_hybrid2965` | large multi-layer hybrid with queue/order guards | `a58ee3a1...` |
| `panel23_demand350` | robust order search, fertilizer wash netting, post-netting reorder | `939c4457...` |
| `panel23_latepurchase16` | mature controller plus one 25% late purchase increase | `0957bac0...` |

All four passed Kaggle-compatible last-callable loading and complete paired-seat
smoke games. Against frozen V48 on the same five fresh seeds:

| Candidate | W-L-T | Mean margin | Worst margin |
|---|---:|---:|---:|
| demand350 | 10-0-0 | +6,659.6 | +623 |
| hybrid2965 | 9-1-0 | +6,529.8 | -3,256 |
| latepurchase16 | 9-1-0 | +6,555.2 | -3,104 |
| Thomas2944 | 9-1-0 | +6,143.8 | -3,540 |

## Four demand branches

`analysis/build_panel23_demand_variants.py` builds four separate single-file
models from the exact demand350 source:

1. `panel23_demand_full`: unchanged v350 production path.
2. `panel23_demand_net_only`: fertilizer wash netting without the second reorder.
3. `panel23_demand_reorder_only`: robust reorder without fertilizer wash netting.
4. `panel23_demand_guarded_supply`: full v350 plus one conservative late
   seed/product top-up, excluding land and animals and requiring $15,000 cash.

Direct paired testing on seeds 622000-622004 showed that both final mechanisms
matter and that the new supply hybrid should be rejected:

| Challenger vs full | W-L-T | Mean margin |
|---|---:|---:|
| net only | 0-10-0 | -238.2 |
| reorder only | 0-10-0 | -325.4 |
| guarded supply | 3-7-0 | +269.8 |

The supply branch has a positive mean only because two larger wins outweigh
more frequent tiny losses; promotion is based on wins, so it is not selected.

## Direct comparison with the other recent algorithms

On seeds 624000-624004, demand-full was 5-5 against Thomas2944, 5-5 against
hybrid2965, and 7-3 against latepurchase16. Margins were small: +57.6, -163.0,
and +402.8 respectively. This means demand-full is the best broad continuation
for our existing panel, but not proof of universal dominance over every current
Code family.

## Decision

Freeze `panel23_demand_full` as the campaign winner. Do not promote the three
ablations/hybrid. Before any Kaggle submission, expand the held-out evaluation
to recent live opponent families and obtain explicit user approval.

