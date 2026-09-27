# Cha22 early slot schedule promotion (2026-09-27)

The first two-step slot patch was expanded only where the live corpus showed a
repeated early close-clone race. The promoted schedule is:

| Step | Product |
|---:|---|
| 150 | WOOL |
| 196 | MILK |
| 249 | MELON |
| 250 | MELON |
| 252 | MELON |
| 270 | MILK |

Every change moves an existing positive sale to market slot 0. Worker commands,
quantities, and the remaining market commands are preserved. The public farm
similarity gate is 0.90.

## Replay-derived validation

On six exact opponent tapes from live submission 56556133, the candidate gained
851–859 coins in every game. Both prior wins remained wins. Two of four prior
losses flipped to wins.

## Fresh validation

On seeds 1044000 and 1044001 in both seats:

- exact Cha22: 0-0-4, mean margin 0;
- v48: 2-2, mean margin +4,238;
- prefund, Kaito, pf_all, protected, and Shop0909: 20-0.

The controller fired zero times and reported zero errors in all 28 fresh games,
so those outcomes are exactly inherited from the Cha22 parent. This panel tests
false positives and parent preservation; the six source-world tapes test the
intended close-clone activation.

## Rejected expansions

- A support-filtered late schedule fired at steps 529, 552, 668, 673, and 684.
  It lost all four fresh games against exact Cha22 by 90–258 coins and is
  rejected.
- Copying five rare opponent worker actions was tested one action at a time.
  Two helped their source world (+130 and +90), three were neutral or harmful.
  Combining the apparently positive actions regressed another clone family and
  is rejected as opponent-specific overfitting.

Promoted local candidate:
`variants/cha22_slot_schedule_early_20260927/main.py`

SHA-256:
`93c7183b581c28933fb6c46fb5c494200738e7dea194c4a847f91b434020f6dd`

No Kaggle submission was made.

