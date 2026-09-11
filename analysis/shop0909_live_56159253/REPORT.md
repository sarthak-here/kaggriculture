# Shop0909 live checkpoint — September 11, 2026

Submission 56159253 is COMPLETE, public score **2162.3** at the check around
10:31 UTC. W13 56139834 is **1591.9**. The episode snapshot contains 85 external
completed games: **52 wins, 20 losses, 13 ties** (61.2% wins/all games; 72.2%
decisive-only). These are current measurements, not a convergence claim.

Two severe losses received an offline audit:

- 107774237, seat 0, bhundreds: **38,020 vs 123,040**, deficit 85,020.
- 107764291, seat 1, グレイラットルーデウス: **34,902 vs 111,499**, deficit 76,597.

Both have the same opening cash/production collapse, before shop routing:

1. Step 0 requests BUY 13 WHEAT, SELL 13 WHEAT, BUY 13 WHEAT.
2. After step 1's purchases and five hires, cash is 1,000.
3. Seed purchases exhaust cash by step 17; subsequent seed requests fail.
4. At step 24 all three scheduled HIRE requests fail with zero cash.
5. Both initial cows disappear by observation 48 after the unstaffed day.
6. At observation 144 the farm still has one quadrant and only 213 coins.
   The later route cannot rebuild its intended economy; final herd is one cow,
   three sheep and one goose in both games.

The official-engine CSV auditor completed both replays. Its cash verification
must be checked before using transaction totals. Raw replays are preserved as
gzip files; expanded raw JSON/CSV remain local and are reproducible with
`analysis/replays_to_csv.py`.

## Bounded one-turn experiment, not a validated agent fix

Using each saved initial observation and the opponent's recorded step-0 action,
replace our three market orders with one BUY 13 WHEAT. Official worker/market
execution gives **2,630 coins instead of 2,578**, with the same **13 net wheat
units** in both cases: **52 coins saved at that transition**.

This does not establish that 52 coins survive subsequent market interactions,
that the cows survive, or that the final loss reverses. No full-game
counterfactual, new agent variant, fresh panel or Kaggle submission was run.
Worker commands are unchanged in this one-turn diagnostic. The diagnostic
never loads an opponent's executable policy.

The earlier W13 opening-net wrapper only applies at steps 2–23; copying it
unchanged would miss this step-0 pattern. A prospective Shop0909 experiment
must separately test the exact step-0 replacement, confirm inventory/cash and
day-1 hiring, then use held-out paired seeds and reacting opponents. Preserve
the submitted archive and do not promote on these selected losses.

`opening_diagnosis.json` records source hashes, checkpoints and the explicit
`full_game_counterfactual_tested: false` flag. Reproduction:

```powershell
.venv/Scripts/python.exe analysis/diagnose_shop0909_opening.py
```

The script expects the two raw downloaded replay JSON files in this directory;
decompress the tracked gzip copies first if restoring on another machine.
The original scheduled W13 crop-controller implementation remains unperformed;
this checkpoint diagnoses the subsequently approved and submitted Shop0909.
