"""Fresh paired evaluation of the narrow Shop0909 opening candidate."""
import argparse,gzip,hashlib,json,subprocess,sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CAND='variants/shop0909_opening_net/main.py'
BASE='public_candidates/shop0909_20260910/main.py'
OPP={'kaito':'submit_v46_three_suffix/main.py','pf_all':'submit_pf_all/main.py',
     'suliman_fixed':'variants/current_top_routes/06_suliman_tadros/main.py',
     'top2_fixed':'variants/current_top_routes/02_3/main.py'}
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--seed',type=int,default=39119000);p.add_argument('--pairs',type=int,default=10)
    p.add_argument('--candidate',default=CAND);p.add_argument('--base',default=BASE)
    a=p.parse_args();out=a.output;out.mkdir(parents=True,exist_ok=False)
    jobs=[('direct',a.candidate,a.base)]+[(arm+'_'+name,path,opp) for name,opp in OPP.items() for arm,path in [('candidate',a.candidate),('base',a.base)]]
    paths={s for _,x,y in jobs for s in (x,y)}|{str(Path(a.candidate).with_name('actions.json')),str(Path(a.base).with_name('actions.json')),'analysis/run_w13_isolated.py'}
    protocol=dict(seed=a.seed,pairs=a.pairs,jobs=jobs,hashes={s:hashlib.sha256((ROOT/s).read_bytes()).hexdigest() for s in sorted(paths)})
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    def run(job):
        name,x,y=job
        with (out/(name+'.log')).open('w',encoding='utf-8') as log:
            r=subprocess.run([sys.executable,'analysis/run_w13_isolated.py',x,y,'--seed',str(a.seed),'--pairs',str(a.pairs),'--output',str(out/(name+'.json'))],cwd=ROOT,stdout=log,stderr=log)
        path=out/(name+'.json')
        rows=json.loads(path.read_text())['rows'] if path.exists() else []
        done=[r for r in rows if r['status']=='DONE']
        result=dict(job=name,returncode=r.returncode,completed=len(done),expected=2*a.pairs,
            wins=sum(r['a']>r['b'] for r in done),losses=sum(r['a']<r['b'] for r in done),
            ties=sum(r['a']==r['b'] for r in done),failures=sum(r['status']!='DONE' for r in rows))
        print(json.dumps(result),flush=True);return result
    with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(run,jobs))
    raw={name:json.loads((out/(name+'.json')).read_text()) for name,_,_ in jobs if (out/(name+'.json')).exists()}
    complete=all(r['completed']==2*a.pairs and r['failures']==0 and r['returncode']==0 for r in results)
    comparisons={}
    if complete:
        for name in OPP:
            c={(r['seed'],r['order']):r for r in raw['candidate_'+name]['rows']}
            b={(r['seed'],r['order']):r for r in raw['base_'+name]['rows']}
            comparisons[name]=dict(gained_wins=sum(c[k]['a']>c[k]['b'] and b[k]['a']<=b[k]['b'] for k in c),
                lost_wins=sum(c[k]['a']<=c[k]['b'] and b[k]['a']>b[k]['b'] for k in c),
                changed_shops=sum(c[k]['shops']!=b[k]['shops'] for k in c),
                changed_own_worker_traces=sum(c[k]['a_workers_sha256']!=b[k]['a_workers_sha256'] for k in c),
                mean_margin_delta=sum(c[k]['a']-c[k]['b']-b[k]['a']+b[k]['b'] for k in c)/len(c),
                day1_understaffed_candidate=sum(r['a_checkpoints']['25']['hands']<3 for r in c.values()),
                day1_understaffed_base=sum(r['a_checkpoints']['25']['hands']<3 for r in b.values()))
    summary=dict(complete=complete,results=results,comparisons=comparisons)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (out/'raw_results.json.gz').write_bytes(gzip.compress(json.dumps(raw).encode(),mtime=0))
    print(json.dumps(summary,indent=2),flush=True)
    if not complete:raise SystemExit('Incomplete panel; do not promote')
if __name__=='__main__':main()
