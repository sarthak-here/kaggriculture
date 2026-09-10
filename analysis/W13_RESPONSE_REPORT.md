# W13 crop response and demand trading — 2026-09-10

The combined candidate beats repaired W13 20-0 on ten fresh paired-seat seeds,
averaging +1,669 coins. It does **not** establish top-10 strength: across six
matched opponent families, it changes zero wins, losses or ties relative to the
baseline. Preserve the improvement as research; do not promote or submit it.

## Frozen artifacts

- Baseline: `variants/w13_zero_replay/main.py`, SHA-256
  `e77dea99e4bb085ee4984ab1b2d21727eb49841a544ebe18b7e85ce376beab96`.
- Combined: `variants/w13_crop_demand/main.py`, SHA-256
  `92fc560beab623fe4ad682f8ed2d3088160ee83591120dfb7e818402e6c75beb`.
- Separate controls: `variants/w13_crop_response/main.py`,
  `variants/w13_demand_gated/main.py`, `variants/w13_demand_ungated/main.py`.
- Original `submit_pf_all/main.py` and existing W13 artifacts were unchanged.

All four candidates independently rebuilt byte-for-byte. Their final top-level
function remains `_kaggle_submission_entrypoint(obs, configuration=None)`.

## Changes and mechanism

The wheat trader uses the existing reserve-aware market expert, a 40-unit batch
cap, 5,000 cash floor and 30 units of shed headroom. It forecasts the official
flat town-center demand. Its gate blocks entry when recent positive public
inventory changes exceed the current demand tick. This statistic includes both
players' trades; it is not a reconstruction of private opponent inventory.
Open positions retain their exit path even when new entry is blocked.

The crop response extracts 61 late wheat cycles from source episode 105165498,
seat 1, whose observed harvest occurs three calendar days after planting. It
buys carrot seed one step before an eligible planting only when current quotes,
with a 30-unit adverse inventory buffer, justify three expected carrots minus
three replacement wheat units and the full extra seed cost by at least 80 coins.
It checks actual worker position, an empty tile and available seeds at planting;
it reserves seeds for the original carrot actions. It changes the selected
PLANT crop, adds carrot sale requests and requests replacement wheat at harvest.
The original movement schedule is retained by the wrapper; future base-policy
reactions to changed observations can still differ.

## Results

All matches use local engine 1.32.7 and separate agent processes. Each fresh
block has ten distinct seeds, each played in both seats. Wins include all games;
ties and failures are reported explicitly. These are paired worlds, not twenty
independent seeds.

| Direct repaired-W13 comparison | Seed block | W-L-T | Mean margin |
|---|---|---:|---:|
| Demand, gated | 313000–313009 | 20-0-0 | +175 |
| Demand, ungated | 313000–313009 | 18-2-0 | +206 |
| Crop response | 315000–315009 | 6-0-14 | +1,515 |
| Combined | 315000–315009 | 20-0-0 | +1,669 |

The crop response also went 2-0-2 in its two-seed discovery block. Its large
first-world gain was not used alone as promotion evidence. Gated-only and
combined results above use different seed blocks; do not subtract them to
estimate the crop contribution.

| Matched opponent | Seed block | Baseline | Combined | Margin change | Outcome flips |
|---|---|---:|---:|---:|---:|
| Kaito reconstruction | 313100–313109 | 18-2 | 18-2 | +219 | 0 |
| Original pf_all | 313200–313209 | 20-0 | 20-0 | +823 | 0 |
| Gronk reconstruction | 316000–316009 | 20-0 | 20-0 | +3,730 | 0 |
| Soil reconstruction | 316100–316109 | 20-0 | 20-0 | +748 | 0 |
| Suliman route, ep106298625 | 317000–317009 | 4-16 | 4-16 | +1,688 | 0 |
| 3정훈 route, ep106288264 | 317100–317109 | 16-4 | 16-4 | +154 | 0 |

The last two opponents are fixed routes rebuilt inside public guards. Their
source teams appeared in the downloaded top-10 snapshot, but these artifacts
do not reproduce those teams' complete live policies. No live-rank inference
is justified. The 18-2 Kaito result also fails the historical strictly-greater-
than-90% promotion criterion, and not every historical submission was tested.

