"""Small direct screen plus matched distinct-family controls; no promotion on this alone."""
import gzip,hashlib,importlib.metadata,json
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from run_w13_isolated import play
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/v45_proactive_20260916'
ARMS={'base':'public_candidates/cloning_v45_20260916/main.py','candidate':'variants/v45_proactive/main.py'}
OPPS={'parent':ARMS['base'],'tomato_h3':'variants/tomato_h3_20260914/main.py',
      'astra':'variants/w13_add_strawberry/main.py','pf_all':'submit_pf_all/main.py',
      'top2_fixed':'variants/current_top_routes/02_3/main.py'}
def run(job):
    arm,opp,seed,seat=job
    return dict(arm=arm,opponent=opp,**play(str(ROOT/ARMS[arm]),str(ROOT/OPPS[opp]),seed,seat))
def main():
    assert importlib.metadata.version('kaggle-environments')=='1.32.7'
    OUT.mkdir(exist_ok=False)
    jobs=[('candidate','parent',s,o) for s in range(39167000,39167004) for o in (0,1)]
    jobs += [(a,p,s,o) for p in OPPS if p!='parent' for a in ARMS for s in range(39167100,39167102) for o in (0,1)]
    paths={Path(__file__),ROOT/'analysis/run_w13_isolated.py'}
    for rel in set(ARMS.values())|set(OPPS.values()):
        p=ROOT/rel;paths.add(p);paths.update(p.parent.glob('*.json'))
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    (OUT/'protocol.json').write_text(json.dumps(dict(jobs=jobs,hashes=hashes),indent=2)+'\n');rows=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for f in as_completed([pool.submit(run,j) for j in jobs]):
            r=f.result();rows.append(r);(OUT/'results.json').write_text(json.dumps(rows)+'\n')
            print(len(rows),r['arm'],r['opponent'],r['seed'],r['order'],r['status'],r.get('a'),r.get('b'),flush=True)
    assert len(rows)==40 and all(r['status']=='DONE' for r in rows)
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    (OUT/'results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
    summary={}
    for a,p in sorted({(r['arm'],r['opponent']) for r in rows}):
        subset=[r for r in rows if r['arm']==a and r['opponent']==p]
        summary[a+'/'+p]=dict(wins=sum(r['a']>r['b'] for r in subset),losses=sum(r['a']<r['b'] for r in subset),
            ties=sum(r['a']==r['b'] for r in subset),mean_margin=sum(r['a']-r['b'] for r in subset)/len(subset),
            proactive_escalations=sum(r['a_telemetry'].get('local_proactive_escalations',0) for r in subset))
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(summary,flush=True)
if __name__=='__main__':main()
