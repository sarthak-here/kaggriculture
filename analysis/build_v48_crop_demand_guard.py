"""Build a shop-gated late CARROT -> WHEAT response on frozen V48.

The wrapper preserves V48's worker paths, order count, quantities, and timing.
It activates only after all eight shops are known and only when the revealed
shop mix has weak carrot demand but broad wheat demand.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public_candidates/v48_clear_queue_20260918/main.py"
OUTPUT = ROOT / "variants/v48_crop_demand_guard/main.py"
EXPECTED_SOURCE_SHA256 = "4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96"

WRAPPER = r'''

# EXP336: late crop-demand guard derived from V48's first external loss.
# Preserve the route and market shape; substitute wheat only after the complete
# shop sequence proves carrot demand is weak and wheat demand is broad.
_E336_BASE=_e335_agent
_E336_WHEAT_SHOPS={'BAKERY','BRUNCH_SPOT','ICE_CREAM_SHOP','PIZZA_SHOP','FARMERS_MARKET'}
_E336_REPORT=dict(activated=0,steps=0,buy_units=0,plant_requests=0,errors=0)
_E336_ACTIVE={}

def _e336_shops(obs):
    town=_get(obs,'town',{})
    return list(_get(town,'unlocked_shops',[]) or [])

def _e336_gate(obs):
    shops=_e336_shops(obs)
    step=int(_get(obs,'step',0))
    # The day-24/25 carrot block is inventory-closed: the tape has zero carrot
    # seeds before it and returns to zero at step 631. Later wheat would not
    # have enough days to reach its maximum yield, so never convert after 623.
    if step<576 or step>=624 or len(shops)<8:return False
    if 'PET_CAFE' in shops or shops.count('FARMERS_MARKET')>1:return False
    return sum(shop in _E336_WHEAT_SHOPS for shop in shops)>=4

def _e336_convert(obs,action):
    seat=int(_get(obs,'player',0));step=int(_get(obs,'step',0))
    active=_e336_gate(obs)
    if active:_E336_ACTIVE[seat]=True
    if not active:return action
    result=dict(action);changed=False
    market=[]
    for order in result.get('market',[]):
        work=list(order)
        if len(work)>=3 and work[0]=='BUY_SEED' and work[1]=='CARROT':
            work[1]='WHEAT';_E336_REPORT['buy_units']+=max(0,int(work[2]));changed=True
        market.append(work)
    result['market']=market
    workers=[list(result.get('farmer',['PASS']))]+[list(c) for c in result.get('hands',[])]
    for command in workers:
        if len(command)>=2 and command[0]=='PLANT' and command[1]=='CARROT':
            command[1]='WHEAT';_E336_REPORT['plant_requests']+=1;changed=True
    result['farmer'],result['hands']=workers[0],workers[1:]
    if changed:_E336_REPORT['steps']+=1
    return result

def agent(observation,configuration=None):
    action=_E336_BASE(observation,configuration)
    try:
        seat=int(_get(observation,'player',0));step=int(_get(observation,'step',0))
        if step==0:
            _E336_ACTIVE.pop(seat,None)
            for key in _E336_REPORT:_E336_REPORT[key]=0
        was_active=_E336_ACTIVE.get(seat,False)
        result=_e336_convert(observation,action)
        if not was_active and _E336_ACTIVE.get(seat,False):_E336_REPORT['activated']+=1
        agent.telemetry=dict(_E336_REPORT)
        return result
    except Exception as exc:
        _E336_REPORT['errors']+=1
        _E336_REPORT['last_error']=repr(exc)
        agent.telemetry=dict(_E336_REPORT)
        return action

agent.telemetry=_E336_REPORT
agent=globals().pop('agent')
'''


def main() -> None:
    source = SOURCE.read_bytes()
    source_sha256 = hashlib.sha256(source).hexdigest()
    if source_sha256 != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(f"frozen V48 changed: {source_sha256}")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    built = source + WRAPPER.encode("utf-8")
    OUTPUT.write_bytes(built)
    manifest = {
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": source_sha256,
        "output": str(OUTPUT.relative_to(ROOT)),
        "output_sha256": hashlib.sha256(built).hexdigest(),
        "experiment": 336,
        "change": "After all eight shops are known, convert the inventory-closed day-24/25 carrot block to wheat when carrot support is weak and wheat support is broad.",
    }
    (OUTPUT.parent / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
