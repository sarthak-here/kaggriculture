"""Verify and summarize the completed waiting-stock panel without replaying games."""
import gzip,hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'analysis/shop0909_waiting_panel_20260912'
    p=json.loads((out/'protocol.json').read_text());raw=json.loads(gzip.decompress((out/'raw_results.json.gz').read_bytes()))
    expected={(s,o) for s in range(p['seed'],p['seed']+p['pairs']) for o in (0,1)}
    assert len(raw)==9
    for path,digest in p['hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    counts={};fills={};comparisons={};losses=[]
    for job,data in raw.items():
        rows=data['rows'];assert len(rows)==20 and {(r['seed'],r['order']) for r in rows}==expected
        assert all(r['status']=='DONE' for r in rows)
        counts[job]={'wins':sum(r['a']>r['b'] for r in rows),'losses':sum(r['a']<r['b'] for r in rows),
            'ties':sum(r['a']==r['b'] for r in rows),'failures':0}
        fills[job]={side:{k:sum(r[side+'_fills'].get(k,0) for r in rows)/20 for k in sorted({k for r in rows for k in r[side+'_fills']})} for side in ('a','b')}
    def sign(v):return (v>0)-(v<0)
    for family in ('kaito','pf_all','suliman_fixed','top2_fixed'):
        c={(r['seed'],r['order']):r for r in raw['candidate_'+family]['rows']}
        b={(r['seed'],r['order']):r for r in raw['base_'+family]['rows']}
        comparisons[family]=dict(outcome_flips=sum(sign(c[k]['a']-c[k]['b'])!=sign(b[k]['a']-b[k]['b']) for k in c),
            own_filled_unit_changes=sum(any(c[k]['a_fills'].get(f,0)!=b[k]['a_fills'].get(f,0) for f in set(c[k]['a_fills'])|set(b[k]['a_fills']) if f.endswith(':units')) for k in c),
            own_worker_changes=sum(c[k]['a_workers_sha256']!=b[k]['a_workers_sha256'] for k in c),
            opponent_worker_changes=sum(c[k]['b_workers_sha256']!=b[k]['b_workers_sha256'] for k in c),
            changed_shops=sum(c[k]['shops']!=b[k]['shops'] for k in c),
            mean_margin_delta=sum(c[k]['a']-c[k]['b']-b[k]['a']+b[k]['b'] for k in c)/20)
        for k,r in c.items():
            if r['a']<r['b']:losses.append(dict(family=family,seed=k[0],seat=k[1],candidate_margin=r['a']-r['b'],
                base_margin=b[k]['a']-b[k]['b'],own_fills=r['a_fills'],opponent_fills=r['b_fills']))
    direct=raw['direct']['rows'];margins=[r['a']-r['b'] for r in direct]
    audit=dict(games=180,counts=counts,comparisons=comparisons,mean_fills=fills,retained_losses=losses,
        direct=dict(mean_margin=sum(margins)/20,min_margin=min(margins),max_margin=max(margins),
            same_workers=sum(r['a_workers_sha256']==r['b_workers_sha256'] for r in direct)))
    (out/'audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    folder=ROOT/'variants/shop0909_waiting_h3'
    archive=out/'candidate.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name in ('main.py','actions.json','LICENSE.txt'):
            info=zipfile.ZipInfo(name,(2026,9,13,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,(folder/name).read_bytes())
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    (out/'candidate_manifest.json').write_text(json.dumps(dict(sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),submitted=False,
        source_sha256=p['hashes']['variants/shop0909_waiting_h3/main.py']),indent=2)+'\n')
    print(json.dumps({k:v for k,v in audit.items() if k not in ('mean_fills','retained_losses')},indent=2))
    print('LOSSES',json.dumps([{k:v for k,v in r.items() if 'fills' not in k} for r in losses]))
    for family in comparisons:
        x=fills['candidate_'+family]['a'];y=fills['base_'+family]['a']
        print(family,'changed mean filled units',{k:x.get(k,0)-y.get(k,0) for k in set(x)|set(y) if k.endswith(':units') and x.get(k,0)!=y.get(k,0)})
    print('DIRECT MILK WOOL STRAWBERRY fills')
    for side in ('a','b'):
        print(side,{k:v for k,v in fills['direct'][side].items() if k.startswith(('SELL:MILK:','SELL:WOOL:','SELL:STRAWBERRY:'))})
if __name__=='__main__':main()
