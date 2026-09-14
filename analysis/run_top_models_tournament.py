"""Protected portfolio versus 18 saved strong/model-lineage checkpoints."""
import ast
import gzip
import hashlib
import importlib.metadata
import json
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from run_w13_isolated import play

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'analysis/top_models_20260914'
CANDIDATE = 'variants/protected_portfolio/main.py'
MODELS = {
    'submitted_tomato432': 'variants/shop0909_tomato432/main.py',
    'shop0909_opening': 'variants/shop0909_opening_net/main.py',
    'shop0909_original': 'public_candidates/shop0909_20260910/main.py',
    'shop0909_h3': 'variants/shop0909_waiting_h3/main.py',
    'late_yarn': 'variants/late_yarn_20260914/main.py',
    'tomato_h3_unprotected': 'variants/tomato_h3_20260914/main.py',
    'astra_strawberry': 'variants/w13_add_strawberry/main.py',
    'w13_full_market': 'variants/wheat13_market_phase/main.py',
    'w13_opening': 'variants/w13_opening_net/main.py',
    'w13_crop_demand': 'variants/w13_crop_demand/main.py',
    'w13_repaired': 'variants/w13_zero_replay/main.py',
    'kaito': 'submit_v46_three_suffix/main.py',
    'kaito_soil': 'variants/kaito_soil_router/main.py',
    'kaito_clone_soil': 'variants/kaito_clone_soil_router/main.py',
    'kaito_gronk_early': 'variants/kaito_gronk_early_router/main.py',
    'pf_all_original': 'submit_pf_all/main.py',
    'prvsiyan': 'submit_prvsiyan/main.py',
    'pub_v3': 'submit_pub_v3/main.py',
}

def execute(job):
    family, seed, seat = job
    return dict(model=family, **play(str(ROOT/CANDIDATE),str(ROOT/MODELS[family]),seed,seat))

def summary(rows):
    result={}
    for model in MODELS:
        subset=[r for r in rows if r['model']==model]
        done=[r for r in subset if r['status']=='DONE']
        w=sum(r['a']>r['b'] for r in done)
        l=sum(r['a']<r['b'] for r in done)
        result[model]=dict(completed=len(subset),expected=20,wins=w,losses=l,
            ties=len(done)-w-l,failures=len(subset)-len(done),
            wins_over_total=w/len(subset) if subset else None,
            decisive_win_rate=w/(w+l) if w+l else None,
            mean_margin=sum(r['a']-r['b'] for r in done)/len(done) if done else None,
            losses_detail=[dict(seed=r['seed'],seat=r['order'],margin=r['a']-r['b'])
                           for r in done if r['a']<r['b']])
    return result

def main():
    assert importlib.metadata.version('kaggle-environments')=='1.32.7'
    paths={Path(__file__),ROOT/'analysis/run_w13_isolated.py'}
    entries={}
    for rel in [CANDIDATE,*MODELS.values()]:
        p=ROOT/rel
        source=p.read_text()
        entries[rel]=[n.name for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)][-1]
        paths.update(f for f in p.parent.rglob('*') if f.is_file() and
                     '__pycache__' not in f.parts and f.suffix in ('.py','.json','.txt'))
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    assert hashes[str(Path('submit_pf_all/main.py'))]=='9f9718cfa6e3ff822fafaf12414cc34ef6bdbf67bfdbad92662a42d0ccfdc0bf'
    OUT.mkdir(exist_ok=False)
    jobs=[(model,seed,seat) for seed in range(39163000,39163010) for model in MODELS for seat in (0,1)]
    (OUT/'protocol.json').write_text(json.dumps(dict(candidate=CANDIDATE,models=MODELS,
        jobs=jobs,hashes=hashes,entrypoints=entries,engine='1.32.7',
        scope='18 saved checkpoints, not all rejected variants or live leaderboard agents',
        caveat='Calls submission entrypoint; exceptions caught internally by agent remain part of its behavior.'),indent=2)+'\n')
    rows=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for f in as_completed([pool.submit(execute,j) for j in jobs]):
            r=f.result();rows.append(r)
            (OUT/'results.json').write_text(json.dumps(rows)+'\n')
            (OUT/'summary.json').write_text(json.dumps(summary(rows),indent=2)+'\n')
            print(len(rows),r['model'],r['seed'],r['order'],r['status'],r.get('a'),r.get('b'),flush=True)
    (OUT/'results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    assert len(rows)==360 and all(r['status']=='DONE' for r in rows)
    print('COMPLETE',json.dumps(summary(rows)),flush=True)

if __name__=='__main__':main()
