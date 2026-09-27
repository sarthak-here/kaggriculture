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

## Initial patch reading and later correction

A guarded recovery used the otherwise ineffective step-69/70/71 farmer slots
for `BUILD_PASTURE`, `PLACE COW`, `CARE`. It created the missing animal and
changed the shared weed/shop RNG trajectory. Our absolute reward fell from
117,201 to 80,077, but the replayed opponent fell further to 60,209: the actual
head-to-head result flipped from -8,132 to +19,868. Rejecting it on absolute
reward was therefore incorrect; Experiment #131 supplies the promotion tests.

This demonstrates that farm edits are not local: end-of-day weed generation
and shop selection share a day-seeded RNG, and the number of empty tiles
changes how many random draws occur before shop selection. Evaluation must use
head-to-head outcomes, not absolute reward or assumed same-seed world identity.

Artifacts:

- `analysis/step1010_brunch_live_56618758/`
- `analysis/results/step1010_pasture33_oleg_exact_20260928.json`
- `analysis/build_step1010_pasture33.py`
- `analysis/build_single_replay_tape.py`

No follow-up Kaggle submission was made.
