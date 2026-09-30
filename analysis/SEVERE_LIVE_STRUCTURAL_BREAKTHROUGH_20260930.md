# Severe live-loss structural diagnosis — 2026-09-30

## Scope

This audit covers all seven recorded losses from frozen Kaggle submission
56704922, the exact no-op-free Severe 114720494 artifact.  Replay-tape tests
below are causal diagnostics; the independent fresh-seed panel is the
promotion evidence.

## What Severe loses to

Six of seven losses occur when YARN_STORE is among the first three shops.
Four are close losses (mean -1,722), while three are structural:

| Opponent | Opening | Severe margin | Opponent terminal farm |
|---|---|---:|---|
| Divyansh Kumar | YARN second | -18,882 | 6 cows / 11 sheep / 13 hands |
| S. Mujtaba Hussain | YARN second | -17,743 | 6 cows / 11 sheep / 11 hands |
| KharinTymofii | milk support | -13,859 | 12 cows / 5 sheep / 13 hands |

Severe remains near 8 cows / 3 sheep / 9-10 geese / 10 hands.  Its losses are
therefore not one terminal-harvest bug: two opponents use a labour-heavy wool
economy and the third uses a labour-heavy milk economy.  The common defect is
Severe's fixed lean livestock/labour architecture in these worlds.

## Patches tested and rejected

- A strict late-YARN detector was inactive-neutral against exact Severe on
  ten fresh YARN-second seeds: 0 wins, 0 losses, 20 ties.
- Route 114605783 plus a low-cash three-cow-to-sheep swap improved Divyansh
  from -18,882 to -15,121 and Mujtaba from -17,743 to -6,558, but flipped no
  result.
- Exact one- and two-cow swaps exhausted the nearby herd grid.  More sheep
  worsened Divyansh; the full three-swap version remained best for Mujtaba but
  still lost.
- Wool-sale timing variants changed Mujtaba by at most +864 and did not flip
  a result.  Divyansh was unchanged at 152 wool units sold.
- Terminal feed and harvest overrides, tested earlier in this audit, also
  failed to flip the structural losses.

The proposed Severe late-YARN patch is therefore rejected.  It is safe when
inactive but not strong enough when active.

## Cross-lineage result

Seven frozen current agents were run against each structural opponent replay
tape.  Step1010 was the only lineage that won all three:

| Agent | Divyansh | Mujtaba | Kharin |
|---|---:|---:|---:|
| Step1010 | +5,926 | +2,224 | +509 |
| Cha22 | +6,397 | +1,957 | -1,178 |
| demand-timing | +5,767 | -326 | -283 |
| V48 | +2,787 | -4,455 | -7,554 |
| V45 | +2,307 | -4,666 | -7,771 |
| Severe | -18,882 | -17,743 | -13,859 |
| pf_all | -35,237 | -23,080 | -29,063 |

This agrees with independent Experiment #135: across a fresh 150-game
six-agent round robin, Step1010 led at 44-6, ahead of Severe at 38-12.
Step1010's advantage is architectural: it builds the sheep/labour economy in
the two YARN worlds and the 12-cow/5-sheep farm in the milk-support world.

## Routing limit

Step1010 and Cha22 first diverge at step 0, while the opponent's defining
opening is not visible until step 1.  A deterministic router cannot safely
select the better chassis after observing the opponent without already having
committed to a different opening.  The honest candidate is therefore the
current no-op-free Step1010 chassis, not a falsely claimed universal router.

## Final disjoint direct panel

Ten new seeds (1100700-1100709), both seat orders, produced 80 completed games
with zero failures:

| Opponent | Step1010 W-L-T | Mean margin |
|---|---:|---:|
| Severe | 10-10-0 | +5,001.7 |
| V48 clear queue | 20-0-0 | +4,293.2 |
| Cha22 | 16-4-0 | -22.4 |
| demand-timing | 20-0-0 | +817.6 |
| **Total** | **66-14-0 (82.5%)** | — |

Margin does not affect Kaggle rating, so Cha22's 16-4 win record is the
relevant result despite its near-zero negative mean margin.  The Severe split
is equally important: Step1010 is broader but not a strict replacement that
beats Severe head-to-head.  Combined with #135, Step1010 is the best ladder
coverage candidate we currently have, while Severe remains a useful counter.

## Decision

Do not promote any Severe patch from this search.  Keep Severe as a strong
matchup-specific counter.  Current no-op-free Step1010 is the broad promotion
candidate after a 66-14 final panel, but it is not universally dominant: its
fresh Severe matchup was exactly 10-10.  No Kaggle submission is authorized by
this report.
