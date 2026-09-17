# Submission 56294314 export incident

Submission 56294314 is broken. It completed at 339.4 and all nine available
ladder games ended at the starting 3,000 coins. This is not a weak strategy result.
The policy did not run.

Replay 109999028 shows the submitted seat returning an object containing
`__raw_path__`, `actTimeout`, `boardSize`, and the rest of the configuration,
combined with `farmer: PASS`, no hands and no market orders. The same submission
locally reproduces 3,000 versus 171,791 in both seats when loaded the way Kaggle
loads source files.

## Root cause

`kaggle_environments.agent.get_last_callable` executes the file and returns the
last callable in namespace insertion order. It does not select the final AST
function definition. The prefund wrapper added `_local_prefund_action`, then
redefined the already-existing `agent` key. Rebinding does not move a dictionary
key to the end. Because the wrapper omitted the V45 convention
`agent=globals().pop('agent')`, Kaggle selected `_local_prefund_action` and passed
it `(observation, configuration)`. That helper interpreted the configuration as
the action and returned it. The replay is an exact signature of this failure.

Our isolated harness selected the last top-level AST `def`, so it chose `agent`
and produced a false packaging pass. The reported local strategy games exercised
the intended policy, but did not validate which callable Kaggle would execute.

## Repair and verification

The broken submitted file remains frozen at SHA-256
`baeffa728ffdad24db7799d8962e2328ae606d87c77032bcac33654d13fc18a0`.
The separate corrected candidate appends only the missing export line and has
SHA-256 `1a9c3a3ef6902d958d6269421a196aa683492e927f660f566c3029698498bf04`.
Kaggle's actual `get_last_callable` selects `_local_prefund_action` for the broken
file and `agent` for the corrected file.

The harness now mirrors Kaggle's namespace-order rule and includes a regression
test for this exact rebinding bug. With that harness:

- broken submission: 0–2, exactly 3,000 versus 171,791 in both seats;
- corrected candidate: 19–1 against `v45_proactive` over seeds 39172000–009,
  both seats, mean margin +142.5, zero execution failures;
- seed 39172005 is asymmetric: −640 in seat zero and +926 in seat one.

The corrected file is not submitted. A 19–1 family mirror is useful but does not
prove top-10 strength, and the user must explicitly approve every new upload.
