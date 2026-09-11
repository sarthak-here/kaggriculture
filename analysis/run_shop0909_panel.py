"""Frozen ten-seed paired baseline comparison. No Kaggle API or submission calls."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
SEED=39117000
SHOP='public_candidates/shop0909_20260910/main.py'
W13='variants/w13_opening_net/main.py'
OPPONENTS={'kaito':'submit_v46_three_suffix/main.py','pf_all':'submit_pf_all/main.py',
           'suliman_fixed':'variants/current_top_routes/06_suliman_tadros/main.py',
           'top2_fixed':'variants/current_top_routes/02_3/main.py'}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'analysis/shop0909_panel');args=ap.parse_args();out=args.output
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True)
    jobs=[('direct',SHOP,W13)]+[(arm+'_'+name,path,opp) for name,opp in OPPONENTS.items() for arm,path in [('shop',SHOP),('w13',W13)]]
    paths={p for _,a,b in jobs for p in (a,b)}|{'public_candidates/shop0909_20260910/actions.json'}
    protocol={'seed_start':SEED,'pairs':10,'seats':[0,1],'jobs':jobs,'hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)}}
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    def run(job):
        name,a,b=job
        with (out/(name+'.log')).open('w',encoding='utf-8') as log:
            r=subprocess.run([sys.executable,'analysis/run_w13_isolated.py',a,b,'--seed',str(SEED),'--pairs','10','--output',str(out/(name+'.json'))],cwd=ROOT,stdout=log,stderr=log)
        result={'job':name,'returncode':r.returncode}
        p=out/(name+'.json')
        if p.exists():
            rows=json.loads(p.read_text())['rows'];done=[r for r in rows if r['status']=='DONE']
            result.update(wins=sum(r['a']>r['b'] for r in done),losses=sum(r['a']<r['b'] for r in done),ties=sum(r['a']==r['b'] for r in done),failures=sum(r['status']!='DONE' for r in rows),completed=len(done))
        print(json.dumps(result),flush=True);return result
    with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(run,jobs))
    raw={name:json.loads((out/(name+'.json')).read_text()) for name,_,_ in jobs}
    if any(r.get('completed')!=20 or r.get('failures') or r['returncode'] for r in results):
        (out/'failure_summary.json').write_text(json.dumps(results,indent=2));raise SystemExit('Incomplete panel; no promotion')
    comparisons={}
    for name in OPPONENTS:
        s={(r['seed'],r['order']):r for r in raw['shop_'+name]['rows']};w={(r['seed'],r['order']):r for r in raw['w13_'+name]['rows']}
        comparisons[name]={'gained_wins':sum(s[k]['a']>s[k]['b'] and w[k]['a']<=w[k]['b'] for k in s),
            'lost_wins':sum(s[k]['a']<=s[k]['b'] and w[k]['a']>w[k]['b'] for k in s),
            'changed_shops':sum(s[k]['shops']!=w[k]['shops'] for k in s),
            'mean_margin_delta':sum((s[k]['a']-s[k]['b'])-(w[k]['a']-w[k]['b']) for k in s)/len(s)}
    summary={'results':results,'comparisons':comparisons,'games':sum(r['completed'] for r in results)}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (out/'raw_results.json.gz').write_bytes(gzip.compress(json.dumps(raw).encode(),mtime=0))
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':main()
