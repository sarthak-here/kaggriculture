"""Build a narrow Shawn404 market-schedule branch on corrected prefund V45."""
import argparse,gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA='1a9c3a3ef6902d958d6269421a196aa683492e927f660f566c3029698498bf04'
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-step',type=int,default=151)
    parser.add_argument('--target-step',type=int,default=150)
    parser.add_argument('--quantity',type=int,default=2)
    parser.add_argument('--name',default='v45_shawn_router_v5')
    args=parser.parse_args()
    base=ROOT/'variants/v45_prefund_10_exported/main.py';raw=base.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    replay=json.loads(gzip.decompress((ROOT/'analysis/v45_prefund_exported_live_20260917/replays/episode-110040845-replay.json.gz').read_bytes()))
    markets={step:replay['steps'][step+1][1]['action'].get('market',[]) for step in range(150,719)}
    moved=['SELL','WOOL',args.quantity]
    assert moved in markets[args.source_step]
    assert len(markets[args.target_step]) < 10
    markets[args.target_step]=[list(order) for order in markets[args.target_step]]+[moved]
    markets[args.source_step]=[order for order in markets[args.source_step] if order != moved]
    wrapper=f'''

_SHAWN_PARENT=agent
_SHAWN_MARKETS={markets!r}
_SHAWN_STATE={{}}
_SHAWN_REPORT={{'shawn_checks':0,'shawn_activations':0,'shawn_turns':0,'shawn_errors':0}}
def agent(observation,configuration=None):
    action=_SHAWN_PARENT(observation,configuration)
    try:
        player=int(observation['player']);step=int(observation['step'])
        state=_SHAWN_STATE.get(player)
        if state is None or step<=state['step']:
            state=_SHAWN_STATE[player]={{'step':-1,'cash1':False,'cash2':False,'active':False}}
        state['step']=step
        if step==0:_SHAWN_REPORT.update(shawn_checks=0,shawn_activations=0,shawn_turns=0,shawn_errors=0)
        rival=observation['farms'][1-player]
        if step==1:state['cash1']=int(rival['money'])==2865
        if step==2:state['cash2']=int(rival['money'])==152
        if step==145 and state['cash1'] and state['cash2']:
            _SHAWN_REPORT['shawn_checks']+=1
            shops=tuple(observation['town'].get('unlocked_shops',[])[:2])
            clone=_race_positions_equal(observation['farms'],player)
            if shops==('FARMERS_MARKET','FARMERS_MARKET') and clone:
                state['active']=True;_SHAWN_REPORT['shawn_activations']+=1
        if state['active'] and step in _SHAWN_MARKETS:
            action=dict(action,market=[list(o) for o in _SHAWN_MARKETS[step]])
            _SHAWN_REPORT['shawn_turns']+=1
    except Exception:_SHAWN_REPORT['shawn_errors']+=1
    _SHAWN_REPORT.update(getattr(_SHAWN_PARENT,'telemetry',{{}}))
    return action
agent.telemetry=_SHAWN_REPORT
agent=globals().pop('agent')
'''
    source=raw.decode()+wrapper;compile(source,'main.py','exec')
    out=ROOT/f'variants/{args.name}';out.mkdir(exist_ok=False)
    encoded=source.encode();(out/'main.py').write_bytes(encoded)
    (out/'provenance.json').write_text(json.dumps({'base_sha256':BASE_SHA,'main_sha256':hashlib.sha256(encoded).hexdigest(),'source_episode':110040845,'activation':'opponent cash 2865 at step1, 152 at step2; FM/FM prefix and exact worker positions at step145','market_override_steps':'150-718','timing_probe':f'move {args.quantity} wool from step {args.source_step} to step {args.target_step}'},indent=2)+'\n')
if __name__=='__main__':main()
