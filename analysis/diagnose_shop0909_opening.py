"""Saved-observation opening audit; one-turn counterfactuals are not full games."""
from collections import Counter
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import requests
from replays_to_csv import load_replay,observations,reconstruct

ROOT=Path(__file__).resolve().parent/'shop0909_live_56159253'

def main():
    from kaggle_environments.envs.kaggriculture import kaggriculture as engine
    cases=[]
    for ep,seat in [(107774237,0),(107764291,1)]:
        path=ROOT/f'episode-{ep}-replay.json';d=load_replay(path)
        before=observations(d['steps'][0]);after=observations(d['steps'][1]);acts=[r['action'] for r in d['steps'][1]]
        original,_,verified=reconstruct(before,acts,after,d['configuration'],engine)
        assert all(verified)
        net=json.loads(json.dumps(acts));net[seat]['market']=[['BUY_PRODUCT','WHEAT',13]]
        alternative,_,_=reconstruct(before,net,after,d['configuration'],engine)
        def cash(fills,s):return before[s]['farms'][s]['money']+sum(v*(1 if op=='SELL' else -1) for (p,op,item,metric),v in fills.items() if p==s and metric=='value')
        def wheat(fills,s):return fills[s,'BUY_PRODUCT','WHEAT','units']-fills[s,'SELL','WHEAT','units']
        checkpoints=[]
        for i in (0,1,2,23,24,25,48,72,144,719):
            obs=observations(d['steps'][i])[seat];f=obs['farms'][seat]
            herd=Counter(t['animal'] for row in f['tiles'] for t in row if isinstance(t,dict) and t.get('animal'))
            checkpoints.append({'step':i,'money':f['money'],'hands':len(f['hands']),'quadrants':len(f['unlocked_quadrants']),'herd':dict(herd)})
        cases.append({'episode_id':ep,'seat':seat,'replay_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'original_step0_orders':acts[seat]['market'],'counterfactual_step0_orders':net[seat]['market'],
            'original_step1_money':cash(original,seat),'counterfactual_step1_money':cash(alternative,seat),
            'one_turn_cash_gain':cash(alternative,seat)-cash(original,seat),
            'original_net_wheat_units':wheat(original,seat),'counterfactual_net_wheat_units':wheat(alternative,seat),
            'checkpoints':checkpoints,'full_game_counterfactual_tested':False})
        # Preserve the source, without deleting the downloaded raw replay.
        (ROOT/f'episode-{ep}-replay.json.gz').write_bytes(gzip.compress(path.read_bytes(),mtime=0))
    result={'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),'cases':cases,
            'engine_sha256':hashlib.sha256(Path(engine.__file__).read_bytes()).hexdigest()}
    (ROOT/'opening_diagnosis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
    r=requests.post('https://www.kaggle.com/api/i/competitions.EpisodeService/ListEpisodes',json={'submissionId':56159253},timeout=60);r.raise_for_status()
    (ROOT/'episode_service_snapshot.json').write_text(json.dumps(r.json(),ensure_ascii=False),encoding='utf-8')

if __name__=='__main__':main()
