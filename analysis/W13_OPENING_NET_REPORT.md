# W13 opening-cash repair — 2026-09-10

## Mechanism

The diagnostic loss at seed 317002, seat 0, is not just a late harvesting gap.
Between steps 4 and 11, the prior combined candidate sells one wheat and buys
one wheat back each turn. Against the Suliman fixed-route reconstruction's
larger intervening trades, those eight round trips lose **21 actual coins**.
The loss is measured from successful `_commit_unit` transactions, not quotes
or requested quantities. The unmatched sale at step 2 and purchase at step 3
remain unchanged and net zero coins in both runs.

That leaves 3 coins at day 1 instead of 24. Only two of four requested hands
are hired. A cow at (4,3) goes unfed for two consecutive nights and escapes.
By day 9 the old run has 16 strawberry plants versus 20 in the repaired run;
at day 12 it has 28 versus 33. Cancelling only the matched opening trades
restores four hires and prevents the early cow escape. Worker actions for
steps 0–23 are identical in the two profiled runs.

The diagnostic outcome changes from **106,526–127,428** (−20,902) to
**149,596–138,897** (+10,699). This is a development seed, not confirmation.
Its later shops also change, so the entire 31,601 margin swing must not be
attributed directly to milk or strawberry production. The official engine
draws shops from the same daily RNG stream after drawing weeds; different farm
occupancy changes the RNG position. Matching seeds does not freeze shops.

## Candidate scope

`variants/w13_opening_net/main.py` wraps the frozen combined crop/demand model.
It nets matching positive integer SELL/BUY_PRODUCT WHEAT requests only during
steps 2–23. Initial allocation, other products, unmatched net purchases/sales,
and all later trading remain in place. It does not directly edit worker actions.
This preserves **requested net quantities**, not a promise that realized cash
or fills remain identical when the opponent intervenes or an order cannot fill.

- Source SHA-256: `92fc560beab623fe4ad682f8ed2d3088160ee83591120dfb7e818402e6c75beb`.
- Candidate SHA-256: `a6a512cdac1a54ff4941ab410dd3b28a14ec0e88c598be541719dc86aeb0ad9a`.
- Source/production incumbents are not modified.
- Independent rebuild is byte-identical; final definition accepts observation.
- Four new controller tests, three reporting tests, and nine inherited tests pass.

## Evaluation

**Confirmed matchup improvement; not a top-10-ready promotion.** All 220 evaluation
games and three diagnostic profile games finished without execution failures.
Each table block uses ten new seeds and both seats; entries are wins–losses–ties.

| Opponent | Seeds | Previous combined | Opening net |
|---|---|---:|---:|
| Suliman reconstruction | 318100–318109 | 2–18–0 | **18–2–0** |
| Suliman, independent confirmation | 319000–319009 | 4–16–0 | **18–2–0** |
| Kaito | 318200–318209 | 18–2–0 | 18–2–0 |
| Original pf_all, not pf_all2 | 319100–319109 | 18–2–0 | 18–2–0 |
| 3정훈 reconstruction | 319200–319209 | 10–10–0 | 10–10–0 |

Against Suliman the two blocks total **36–4 versus 6–34**, with thirty losses
turned into wins and no wins turned into losses. Average margin delta is
+23,233 in the first block and +21,252 in confirmation. All forty Suliman
shop sequences change, which is an explicit confound for margin attribution,
not something hidden by the seed matching. Kaito, pf_all and 3정훈 have exactly
the same rewards and shop sequences as the previous combined candidate.

Directly against the previous combined model on seeds 318000–318009, the result
is **1–1–18**, exactly zero mean margin; the two non-ties swap rewards with
seat order. It is not a mirror improvement. Its value is resisting the opening
trade interaction that previously damaged the Suliman matchup. This does not
meet the historical >90%-against-every-model promotion bar.

The explicit manifest and integrity checks are in `summarize_w13_opening_net.py`.
`w13_opening_net_raw.json.gz` preserves all 220 rows, source/runner hashes,
actual fills, action hashes and telemetry. `w13_opening_net_results.json` contains
matched outcome comparisons. `w13_opening_net_profiles.json.gz` preserves all
three diagnostic state/action traces with policy hashes. Re-running the
summarizer rejects incomplete local runs and conflicting archived evidence.

## Remaining work

The repaired model still loses Suliman seeds 318105 and 319000 in both seats,
and Kaito seed 318205. Those towns have important wool demand. For example,
against Kaito at 318205 it sells 195 wool for 46,500 versus 270 for 64,218.
That is a measured gap, not proof that a generic cow-to-sheep swap is safe.

The 3정훈 panel remains only 10–10, including losses of 732 and 324 coins on
seeds 319202 and 319204. At 319204 the opponent sells 123 carrots for 7,133
versus our 9 for 537. The full production trace reproduces the 324-coin loss.
At observation 718 our farm still has six wheat units growing and carried
fertilizer; these are pre-final-action quantities, not proven recoverable profit.
The next scoped investigation is state-compatible short crop cycles with actual
feed, harvest, return and sale accounting. Gross wheat sale totals must not be
treated as profit; they include repurchased wheat.

The existing five-hour continuation is updated to this next focused research
round, with the same no-submission and private-repository constraints.

## Limitations

Suliman and the second top-player opponent are guarded **fixed replay routes**,
not their live policies. Paired-seat outcomes can duplicate one another; twenty
games are ten independent seed worlds, not twenty independent samples. A local
matchup improvement is not proof of top-10 ladder strength. The inherited crop
wrapper's replacement feed remains tracked at order issuance rather than
observed settlement, as documented in Experiment #97.

## Reproduce

Use `.venv/Scripts/python.exe` and pinned kaggle-environments 1.32.7.
Builders and match runners refuse existing output files; choose new paths.

```powershell
.venv/Scripts/python.exe analysis/test_w13_opening_net.py
.venv/Scripts/python.exe analysis/test_w13_opening_summary.py
.venv/Scripts/python.exe analysis/build_w13_opening_net.py --output analysis/reproduction_opening/main.py
.venv/Scripts/python.exe analysis/run_w13_isolated.py variants/w13_opening_net/main.py variants/current_top_routes/06_suliman_tadros/main.py --seed 319000 --pairs 10 --output analysis/reproduction_opening_suliman.json
.venv/Scripts/python.exe analysis/profile_w13_herd_units.py variants/w13_opening_net/main.py variants/current_top_routes/06_suliman_tadros/main.py --seed 317002 --order 0 --output analysis/reproduction_opening_profile.json
.venv/Scripts/python.exe analysis/summarize_w13_opening_net.py
```

No Kaggle submission is authorized or made by this experiment.
