# Waiting-stock sale timing — discovery checkpoint, September 12

The separate candidate is `variants/shop0909_waiting_h3/main.py`, built from
the frozen opening guard submitted as56182426. No new candidate was uploaded.

Mechanism: between steps144–647, inspect sales scheduled two or three turns
ahead within the same day. Add requests only for stock projected to be in the
shed, excluding wheat/fertilizer, current sale items, buying/hiring turns and
consumption-boundary turns. Respect the ten-order limit. Worker commands and
action tapes stay unchanged. Future sale requests remain intact, so this is
**additional eligible-stock selling, not an exact quantity-conserving shift**.

Four unit tests pass. On original observations from the ibr mo sal loss107749417,
seat1,719 worker vectors remain identical and23 market-action steps change.
The probe requests14 wool at394 where the original route waits until397.
This proves activation on the targeted situation, not a realized full-game gain.
See `shop0909_waiting_mechanism_20260912.json`.

Discovery direct comparison against the submitted opening guard:

| Seed | Candidate seat | Candidate | Guard | Margin |
| --- | ---: | ---: | ---: | ---: |
| 39121000 | 0 | 116291 | 113899 | 2392 |
| 39121000 | 1 | 116291 | 113899 | 2392 |
| 39121001 | 0 | 92684 | 90002 | 2682 |
| 39121001 | 1 | 92684 | 90002 | 2682 |

**4 wins,0 losses,0 ties,0 failures. Two seeds only; not promotion evidence.**
Raw results: `shop0909_waiting_screen_20260912.json`.

A distinct ten-seed paired panel has been launched at39122000–39122009 in
`shop0909_waiting_panel_20260912/`:180 planned games covering direct vs guard
and both candidate/control against Kaito, original pf_all, Suliman fixed and
top2 fixed. **Still running at this checkpoint.** Do not infer results from
the discovery screen or submit it without the completed panel and approval.

Reproduce with `build_shop0909_waiting_sales.py`, then
`test_shop0909_waiting_sales.py`. The generic panel runner accepts
`--candidate` and `--base`; its frozen protocol records exact file hashes.
Do not reuse the opening-specific finalizer for this experiment.

Submission56182426 was separately checked COMPLETE at1971.4 during this work.
That is a live score snapshot, not a claim of convergence or rank improvement.
