"""Summarize exact fills and preserve raw experiments in a deterministic gzip."""
from pathlib import Path
import gzip
import hashlib
import json
import statistics
import os
import tempfile

ROOT=Path(__file__).resolve().parents[1]

def validate(data, name):
    if not isinstance(data,dict) or not isinstance(data.get('rows'),list) or not data['rows']:
        raise ValueError(f'{name}: expected a nonempty experiment')
    if not all(key in data for key in ('a','b','engine')):
        raise ValueError(f'{name}: missing experiment identity')
    keys=[]
    for row in data['rows']:
        if row.get('status') not in ('DONE','FAILED'):
            raise ValueError(f'{name}: invalid row status')
        keys.append((row['seed'],row['order']))
    if len(set(keys))!=len(keys):
        raise ValueError(f'{name}: duplicate seed/order rows')

def merge(previous, incoming, name):
    """Add disjoint rows; never silently replace an existing result or provenance."""
    result=dict(previous)
    for key,value in incoming.items():
        if key=='rows':continue
        if key in result and result[key]!=value:
            raise ValueError(f'{name}: conflicting {key}; use a new experiment filename')
        result[key]=value
    rows={(r['seed'],r['order']):r for r in previous['rows']}
    for row in incoming['rows']:
        key=(row['seed'],row['order'])
        if key in rows and rows[key]!=row:
            raise ValueError(f'{name}: conflicting result {key}; use a new experiment filename')
        rows[key]=row
    result['rows']=[rows[key] for key in sorted(rows)]
    return result

def summarize(root=ROOT):
    target=root/'analysis/w13_sales_raw_runs.json.gz'
    existing=target.read_bytes() if target.exists() else None
    archived=json.loads(gzip.decompress(existing)) if existing is not None else {}
    if not isinstance(archived,dict):raise ValueError('Archive must contain an experiment dictionary')
    experiments=dict(archived);summary={}
    for name,data in archived.items():validate(data,name)
    for path in sorted((root/'analysis/w13_runs').glob('*.json')):
        data=json.loads(path.read_text());validate(data,path.name)
        experiments[path.name]=merge(experiments[path.name],data,path.name) if path.name in experiments else data
    if not experiments:raise ValueError('No archived or local runs; refusing to overwrite evidence')
    for name,data in sorted(experiments.items()):
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
        summary[name]=result
    payload=json.dumps(experiments,separators=(',',':'),sort_keys=True).encode()
    raw=existing if experiments==archived else gzip.compress(payload,mtime=0)
    output={'raw_sha256':hashlib.sha256(raw).hexdigest(),'experiments':summary,
            'note':'The two non-fixed Fleong batches are harness failures, not agent losses; corrected batches are separate.'}
    # Parse, validate, merge and serialize everything before touching either output.
    # Stage both files first and replace each atomically. Run only one summarizer
    # at a time; the two paths are not a filesystem-wide atomic transaction.
    staged=[]
    try:
        for path,content in [(target,raw),(root/'analysis/w13_sales_results.json',(json.dumps(output,indent=2)+'\n').encode())]:
            path.parent.mkdir(parents=True,exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=path.parent,delete=False) as handle:
                staged.append((Path(handle.name),path));handle.write(content)
        for temporary,path in staged:os.replace(temporary,path)
    finally:
        for temporary,_ in staged:temporary.unlink(missing_ok=True)
    for name,r in summary.items():print(name,r['wins'],r['losses'],r['ties'],r['failures'])

def main():summarize()

if __name__=='__main__':main()
