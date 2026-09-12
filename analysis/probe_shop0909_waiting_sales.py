"""Mechanism-only probe on original observations; not a full-game counterfactual."""
import json,gzip
from pathlib import Path
from replays_to_csv import observations
ROOT=Path(__file__).resolve().parents[1]
def load(folder):
    path=ROOT/folder/'main.py';n={'__file__':str(path),'__name__':'probe'}
    exec(compile(path.read_text(),str(path),'exec'),n);return n['Policy'](path.parent)
def main():
    root=ROOT/'analysis/shop0909_all_losses_20260911'
    r=json.loads(gzip.decompress((root/'replays/episode-107749417-replay.json.gz').read_bytes()))
    base=load('variants/shop0909_opening_net');candidate=load('variants/shop0909_waiting_h3')
    rows=[]
    for i,record in enumerate(r['steps'][:-1]):
        obs=observations(record)[1];a=base.act(obs);b=candidate.act(obs)
        assert {k:v for k,v in a.items() if k!='market'}=={k:v for k,v in b.items() if k!='market'}
        if a['market']!=b['market']:rows.append(dict(step=i,before=a['market'],after=b['market']))
    result=dict(episode_id=107749417,seat=1,worker_changes=0,changed_steps=len(rows),events=rows)
    (ROOT/'analysis/shop0909_waiting_mechanism_20260912.json').write_text(json.dumps(result,indent=2)+'\n')
    print('changed steps',len(rows));print(json.dumps(rows[:5],indent=2))
if __name__=='__main__':main()
