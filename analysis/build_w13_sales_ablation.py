"""Statically audit W13 payloads and build reproducible market-only ablations.

Never executes the source while decoding. Outputs retain the base's bundled
modules, config and worker schedules. Run from any directory.
"""
from __future__ import annotations
import ast
import base64
import collections
import copy
import hashlib
import importlib.metadata
import json
from pathlib import Path
import zlib

ROOT = Path(__file__).resolve().parents[1]

def decode(source, name):
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == name for t in n.targets))
    payload = max((x.value for x in ast.walk(node.value)
                   if isinstance(x, ast.Constant) and isinstance(x.value, str)), key=len)
    return node, json.loads(zlib.decompress(base64.b85decode(payload)))

def encode(name, value):
    payload = base64.b85encode(zlib.compress(json.dumps(value, separators=(',', ':')).encode(), 9)).decode()
    return f'{name} = json.loads(zlib.decompress(base64.b85decode({payload!r})).decode())\n'

def replace_assignment(source, node, value):
    lines = source.splitlines(keepends=True)
    lines[node.lineno-1:node.end_lineno] = [value]
    return ''.join(lines)

def main():
    base = (ROOT/'variants/panel_wheat13/main.py').read_text()
    phase = (ROOT/'variants/wheat13_market_phase/main.py').read_text()
    node, routes = decode(base, '_V44_ROUTES')
    _, other = decode(phase, '_V44_ROUTES')
    _, modules = decode(base, '_V44_MODULES')
    assert modules == decode(phase, '_V44_MODULES')[1]
    config = lambda src: next(ast.dump(n.value) for n in ast.parse(src).body
                              if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id=='_V44_CONFIG' for t in n.targets))
    assert config(base) == config(phase)
    audit = {'base_sha256': hashlib.sha256(base.encode()).hexdigest(), 'slots': {}, 'variants': {}}
    for name, route in routes.items():
        added = collections.Counter()
        changed = []
        assert len(route) == len(other[name]) == 719
        for step, (a,b) in enumerate(zip(route, other[name])):
            assert {k:v for k,v in a.items() if k!='market'} == {k:v for k,v in b.items() if k!='market'}
            aa, bb = collections.Counter(map(tuple,a['market'])), collections.Counter(map(tuple,b['market']))
            assert not aa-bb, 'Candidate removes/replaces baseline orders'
            if a != b: changed.append(step)
            for order,count in (bb-aa).items():
                assert order[0] == 'SELL'
                added[order[1]] += order[2]*count
        audit['slots'][name] = {'changed_steps': changed, 'added_requested_units': dict(added), 'worker_changes':0}
    groups = {'strawberry':{'STRAWBERRY'}, 'fertilizer':{'FERTILIZER'},
              'milk_wool':{'MILK','WOOL'}, 'non_strawberry':{'FERTILIZER','MILK','WOOL'}}
    for label, items in groups.items():
        new = copy.deepcopy(routes)
        for name, route in new.items():
            for step, action in enumerate(route):
                remaining = collections.Counter(map(tuple, routes[name][step]['market']))
                selected = []
                for row in other[name][step]['market']:
                    key = tuple(row)
                    if remaining[key]:
                        selected.append(copy.deepcopy(row)); remaining[key]-=1
                    elif row[0]=='SELL' and row[1] in items:
                        selected.append(copy.deepcopy(row))
                action['market'] = selected
        target = ROOT/f'variants/w13_add_{label}/main.py'
        source = replace_assignment(base, node, encode('_V44_ROUTES',new))
        compile(source,str(target),'exec');target.parent.mkdir(parents=True,exist_ok=True);target.write_text(source)
        audit['variants'][label] = {'path':str(target.relative_to(ROOT)), 'sha256':hashlib.sha256(source.encode()).hexdigest()}
    # Factorial control: preemption on/off in both base and reconstructed phase.
    for label, source in [('base',base),('phase',phase)]:
        needle = '_V44_POLICY = _v44_build(_V44_ROUTES, _V44_CONFIG)'
        replacement = ('from dataclasses import replace as _w13_replace\n'
                       '_V44_CONFIG = _w13_replace(_V44_CONFIG, clone_preempt_horizon=0, clone_phase_horizon=0)\n'+needle)
        assert source.count(needle)==1
        target=ROOT/f'variants/w13_{label}_no_preempt/main.py'
        target.parent.mkdir(parents=True,exist_ok=True);target.write_text(source.replace(needle,replacement))
    distribution=importlib.metadata.distribution('kaggle-environments')
    assert distribution.version=='1.32.7', 'Use the pinned competition engine'
    engine_source=distribution.locate_file('kaggle_environments/envs/kaggriculture/kaggriculture.py').read_text()
    shop_node=next(n for n in ast.parse(engine_source).body if isinstance(n,ast.Assign)
                   and any(isinstance(t,ast.Name) and t.id=='SHOPS' for t in n.targets))
    shops=ast.literal_eval(shop_node.value)
    wrapper=(ROOT/'analysis/w13_sales_delay.py').read_text()
    wrapper=wrapper[wrapper.index('import copy'):]
    for label, gate in [('guarded',True),('quiet',False)]:
        injected=('\n'+wrapper+'\nfrom scripts.v22_market_impact import market_price as _w13_price\n'
                  +f'_V44_POLICY = wrap_sales_delay(_V44_POLICY, _V44_ROUTES, _w13_price, {shops!r}, require_recovery={gate!r})\n')
        target=ROOT/f'variants/w13_delay_{label}/main.py'
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(base.replace('\ndef agent(obs, configuration=None):',injected+'\ndef agent(obs, configuration=None):'))
        compile(target.read_text(),str(target),'exec')
    (ROOT/'analysis/w13_sales_static_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2))

if __name__=='__main__': main()
