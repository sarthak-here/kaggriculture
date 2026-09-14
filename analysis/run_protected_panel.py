"""Matched held-out panel; fixed recordings are explicitly not live policies."""
import gzip
import hashlib
import importlib.metadata
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from run_w13_isolated import play

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'analysis/protected_panel_20260914'
ARMS = {'base': 'variants/shop0909_tomato432/main.py',
        'candidate': 'variants/protected_portfolio/main.py'}
OPPONENTS = {'kaito': 'submit_v46_three_suffix/main.py',
             'pf_all': 'submit_pf_all/main.py',
             'suliman_fixed': 'variants/current_top_routes/06_suliman_tadros/main.py',
             'top2_fixed': 'variants/current_top_routes/02_3/main.py'}

def execute(job):
    arm, family, seed, seat = job
    return dict(arm=arm, family=family,
                **play(str(ROOT/ARMS[arm]), str(ROOT/OPPONENTS[family]), seed, seat))

def summarize(rows):
    summary = {}
    for family in OPPONENTS:
        pairs = {}
        family_result = {}
        for arm in ARMS:
            subset = [r for r in rows if r['family'] == family and r['arm'] == arm]
            done = [r for r in subset if r['status'] == 'DONE']
            wins = sum(r['a'] > r['b'] for r in done)
            losses = sum(r['a'] < r['b'] for r in done)
            family_result[arm] = dict(total=len(subset), wins=wins, losses=losses,
                ties=len(done)-wins-losses, failures=len(subset)-len(done),
                wins_over_total=wins/len(subset) if subset else None,
                decisive_win_rate=wins/(wins+losses) if wins+losses else None)
            pairs[arm] = {(r['seed'],r['order']): r for r in done}
        common = pairs['base'].keys() & pairs['candidate'].keys()
        gained = lost = 0
        for key in common:
            b,c = pairs['base'][key],pairs['candidate'][key]
            gained += c['a'] > c['b'] and b['a'] <= b['b']
            lost += b['a'] > b['b'] and c['a'] <= c['b']
        family_result.update(matched=len(common),gained_wins=gained,lost_wins=lost)
        summary[family] = family_result
    return summary

def main():
    assert importlib.metadata.version('kaggle-environments') == '1.32.7'
    OUT.mkdir(exist_ok=False)
    paths = {Path(__file__),ROOT/'analysis/run_w13_isolated.py'}
    for rel in [*ARMS.values(),*OPPONENTS.values()]:
        path=ROOT/rel
        paths.add(path)
        paths.update(path.parent.glob('*.json'))
        paths.update(path.parent.glob('*.py'))
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    jobs=[(arm,family,seed,seat) for seed in range(39162000,39162010)
          for family in OPPONENTS for arm in ARMS for seat in (0,1)]
    (OUT/'protocol.json').write_text(json.dumps(dict(engine='1.32.7',jobs=jobs,
        hashes=hashes,caveat='suliman_fixed and top2_fixed are recordings, not live policies'),indent=2)+'\n')
    rows=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for future in as_completed([pool.submit(execute,j) for j in jobs]):
            rows.append(future.result())
            (OUT/'results.json').write_text(json.dumps(rows)+'\n')
            (OUT/'summary.json').write_text(json.dumps(summarize(rows),indent=2)+'\n')
            r=rows[-1]
            print(len(rows),r['arm'],r['family'],r['seed'],r['order'],r['status'],r.get('a'),r.get('b'),flush=True)
    (OUT/'results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
    assert len(rows)==160 and all(r['status']=='DONE' for r in rows)
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    print(json.dumps(summarize(rows),indent=2),flush=True)

if __name__ == '__main__':
    main()
