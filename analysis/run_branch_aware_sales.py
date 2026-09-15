"""Fresh ten-seed paired screen of the branch-aware sales candidate."""
import gzip,hashlib,importlib.metadata,json
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from run_w13_isolated import play
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/branch_aware_sales_20260915'
A=ROOT/'variants/branch_aware_sales/main.py'
OPPS={'protected':'variants/protected_portfolio/main.py',
      'unprotected_h3':'variants/tomato_h3_20260914/main.py',
      'submitted':'variants/shop0909_tomato432/main.py'}

def run(job):
    opponent,seed,seat=job
    return dict(opponent=opponent,**play(str(A),str(ROOT/OPPS[opponent]),seed,seat))

def main():
    assert importlib.metadata.version('kaggle-environments')=='1.32.7'
    OUT.mkdir(exist_ok=False)
    files={Path(__file__),ROOT/'analysis/run_w13_isolated.py'}
    for p in [A,*[ROOT/v for v in OPPS.values()]]:
        files.update(f for f in p.parent.iterdir() if f.is_file() and f.suffix in ('.py','.json','.txt'))
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    (OUT/'protocol.json').write_text(json.dumps(dict(candidate=str(A.relative_to(ROOT)),opponents=OPPS,
        seeds=list(range(39165000,39165010)),seats=[0,1],hashes=hashes),indent=2)+'\n')
    rows=[]
    jobs=[(o,s,seat) for s in range(39165000,39165010) for o in OPPS for seat in (0,1)]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for f in as_completed([pool.submit(run,j) for j in jobs]):
            r=f.result();rows.append(r)
            (OUT/'results.json').write_text(json.dumps(rows)+'\n')
            summary={}
            for o in OPPS:
                done=[x for x in rows if x['opponent']==o and x['status']=='DONE']
                summary[o]=dict(wins=sum(x['a']>x['b'] for x in done),losses=sum(x['a']<x['b'] for x in done),
                    ties=sum(x['a']==x['b'] for x in done),failures=sum(x['opponent']==o and x['status']!='DONE' for x in rows),
                    completed=len(done),expected=20)
            (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
            print(len(rows),r['opponent'],r['seed'],r['order'],r['status'],r.get('a'),r.get('b'),flush=True)
    (OUT/'results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
    assert len(rows)==60 and all(r['status']=='DONE' for r in rows)
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items())
    print('COMPLETE',summary,flush=True)
if __name__=='__main__':main()
