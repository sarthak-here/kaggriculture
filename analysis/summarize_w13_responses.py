"""Archive auditable local results, retaining ties, failures, and matched controls."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RUNS=ROOT/'analysis/demand_trader_runs'


def main():
    source_replay=ROOT/'loss_analysis/kaito_clone_router_55874991_20260905/episode-105165498-replay.json'
    if source_replay.exists():
        (ROOT/'analysis/w13_crop_source_replay.json.gz').write_bytes(gzip.compress(source_replay.read_bytes(),mtime=0))
    archive=ROOT/'analysis/w13_response_raw.json.gz'
    raw=json.loads(gzip.decompress(archive.read_bytes())) if archive.exists() else {}
    for path in sorted(RUNS.glob('*.json')):
        data=json.loads(path.read_text())
        if 'a_sha256' not in data:continue
        if path.name in raw:
            old=raw[path.name]
            if old['a_sha256']!=data['a_sha256'] or old['b_sha256']!=data['b_sha256']:
                raise ValueError('provenance conflict '+path.name)
            if data['rows'][:len(old['rows'])] != old['rows']:
                raise ValueError('result conflict '+path.name)
        raw[path.name]=data
    if not raw:raise ValueError('no results')
    result={}
    for name,data in raw.items():
        rows=data['rows'];done=[r for r in rows if r['status']=='DONE']
        margins=[r['a']-r['b'] for r in done]
        result[name]={'games':len(rows),'seeds':len({r['seed'] for r in rows}),
            'wins':sum(x>0 for x in margins),'losses':sum(x<0 for x in margins),
            'ties':sum(x==0 for x in margins),'failures':len(rows)-len(done),
            'mean_margin':sum(margins)/len(margins) if margins else None,
            'crop_active_games':sum(r.get('a_telemetry',{}).get('planted',0)>0 for r in done),
            'a_sha256':data['a_sha256'],'b_sha256':data['b_sha256']}
        for family in ('kaito','pfall','gronk','soil','suliman','top2'):
            base_name=f'base_{family}_fresh.json'
            if name.endswith(f'_{family}_fresh.json') and name!=base_name and base_name in raw:
                base={(r['seed'],r['order']):r for r in raw[base_name]['rows'] if r['status']=='DONE'}
                paired=[(r,base[r['seed'],r['order']]) for r in done if (r['seed'],r['order']) in base]
                def sign(r):return (r['a']>r['b'])-(r['a']<r['b'])
                result[name]['matched_baseline']={'games':len(paired),
                    'improved_outcomes':sum(sign(a)>sign(b) for a,b in paired),
                    'worsened_outcomes':sum(sign(a)<sign(b) for a,b in paired),
                    'margin_delta':sum((a['a']-a['b'])-(b['a']-b['b']) for a,b in paired)/len(paired) if paired else None}
    packed=gzip.compress(json.dumps(raw,sort_keys=True,separators=(',',':')).encode(),mtime=0)
    archive.write_bytes(packed)
    audit_archive=ROOT/'analysis/w13_response_audits.json.gz'
    audits=json.loads(gzip.decompress(audit_archive.read_bytes())) if audit_archive.exists() else {}
    for path in sorted(RUNS.glob('*.json')):
        if path.name.startswith('feed_audit_') or path.name=='top50_verified_fills.json':
            data=json.loads(path.read_text())
            if path.name in audits and audits[path.name]!=data:
                raise ValueError('audit conflict '+path.name)
            audits[path.name]=data
    audit_archive.write_bytes(gzip.compress(json.dumps(audits,sort_keys=True,separators=(',',':')).encode(),mtime=0))
    summary={'experiments':result,'raw_sha256':hashlib.sha256(packed).hexdigest()}
    (ROOT/'analysis/w13_response_results.json').write_text(json.dumps(summary,indent=2)+'\n')
    for name,r in result.items():
        print(name, f"{r['wins']}-{r['losses']}-{r['ties']}", 'failures',r['failures'],
              'margin',round(r['mean_margin'] or 0,1), 'matched',r.get('matched_baseline'))


if __name__=='__main__':main()
