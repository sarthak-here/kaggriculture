"""Cash-reconciled replay analysis in JSON; no requested orders counted as fills."""
import argparse,hashlib,json
from collections import Counter
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from replays_to_csv import load_replay,observations,reconstruct,farm_stats,PRODUCTS
def audit(job):
    path,label=job
    from kaggle_environments.envs.kaggriculture import kaggriculture as eng
    replay=load_replay(path);steps=replay['steps'];assert len(steps)==720
    totals=Counter();same=0;daily=[]
    for i in range(719):
        before=observations(steps[i]);after=observations(steps[i+1]);actions=[steps[i+1][s]['action'] or {} for s in (0,1)]
        fills,harvests,verified=reconstruct(before,actions,after,replay['configuration'],eng)
        assert all(verified),(label['episode_id'],i)
        totals.update(fills)
        same+=({k:v for k,v in actions[0].items() if k!='market'}=={k:v for k,v in actions[1].items() if k!='market'})
        if i%24==23:daily.append([i,*[after[s]['farms'][s]['money'] for s in (0,1)]])
    a=label['seat'];b=1-a;result=dict(label,worker_agreement=same/719,seed=replay['info']['seed'],verified_transitions=1438,
        shops=steps[-1][0]['observation']['town']['unlocked_shops'],daily_money=daily,
        replay_sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())
    for prefix,s in [('own',a),('opp',b)]:
        result[prefix+'_fills']={':'.join((op,item,metric)):v for (seat,op,item,metric),v in totals.items() if seat==s}
        result[prefix+'_terminal']=farm_stats(observations(steps[-1])[s],s)
    result['same_core_units']=all(totals[a,'SELL',p,'units']==totals[b,'SELL',p,'units'] for p in ('MILK','WOOL','TOMATO','CARROT','MELON','EGG'))
    result['group']='near_clone_timing' if same/719>=.97 and result['same_core_units'] else 'production_or_route'
    result['receipt_gaps']={p:totals[a,'SELL',p,'value']-totals[b,'SELL',p,'value'] for p in PRODUCTS}
    return result
def main():
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args();m=json.loads((a.directory/'manifest.json').read_text(encoding='utf-8'));rows=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for f in as_completed([pool.submit(audit,(str(a.directory/r['path']),r['labels'][0])) for r in m['replays']]):
            row=f.result();rows.append(row);print(row['episode_id'],row['margin'],row['group'],flush=True)
    rows.sort(key=lambda r:r['margin']);(a.directory/'audit.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print('DONE',len(rows),'verified',sum(r['verified_transitions'] for r in rows))
if __name__=='__main__':main()
