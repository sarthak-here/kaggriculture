"""Turn the top-10 replay corpus into a behaviour-cloning dataset (#63).

Layout is relational on purpose. The per-step features (global + grid) are
identical for every unit deciding at that step, so storing them per unit would
duplicate ~2.2k floats about 12 times over. Instead:

    glob   [T, G]     per step
    grid   [T, GRID]  per step
    unit   [N, U]     per unit-decision
    sidx   [N]        which step each unit-decision belongs to
    label  [N]        action class (see features.UNIT_ACTIONS)
    count  [N]        PICKUP count, 0 when not applicable

One .npz per episode, so extraction is resumable and never holds the whole
corpus in memory.

Only the TARGET team's seat is extracted -- the manifest records which seat that
is, and #61 verified all 373 labels against the replay's own reward array.

Usage:
    python analysis/extract_bc_dataset.py --teams "tetsuya,Ryo Hasegawa"
    python analysis/extract_bc_dataset.py --all --workers 12
"""

import argparse
import gzip
import json
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "analysis"))
sys.path.insert(0, REPO)

import features as F  # noqa: E402

CORPUS = os.path.join(REPO, "replays_top")
MANIFEST = os.path.join(CORPUS, "manifest.json")
OUT = os.path.join(REPO, "bc_data")


def extract_one(row):
    episode_id = row["episode_id"]
    out_path = os.path.join(OUT, "ep-%d.npz" % episode_id)
    if os.path.exists(out_path):
        return (episode_id, -1, "cached")

    src = os.path.join(CORPUS, "episode-%d-replay.json.gz" % episode_id)
    try:
        with gzip.open(src, "rt", encoding="utf-8") as fh:
            data = json.load(fh)
    except Exception as exc:                      # noqa: BLE001
        return (episode_id, 0, "read error: %s" % exc)

    config = data.get("configuration") or {}
    seat = int(row["seat"])
    steps = data.get("steps") or []

    globs, grids, markets = [], [], []
    units, sidx, labels, counts = [], [], [], []
    skipped = 0

    # OFF-BY-ONE, VERIFIED (EXPERIMENTS #64): the observation stored at index i
    # ALREADY contains the effect of the action stored at index i -- at step 1
    # money already reads 25 with 5 hands while the 5 HIRE orders sit in that
    # same entry, and of 365 WATER actions every one had watered_today already
    # true on its own tile (0 under the shifted pairing). Training obs[i] against
    # action[i] therefore leaks the label: the model learns "watered_today is set
    # -> emit WATER", which is unlearnable at play time and produced an agent
    # that scored 0. The decision that produced action[i+1] was made at obs[i].
    for i in range(len(steps) - 1):
        try:
            entry = steps[i][seat]
            nxt = steps[i + 1][seat]
        except (IndexError, TypeError):
            continue
        obs = entry.get("observation")
        act = nxt.get("action")
        if not isinstance(obs, dict) or not isinstance(act, dict):
            continue
        # The replay stores each seat's own observation; make sure the encoder
        # reads it as that seat rather than trusting a stale `player` field.
        obs = dict(obs)
        obs["player"] = seat

        try:
            cache = F.encode_step(obs, config)
        except Exception:                          # noqa: BLE001
            skipped += 1
            continue

        ops = [act.get("farmer")] + list(act.get("hands") or [])
        n_units = len(F.unit_positions(cache))
        rows_here = []
        for i, op in enumerate(ops):
            if i >= n_units or not op:
                continue
            lab = F.action_label(op)
            if lab is None:
                skipped += 1
                continue
            vec = F.encode_unit(cache, i)
            if vec is None:
                skipped += 1
                continue
            rows_here.append((vec, lab[0], lab[1]))

        # Market labels are PER STEP: total quantity per verb|item class.
        # HIRE repeats as separate lines, so quantities accumulate.
        mrow = np.zeros(F.N_MARKET_ACTIONS, dtype=np.int16)
        for order in act.get("market") or []:
            m = F.market_label(order)
            if m is not None:
                mrow[m[0]] += m[1]

        if not rows_here and not mrow.any():
            continue
        step_index = len(globs)
        globs.append(cache.glob)
        grids.append(cache.grid)
        markets.append(mrow)
        for vec, lab, cnt in rows_here:
            units.append(vec)
            sidx.append(step_index)
            labels.append(lab)
            counts.append(cnt)

    if not units:
        return (episode_id, 0, "no usable decisions")

    np.savez_compressed(
        out_path,
        glob=np.asarray(globs, dtype=np.float16),
        grid=np.asarray(grids, dtype=np.float16),
        unit=np.asarray(units, dtype=np.float16),
        sidx=np.asarray(sidx, dtype=np.int32),
        label=np.asarray(labels, dtype=np.int8),
        count=np.asarray(counts, dtype=np.int8),
        market=np.asarray(markets, dtype=np.int16),
        meta=np.asarray([episode_id, seat, int(row["reward"]), int(row.get("rank", 0))],
                        dtype=np.int64),
    )
    return (episode_id, len(units), "skipped %d" % skipped)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--teams", default="tetsuya,Ryo Hasegawa",
                    help="comma-separated team names; #61 says prefer the REACTIVE ones")
    ap.add_argument("--all", action="store_true", help="every team in the manifest")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    manifest = json.load(open(MANIFEST))
    if not args.all:
        wanted = {t.strip() for t in args.teams.split(",") if t.strip()}
        manifest = [r for r in manifest if r["team_name"] in wanted]
    if args.limit:
        manifest = manifest[: args.limit]

    print("extracting %d episodes with %d workers" % (len(manifest), args.workers))
    print("dims: %s" % (F.dims(
        {"player": 0, "farms": [{"tiles": [[None] * 10] * 10}], "day": 0,
         "hour": 0, "step": 0, "market": {}, "private": {}, "town": {}},
    ),))

    t0 = time.time()
    total = 0
    with Pool(args.workers) as pool:
        for i, (eid, n, note) in enumerate(pool.imap_unordered(extract_one, manifest), 1):
            if n > 0:
                total += n
            if i % 10 == 0 or i == len(manifest):
                print("  %d/%d episodes, %d unit-decisions, %.0fs elapsed"
                      % (i, len(manifest), total, time.time() - t0), flush=True)
            if n == 0:
                print("    episode %d: %s" % (eid, note))

    size = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
    print("\ndone: %d unit-decisions, %.0f MB in %s" % (total, size / 1e6, OUT))


if __name__ == "__main__":
    main()
