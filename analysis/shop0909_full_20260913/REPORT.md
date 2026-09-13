# Full submitted-model replay audit — September 13, 2026

Submission **56182426**, frozen Shop0909 opening guard. Snapshot:
2026-09-13 03:27 UTC. Public score checked this round: **1910.1**.
This is not pf_all, pf_all2, or the unsubmitted waiting-stock candidate.

## Coverage and verification

- Downloaded **all 170 available submission episodes**, with no excluded/incomplete records, plus five recent games from current rank one.
- External record: **54 wins, 68 losses, 47 ties**. One self-play tie is excluded from that record.
- Win rate across all external games: **32.0%**. Decisive win rate: **44.3%**. These are different denominators.
- All 175 replays exported through the pinned engine: **251,650 verified cash transitions, zero mismatches**. Seven exporter tests pass.
- Original JSON.gz replays and audited CSV tables are archived with SHA256/CRC verification. Expanded working copies are not needed to reproduce the analysis.
- Complete coverage means all episodes returned by the API at this snapshot, not future ladder games.

## What is failing

| Descriptive loss group | Games | Evidence |
|---|---:|---|
| Different production mix | 40 | Opponents produce different quantities, particularly tomatoes and wool. This residual category is not a causal diagnosis by itself. |
| Near-clone sale price/timing | 27 | At least 97% exact worker agreement and equal quantities for six core products. Other products and order timing can differ. |
| Opening seed shortfall | 1 | Fewer than seven initial wheat seeds; no day-one staffing collapse. |

Losses split evenly by seat: 34 each. **No loss has fewer than three hands at turn25**. The previous catastrophic opening failure is absent in this cohort; this is observational evidence, not proof that the guard caused the change.

Thirteen losses are by at most10 coins,15 by at most100,22 by at most1000.
All68 losses finish with zero carried/shed stock and zero crop yield remaining on tiles. Two animal tiles retain yield, so this does not mean every possible harvest was recovered.

The worst loss is [Skyspace, episode108145550](https://www.kaggle.com/competitions/kaggriculture/episodes/108145550): **-37,042 coins**. Tomato receipts account for **-40,752**, offset partly by other income/cost differences. Skyspace sells80 tomatoes; our agent sells0.

Other large deficits include wool against Mark #3/OceanMix and tomatoes against JAZ COLD HORN. Full individual loss rows, prices, sold quantities and economy checkpoints are in `loss_review.csv`; all wins and ties remain in `match_summary.csv` and the replay archive.

The first-two-shop samples are small:58 distinct ordered pairs across169 external games. For example Yarn/IceCream loses4/4, whereas Smoothie/Yarn has1 win and3 ties. Neither is enough to claim a stable population loss rate. Late shops matter too, but our incumbent commits its main route after only two.

## Current rank-one comparison

Leaderboard snapshot: **Majkel1337**, score**3227.9**, public submission**56156662**. Five most recent completed games were selected by recency, not reward. They include3 wins and2 losses.

| Episode | Margin | Tomatoes sold | Melons sold | Milk sold | Wool sold |
|---|---:|---:|---:|---:|---:|
|108381189|-2457|113|72|160|88|
|108385318|-4590|20|67|298|64|
|108390115|9833|20|72|299|95|
|108395112|10567|46|66|245|63|
|108399446|8290|56|72|287|60|

The farm mix varies substantially: maximum cows7–12 and sheep3–5 across these recordings. This is stronger evidence for differing production decisions than a universal fixed route. It does not reveal the private policy implementation.

Five coherent replay-route probes were built with baseline weed/final-sale guards and screened on two new seeds, both seats. **All five went0–4:20 losses total, zero failures.** These are fixed-route probes, not matches against the live rank-one model. Do not promote them.

## Important seed correction

`configuration.seed` is null, but these replays include **`info.seed`**. Replaying both recorded streams for108381189 with that seed reproduced both rewards and all checked farm, market, town and private state at all720 records: **zero differences**.

For ten selected own losses, the frozen submitted agent against each recorded opponent also reproduced both original final rewards exactly. This permits meaningful actual-seed counterfactual tests. An opponent action recording still cannot adapt when our candidate changes its observations.

## New candidate: state-compatible tomato continuation

At turn432 in108145550, both farms have identical non-cash farm state, private inventory and seeds. Workers first differ after Skyspace buys land and10 tomato seeds at433.

`analysis/build_shop0909_tomato_suffix.py` builds `variants/shop0909_tomato432` from the frozen submitted ZIP. It switches at432 only if:

- default plan0 is active and no worker repair queue is pending;
- full non-cash farm state and all private state match the reference;
- at least two Farmer/Pizza shops are unlocked and cash is at least10000.

The complete continuation is kept together through the final day, including harvest/return/sales. It does not splice movements across incompatible farm compositions. Otherwise it retains the submitted agent. Eight compatibility/activation tests pass.

Ten actual loss scenarios,30 games across baseline/tomato/h3: baseline0–10; tomato2–8; h3 sale-timing2–8. The tomato candidate changes Skyspace from-37042 to-460, JAZ COLD HORN from-17597 to+2120, and ansheng jhang from-4209 to+700. These selected losses are diagnostic, not a held-out promotion panel.

The180-game fresh paired-seat panel completed with zero failures. Direct:
5W/1L/14T, mean margin+1908.6. Distinct opponents:78–2 for both arms, no
win/loss flips. Margins improve against Kaito, pf_all and Suliman but fall
against historical top2. This does not establish a broad win-rate gain.
Full results and frozen package: `analysis/tomato_panel_20260913/REPORT.md`.

An observation-only activation audit finds69/169 eligible external games
(25 wins,16 ties,28 losses), with zero pre-432 action mismatches. Eligibility
does not prove that the counterfactual game would improve. Additional fresh
Skyspace-recording tests on10 seeds, both seats: candidate9–11 versus baseline
8–12, one gained win and no lost wins, average margin change+2243.7. All40
games completed without failures. This is a modest targeted gain, not a
top-ten model claim. **No Kaggle upload.**

## Reproduction

```powershell
python analysis/collect_replay_csv_corpus.py --submission 56182426 --output analysis/shop0909_full_20260913 --all-own --top-count 1 --top-replays 5
.venv/Scripts/python.exe analysis/replays_to_csv.py --manifest analysis/shop0909_full_20260913/manifest.json --output NEW_CSV_DIRECTORY --audit-fills --workers 4
python analysis/build_shop0909_tomato_suffix.py
.venv/Scripts/python.exe -m unittest discover -s analysis -p test_shop0909_tomato_suffix.py
.venv/Scripts/python.exe analysis/run_tomato_loss_diagnostics.py --output NEW_DIAGNOSTIC_DIRECTORY
```

Builders refuse existing output directories. Restore the replay archive at this directory and the frozen baseline ZIP at its tracked path before rebuilding. The collector resumes its cached snapshot; use a new output directory for a fresh snapshot.
