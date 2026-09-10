"""Price-gated three-day carrot cycles with explicit replacement wheat."""
import argparse
import gzip
import json
from pathlib import Path
from build_w13_zero_replay import assignment, decode

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = '''
from v23.state_encoder import get as _cr_get
from v23.simulator import market_price as _cr_price
class _CropResponse:
    def __init__(self, base, cycles):
        self.base, self.cycles = base, cycles
        self.pending = {}
        self.converted = set()
        self.feed_debt = 0
        self.delay_telemetry = dict(selected=0, planted=0, harvested=0, replacement_wheat=0)
    def __call__(self, obs, configuration=None):
        step = int(_cr_get(obs, 'step', 0))
        if step == 0:
            self.pending.clear(); self.converted.clear(); self.feed_debt = 0
        a = self.base(obs, configuration)
        a = dict(a, farmer=list(a['farmer']), hands=[list(x) for x in a['hands']], market=[list(x) for x in a['market']])
        seat = int(_cr_get(obs, 'player', 0)); farm = _cr_get(obs, 'farms', [])[seat]
        private = _cr_get(obs, 'private', {}); shed = _cr_get(private, 'shed', {})
        positions = [_cr_get(farm, 'farmer', [0,0]), *_cr_get(farm, 'hands', [])]
        units = [a['farmer'], *a['hands']]; tiles = _cr_get(farm, 'tiles', [])
        slots = int(_cr_get(configuration, 'maxMarketOrdersPerTurn', 10))
        # Harvest replacement feed is funded from existing cash; crops still follow
        # the original return schedule. It is additional to the base's own buys.
        for u, act in enumerate(units):
            if u >= len(positions): continue
            x,y = positions[u]; tile = tiles[y][x]
            if act == ['HARVEST'] and (x,y) in self.converted and isinstance(tile,dict) and tile.get('crop')=='CARROT':
                self.feed_debt += 3
                self.converted.remove((x,y))
                self.delay_telemetry['harvested'] += 1
        seeds = int(_cr_get(_cr_get(private,'seeds',{}),'CARROT',0))
        baseline_need = sum(act == ['PLANT','CARROT'] for act in units)
        for u,x,y in self.pending.pop(step, []):
            if (u < len(units) and positions[u] == [x,y] and tiles[y][x] is None
                    and units[u] == ['PLANT','WHEAT'] and seeds > baseline_need):
                units[u][1] = 'CARROT'; seeds -= 1
                self.converted.add((x,y)); self.delay_telemetry['planted'] += 1
        if len(a['market']) < slots and int(_cr_get(shed,'CARROT',0)) > 0:
            a['market'].append(['SELL','CARROT',int(_cr_get(shed,'CARROT',0))])
        if self.feed_debt and len(a['market']) < slots:
            a['market'].append(['BUY_PRODUCT','WHEAT',self.feed_debt])
            self.delay_telemetry['replacement_wheat'] += self.feed_debt
            self.feed_debt = 0
        upcoming = self.cycles.get(str(step+1), [])
        if upcoming and len(a['market']) < slots and float(_cr_get(farm,'money',0)) >= 5000:
            inv = _cr_get(_cr_get(obs,'market',{}),'inventory',{})
            carrot = _cr_price('CARROT',int(_cr_get(inv,'CARROT',10000))+30)
            wheat = _cr_price('WHEAT',int(_cr_get(inv,'WHEAT',10000))-30)
            # Assume only three carrots, charge three replacement feed units plus
            # the entire extra seed cost. Demand growth is not credited.
            if 3*(carrot-wheat)-20 >= 80:
                a['market'].append(['BUY_SEED','CARROT',len(upcoming)])
                self.pending[step+1] = upcoming
                self.delay_telemetry['selected'] += len(upcoming)
        return a
_V44_POLICY = _CropResponse(_V44_POLICY, CYCLES_VALUE)
'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=ROOT/'variants/w13_zero_replay/main.py')
    parser.add_argument('--output', type=Path, default=ROOT/'variants/w13_crop_response/main.py')
    args = parser.parse_args()
    source = args.source.read_text()
    routes = decode(assignment(source, '_V44_ROUTES'))
    assert all(v == routes['default'] for v in routes.values())
    replay_path = ROOT/'loss_analysis/kaito_clone_router_55874991_20260905/episode-105165498-replay.json'
    if replay_path.exists():
        replay = json.loads(replay_path.read_text())
    else:
        replay = json.loads(gzip.decompress((ROOT/'analysis/w13_crop_source_replay.json.gz').read_bytes()))
    active, cycles = {}, {}
    for step in range(len(replay['steps'])-1):
        farm = replay['steps'][step][0]['observation']['farms'][1]
        after = replay['steps'][step+1][0]['observation']['farms'][1]
        a = replay['steps'][step+1][1].get('action') or {}
        pos = [farm['farmer'], *farm['hands']]
        for u,act in enumerate([a.get('farmer',[]), *a.get('hands',[])]):
            if u>=len(pos): continue
            x,y = pos[u]; tile = farm['tiles'][y][x]; new = after['tiles'][y][x]
            if act==['PLANT','WHEAT'] and isinstance(new,dict) and new.get('crop')=='WHEAT':
                active[x,y] = (step,u)
            if act==['HARVEST'] and isinstance(tile,dict) and tile.get('crop')=='WHEAT' and (x,y) in active:
                p,pu = active.pop((x,y))
                if p>=300 and step//24-p//24==3:
                    cycles.setdefault(str(p),[]).append([pu,x,y])
    marker = '\ndef agent(obs, configuration=None):'
    assert source.count(marker)==1
    candidate = source.replace(marker,'\n'+WRAPPER.replace('CYCLES_VALUE',repr(cycles))+marker)
    target = args.output
    if target.exists(): raise FileExistsError(target)
    compile(candidate,str(target),'exec')
    target.parent.mkdir(parents=True,exist_ok=True);target.write_text(candidate)
    print('eligible_cycles',sum(map(len,cycles.values())), 'path',target)

if __name__=='__main__': main()
