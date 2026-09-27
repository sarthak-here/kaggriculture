# Step1010 / Cha22 compatible-state router — 2026-09-27

## Result

The promoted local candidate is:

- `variants/step1010_cha22_router_step144_brunch_brunch_20260927/main.py`
- SHA-256 `77c115ecf1f82a943a171ca8f661a295ce9be4fcfb9319e3064a2c811a30c588`
- 1,040,259 bytes
- Kaggle-selected callable: `step1010_cha22_router_agent`

It runs Step1010 and Cha22 in isolated namespaces through observation step 144.
When the first two unlocked shops are exactly `BRUNCH_SPOT, BRUNCH_SPOT` and
the public farm-layout similarity is at least 0.90, it continues with the warm
Cha22 policy. Every other world commits to exact Step1010 at step 144.

Exact-source confirmation on one discovery and three held-out shop worlds,
both seats:

| opponent | record | mean margin |
|---|---:|---:|
| exact Step1010 | **8-0** | **+4,034** |
| exact submitted Cha22 source | **8-0** | **+887** |

Seeds: `993004`, `1003033`, `1003048`, `1003059`. All 16 games completed
without an execution failure. Raw result:
`analysis/results/brunch_router_exact_confirmation_20260927.json`.

## Why the handoff is possible

Step1010 and Cha22 issue different market lists early, but their complete own
farm/private observations remain identical through step 91 in six prefix
checks (three seeds, both seats). The first shop is visible at step 72. Their
first physical/private divergence is the money created by Cha22's three-unit
WHEAT sale at step 91. Both policy states are therefore warmed independently;
the router does not try to initialize Cha22 after the fact.

The engine also reuses each day's RNG for weed spawning and shop selection.
Because weed RNG consumption depends on both farms' occupied tiles, a numeric
seed does not define one opponent-independent shop world. Direct paired A/B
games remain valid; comparing shop labels across different opponent pairings
does not. `scan_step1010_cha22_signatures.py` consequently runs the exact
Step1010-vs-Cha22 pairing through the third shop.

## Selection discipline

The broad Step1010-vs-Cha22 discovery sample was 25-5 for Step1010 over 30
unique worlds. A general switch to Cha22 would therefore be wrong. Candidate
branches were tested independently and then on unseen matching-shop worlds:

| branch | evidence | decision |
|---|---|---|
| `BRUNCH_SPOT > BRUNCH_SPOT` at 144 | 8-0 vs each exact parent; three held-out worlds | **keep** |
| first-shop `PET_CAFE` at 72 | unseen 0-2 vs Step1010, -806 | reject |
| `BAKERY > PIZZA_SHOP` at 144 | unseen 0-2 vs Step1010, -209 | reject |
| `BAKERY > YARN_STORE` at 144 | unseen 2-2 vs Step1010 | reject |
| all close clones at 144 | 7-13 vs Step1010 on ten fresh worlds | reject |
| `YARN > SMOOTHIE > YARN` at 216 | source repair still 0-2 vs Cha22 | reject |
| `ICE_CREAM > BRUNCH > YARN` at 216 | one source repair only; no unseen occurrence in valid scan | do not promote |

The discarded multistage prototype did go 12-0 against Step1010 on the six
known failure worlds, but its PET and BAKERY branches failed unseen tests. That
12-0 result is retained as an overfitting warning, not promotion evidence.

## Packaging and safety

The candidate compiles and Kaggle's `get_last_callable` selects the intended
router. Both parent sources retain their Apache-2.0 notices. The recursive
static audit reports three inherited findings in Step1010: two unused `os`
imports and an `open(path)` under a literal `path = None` guard. The exact body
was inspected; that branch is unreachable and the aliases have no other uses.
The router adds no filesystem, network, subprocess, or environment access.

No Kaggle submission was made. A fresh explicit approval is required.
