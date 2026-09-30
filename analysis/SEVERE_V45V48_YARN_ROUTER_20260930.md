# Severe V45/V48 YARN router — 2026-09-30

## Decision

Preserve as a separate local candidate. It is a narrow matchup improvement,
not a replacement for Severe against every family, and has not been submitted.

Exact artifact:

- `variants/severe_v45v48_yarn_114605783_20260930/main.py`
- SHA-256 `a690ab09f2909d254621d88085d64b3bbe2d949d384e978f3b4e6e51e94c10be`
- 203,780 bytes
- Kaggle-selected callable `current_rule_noop_free_agent`

## Mechanism

Severe's five fresh-round-robin losses against each of V45, V48, and Step1010
all occurred on the same two first-shop-YARN worlds. A broad YARN replacement
was rejected: replay 114268528 changed Severe from 8-12 to 6-14 against Step
and left V45/V48 at 8-12 while worsening all three mean margins.

The relevant opening families are observable after turn zero. V45 and V48 have
no hands or tiles, farmer `[4,4]`, and exactly $2,867. Step and MarketShock have
$2,857; Severe has $2,600; protected portfolio and Shop0909 have $2,643;
Jaxa has $3,000; pf_all and Kaito/Soil have visibly different farms. The router
therefore selects a specialist only for the $2,867 signature and retains
Severe for every other observed family and for unknown openings.

Ten preserved YARN routes were screened on the two exact V48 failure worlds.
Eight went 0-4. Routes 114268528 and 114605783 went 4-0; 114605783 was stronger
on the diagnostic margin (+8,942 versus +1,746) and advanced to holdout.

## Paired-seat evidence

All games completed without failures.

| Test | Severe control | final router | Result |
|---|---:|---:|---|
| repaired V48, same 10 held-out seeds | 8-12 | **12-8** | +4 wins |
| repaired V45, same 10 held-out seeds | 8-12 | **12-8** | +4 wins |
| older V45 exported, 10 fresh seeds | 12-8 | 12-8 | record preserved |
| V48 Mingxi router, 10 fresh seeds | 8-12 | 8-12 | record preserved |
| router versus Severe, 5 fresh seeds | — | 4-4-2, mean 0 | inactive-path identity check |

The router's margins against the two older family members were worse even
though win/loss records were unchanged. This prevents claiming universal
family dominance. Promotion should be based on win/loss only, but the margin
change is retained as a warning about market coupling.

## Execution validation

The exact final file completed 720 steps on Kaggriculture 1.32.7 with zero hard
action errors and zero ignored market orders. Repeated-shop coverage was
present. The final normalization wrapper removes malformed, empty, PASS, and
non-positive market entries and is the last callable in the file.

No Kaggle submission was made for this routed candidate. A fresh explicit
approval is required before any submission.
