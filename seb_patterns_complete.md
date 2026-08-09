> **⚠️ READ THIS BEFORE USING ANYTHING BELOW — these are NOT techniques.**
>
> Seb is a **replayed fixed script**. His first 30 turns are byte-identical across all
> five games — same buys, same tiles, same units, same hours, down to
> `h5(0,3):PLANT-WHEAT at t16`, with money at t1 = $1,807 in every game. The patterns
> documented here are the *output of one script meeting five different seeds*, not
> decisions.
>
> **This invalidates the "adaptation" reading, including the day-10 cow branch below.**
> The cow counts (13/11/9/7/7 against milk demand 4/3/1/1/0) are not a conditional — they
> are the same scripted `BUY_ANIMAL` orders either clearing or failing on insufficient
> funds. High milk price → more revenue → the orders clear. Low price → they fail.
> **Demand did not cause him to buy cows; it caused him to afford the cows the script
> always attempts.** His 59k→137k spread on an identical script is therefore mostly the
> draw, not skill.
>
> **Four experiments derived from this document have already been run and CLOSED —
> do not re-run them** (see `EXPERIMENTS.md` #12, #13, #14, #16):
> herd sizing, shop-adaptive herd sizing, land-schedule copying (d4/d6/d10 + Q4), and
> milk-inventory discipline. All neutral or negative. They presuppose a feed cost we do
> not have.
>
> **What is still legitimately usable here:** the *mechanical* comparisons — feed
> delivery cost, moves per trip, wasted actions, action mix. Those are execution
> properties that hold whether or not the policy was scripted.
>
> Also note the ladder data (2026-08-09, 8 real matches) contradicts the milk emphasis
> below entirely: against the real field our milk revenue is *even* ($21.2k v $21.5k).
> Our actual deficit is **melon, −$17,285**.

# Seb Replay Patterns — Complete Breakdown (5 games, 59k–137k)

Derived from all 106 columns of 5 per-step replays. The headline finding drives everything:

**Seb runs a near-fixed script. Every decision column is 97–100% identical across all 5 games. His score spread (59k → 137k) is driven almost entirely by the shop draw (milk demand), NOT by in-game adaptation.** When the draw gives high milk demand, the same fixed herd sells milk above I0 at ~$245 and scores 137k; when it gives 0 milk shops, the identical actions sell into a glut at ~$139 and score 59k.

The one genuinely conditional decision is the **day-10+ cow extension** (detailed below). Everything else is a hardcoded schedule.

---

## 1. COW BUYS — fixed opening, then ONE conditional branch

| day | 128k | 137k | 59k | 60k | 93k |
|----|----|----|----|----|----|
| 0 | 2 | 2 | 2 | 2 | 2 |
| 1 | 1 | 1 | 1 | 1 | 1 |
| 3 | 1 | 1 | 1 | 1 | 1 |
| 4 | 1 | 1 | 1 | 1 | 1 |
| 9 | 2 | 2 | 2 | 2 | 2 |
| 10 | 2 | 2 | **0** | **0** | 2 |
| 11 | 2 | 2 | **0** | **0** | 0 |
| 13 | 2 | 0 | 0 | 0 | 0 |

**Fixed part (identical in all 5):** 2 cows day 0 → 1 each on days 1, 3, 4 → 2 on day 9. Every game reaches **7 cows by day 9** no matter what.

**Conditional part (day 10+):** this is the ONLY real decision in his whole program.
- Final cow counts: 59k→7, 60k→7, 93k→9, 128k→13, 137k→11.
- The 0-milkshop and 1-milkshop-low-demand games (59k, 60k) **stop at 7** — they buy nothing on day 10+.
- The high-demand games (128k, 137k) push to **11–13**.
- 93k (1 milkshop but demand held) goes to **9**.

**The trigger** (best single-variable read): continue buying cows past 7 only while `mktinv_MILK < I0` (10,000) at the day-10 decision. In 59k/60k milk inventory was already ABOVE I0 (10,010 / 10,009) and price had cratered to ~139 → he stopped. In 128k/137k inventory stayed BELOW I0 (9,953→9,905), price held 220–245 → he kept going.

⚠️ n=5, markets confounded — treat this trigger as a strong hypothesis, not proven. But it is the only place his behaviour varies, and it keys on `mktinv_MILK`, the correct control variable.

---

## 2. SHEEP BUYS — essentially fixed, NOT wool-reactive

| day | 128k | 137k | 59k | 60k | 93k |
|----|----|----|----|----|----|
| 0 | 2 | 2 | 2 | 2 | 2 |
| 9 | 1 | 2 | 2 | 0 | 2 |
| 10 | 2 | 1 | 2 | 0 | 1 |
| 11 | 2 | 2 | 0 | 2 | 2 |
| 12 | 0 | 2 | 1 | 2 | 2 |
| 13+ | 1 | 1 | 3 | 6 | 0 |

Final sheep: 59k→11, 60k→12, 93k→9, 128k→8, 137k→10.

**Sheep do NOT follow wool inventory.** Wool inventory is ABOVE I0 (10,012–10,047) and wool price FALLING (206→72) at nearly every sheep buy, yet he keeps buying. There is no "stop when wool gluts" rule. Sheep are roughly a fixed ~8–12 buildout, with the low-milk games ending up with slightly MORE sheep (11–12) than the high-milk games (8) — likely just because those games had spare animal budget the cow branch didn't consume. **No clean conditional rule here.** Treat sheep as a fixed target of ~10.

---

## 3. LAND — 100% FIXED

| day | all 5 games |
|----|----|
| 4 | +1 quadrant |
| 6 | +1 quadrant |
| 10 | +1 quadrant |

Bought on days **4, 6, 10** in every single game. Zero variation. Never a 4th purchase. Transcribe directly.

(Note: this differs from your v10's schedule of Q2 day 7 / Q3 day 11 — Seb lands EARLIER and buys THREE, not two. Worth reconciling: your v10 landed on days 7/11, Seb lands 4/6/10. His earlier land = earlier planting = more crop-days.)

---

## 4. HIRES — 100% FIXED ramp

Identical in all 5 games:
- Days 0–5: **7 hands**
- Day 6: 7–8
- Day 7: **8**
- Day 8: **9**
- Day 9: **11**
- Day 10 onward: **12**, flat for the rest of the game (through day 28).

He does NOT hire past 12. Steady state is 12 hands from day 10. No endgame hiring surge, no drop. Dead simple: 7 early, ramp to 12 by day 10, hold 12.

---

## 5. WHEAT SEED — fixed opening, reactive endgame fill

| phase | pattern |
|----|----|
| day 0 | **exactly 14** every game |
| days 5–11 | small, ~1–4/day, roughly fixed |
| days 16–27 | **VARIES** — low-milk games plant far more |

Day 0 = 14 wheat, always. The endgame (day 16+) is where it diverges: 59k/60k/93k plant heavy wheat on days 21–27 (filling days: 21,22,23,24,25,26,27), while 128k/137k plant almost none late. **This is compensation, not strategy** — when milk didn't pay, he backfilled empty tiles with cheap endgame wheat to salvage the land. Wheat is his fallback crop.

---

## 6. STRAWBERRY SEED — FIXED schedule

| day | approx qty (all games similar) |
|----|----|
| 5 | ~10–11 |
| 7 | ~9–10 |
| 8 | ~0–3 |
| 9 | ~6–10 |
| 10 | ~0–4 |
| 11 | ~7–10 |
| 12 | ~0–3 |

Nearly identical across all 5 games regardless of score. Big waves on days 5, 7, 9, 11. This is his premium crop and it is **not** demand-reactive — same planting in the 59k game as the 137k game. Fixed.

---

## 7. MELON SEED — FIXED schedule

| day | qty |
|----|----|
| 0 | **3** every game |
| 5 | ~4–7 |
| 7 | ~1–3 |
| 8–11 | trickle ~1–4/day |
| 17+ | occasional 1–2 |

3 on day 0 always, main wave day 5, trickle through day 11. Fixed across all games.

---

## 8. FEED WHEAT (buyprod_WHEAT) — scales with herd, this is the cost sink

| phase | pattern |
|----|----|
| days 0–4 | fixed: 8, 6, 5, 7, 1 |
| days 5–9 | ~3–9/day, roughly fixed |
| days 10–28 | **15–25/day**, tracks herd size |

Feed buys ramp with the herd and sit at ~18–21/day steady state in the high-herd games. Note the high-cow games (128k/137k) buy MORE feed wheat (20–25/day) than the capped games (59k/60k at 11–18/day) — consistent, feed scales with animals. **This is exactly the cost center your v14 pickup-cap targets.**

---

## 9. SELLING — TRICKLE, no hold window (confirms your v9 deletion)

Milk selling **starts day 8 in every game** (first yields land day 8 by biology) and trickles continuously to day 29 — 6–40 units/day, never a big held dump. He does NOT hoard and release. Late revenue comes from PRODUCTION timing (strawberry yields land d17–27, herd matures), not inventory hoarding. **This validates v10's "no hold window" design.**

---

## 10. NEVER DOES

- `buyanimal_GOOSE` = 0, `herd_GOOSE` = 0, `act_BUILD_COOP` = 0 — **never touches geese**, all games.
- `buyseed_CARROT` = 0, `buyseed_TOMATO` = 0, `tiles_CARROT`/`tiles_TOMATO` = 0 — **never plants carrot or tomato.**
- Never hires past 12. Never buys a 4th land quadrant.

---

## SUMMARY — what's fixed vs what's a decision

**FIXED SCHEDULE (transcribe directly, no logic):**
- Land: days 4, 6, 10 (three quadrants)
- Hires: 7 → ramp → 12 by day 10, hold
- Cows: opening to 7 by day 9
- Sheep: ~10 buildout days 0–13
- Strawberry: waves days 5/7/9/11
- Melon: 3 on d0, wave d5, trickle to d11
- Wheat: 14 on d0
- No goose, no carrot, no tomato
- Sell: trickle from day 8, no hold

**THE ONLY REAL DECISION:**
- Day 10+: extend cows from 7 toward 11–13 **only while `mktinv_MILK < I0`** (equivalently price_MILK > ~200 / milk demand ≥ 3). If milk has already glutted past I0, stop at 7 and let the wheat-fill fallback take the empty tiles.

**WHAT THIS MEANS FOR YOU:**
1. Seb has NO sophisticated adaptation. His 137k vs 59k is a good vs bad shop draw on a fixed script. Don't chase a hidden rule — there isn't one.
2. Your v10 already transcribes most of this. Two concrete diffs to test: he lands EARLIER (4/6/10 vs your 7/11) and buys THREE quadrants; his hire cap is 12 (matches your FULL_HANDS_CAP=14 loosely — his is tighter).
3. The one rule worth adding: the `mktinv_MILK < I0` cow-extension gate. A/B it.
4. Your real edge isn't copying Seb — it's ADAPTING where he can't. His fixed herd bleeds money in glutted-milk games. An agent that redirects budget to wool/crops when milk gluts beats his fixed script on the bad draws while matching it on good ones.
5. Score variance is draw-driven, so ALWAYS average over many seeds (your 40-game sweeps), never trust one game.
