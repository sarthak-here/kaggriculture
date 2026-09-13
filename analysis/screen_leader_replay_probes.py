"""Small discovery screen of coherent routes; not a leaderboard-policy benchmark."""
import argparse,json,subprocess,sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument('--index',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--seed',type=int,required=True);p.add_argument('--pairs',type=int,default=2);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    index=json.loads(a.index.read_text())
    def run(row):
        ep=str(row['episode']);out=a.output/(ep+'.json')
        with (a.output/(ep+'.log')).open('w') as log:
            r=subprocess.run([sys.executable,'analysis/run_w13_isolated.py',row['path'],
                'variants/shop0909_opening_net/main.py','--seed',str(a.seed),'--pairs',str(a.pairs),'--output',str(out)],stdout=log,stderr=log)
        rows=json.loads(out.read_text())['rows'] if out.exists() else []
        done=[x for x in rows if x['status']=='DONE']
        result=dict(episode=row['episode'],returncode=r.returncode,expected=2*a.pairs,completed=len(done),
            failures=sum(x['status']!='DONE' for x in rows),wins=sum(x['a']>x['b'] for x in done),
            losses=sum(x['a']<x['b'] for x in done),ties=sum(x['a']==x['b'] for x in done),
            mean_margin=sum(x['a']-x['b'] for x in done)/len(done) if done else None)
        print(json.dumps(result),flush=True);return result
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,index))
    (a.output/'summary.json').write_text(json.dumps(results,indent=2)+'\n')
if __name__=='__main__':main()
