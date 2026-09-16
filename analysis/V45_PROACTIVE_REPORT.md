# V45 proactive clone reservation experiment — September 16, 2026

Original V45 is frozen under public_candidates/cloning_v45_20260916.
Its SHA256 remains2536d41ed5a00c75204b6350f1c76c54259c774cb065ba2a3a0072eedf210d94.

Separate candidate: variants/v45_proactive/main.py,
SHA256831dcc2cba277f12947966a38e25f04fb7854c3116f9669a04c0d00cf611b87f.
All inherited notices remain. This is a local derivative, not an original-source claim.

## Mechanism

V45 uses an8-turn reservation horizon for detected clones and escalates to24
after observing a lost drop-turn sale race. Candidate proactively selects24 only
after six matching worker-position observations plus exactly matching production
layout. Existing sale-stock projection, future pickup exclusions, reservation
debt accounting, terminal limits and72-turn route-boundary limits remain intact.
Nonconfirmed opponents keep the parent behavior. Opening remains unchanged.

Six tests pass, including structural identity of both reservation implementations,
the lost-race detector and the production-layout comparator. Harness now captures
the agent's ordinary telemetry as well as the older delay_telemetry attribute.

## Discovery

Forty games, no failed games or nonzero reported error counters.
Direct four-seed paired screen against original:6W/2L, mean+73.25coins.
Mechanism activated in all8direct games. This is a small mirror improvement.
Matched four-family panel: both versions16W/0L with identical margins:
Astra, original pf_all, tomato+h3 and historical top2 recording, four games each.
The recording is not the live opponent. No broad-strength improvement demonstrated.

Ten untouched seeds39168000–39168009 in both seats are used for confirmation.
No parameter tuning after discovery. Results: analysis/v45_confirmation_20260916.
Do not infer a leaderboard score or top10 placement from these local results.
No Kaggle submission is authorized or made in this work.

## Confirmation complete

Twenty completed games:16W/4L/0T/0failures, mean+399.6coins, worst-113coins.
Combined direct discovery+confirmation:22W/6L. Both losses and wins are retained.
This supports a modest mirror improvement, not universal superiority. Do not
promote under the historical greater-than90%-against-every-model criterion.
Next evaluation should expand distinct-family and counter-opening coverage;
no additional activation thresholds were selected using these confirmation seeds.
