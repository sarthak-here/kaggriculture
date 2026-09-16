"""Ten untouched paired seeds against pinned V45; no parameter changes after screen."""
import gzip,hashlib,json
from concurrent.futures import ProcessPoolExecutor,as_completed
from screen_v45_proactive import ROOT,run

def main():
    out=ROOT/'analysis/v45_confirmation_20260916';out.mkdir(exist_ok=False)
    previous=json.loads((ROOT/'analysis/v45_proactive_20260916/protocol.json').read_text())
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in previous['hashes'].items())
    jobs=[('candidate','parent',s,o) for s in range(39168000,39168010) for o in (0,1)]
    (out/'protocol.json').write_text(json.dumps(dict(jobs=jobs,hashes=previous['hashes']),indent=2)+'\n')
    rows=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for f in as_completed([pool.submit(run,j) for j in jobs]):
            r=f.result();rows.append(r);(out/'results.json').write_text(json.dumps(rows)+'\n')
            print(len(rows),r['status'],r.get('a'),r.get('b'),flush=True)
    assert len(rows)==20 and all(r['status']=='DONE' for r in rows)
    result=dict(wins=sum(r['a']>r['b'] for r in rows),losses=sum(r['a']<r['b'] for r in rows),
        ties=sum(r['a']==r['b'] for r in rows),failures=0,
        mean_margin=sum(r['a']-r['b'] for r in rows)/20,worst_margin=min(r['a']-r['b'] for r in rows))
    (out/'results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(result,flush=True)
if __name__=='__main__':main()
