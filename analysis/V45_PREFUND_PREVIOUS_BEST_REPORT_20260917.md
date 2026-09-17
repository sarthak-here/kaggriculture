# Corrected V45 prefund versus previous-best models

## Result

The corrected export is genuinely stronger than every frozen previous-best model
in this panel: **160 wins, zero losses, zero ties** across ten fresh seeds and both
seats for each of eight opponents. It had no execution failures or nonzero error
telemetry. It has not been submitted.

| Opponent | W-L-T | Mean margin | Worst margin |
|---|---:|---:|---:|
| V45 proactive (last functioning submission) | 20-0-0 | +143.6 | +55 |
| Original V45 | 20-0-0 | +150.3 | +32 |
| pf_all | 20-0-0 | +33,331.1 | +24,195 |
| Kaito clone+Soil router | 20-0-0 | +25,274.1 | +8,711 |
| Reconstructed W13 | 20-0-0 | +20,367.3 | +9,887 |
| Astra W13 | 20-0-0 | +20,832.8 | +10,162 |
| W13 opening-net | 20-0-0 | +17,371.6 | +9,778 |
| Shop0909 tomato432 | 20-0-0 | +6,529.0 | +3,346 |

The direct V45 result isolates the prefunding change: it creates a small but
consistent economic edge. The large margins against older distinct families mostly
show the strength of the V45 base, not a 20k-coin gain caused by prefunding alone.

## Execution accounting

The initial four-worker run made 160 attempts. Six Kaito seat-zero processes timed
out on their first action under parallel startup load; the candidate was seat one
in all six and did not fail. Those attempts are preserved in `results.json` and the
initial `summary.json`. Every exact failed seed/seat was rerun serially and completed;
all six were candidate wins. The resolved table therefore represents 160 valid
games, not 154 wins plus six silently discarded failures.

The repaired harness uses Kaggle's namespace-insertion-order callable rule. It no
longer selects the last AST function definition. Candidate SHA-256:
`1a9c3a3ef6902d958d6269421a196aa683492e927f660f566c3029698498bf04`.

## What this proves—and does not prove

This clears the user's prior-model bar: every tested previous best lost 100% of
valid games. It is much stronger evidence than the earlier parent-only 20-0.
However, this panel contains frozen local agents. It does not prove the candidate
will reach the current top ten, and the V45-parent wins are only tens or hundreds
of coins. A current-leader replay panel and live ladder behavior remain separate
questions. No Kaggle upload was made from this experiment.

Reproduce with pinned `kaggle-environments==1.32.7`:

```text
.venv/Scripts/python.exe analysis/tournament_v45_prefund_exported.py
.venv/Scripts/python.exe analysis/retry_v45_prefund_previous_best.py
```

Protocol, hashes, compressed full results, original failures, serial retries and
the resolved summary are under
`analysis/v45_prefund_exported_previous_best_20260917/`.
