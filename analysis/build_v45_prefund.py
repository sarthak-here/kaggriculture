"""Retain five units for feed instead of selling and repurchasing them."""
import argparse,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
WRAPPER='''

_LOCAL_PREFUND_PARENT=agent
_LOCAL_PREFUND_REPORT={'prefund_openings':0,'prefund_held_feed':0}

def _local_prefund_action(obs, action, config=None):
    standard=config is None or all(config.get(k,v)==v for k,v in
        [('boardSize',10),('turnsPerDay',24),('shedCapacity',100),
         ('maxMarketOrdersPerTurn',10),('startingMoney',3000)])
    if not standard:return action
    step=int(obs['step'])
    if step==0 and action.get('market')==[['BUY_PRODUCT','WHEAT',70],['SELL','WHEAT',70]]:
        _LOCAL_PREFUND_REPORT['prefund_openings']+=1
        return dict(action,market=[['BUY_PRODUCT','WHEAT',LOCAL_QUANTITY],['SELL','WHEAT',LOCAL_QUANTITY-5]])
    if step==1 and obs['private']['shed'].get('WHEAT',0)==5:
        orders=action.get('market',[])
        if orders[:2]==[['SELL','WHEAT',13],['BUY_PRODUCT','WHEAT',5]]:
            _LOCAL_PREFUND_REPORT['prefund_held_feed']+=1
            # Keep order indices: removing orders changes simultaneous matching.
            return dict(action,market=[['SELL','WHEAT',0],['BUY_PRODUCT','WHEAT',0]]+orders[2:])
    return action

def agent(observation,configuration=None):
    if int(observation['step'])==0:
        _LOCAL_PREFUND_REPORT.update(prefund_openings=0,prefund_held_feed=0)
    action=_LOCAL_PREFUND_PARENT(observation,configuration)
    result=_local_prefund_action(observation,action,configuration)
    _LOCAL_PREFUND_REPORT.update(getattr(_LOCAL_PREFUND_PARENT,'telemetry',{}))
    return result
agent.telemetry=_LOCAL_PREFUND_REPORT
'''
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--quantity',type=int,required=True)
    args=parser.parse_args();assert 5<=args.quantity<=100
    base=ROOT/'variants/v45_proactive/main.py';raw=base.read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='831dcc2cba277f12947966a38e25f04fb7854c3116f9669a04c0d00cf611b87f'
    source=raw.decode()+WRAPPER.replace('LOCAL_QUANTITY',str(args.quantity))
    compile(source,'main.py','exec');out=ROOT/f'variants/v45_prefund_{args.quantity}'
    out.mkdir(exist_ok=False);(out/'main.py').write_bytes(source.encode())
    (out/'provenance.json').write_text(json.dumps({'base_sha256':hashlib.sha256(raw).hexdigest(),'main_sha256':hashlib.sha256(source.encode()).hexdigest(),'quantity':args.quantity,'feed_retained':5},indent=2))
if __name__=='__main__':main()
