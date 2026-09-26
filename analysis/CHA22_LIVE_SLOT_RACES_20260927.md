# Cha22 live close-clone slot races (2026-09-27)

## Scope

Submission 56556133 supplied 142 live replays. Ninety-three decisive games
against external agents with action agreement at least 0.90 were treated as the
close-clone cohort. Fills come only from the cash-verified replay CSV exporter.

## Rejected routes

- A broad replay-route portfolio lost 6 and tied 4 of 10 games against exact
  Cha22.
- Exact shop-pair routing improved to 1-3-16 after fixing a cross-route global
  tomato-eligibility scan, but still did not beat the parent.
- Two source-world route specialists won their source replay, then scored only
  5-11-28 on held-out matching-shop worlds. Replay route transplantation is
  rejected.
- Starting the clone sale-reservation controller earlier at steps 120, 144,
  168, or 192 changed no result. The problem was order position, not horizon.

## Verified mechanism

In close-clone games both farms often sell the same product, quantity, and
turn. Cha22 can nevertheless receive the lower quote when a buy occupies its
market slot 0 while the rival places the sale in slot 0.

Two repeated signatures were strong enough to affect outcomes:

| Step | Product | Cha22 slot | Rival slot | Games | Losses | Value/game |
|---:|---|---:|---:|---:|---:|---:|
| 196 | MILK (12) | 1 | 0 | 6 | 4 | +370 |
| 250 | MELON (24) | 1 | 0 | 6 | 4 | +282 |

The candidate preserves every worker command, market command, and quantity. It
only moves an existing positive sale to slot 0 at those two steps, gated on
public-farm similarity >= 0.90.

## Validation

- Six exact replay-derived opponent tapes: **+652 margin in every game**.
- The two source wins remained wins and became +652 stronger.
- Two of four source losses flipped to wins; the other two improved by +652.
- Exact Cha22, five fresh seeds in both seats: **0-0-10**, mean margin 0.
- Diverse historical panel (v48, prefund, Kaito, pf_all, protected, Shop0909),
  two fresh seeds in both seats: **24-0**, zero failures.
- The similarity gate fired zero times in all 24 diverse-panel games and
  reported zero errors.

Candidate: `variants/cha22_slot_schedule_v1_20260927/main.py`

SHA-256: `2ee70d3c2b7372a8cd04d714d4d45a1f9c1c53d107d1941b29a5a94ece49cf18`

This is a safe measured improvement for one live close-clone family. It is not
evidence of a universal top-10 breakthrough, and no Kaggle submission was made.

