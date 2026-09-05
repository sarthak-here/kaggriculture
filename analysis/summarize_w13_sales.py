"""Summarize exact fills and preserve raw experiments in a deterministic gzip."""
from pathlib import Path
import gzip
import hashlib
import json
import statistics

ROOT=Path(__file__).resolve().parents[1]

def main():
    experiments={};summary={}
    for path in sorted((ROOT/'analysis/w13_runs').glob('*.json')):
        data=json.loads(path.read_text());experiments[path.name]=data
        rows=data['rows'];ok=[r for r in rows if r['status']=='DONE']
        result={'games_attempted':len(rows),'wins':sum(r['a']>r['b'] for r in ok),
                'losses':sum(r['a']<r['b'] for r in ok),'ties':sum(r['a']==r['b'] for r in ok),
                'failures':len(rows)-len(ok),'seeds':sorted(set(r['seed'] for r in rows))}
        if ok:
            result['mean_margin']=statistics.mean(r['a']-r['b'] for r in ok)
            result['worker_hash_equal_games']=sum(r['a_workers_sha256']==r['b_workers_sha256'] for r in ok)
            for side in ('a','b'):
                keys=sorted(set().union(*(r[side+'_fills'].keys() for r in ok)))
                result[side+'_mean_fills']={k:statistics.mean(r[side+'_fills'].get(k,0) for r in ok) for k in keys}
                result[side+'_delay_entries']=sum(r.get(side+'_telemetry',{}).get('entries',0) for r in ok)
        summary[path.name]=result
    payload=json.dumps(experiments,separators=(',',':'),sort_keys=True).encode()
    target=ROOT/'analysis/w13_sales_raw_runs.json.gz'
    target.write_bytes(gzip.compress(payload,mtime=0))
    output={'raw_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'experiments':summary,
            'note':'The two non-fixed Fleong batches are harness failures, not agent losses; corrected batches are separate.'}
    (ROOT/'analysis/w13_sales_results.json').write_text(json.dumps(output,indent=2)+'\n')
    for name,r in summary.items():print(name,r['wins'],r['losses'],r['ties'],r['failures'])

if __name__=='__main__':main()
