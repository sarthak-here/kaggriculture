"""Fresh paired seats plus a small matched family panel; no automatic promotion."""
import gzip,hashlib,importlib.metadata,json
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from run_w13_isolated import play
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/v45_prefund_fresh_20260917'
ARMS={'candidate':'variants/v45_prefund_10/main.py','submitted':'variants/v45_proactive/main.py'}
OPPS={'submitted':ARMS['submitted'],'original':'public_candidates/cloning_v45_20260916/main.py',
      'pf_all':'submit_pf_all/main.py','astra':'variants/w13_add_strawberry/main.py',
      'top2_fixed':'variants/current_top_routes/02_3/main.py'}
def run(job):
    arm,opp,seed,seat=job
    return dict(arm=arm,opponent=opp,**play(str(ROOT/ARMS[arm]),str(ROOT/OPPS[opp]),seed,seat))
def main():
    assert importlib.metadata.version('kaggle-environments')=='1.32.7'
    jobs=[('candidate','submitted',s,o) for s in range(39171000,39171010) for o in (0,1)]
    jobs += [(a,p,39171100,o) for p in OPPS if p!='submitted' for a in ARMS for o in (0,1)]
    OUT.mkdir(exist_ok=False);rows=[]
    paths=set(ARMS.values())|set(OPPS.values())|{'analysis/run_w13_isolated.py','analysis/validate_v45_prefund.py'}
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    (OUT/'protocol.json').write_text(json.dumps({'jobs':jobs,'hashes':hashes,'caveat':'Panel is a small regression screen, not proof of top10 strength; top2_fixed is a historical fixed tape'},indent=2))
    with ProcessPoolExecutor(max_workers=4) as pool:
        for f in as_completed([pool.submit(run,j) for j in jobs]):
            r=f.result();rows.append(r);(OUT/'results.json').write_text(json.dumps(rows))
            print(len(rows),r['arm'],r['opponent'],r['seed'],r['order'],r['status'],r.get('a'),r.get('b'),flush=True)
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    (OUT/'results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
    summary={}
    for a,p in sorted({(r['arm'],r['opponent']) for r in rows}):
        group=[r for r in rows if r['arm']==a and r['opponent']==p];done=[r for r in group if r['status']=='DONE']
        summary[a+'/'+p]={'total':len(group),'failed':len(group)-len(done),'wins':sum(r['a']>r['b'] for r in done),'ties':sum(r['a']==r['b'] for r in done),'losses':sum(r['a']<r['b'] for r in done),'mean_margin':sum(r['a']-r['b'] for r in done)/len(done) if done else None}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2))
    assert len(rows)==36 and all(r['status']=='DONE' for r in rows)
if __name__=='__main__':main()
