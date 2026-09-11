# Shop Router 0909: unchanged baseline evaluation

Completed September 11, 2026. **180 full local games, zero failures, zero ties. No Kaggle submission.**

## Decision

Keep the unchanged Shop0909 as a separate, promising research baseline. It beats our submitted W13 opening-net **20–0** and gains four wins without losing an incumbent win on the matched panel. It is **not a demonstrated top-ten agent or a universally dominant replacement**: one fixed-route opponent still beats it in six of twenty games. No incumbent was edited.

This round follows Experiment #99's live-loss diagnosis rather than adding another narrow wrapper to W13. The older scheduled carrot investigation is not being represented as completed: this is a new production-baseline evaluation, not a new crop-controller implementation.

## Frozen protocol and source

- Ten unused seed values **39117000–39117009**, each in both seat orders. The same block was used for each candidate/control comparison. Twenty games represent ten seed groups, not twenty independent worlds.
- Separate processes per agent via `analysis/run_w13_isolated.py`; official engine **1.32.7**. Final statuses, actual successful per-unit market fills, worker hashes and shop sequences are stored. These runs are local evaluation, not a Kaggle runtime certification.
- Shop0909 downloaded September 10 and preserved in the prior notebook archive. Builder extracts literal data and the inspected main source without executing notebook cells. All three files match the notebook's published hashes.
- Published main.py SHA-256: `d6d74997dc5b483db63d8e39cafa1afeec0f366824e75107e109123f111e866b`.
- actions.json SHA-256: `17d503f2fd20d59f9c0f14024d1e74a8add8bb9b5561d4d908b45deecb5495ef`.
- W13 is the submitted **56139834** artifact, SHA-256 `a6a512cdac1a54ff4941ab410dd3b28a14ec0e88c598be541719dc86aeb0ad9a`.
- `protocol.json` pins every opponent file and the action data. Original `submit_pf_all/main.py` was used, never pf_all2.

## Complete results

| Opponent | Shop0909 W–L | W13 W–L | Gained wins | Lost wins |
| --- | ---: | ---: | ---: | ---: |
| W13 opening-net, direct | 20–0 | — | — | — |
| Frozen Kaito | 20–0 | 18–2 | 2 | 0 |
| Original pf_all | 20–0 | 20–0 | 0 | 0 |
| Suliman fixed reconstruction | 18–2 | 18–2 | 0 | 0 |
| 3정훈 fixed reconstruction | 14–6 | 12–8 | 2 | 0 |
| Shared-opponent panel total | **72–8** | **68–12** | **4** | **0** |

All denominators include every completed game. Gained wins are paired outcome flips, not extra independent discoveries. The panel has two older reacting agents and two fixed reconstruction controls; it must not be described as four independent modern top-player policies.

Against W13 directly, mean margin is **+13,202.4**, minimum margin **+3,340**. Against original pf_all it is +24,975.9, with minimum +12,623. Mean margin improvements over W13 against Kaito / pf_all / Suliman / 3정훈 are +5,465.35 / +9,905.65 / +10,396.10 / +3,494.60 respectively. A higher mean does not erase losses: the worst 3정훈 loss is -15,088, compared with W13's worst -14,711.

Candidate/control shop sequences differ in **16/20 Kaito**, **0/20 pf_all**, **2/20 Suliman**, and **0/20 3정훈** comparisons. Policy changes can alter weed RNG consumption and later shops; equal seeds are not a guarantee of identical towns.

## Does this address the production gap?

Direct-comparison average executed sales:

| Product | Shop0909 units | W13 units |
| --- | ---: | ---: |
| Carrot | 83.1 | 9.0 |
| Egg | 54.6 | 0.0 |
| Milk | 228.8 | 242.1 |
| Wool | 195.0 | 195.0 |
| Strawberry | 247.9 | 258.65 |

The broader farm wins while sacrificing some milk and strawberry volume. In these ten direct seed worlds it ends with either 8 cows/6 sheep/3 geese or 6 cows/11 sheep, rather than W13's rigid 9-cow/8-sheep pattern. This supports the production-composition hypothesis from #99, but it is a comparison of whole policies, not an isolated causal estimate of eggs or carrots.

## Remaining failures: retain these cases

1. **Suliman, seed 39117007, both seats:** -4,299 and -3,626. Shops begin FARMERS_MARKET, BRUNCH_SPOT, then YARN_STORE. Shop0909 uses its non-Yarn plan selected after two shops and sells 161 wool; the opponent sells 242. Later wool demand is a specific investigation target, not proof that switching to another tape at step 216 is safe.
2. **3정훈, seeds 39117001 / 39117004 / 39117009, both seats:** -5,860 / -6,130 / -15,088. Our ordinary plan sells 84 carrots, 78 eggs, 245 milk, 161 wool and 249 strawberries; that opponent sells 123 carrots, 29 eggs, 261 milk, 76 wool and 315 strawberries. At 39117009 its strawberry revenue exceeds ours by **11,146**, and milk revenue by **4,126**. More eggs/wool are not always the right allocation.

Observed route IDs in the candidate panel are **0, 1, 3, 7, 8, 9**, plus the common step-648 ending. This does not exercise all thirteen plans or every shop pair. Additional seed blocks and distinct reacting public opponents are required before a broad-strength claim.

The next focused development should distinguish late-Yarn wool demand from milk/strawberry-heavy towns. Any new continuation must confirm positions, seeds, carried goods, cash, animal deliveries and policy state at its branch point. Matching movement alone is insufficient. Do not transplant a W13 continuation into this unrelated opening.

## Artifacts and reproduction

Five tests pass: published hashes, plan lengths, deterministic resets without observation mutation, shop selection/player isolation, and common ending selection. The final validator checks all 180 seed/seat records, completed statuses and frozen source identities.

- `analysis/shop0909_panel/protocol.json`: pre-run protocol and all file hashes.
- `raw_results.json.gz`: complete nine-run evidence.
- `summary.json`: paired outcome flips and changed shops.
- `validated_details.json`: records, failure seeds, production averages and route coverage.
- `agent.zip`: unchanged main.py + actions.json + LICENSE.txt at archive root. CRC and member hashes verified. SHA-256 **`9fa78bee25ec86381f59c10025b1713bb5f37294320ca009eb3ab91a99851dde`**. It is a saved research artifact, **not submitted**.

```powershell
# Builder refuses to overwrite an existing baseline directory.
python analysis/build_shop0909_baseline.py
.venv/Scripts/python.exe -m unittest discover -s analysis -p test_shop0909_baseline.py -v
.venv/Scripts/python.exe analysis/run_shop0909_panel.py --output analysis/shop0909_reproduction
.venv/Scripts/python.exe analysis/summarize_shop0909_panel.py --directory analysis/shop0909_reproduction
```

Public source reference: https://www.kaggle.com/code/yhay81/shop-router-0909 (September 10 snapshot). Its author appeared in our top-ten snapshot; we have not established that the published file is identical to their ranked submission. No Kaggle submission is authorized by this report.
