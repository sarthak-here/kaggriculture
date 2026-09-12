"""Audit step-zero purchase replacement across the frozen 29-replay cohort."""
import json,gzip,hashlib
from pathlib import Path
from replays_to_csv import load_replay,observations,reconstruct
ROOT=Path(__file__).resolve().parents[1]
def main():
    from kaggle_environments.envs.kaggriculture import kaggriculture as eng
    corpus=ROOT/'analysis/shop0909_all_losses_20260911'
    manifest=json.loads((corpus/'manifest.json').read_text(encoding='utf-8'));rows=[]
    for entry in manifest['replays']:
        label=entry['labels'][0];s=label['seat'];d=load_replay(corpus/entry['path'])
        before=observations(d['steps'][0]);after=observations(d['steps'][1])
        acts=[r.get('action') or {} for r in d['steps'][1]]
        assert acts[s]['market']==[['BUY_PRODUCT','WHEAT',13],['SELL','WHEAT',13],['BUY_PRODUCT','WHEAT',13]]
        original,_,verified=reconstruct(before,acts,after,d['configuration'],eng);assert all(verified)
        altered=json.loads(json.dumps(acts));altered[s]['market']=[['BUY_PRODUCT','WHEAT',13]]
        changed,_,_=reconstruct(before,altered,after,d['configuration'],eng)
        def cash(f):return before[s]['farms'][s]['money']+sum(v*(1 if op=='SELL' else -1) for (p,op,item,metric),v in f.items() if p==s and metric=='value')
        def wheat(f):return f[s,'BUY_PRODUCT','WHEAT','units']-f[s,'SELL','WHEAT','units']
        assert wheat(original)==wheat(changed)==13
        rows.append(dict(episode_id=label['episode_id'],seat=s,cohort=label['cohort'],opponent=label['opponent'],
            original_cash=cash(original),candidate_cash=cash(changed),gain=cash(changed)-cash(original),net_wheat=13))
    out=ROOT/'analysis/shop0909_opening_diagnostics_20260912/one_turn.json'
    out.write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('cash gain range',min(r['gain'] for r in rows),max(r['gain'] for r in rows),'improved',sum(r['gain']>0 for r in rows),'worse',sum(r['gain']<0 for r in rows))
if __name__=='__main__':main()