There are 432 evaluation games in `w13_response_raw.json.gz`, plus four repeated
games for two transaction audits. All completed without execution failures.
The combined panel is 118-22 including the direct W13 games; the six non-W13
families are 98-22 for both baseline and candidate.

## Actual execution and feed audit

Action telemetry counts requests and cannot alone prove successful harvests.
`audit_w13_feed_fills.py` instruments the official unit-action and per-order
market commit functions, without modifying either policy's returned actions.

On seed 315002 in each seat, the combined candidate successfully planted and
harvested all 24 tracked replacement crops, collected 71 carrots, and left zero
tracked crops unharvested. All 770 requested wheat units after step 300 filled,
including the 72 requested replacement units. The margin was +9,754 in both
seats. The audit reproduced rewards, action hashes and aggregate fills exactly.
The crop-only version scored +9,624 there. This audit validates those games;
it is not a universal guarantee of feed-order fulfillment. In particular, the
current controller clears feed debt when it issues an order, not when it observes
settlement. This remains a robustness limitation for any future promotion.

## Remaining weakness

The improvements do not close the lean Suliman-route production gap. On seed
317002, seat 0, the combined model loses by 20,902 coins. It sells 206 strawberries
versus 259, and 164 milk versus 189. Strawberry receipts trail by 11,402 and milk
receipts by 6,713; melon sales are equal at 72 units. Its crop switch is inactive.
On seed 317003 the crop response cuts a 14,572 loss to 7,369, but still loses.
This supports investigating the production schedule against that family rather
than treating a higher margin against W13 as broad dominance. These seeds are
diagnostic data; any future tuned patch requires new confirmation worlds.

## Correction to the earlier top-replay interpretation

`audit_top_market_fills.py` processes both actors and markets from each saved
observation and checks the resulting cash against the next recorded observation.
47 of 50 replays reproduce every transition's cash. Three have terminal-step
discrepancies: episodes 106227107, 106045837 and 106231572. Their unverified totals
must not be pooled with the fully reproduced episodes; the audit deliberately
returns nonzero when discrepancies exist and preserves them for inspection.

The official engine accepts BUY_PRODUCT only for WHEAT and FERTILIZER. SpaTaro's
many requested purchases of other products produce no fills, despite all five
of its audited games reproducing cash exactly. Earlier inference of multi-product
market making from requested purchases was therefore wrong. Low agreement across
recorded actions also suggests variability, not proof of a particular reactive
policy implementation. The verified audit is stored in `w13_response_audits.json.gz`.

## Reproduce

Use the pinned environment and new output paths; match runners reject an
existing output. The builders retain frozen candidate files and source replay.

```powershell
.venv/Scripts/python.exe analysis/build_w13_demand_trader.py --output-root analysis/reproduction
.venv/Scripts/python.exe analysis/build_w13_crop_response.py --source analysis/reproduction/w13_demand_gated/main.py --output analysis/reproduction/combined.py
.venv/Scripts/python.exe analysis/test_w13_demand_trader.py
.venv/Scripts/python.exe analysis/test_w13_crop_response.py
.venv/Scripts/python.exe analysis/run_w13_isolated.py variants/w13_crop_demand/main.py variants/w13_zero_replay/main.py --seed 315000 --pairs 10 --output analysis/demand_trader_runs/reproduction_w13.json
.venv/Scripts/python.exe analysis/audit_w13_feed_fills.py variants/w13_crop_demand/main.py variants/w13_zero_replay/main.py --seed 315002 --output analysis/demand_trader_runs/feed_audit_reproduction.json
.venv/Scripts/python.exe analysis/summarize_w13_responses.py
```

Nine controller tests pass. `w13_response_raw.json.gz` includes per-game hashes,
actual fills, outcomes and telemetry; the summarizer preserves that archive on a
checkout with no local run directory. The crop builder can use the committed
`w13_crop_source_replay.json.gz` when the original download is absent. Full top-50
audit reruns additionally require the original downloaded manifest and replays.

No Kaggle submission was made. Research checkpoint complete; the usage-reset
automation is paused after saving this report.
