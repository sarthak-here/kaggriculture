# Protected base improvements — 2026-09-14

Foundation: frozen submitted Shop0909 tomato432 (submission 56226432).
The public base, worker schedules, and safety repairs remain the foundation.
This is an incremental research candidate, not a demonstrated top-10 model.

## Completed evidence

All 41 recorded scenarios reproduce both original rewards with the baseline.
The 83-game diagnostic set includes baseline/candidate on all 33 losses and
eight recent winning controls, plus one opening-recovery-only ablation.
There are no failed games. Four losses turn into wins; no winning control is lost.

| Replay | Baseline margin | Candidate margin |
|---|---:|---:|
|108877836|-71|78|
|108893177|-6651|496|
|108903618|-773|469|
|108912723|-2287|9447|

Yusuke Hayashi 108886864 improves from -70,665 to -15,596, but remains a loss.
Recovery alone reaches -15,760. Selling one spare wheat before the three dawn
hires restores three hands; it does not solve the entire production deficit.
These are counterfactual games against fixed opponent recordings, not live policies.

Ten fresh direct seeds 39151000–39151009, both seats: 14 wins, zero losses,
six ties, zero failures. Wins/all games is 70%, not 100%. Seven guard tests pass.

## Changes and limits

- Keep the original opening and worker schedule, with a narrowly guarded dawn
  cash recovery at step 24.
- Retain exact-state-compatible sheep continuations, with complete private-state
  and worker-queue checks.
- Do not enable additional held-stock sales until after step 432, and only when
  neither production continuation is active. Earlier sales broke tomato activation
  in experiment #106.

The standalone crop-only adaptive_agent prototype is PARKED. Its four-game smoke
test lost all four games (33,596 vs 150,394 and 35,798 vs 125,517 in both seats).
It is not a successor to the proven public base and is not a submission candidate.

## Held-out matched panel

Run `.venv/Scripts/python.exe analysis/run_protected_panel.py` once in a clean
output location. It refuses to overwrite an existing experiment.
Seeds 39162000–39162009, paired seats, baseline and candidate against Kaito,
original pf_all (not pf_all2), Suliman fixed recording, and historical top-2 fixed
recording: 160 games. The latter two are not current live competitors.
Protocol, source/asset hashes, failures, ties, per-family records and matched
gained/lost wins are saved under analysis/protected_panel_20260914.
The panel is running; no conclusion is drawn from partial results.

No further Kaggle submission is authorized or made.
