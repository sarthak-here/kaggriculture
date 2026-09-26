# Latest public-agent search — 2026-09-26

## Outcome

No newly published agent beat the current Cha22 checkpoint. The search did find
a four-turn forecast controller that is much stronger than historical `pf_all`,
but Cha22 already contains a stronger descendant of that policy family.

No Kaggle submission was made.

## Sources reviewed

- Kaggle's newest competition notebooks (200 rows, sorted by `dateRun`).
- Current competition discussions, including RL, replay measurement, ranking,
  opponent copying, and fertilizer-sale threads.
- `leoprovorov/a-song-of-ice-and-fire-fixed-flexible`.
- `leoprovorov/god-s-mode-hacked-stores`.
- `leoprovorov/four-turn-forecast-notebook-version-2`.
- `georgymamarin/kaggriculture-what-2600-farms-do-differently`.
- `guruprasaathas111/kaggriculture-top-2-master-engine-v4`.
- `evgendvorkin/kaggriculture-version-31-26-09-bronze-going-up`.
- `salemali7/kaggriculture-2900`.
- `haideptry/the-2950-peak-farm`.
- `hakdevelopment/kaggriculture-2887-score-fieldcraft-agent`.

All executable candidates were compiled and recursively safety-reviewed before
local simulation. Multi-file notebook payloads were extracted with
`analysis/extract_literal_bundle.py`, which evaluates literals only, validates
safe relative paths, and verifies every publisher-provided SHA-256.

## Fresh paired-seat screens

All results use Kaggriculture 1.32.7 and play every seed in both seat orders.

| Candidate | Opponent | Fresh seeds | Result | Mean margin | Decision |
|---|---|---:|---:|---:|---|
| Four-Turn Forecast v2 | frozen `pf_all` | 1030000–002 | 6–0 | +38,118 | confirm |
| Four-Turn Forecast v2 | frozen `pf_all` | 1030100–109 | **20–0** | **+30,009** | real upgrade over pf_all |
| Four-Turn Forecast v2 | Cha22 | 1030200–204 | **1–9** | −813 | reject |
| Top-2 Master V4 | Cha22 | 1030300–302 | 0–6 | −1,148 | reject |
| 2950 Peak | Cha22 | 1030310–312 | 2–4 | −676 | reject |
| V31 Bronze | Cha22 | 1030320–322 | 0–0–6 | 0 | exact behavioral clone |
| Salem 2900 | Cha22 | 1030330–332 | 0–6 | −31,845 | reject |
| Fieldcraft 2887 | Cha22 | 1030340–342 | 0–6 | −4,500 | reject |
| God's Mode released overlay | Cha22 | 1030430–432 | 0–6 | −3,077 | reject |

The Four-Turn result against pf_all is production-driven, not just a queue
artifact: over the 20-game confirmation it planted 763 carrots and sold 2,358,
versus pf_all's 154 planted and 338 sold. Against Cha22, however, its production
was nearly the same and it lost nine of ten games.

V31 and Cha22 returned identical rewards and carrot counts in all six matched
games. This shows that at least one new publication is the same live policy in
behavior, despite different packaging.

## Shop-seed research boundary

The hidden-seed paper demonstrates that farm occupancy can alter future shop
draws, but its released controller does not perform directed shop control.
`shop_overlay.py` records predictions with `acted: False`; its action change is
only a bounded delay of already revealed-shop sales. The paper itself reports
that its first forced-PET_CAFE campaign reversed four positive margins into
losses. This mechanism is research, not a validated score improvement.

## Clone-horizon probe

Cha22 already contains a >=95%-similarity clone detector, adaptive premium-sale
reservation, and lockstep SELL ordering. Three exact variants changed only
`_RACE_HORIZON_MIRROR` from 24 to 32, 48, or 72.

| Variant | Seeds | Result vs Cha22 | Effect |
|---|---:|---:|---|
| H32 | 1030400–402 | 0–0–6 | exact no-op |
| H48 | 1030410 | 0–0–2 | exact no-op |
| H72 | 1030420 | 0–0–2 | exact no-op |

The reservation layer has no additional eligible sales beyond the current
window in these games. Larger constants are not a breakthrough and should not
be submitted.

## Conclusion

Cha22 remains the strongest local checkpoint, but its live score shows that the
shared public lineage does not transfer reliably to the current ladder. The
latest public code does not contain a tested top-10 breakthrough. The useful
next research target is a genuinely different observation-conditioned
production policy, evaluated against live-loss families—not another route tape,
score-labelled repackaging, queue reorder, or wider clone horizon.
