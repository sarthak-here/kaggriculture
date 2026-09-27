# Step1010 BRUNCH router: first live loss audit

Submission: `56618758`  
Submitted SHA256: `77c115ecf1f82a943a171ca8f661a295ce9be4fcfb9319e3064a2c811a30c588`

## What was actually submitted

The uploaded file is the exact frozen candidate validated in Experiment #129.
It routes only `BRUNCH_SPOT > BRUNCH_SPOT` to Cha22 and otherwise executes the
exact Step1010 parent.  Neither of the first two Kaggle worlds matched that
prefix, so the new branch was not involved.

At the time of this audit Kaggle reported six matches: 4 wins and 2 losses.
The first recorded loss (episode `114342540`, margin -657) was validation
self-play against the same submission.  The first external loss was episode
`114345819` against Oleg Smirnov, 117,201 to 125,333 (margin -8,132).

## Audited external loss

- Shops: `ICE_CREAM_SHOP > YARN_STORE > PIZZA_SHOP`
- Worker-action agreement: 96.66%; both policies share the same opening hash.
- Our farm sold 159 MILK and 307 FERTILIZER.
- Oleg sold 191 MILK and 329 FERTILIZER.
- The +32 MILK (+7,167 coins) and +22 FERTILIZER (+1,021 coins) account for
  8,188 coins, essentially the full 8,132-point result.

The causal trigger was asymmetric weed placement, not the BRUNCH router.  At
step 33 both second hands occupied `(4,2)`, but our tile was a WEED while
Oleg's was empty.  Oleg's `BUILD_PASTURE` succeeded.  Step1010 changed the
blocked build to `DIG`, but did not reschedule it.  At step 69 the farmer
arrived carrying a cow and issued `PLACE COW` on the still-empty tile; that
placement and the following `CARE` were ineffective.  Oleg therefore retained
one additional cow from day 2 and converted it into the milk/fertilizer lead.

All 719 transitions per seat passed the CSV cash audit.  This rules out a
packaging, timeout, stationary-agent, or replay-decoding failure.

## Patch attempt and rejection

A guarded recovery used the otherwise ineffective step-69/70/71 farmer slots
for `BUILD_PASTURE`, `PLACE COW`, `CARE`.  It did create the missing animal,
but the added farm state perturbed Step1010's fixed-point controller on 565 of
719 actions and reduced the exact-seed reward from 117,201 to 80,077.  The
candidate is rejected without broader screening.

This demonstrates that Step1010's closed-loop market/action controller is not
locally composable: a physically dominant farm repair can alter its later
fixed point catastrophically.  Future repair must either preserve the
controller's reference state or replace the affected route/controller as a
complete compatible unit.

Artifacts:

- `analysis/step1010_brunch_live_56618758/`
- `analysis/results/step1010_pasture33_oleg_exact_20260928.json`
- `analysis/build_step1010_pasture33.py`
- `analysis/build_single_replay_tape.py`

No follow-up Kaggle submission was made.
