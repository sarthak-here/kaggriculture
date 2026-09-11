"""Validate archived panel identities and derive reproducible concise evidence."""
import argparse
import ast
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import zipfile

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,default=Path(__file__).resolve().parent/'shop0909_panel');args=ap.parse_args();root=args.directory
    protocol=json.loads((root/'protocol.json').read_text());raw=json.loads(gzip.decompress((root/'raw_results.json.gz').read_bytes()))
    repo=Path(__file__).resolve().parents[1]
    for path,digest in protocol['hashes'].items():assert hashlib.sha256((repo/path).read_bytes()).hexdigest()==digest,path
    tree=ast.parse((repo/'public_candidates/shop0909_20260910/main.py').read_text())
    shop_map=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SHOP_PLANS' for t in n.targets))
    keys={(s,o) for s in range(protocol['seed_start'],protocol['seed_start']+protocol['pairs']) for o in (0,1)}
    details={}
    for name,a,b in protocol['jobs']:
        result=raw[name];rows=result['rows']
        assert result['a_sha256']==protocol['hashes'][a] and result['b_sha256']==protocol['hashes'][b]
        assert len(rows)==len(keys) and {(r['seed'],r['order']) for r in rows}==keys
        assert all(r['status']=='DONE' for r in rows)
        margins=[r['a']-r['b'] for r in rows]
        details[name]={'wins':sum(m>0 for m in margins),'losses':sum(m<0 for m in margins),'ties':sum(m==0 for m in margins),'failures':0,
            'win_fraction_total':sum(m>0 for m in margins)/len(rows),'mean_margin':sum(margins)/len(rows),'worst_margin':min(margins),
            'loss_cases':[{k:r[k] for k in ('seed','order','a','b','shops')} for r in rows if r['a']<r['b']],
            'shop0909_route_counts':dict(Counter(str(shop_map.get(tuple(r['shops'][:2]),0)) for r in rows)) if name=='direct' or name.startswith('shop_') else None,
            'mean_sales':{side:{p:sum(r[side+'_fills'].get('SELL:'+p+':units',0) for r in rows)/len(rows) for p in ('CARROT','EGG','MILK','WOOL','STRAWBERRY')} for side in ('a','b')}}
    final={'source_protocol_sha256':hashlib.sha256((root/'protocol.json').read_bytes()).hexdigest(),'details':details}
    package=root/'agent.zip'
    if package.exists():raise FileExistsError(package)
    with zipfile.ZipFile(package,'w') as z:
        for name in ('main.py','actions.json','LICENSE.txt'):
            info=zipfile.ZipInfo(name,date_time=(2026,9,10,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,(repo/'public_candidates/shop0909_20260910'/name).read_bytes())
    with zipfile.ZipFile(package) as z:
        assert z.testzip() is None and sorted(z.namelist())==['LICENSE.txt','actions.json','main.py']
        for name in ('main.py','actions.json'):
            assert hashlib.sha256(z.read(name)).hexdigest()==protocol['hashes']['public_candidates/shop0909_20260910/'+name]
    final['package_sha256']=hashlib.sha256(package.read_bytes()).hexdigest()
    (root/'validated_details.json').write_text(json.dumps(final,indent=2)+'\n')
    print(json.dumps(final,indent=2))

if __name__=='__main__':main()
