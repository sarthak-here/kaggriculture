# Submission56226432 loss refresh

Public score1960.3 at the start of this round; prior opening-only submission
1794.0. These are snapshot ratings, not a controlled comparison or convergence claim.
API snapshot contains75 completed games:40 wins,33 losses,2 ties.

Downloaded every one of the33 available losses plus eight recent wins.
All41 replays reconcile through the pinned game engine:58958 cash transitions,
zero mismatches. `audit.json` contains verified filled units/values, daily
cash, full worker-action agreement and terminal farm state. `replay_corpus.zip`
preserves source replays and API metadata with SHA256/CRC verification.

## Current weaknesses

-15 losses satisfy >=97% exact worker agreement and equal core product sale
quantities. These are near-clone timing/pricing cases.
-18 remaining losses include opening collapse, production/route differences
and small quantity differences. This residual group is not a causal diagnosis.
-Worst: Yusuke Hayashi108886864, margin-70665. At20 we spend the final20coins
on two wheat seeds. At24 cash is0 and no hands are hired, while the opponent
hires3. Milk/wool production subsequently collapses. Netting the initial
wheat round-trip alone did not prevent this scenario.
-Other major losses: Laplacenvmv-9991, Пётр П-7580, Dmytro Maliarenko-7201,
Yuuki4543-6651. Tomato production alone does not cover every matchup.

## Separate experiments started

`day1_recovery`: only at24, only the exact three-HIRE market list, cash<4,
projected wheat stock>=2 and quoted wheat price>=4: prepend a one-unit wheat
sale to fund hiring. Preserve worker actions and leave at least one projected
shed wheat. This is an experiment, not a proven universal recovery.

`protected_portfolio`: retain the existing tomato branch, add the previously
built exact-state sheep branches at288, and allow h3 sale additions only after
432 when neither production continuation is active. This protects the decision
prefix that the earlier19-1 h3 experiment accidentally disrupted.

Seven new guard tests pass. Both candidates remain separate from the submitted
ZIP. An83-game original-seed experiment covers all33 losses and8 win controls
with submitted/candidate pairs, plus the recovery-only catastrophic case.
A ten-fresh-seed paired comparison is also running. Recorded opponents cannot
adapt to candidate changes, so these diagnostics do not establish live strength.

No new Kaggle submission. Completed results will be documented separately.
