# Replay-to-CSV tools

Run from the repository root. The collector uses the authenticated Kaggle CLI and `requests`. It only downloads public data; it never submits. Use a **new output directory** for a fresh ladder snapshot; its API cache is intentionally reused when resuming an interrupted collection.

```powershell
python analysis/collect_replay_csv_corpus.py --submission 56139834 --output analysis/new_snapshot
.venv/Scripts/python.exe analysis/replays_to_csv.py --manifest analysis/new_snapshot/manifest.json --output analysis/new_snapshot/csv_audited --audit-fills --workers 4
.venv/Scripts/python.exe analysis/summarize_replay_csv.py --directory analysis/new_snapshot
.venv/Scripts/python.exe analysis/profile_replay_terminals.py --directory analysis/new_snapshot
```

For individual `episode-N-replay.json` or `.json.gz` files:

```powershell
.venv/Scripts/python.exe analysis/replays_to_csv.py path/to/episode-123-replay.json.gz --output analysis/single_csv --audit-fills
.venv/Scripts/python.exe -m unittest discover -s analysis -p test_replays_to_csv.py -v
```

Without `--audit-fills`, the exporter needs only Python's standard library. Engine-derived fill/harvest fields remain absent or blank. Auditing requires `kaggle-environments==1.32.7`; the engine SHA is saved. Output directories must not exist, duplicate episode IDs are rejected, and failed exports are explicitly recorded and produce a nonzero exit code. Input filenames in positional mode must contain a numeric episode ID as shown above.

## Table dictionary

| Table | Grain / primary key | Important distinction |
| --- | --- | --- |
| episodes.csv | episode_id, seat | Final farm and reward, team labels, hashes, reconciliation counts. |
| turns.csv | episode_id, seat, step | State **before** executing the next recorded action; prices, shops, inventory and observed cash delta. |
| actions.csv | episode_id, seat, step, unit | Worker **requests**, pre-action position/tile, reconstructed harvested units. Unit 0 is farmer. |
| orders.csv | episode_id, seat, step, order_index | Market **requests**, not executed quantities. |
| fills.csv | episode_id, seat, step, operation, item | Engine-executed aggregated units/value, with cash verification. HIRE/BUY_LAND have blank item. |
| days.csv | episode_id, seat, day | Day cash and maximum farm counts; only cash-verified transactions enter fill totals. |

Days are zero-based. CSV text uses UTF-8 BOM for Excel, and formula-like text is escaped; numeric negatives stay numeric. Unknown private values are blank rather than fabricated zeros. Quantities still on crops are not necessarily mature: consult `terminal_tiles.csv` from the terminal profiler. Reconstructed harvest is not independently reconciled against the complete private-state lifecycle, whereas cash is checked against every next observation. Missing audit values are not proof of zero activity.

`worker_agreement` in episodes compares each whole worker-action vector, retaining the first two arguments. `opponent_trace_neighbors.csv` instead compares all arguments against the sampled top-ten vectors. Neither metric includes market orders or establishes common source code.

## Saved September 10 snapshot

Extract `replay_csv_56139834/replay_corpus.zip` into that same directory to restore `replays/`, the manifest and the leaderboard snapshot. Extract `csv_tables.zip` there to restore `csv_audited/`. `public_notebook_sources.zip` restores three inspected public notebooks without executing them. Archive SHA-256 values are in `archive_index.json`.

The collector stores loss and control labels and picks the two latest completed games of each top team's leaderboard submission. Shared games are deduplicated; self-play is excluded from our performance record. The API omits `index` for seat zero. Successful raw downloads are compressed and verified before only their exact uncompressed duplicates are removed.
