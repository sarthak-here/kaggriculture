"""Corrected-prefund tournament against eight frozen previous-best models."""
from __future__ import annotations
import gzip,hashlib,importlib.metadata,json
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from run_w13_isolated import play

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/v45_prefund_exported_previous_best_20260917'
CANDIDATE='variants/v45_prefund_10_exported/main.py'
OPPONENTS={
    'v45_proactive':'variants/v45_proactive/main.py',
    'v45_original':'public_candidates/cloning_v45_20260916/main.py',
    'pf_all':'submit_pf_all/main.py',
    'kaito_clone_soil':'variants/kaito_clone_soil_router/main.py',
    'w13_reconstructed':'variants/panel_wheat13/main.py',
    'w13_astra':'variants/w13_add_strawberry/main.py',
    'w13_opening_net':'variants/w13_opening_net/main.py',
    'shop0909_tomato432':'variants/shop0909_tomato432/main.py',
}
SEEDS=range(39173000,39173010)

def run(job):
    opponent,seed,seat=job
    return dict(opponent=opponent,**play(str(ROOT/CANDIDATE),str(ROOT/OPPONENTS[opponent]),seed,seat))

def main():
    assert importlib.metadata.version('kaggle-environments')=='1.32.7'
    if OUT.exists():raise FileExistsError(OUT)
    OUT.mkdir()
    jobs=[(opponent,seed,seat) for opponent in OPPONENTS for seed in SEEDS for seat in (0,1)]
    paths={CANDIDATE,'analysis/run_w13_isolated.py','analysis/tournament_v45_prefund_exported.py',*OPPONENTS.values()}
    # Include data files loaded by the Shop0909 model.
    paths.update(str(p.relative_to(ROOT)) for p in (ROOT/'variants/shop0909_tomato432').glob('*.json'))
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)}
    protocol={'jobs':jobs,'hashes':hashes,'engine':'1.32.7',
              'selection':'Eight frozen previous-best models, preregistered before outcomes; ten new seeds, both seats.',
              'limitations':'Direct local policies, not a live ladder or proof of top-10 strength.'}
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    rows=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(run,job) for job in jobs]
        for future in as_completed(futures):
            row=future.result();rows.append(row)
            (OUT/'results.json').write_text(json.dumps(rows)+'\n')
            print(len(rows),row['opponent'],row['seed'],row['order'],row['status'],row.get('a'),row.get('b'),flush=True)
    assert len(rows)==len(jobs)
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    summary={}
    for opponent in OPPONENTS:
        group=[r for r in rows if r['opponent']==opponent];done=[r for r in group if r['status']=='DONE']
        summary[opponent]={
            'games':len(group),'failures':len(group)-len(done),
            'wins':sum(r['a']>r['b'] for r in done),
            'losses':sum(r['a']<r['b'] for r in done),
            'ties':sum(r['a']==r['b'] for r in done),
            'win_rate_all_games':sum(r['a']>r['b'] for r in done)/len(group),
            'mean_margin':sum(r['a']-r['b'] for r in done)/len(done) if done else None,
            'worst_margin':min((r['a']-r['b'] for r in done),default=None),
        }
    aggregate={'games':len(rows),'failures':sum(r['status']!='DONE' for r in rows),
               'wins':sum(r.get('a',0)>r.get('b',0) for r in rows if r['status']=='DONE'),
               'losses':sum(r.get('a',0)<r.get('b',0) for r in rows if r['status']=='DONE'),
               'ties':sum(r.get('a')==r.get('b') for r in rows if r['status']=='DONE')}
    result={'aggregate':aggregate,'by_opponent':summary}
    (OUT/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
    assert aggregate['failures']==0
    print(json.dumps(result,indent=2),flush=True)

if __name__=='__main__':main()
