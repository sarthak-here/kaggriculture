"""Search the corpus for the best hard-coded route (#71).

pub_v2 works because one coherent expert route beats a twelve-trace average
(92.9%). But which route is best is NOT predictable from episode reward -- the
highest-scoring episode in the corpus (tetsuya, 165,467) made the WORST route
tested, 20% against the base agent, while peikopon's 160,658 made the best.

A high episode reward can come from a soft opponent or a kind seed; what a route
needs is to be robust when replayed onto a different seed against a different
opponent. There is no way to read that off the reward, so screen empirically:
build a route from each candidate episode, play a short paired-seat match
against the incumbent, and duel the survivors properly.

Usage:
    python analysis/route_search.py build 2      # 2 best episodes per team
    python analysis/route_search.py screen 3     # 3 seeds x 2 orders each
"""

import base64
import json
import os
import re
import subprocess
import sys
import zlib

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "analysis"))

from rebuild_route import load, route_of, SRC  # noqa: E402

CORPUS = os.path.join(REPO, "replays_top")
MANIFEST = os.path.join(CORPUS, "manifest.json")
OUTROOT = os.path.join(REPO, "variants", "rs")
INCUMBENT = os.path.join(REPO, "variants", "pub_v2", "main.py")
PAT = re.compile(
    r"_ACTIONS = json\.loads\(zlib\.decompress\(base64\.b85decode\('[^']*'\)\)\.decode\('utf-8'\)\)")


def candidates(per_team):
    man = json.load(open(MANIFEST))
    by_team = {}
    for r in sorted(man, key=lambda r: -r["reward"]):
        by_team.setdefault(r["team_name"], []).append(r)
    out = []
    for team, rows in by_team.items():
        out.extend(rows[:per_team])
    return out


def build(per_team):
    src = open(SRC, encoding="utf-8").read()
    # carry pub_v2's two non-route fixes so the screen isolates the ROUTE only
    src = src.replace("_PREEMPT_ENABLED = False", "_PREEMPT_ENABLED = True")
    v2 = open(INCUMBENT, encoding="utf-8").read()
    for marker in ('"CARROT": (35, 10000, 450, "hinge", 1.0, "sqrt", 0.7),',
                   '"TOMATO": (60, 10000, 200, "hinge", 0.4, "sqrt", 0.6),',
                   '"EGG": (50, 10000, 332, "hinge", 0.4, "log", 0.2),'):
        old = marker.replace('"hinge", 1.0', '"log", 0.2').replace(
            '"hinge", 0.4, "sqrt"', '"linear", 0.4, "sqrt"').replace(
            '"hinge", 0.4, "log"', '"linear", 0.4, "log"')
        src = src.replace(old, marker)
    # hinge branch + scale threading, lifted verbatim from the built pub_v2
    start = v2.index("def _shape(")
    end = v2.index("def _market_price(")
    src = src[:src.index("def _shape(")] + v2[start:end] + src[src.index("def _market_price("):]
    for a, b in (("_shape(below_func, scale)", "_shape(below_func, scale, scale)"),
                 ("_shape(below_func, equilibrium - inventory)",
                  "_shape(below_func, equilibrium - inventory, scale)"),
                 ("_shape(above_func, scale)", "_shape(above_func, scale, scale)"),
                 ("_shape(above_func, inventory - equilibrium)",
                  "_shape(above_func, inventory - equilibrium, scale)")):
        src = src.replace(a, b)

    rows = candidates(per_team)
    os.makedirs(OUTROOT, exist_ok=True)
    made = []
    for r in rows:
        name = "ep%d" % r["episode_id"]
        d = os.path.join(OUTROOT, name)
        os.makedirs(d, exist_ok=True)
        target = os.path.join(d, "main.py")
        if not os.path.exists(target):
            rt = route_of(load(r["episode_id"]), r["seat"])
            blob = base64.b85encode(zlib.compress(
                json.dumps(rt, separators=(",", ":")).encode(), 9)).decode()
            new = ("_ACTIONS = json.loads(zlib.decompress(base64.b85decode('%s'))"
                   ".decode('utf-8'))" % blob)
            open(target, "w", encoding="utf-8").write(PAT.sub(lambda _m: new, src, count=1))
        made.append((name, r))
    print("built %d route variants in %s" % (len(made), OUTROOT))
    json.dump([{"name": n, **r} for n, r in made],
              open(os.path.join(OUTROOT, "index.json"), "w"), indent=1)
    return made


def screen(seeds):
    idx = json.load(open(os.path.join(OUTROOT, "index.json")))
    py = os.path.join(REPO, ".venv", "Scripts", "python.exe")
    duel = os.path.join(REPO, "analysis", "duel.py")
    results = []
    for i, row in enumerate(idx, 1):
        path = os.path.join(OUTROOT, row["name"], "main.py")
        try:
            out = subprocess.run([py, "-u", duel, path, INCUMBENT, str(seeds)],
                                 capture_output=True, text=True, timeout=1800).stdout
        except subprocess.TimeoutExpired:
            print("  %-16s TIMEOUT" % row["name"])
            continue
        m = re.search(r"A WIN RATE \(decisive games\): ([0-9.]+)%", out)
        g = re.search(r"mean margin \(diagnostic only\): ([+-][0-9,]+)", out)
        if not m:
            print("  %-16s no result" % row["name"])
            continue
        wr = float(m.group(1))
        margin = int(g.group(1).replace(",", "").replace("+", "")) if g else 0
        results.append((wr, margin, row))
        print("  %2d/%d  %-16s %-18s reward %7.0f   win %5.1f%%  margin %+7d"
              % (i, len(idx), row["name"], row["team_name"][:18], row["reward"], wr, margin),
              flush=True)

    results.sort(key=lambda t: (-t[0], -t[1]))
    print("\n=== TOP ROUTES vs pub_v2 ===")
    for wr, margin, row in results[:8]:
        print("  %-16s %-18s reward %7.0f   win %5.1f%%  margin %+7d"
              % (row["name"], row["team_name"][:18], row["reward"], wr, margin))
    json.dump([{"win": w, "margin": m, **r} for w, m, r in results],
              open(os.path.join(OUTROOT, "screen.json"), "w"), indent=1)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    arg = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    if cmd == "build":
        build(arg)
    else:
        screen(arg)
