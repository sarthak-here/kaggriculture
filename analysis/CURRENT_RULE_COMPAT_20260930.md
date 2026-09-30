# Historical-agent current-rule compatibility round — 2026-09-30

## Outcome

Five distinct historical checkpoints were run under Kaggriculture 1.32.7 on
fresh, paired-seat worlds.  All games completed, so none has an engine/API
compatibility failure.  Their remaining differences are strategic.

On seeds 1100100-1100102, the strict five-base ordering was:

1. Step1010 missed-pasture recovery
2. V48 clear-the-queue
3. corrected V45 prefund
4. frozen pf_all

Step1010 beat each of pf_all, V45 and V48 6-0.  V48 beat V45 6-0, and both
beat pf_all 6-0.  The severe 114720494 route remains a separate high-variance
lineage: it beat pf_all 10-0 on seeds 1100000-1100004 and V48 4-2 on
1100100-1100102, but lost 0-10 to Step1010, Cha22 and demand-timing on
1100000-1100004.

## Shop-portfolio compatibility finding

Step1010, V48, V45, demand-timing and MarketShock all contain the exact same
modern `_R108_DATA` payload:

- 3,982 actions
- 41 routes
- 64 shop states
- canonical SHA-256
  `4f14e67e729651a46e73eacb9ec45ee559cdc0326815c59c31cd28b1e2e1a680`

Therefore route-data transplantation among those five creates byte-identical
Step1010 children.  Their performance differences come from controller
overlays, reservations, queue handling, recovery logic and branch routing—not
from different shop tables.  The severe agent uses the incompatible older
`_V44_ROUTES` architecture and was correctly rejected as an R108 transplant.

`analysis/build_current_rule_compat_cohort.py` statically traverses compressed
Python wrappers, hashes these payloads, and now records identical donors as a
no-op instead of manufacturing fake variants.

## Genuine old-rule repair: Flexonafft

Frozen `agents/flexonafft.py` already observes unlocked shops dynamically and
caps market orders at ten, but still prices CARROT/TOMATO/EGG with the old
log/linear/linear curves.  The isolated child at
`variants/flexonafft_current_rules_20260930/main.py` changes only those three
products to the 1.32.7 hinge formula.

Direct parent A/B, seeds 1100200-1100209, both seats:

- child 13 wins, parent 5 wins, 2 ties
- decisive win rate 72.2%; all-game win rate 65.0%
- mean margin +65
- zero failures; identical carrot production

This proves the rule correction affects market timing, but the broad panel
rejects it as a competitive promotion.  On seeds 1100300-1100304, both seats,
the child lost 0-10 to each of Step1010, V48, V45 and severe, by mean margins
of -32,343, -29,755, -29,966 and -56,918 respectively.

## Decision

- Preserve the Flexonafft repair as a valid current-engine compatibility
  artifact, but do not promote or submit it.
- Use Step1010 as the current chassis for further work.
- Keep severe as a separate specialist/control; do not force its V44 routes
  into the incompatible R108 portfolio.
- Do not retry route transplants among Step/V48/V45/demand/MarketShock: their
  route/shop payloads are already identical.

No Kaggle submission was made.

## Strict execution audit

`analysis/audit_current_rule_execution.py` then checked the six concrete agents
against the installed 1.32.7 engine rather than treating a final score as proof
of compatibility.  Every agent completed all 720 steps, exposed a callable via
Kaggle's own last-callable selector, emitted no structurally invalid unit or
market action, and completed a world containing duplicate shop instances.

The repaired Flexonafft `_market_price` matched the engine at 117 boundary and
off-boundary points across all nine products, with zero mismatches.  This
directly verifies the hinge implementation and parameters.

There are accepted market no-ops in several controller families: pf_all emits
two market `PASS` placeholders, V45 emits three empty/zero-quantity orders, V48
emits 122, and Step1010 emits 13.  The engine deliberately ignores these and all
games complete; in V48/Step they are part of queue-clearing overlays.  They are
not an API/rule incompatibility, but they prevent describing the agents as
"perfect".  Severe and repaired Flexonafft emitted none in the audited games.

Therefore the precise conclusion is: the current-rule repair is correct and
all six agents are executable on 1.32.7, but only Flexonafft was actually
rewritten for stale rules, and finite execution tests do not prove strategic
perfection.  Flexonafft remains rejected by the broad competitive panel.
