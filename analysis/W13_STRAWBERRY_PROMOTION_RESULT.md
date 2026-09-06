# W13 strawberry-only promotion result

Candidate: `variants/w13_add_strawberry/main.py`

Engine: `kaggle-environments==1.32.7`. Every opponent used ten fresh seeds in
both seat orders. Agents ran in isolated processes and failures were counted.

| Opponent | Candidate result | Mean margin |
|---|---:|---:|
| frozen W13 | 19-1 | +2,103.6 |
| frozen Kaito | 20-0 | +12,689.2 |
| pf_all | 20-0 | +11,741.7 |
| Soil | 20-0 | +18,015.4 |
| Salem | 20-0 | +18,580.6 |
| Fleong | 20-0 | +37,731.2 |
| latest clone/Soil router | 16-4 | +3,074.0 |
| reconstructed Gronk | 17-3 | +15,216.0 |

All 160 candidate games completed without failure or tie.

Matched controls on the two sub-90% opponents:

| Opponent | Baseline W13 | Strawberry-only | Outcome flips | Margin change |
|---|---:|---:|---:|---:|
| latest clone/Soil router | 16-4 | 16-4 | 0/20 | -473.8 |
| reconstructed Gronk | 17-3 | 17-3 | 0/20 | -543.0 |

Worker-action hashes matched baseline in all forty controlled games. The added
strawberry sales therefore create no broad wins in the tested failure families
and reduce margins. Their demonstrated benefit remains W13 mirror share capture.

Decision: reject promotion and do not submit to Kaggle. The candidate fails the
historical greater-than-90-percent requirement against every previous model.
Future work should target W13's underlying latest-router and Gronk losses rather
than adding more unconditional strawberry sale requests.
