"""Behaviour-cloning baseline for the unit policy (#63). numpy only.

Architecture mirrors the inference constraint rather than fighting it. Per-step
features (global, grid) are projected ONCE per step and gathered per unit:

    h = relu( Wg @ glob[s] + Wr @ grid[s] + Wu @ unit + b )
    logits = Wo @ h + bo

At play time that means one matmul per step for the shared half and one small
matmul per unit, which is what keeps ~15 decisions inside the 1s actTimeout.

THE SPLIT IS BY EPISODE, never by row. Units within one game share a board and
a market; a random row split leaks the answer across the boundary and reports a
score the live agent will never reproduce.
"""

import argparse
import glob as globmod
import os
import sys
import time

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "analysis"))
sys.path.insert(0, REPO)

import features as F  # noqa: E402

DATA = os.path.join(REPO, "bc_data")


def load(paths):
    G, R, U, S, Y = [], [], [], [], []
    step_offset = 0
    for p in paths:
        z = np.load(p)
        G.append(z["glob"])
        R.append(z["grid"])
        U.append(z["unit"])
        S.append(z["sidx"].astype(np.int64) + step_offset)
        Y.append(z["label"].astype(np.int64))
        step_offset += z["glob"].shape[0]
    return (np.concatenate(G), np.concatenate(R), np.concatenate(U),
            np.concatenate(S), np.concatenate(Y))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hidden", type=int, default=256)
    ap.add_argument("--epochs", type=int, default=6)
    ap.add_argument("--batch", type=int, default=4096)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--val-frac", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    files = sorted(globmod.glob(os.path.join(DATA, "ep-*.npz")))
    if not files:
        print("no data in %s -- run extract_bc_dataset.py first" % DATA)
        return
    rng = np.random.default_rng(args.seed)
    rng.shuffle(files)
    n_val = max(1, int(len(files) * args.val_frac))
    val_files, train_files = files[:n_val], files[n_val:]
    print("episodes: %d train / %d val  (split BY EPISODE)" % (len(train_files), len(val_files)))

    gtr, rtr, utr, str_, ytr = load(train_files)
    gva, rva, uva, sva, yva = load(val_files)
    print("train %d unit-decisions over %d steps | val %d over %d"
          % (len(ytr), len(gtr), len(yva), len(gva)))

    Dg, Dr, Du = gtr.shape[1], rtr.shape[1], utr.shape[1]
    K = F.N_UNIT_ACTIONS
    H = args.hidden

    # majority-class baseline on the validation set
    counts = np.bincount(ytr, minlength=K)
    major = int(counts.argmax())
    base_acc = float((yva == major).mean())
    print("majority class = %s  -> val accuracy %.4f"
          % (F.UNIT_ACTIONS[major], base_acc))

    scale = lambda a, b: np.sqrt(2.0 / a)  # noqa: E731
    Wg = (rng.standard_normal((Dg, H)) * scale(Dg, H)).astype(np.float32)
    Wr = (rng.standard_normal((Dr, H)) * scale(Dr, H)).astype(np.float32)
    Wu = (rng.standard_normal((Du, H)) * scale(Du, H)).astype(np.float32)
    b = np.zeros(H, dtype=np.float32)
    Wo = (rng.standard_normal((H, K)) * scale(H, K)).astype(np.float32)
    bo = np.zeros(K, dtype=np.float32)

    params = [Wg, Wr, Wu, b, Wo, bo]
    m = [np.zeros_like(p) for p in params]
    v = [np.zeros_like(p) for p in params]
    b1, b2, eps = 0.9, 0.999, 1e-8
    t = 0

    def forward(gi, ri, ui):
        pre = gi @ Wg + ri @ Wr + ui @ Wu + b
        h = np.maximum(pre, 0.0)
        return pre, h, h @ Wo + bo

    def evaluate(g, r, u, s, y, bs=8192):
        correct = 0
        loss = 0.0
        for i in range(0, len(y), bs):
            sl = slice(i, i + bs)
            si = s[sl]
            gi = g[si].astype(np.float32)
            ri = r[si].astype(np.float32)
            ui = u[sl].astype(np.float32)
            _, _, logits = forward(gi, ri, ui)
            logits -= logits.max(axis=1, keepdims=True)
            expz = np.exp(logits)
            p = expz / expz.sum(axis=1, keepdims=True)
            yi = y[sl]
            loss += -np.log(np.maximum(p[np.arange(len(yi)), yi], 1e-12)).sum()
            correct += int((logits.argmax(axis=1) == yi).sum())
        return correct / len(y), loss / len(y)

    n = len(ytr)
    for epoch in range(args.epochs):
        order = rng.permutation(n)
        t0 = time.time()
        running = 0.0
        nb = 0
        for i in range(0, n, args.batch):
            idx = order[i:i + args.batch]
            si = str_[idx]
            gi = gtr[si].astype(np.float32)
            ri = rtr[si].astype(np.float32)
            ui = utr[idx].astype(np.float32)
            yi = ytr[idx]

            pre, h, logits = forward(gi, ri, ui)
            logits -= logits.max(axis=1, keepdims=True)
            expz = np.exp(logits)
            p = expz / expz.sum(axis=1, keepdims=True)
            B = len(yi)
            running += float(-np.log(np.maximum(p[np.arange(B), yi], 1e-12)).mean())
            nb += 1

            dlogits = p
            dlogits[np.arange(B), yi] -= 1.0
            dlogits /= B

            gWo = h.T @ dlogits
            gbo = dlogits.sum(axis=0)
            dh = dlogits @ Wo.T
            dh[pre <= 0] = 0.0
            gWg = gi.T @ dh
            gWr = ri.T @ dh
            gWu = ui.T @ dh
            gb = dh.sum(axis=0)

            t += 1
            for pi, (par, grad) in enumerate(zip(params, [gWg, gWr, gWu, gb, gWo, gbo])):
                m[pi] = b1 * m[pi] + (1 - b1) * grad
                v[pi] = b2 * v[pi] + (1 - b2) * (grad * grad)
                mh = m[pi] / (1 - b1 ** t)
                vh = v[pi] / (1 - b2 ** t)
                par -= args.lr * mh / (np.sqrt(vh) + eps)

        acc, vloss = evaluate(gva, rva, uva, sva, yva)
        print("epoch %d  train loss %.4f  |  VAL acc %.4f  loss %.4f  (%.0fs)"
              % (epoch + 1, running / max(1, nb), acc, vloss, time.time() - t0), flush=True)

    acc, _ = evaluate(gva, rva, uva, sva, yva)
    print("\nFINAL val accuracy %.4f   vs majority %.4f   (lift %.2fx)"
          % (acc, base_acc, acc / max(1e-9, base_acc)))

    # per-class recall, to see WHERE it learns
    preds = np.empty(len(yva), dtype=np.int64)
    for i in range(0, len(yva), 8192):
        sl = slice(i, i + 8192)
        si = sva[sl]
        _, _, lg = forward(gva[si].astype(np.float32), rva[si].astype(np.float32),
                           uva[sl].astype(np.float32))
        preds[sl] = lg.argmax(axis=1)
    print("\n  %-22s %8s %8s %8s" % ("class", "support", "recall", "share"))
    for k in np.argsort(-np.bincount(yva, minlength=K))[:14]:
        mask = yva == k
        sup = int(mask.sum())
        if not sup:
            continue
        print("  %-22s %8d %8.3f %7.2f%%"
              % (F.UNIT_ACTIONS[k], sup, float((preds[mask] == k).mean()),
                 100.0 * sup / len(yva)))

    np.savez(os.path.join(REPO, "bc_model.npz"),
             Wg=Wg, Wr=Wr, Wu=Wu, b=b, Wo=Wo, bo=bo)
    print("\nsaved bc_model.npz")


if __name__ == "__main__":
    main()
