"""Market-order policy for behaviour cloning (#64). numpy only.

The unit policy decides what the 15 workers do; this decides what the farm
BUYS and SELLS. Without it the agent never hires, so it has no hands at all --
the game is unplayable. It is a separate model because the decision is per STEP,
not per unit, and because 80.35% of steps emit no order (#63).

Two heads over the shared per-step features:

    emit[k]  sigmoid  -- does class k appear this step?
    qty[k]   linear   -- log1p(quantity), trained ONLY where it appears

Trained on log1p because quantities are heavy-tailed (HIRE x5 at step 0,
SELL FERTILIZER x4 all game, terminal sweeps of 30+).
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
    G, R, M = [], [], []
    for p in paths:
        z = np.load(p)
        G.append(z["glob"])
        R.append(z["grid"])
        M.append(z["market"])
    return np.concatenate(G), np.concatenate(R), np.concatenate(M)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hidden", type=int, default=256)
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--batch", type=int, default=2048)
    ap.add_argument("--lr", type=float, default=2e-3)
    ap.add_argument("--val-frac", type=float, default=0.2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-episodes", type=int, default=160)
    args = ap.parse_args()

    files = sorted(globmod.glob(os.path.join(DATA, "ep-*.npz")))
    rng = np.random.default_rng(args.seed)
    rng.shuffle(files)
    files = files[: args.max_episodes]
    n_val = max(1, int(len(files) * args.val_frac))
    val_files, train_files = files[:n_val], files[n_val:]
    print("episodes: %d train / %d val (split BY EPISODE)" % (len(train_files), len(val_files)))

    gtr, rtr, mtr = load(train_files)
    gva, rva, mva = load(val_files)
    print("train steps %d | val steps %d" % (len(gtr), len(gva)))

    K = F.N_MARKET_ACTIONS
    Dg, Dr, H = gtr.shape[1], rtr.shape[1], args.hidden

    ytr = (mtr > 0).astype(np.float32)
    yva = (mva > 0).astype(np.float32)
    qtr = np.log1p(np.maximum(0, mtr).astype(np.float32))
    qva = np.log1p(np.maximum(0, mva).astype(np.float32))
    print("steps with at least one order: train %.1f%%  val %.1f%%"
          % (100.0 * (ytr.any(axis=1)).mean(), 100.0 * (yva.any(axis=1)).mean()))

    sc = lambda a: np.sqrt(2.0 / a)  # noqa: E731
    Wg = (rng.standard_normal((Dg, H)) * sc(Dg)).astype(np.float32)
    Wr = (rng.standard_normal((Dr, H)) * sc(Dr)).astype(np.float32)
    b = np.zeros(H, dtype=np.float32)
    We = (rng.standard_normal((H, K)) * sc(H)).astype(np.float32)
    be = np.full(K, -3.0, dtype=np.float32)     # rare events: start pessimistic
    Wq = (rng.standard_normal((H, K)) * sc(H)).astype(np.float32)
    bq = np.zeros(K, dtype=np.float32)

    params = [Wg, Wr, b, We, be, Wq, bq]
    m = [np.zeros_like(p) for p in params]
    v = [np.zeros_like(p) for p in params]
    b1, b2, eps = 0.9, 0.999, 1e-8
    t = 0

    def fwd(gi, ri):
        pre = gi @ Wg + ri @ Wr + b
        h = np.maximum(pre, 0.0)
        return pre, h, h @ We + be, h @ Wq + bq

    def evaluate(g, r, y, q, bs=8192):
        tp = fp = fn = 0
        qerr = qn = 0.0
        for i in range(0, len(g), bs):
            sl = slice(i, i + bs)
            _, _, le, lq = fwd(g[sl].astype(np.float32), r[sl].astype(np.float32))
            pred = (le > 0.0)
            act = y[sl] > 0.5
            tp += int((pred & act).sum())
            fp += int((pred & ~act).sum())
            fn += int((~pred & act).sum())
            mask = act
            if mask.any():
                qerr += float((np.abs(np.expm1(np.clip(lq, 0, 6)) - np.expm1(q[sl]))[mask]).sum())
                qn += float(mask.sum())
        prec = tp / max(1, tp + fp)
        rec = tp / max(1, tp + fn)
        f1 = 2 * prec * rec / max(1e-9, prec + rec)
        return prec, rec, f1, (qerr / max(1.0, qn))

    n = len(gtr)
    for epoch in range(args.epochs):
        order = rng.permutation(n)
        t0 = time.time()
        run = 0.0
        nb = 0
        for i in range(0, n, args.batch):
            idx = order[i:i + args.batch]
            gi = gtr[idx].astype(np.float32)
            ri = rtr[idx].astype(np.float32)
            yi = ytr[idx]
            qi = qtr[idx]
            B = len(idx)

            pre, h, le, lq = fwd(gi, ri)
            p = 1.0 / (1.0 + np.exp(-np.clip(le, -30, 30)))
            loss = -(yi * np.log(p + 1e-9) + (1 - yi) * np.log(1 - p + 1e-9)).mean()
            dle = (p - yi) / (B * K)

            mask = yi > 0.5
            dq = np.where(mask, (lq - qi), 0.0)
            denom = max(1.0, float(mask.sum()))
            loss += float((dq ** 2).sum() / denom)
            dlq = 2.0 * dq / denom

            run += float(loss)
            nb += 1

            gWe = h.T @ dle
            gbe = dle.sum(axis=0)
            gWq = h.T @ dlq
            gbq = dlq.sum(axis=0)
            dh = dle @ We.T + dlq @ Wq.T
            dh[pre <= 0] = 0.0
            gWg = gi.T @ dh
            gWr = ri.T @ dh
            gb = dh.sum(axis=0)

            t += 1
            for pi, (par, grad) in enumerate(
                    zip(params, [gWg, gWr, gb, gWe, gbe, gWq, gbq])):
                m[pi] = b1 * m[pi] + (1 - b1) * grad
                v[pi] = b2 * v[pi] + (1 - b2) * (grad * grad)
                par -= args.lr * (m[pi] / (1 - b1 ** t)) / (np.sqrt(v[pi] / (1 - b2 ** t)) + eps)

        prec, rec, f1, qerr = evaluate(gva, rva, yva, qva)
        print("epoch %d  loss %.4f | VAL precision %.3f recall %.3f F1 %.3f  qty MAE %.2f  (%.0fs)"
              % (epoch + 1, run / max(1, nb), prec, rec, f1, qerr, time.time() - t0), flush=True)

    # ---- per-class threshold calibration -------------------------------
    # A single 0.5 cut leaves rare-but-essential classes (BUY_ANIMAL, SELL|WOOL,
    # BUY_PRODUCT feed) at ~0 recall, and an agent that never buys feed or sells
    # wool is not playable. Pick each class's threshold to maximise F1 on the
    # held-out episodes instead.
    nval = min(60000, len(gva))
    _, _, le, _ = fwd(gva[:nval].astype(np.float32), rva[:nval].astype(np.float32))
    act = yva[:nval] > 0.5
    thresholds = np.zeros(K, dtype=np.float32)
    print("\nper-class emit, threshold calibrated on held-out episodes:")
    for k in range(K):
        sup = int(act[:, k].sum())
        if sup < 20:
            thresholds[k] = 1e9          # never fire a class we cannot judge
            continue
        best_f1, best_t = -1.0, 0.0
        for t_ in np.quantile(le[:, k], np.linspace(0.50, 0.999, 60)):
            pred = le[:, k] > t_
            tp = float((pred & act[:, k]).sum())
            if tp == 0:
                continue
            prec = tp / max(1.0, float(pred.sum()))
            rec = tp / sup
            f1 = 2 * prec * rec / max(1e-9, prec + rec)
            if f1 > best_f1:
                best_f1, best_t = f1, float(t_)
        thresholds[k] = best_t
        pred = le[:, k] > best_t
        tp = float((pred & act[:, k]).sum())
        print("  %-24s support %6d  recall %.3f  precision %.3f  F1 %.3f"
              % (F.MARKET_ACTIONS[k], sup, tp / sup,
                 tp / max(1.0, float(pred.sum())), best_f1))

    pred_all = le > thresholds[None, :]
    tp = float((pred_all & act).sum())
    prec = tp / max(1.0, float(pred_all.sum()))
    rec = tp / max(1.0, float(act.sum()))
    print("\ncalibrated OVERALL: precision %.3f recall %.3f F1 %.3f"
          % (prec, rec, 2 * prec * rec / max(1e-9, prec + rec)))

    np.savez(os.path.join(REPO, "bc_market.npz"),
             Wg=Wg, Wr=Wr, b=b, We=We, be=be, Wq=Wq, bq=bq, thr=thresholds)
    print("\nsaved bc_market.npz")


if __name__ == "__main__":
    main()
