"""Did the preemption path actually fire? Count shifts + clone-distance profile."""
import sys, os, importlib.util
sys.path.insert(0, os.path.abspath('.'))
from kaggle_environments import make

spec = importlib.util.spec_from_file_location("pubp", "variants/pub_preempt/main.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

fired = []
dists = []
orig = m._preempt_shift
def traced(obs, action, step):
    before = len(list(action.get("market") or []))
    if m._PREEMPT_START <= step < m._PREEMPT_STOP:
        dists.append(m._clone_distance(obs))
    out = orig(obs, action, step)
    after = len(list(out.get("market") or []))
    st = m._SHIFT_STATE[m._seat(obs)]
    if st.get("due_step") == step + 1 and st.get("due"):
        fired.append((step, dict(st["due"])))
    return out
m._preempt_shift = traced

env = make('kaggriculture', configuration={'seed': 2001}, debug=False)
env.run([m.agent, 'variants/pub_base/main.py'])
print("final rewards:", [s['reward'] for s in env.steps[-1]])
print("preempt fired %d times" % len(fired))
tot = {}
for _, due in fired:
    for k, v in due.items(): tot[k] = tot.get(k, 0) + v
print("units shifted forward by item:", tot)
print("first 5 firings:", fired[:5])
if dists:
    dists.sort()
    print("clone_distance: min %d median %d max %d ; <=6 in %d/%d steps"
          % (dists[0], dists[len(dists)//2], dists[-1],
             sum(1 for d in dists if d <= 6), len(dists)))
