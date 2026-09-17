"""Exact-engine opening cash frontier; no replay outcomes used for selection.

Enumerates buy/sell round trips against distinct observed two-turn openings.
This is a diagnostic, not a full-game win-rate benchmark.
"""
import argparse
import copy
import gzip
import importlib.metadata
import json
from pathlib import Path
from kaggle_environments import make

ROOT = Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--prefund-feed',action='store_true')
    args=parser.parse_args()
    assert importlib.metadata.version('kaggle-environments') == '1.32.7'
    corpus = ROOT/'analysis/v45_live_20260916'
    manifest = json.loads((corpus/'manifest.json').read_text(encoding='utf-8'))
    openings = {}
    ours = None
    for entry in manifest['replays']:
        label = next((x for x in entry['labels'] if x['submission'] == 56278443 and not x['self_play']), None)
        if label is None:
            continue
        replay = json.loads(gzip.decompress((corpus/entry['path']).read_bytes()))
        seat = label['seat']
        rival = [x[1-seat]['action'] for x in replay['steps'][1:3]]
        key = json.dumps(rival, sort_keys=True)
        openings.setdefault(key, {'actions': rival, 'examples': []})['examples'].append(label['episode_id'])
        own = [x[seat]['action'] for x in replay['steps'][1:3]]
        if ours is None:
            ours = own
        assert own == ours, 'Different own opening requires a separate stratum'
    rows = []
    quantities=range(5,101,5) if args.prefund_feed else range(0,101)
    for quantity in quantities:
        cash = []
        for case in openings.values():
            for seat in (0, 1):
                env = make('kaggriculture', configuration={'seed': 39170000}, debug=False)
                env.reset(2)
                for step in range(2):
                    own = copy.deepcopy(ours[step])
                    if step == 0:
                        own['market'] = [['BUY_PRODUCT','WHEAT',quantity],['SELL','WHEAT',quantity-(5 if args.prefund_feed else 0)]]
                    elif args.prefund_feed:
                        assert own['market'][:2]==[['SELL','WHEAT',13],['BUY_PRODUCT','WHEAT',5]]
                        own['market'][:2]=[['SELL','WHEAT',0],['BUY_PRODUCT','WHEAT',0]]
                    actions = [own, case['actions'][step]] if seat == 0 else [case['actions'][step], own]
                    env.step(actions)
                farm = env.state[0].observation.farms[seat]
                cash.append({'episode':case['examples'][0], 'seat':seat, 'money':farm['money'],
                             'wheat':env.state[seat].observation.private.shed['WHEAT'], 'hands':len(farm['hands'])})
        rows.append({'quantity':quantity,'minimum_cash':min(x['money'] for x in cash),
                     'mean_cash':sum(x['money'] for x in cash)/len(cash), 'cases':cash})
        if quantity % 10 == 0:
            print(quantity, rows[-1]['minimum_cash'], flush=True)
    out = ROOT/('analysis/v45_prefund_frontier_20260917.json' if args.prefund_feed else 'analysis/v45_opening_frontier_20260917.json')
    with out.open('x', encoding='utf-8') as f:
        json.dump({'openings':list(openings.values()), 'rows':rows}, f)
    feasible=[r for r in rows if all(c['wheat']==5 and c['hands']==5 for c in r['cases'])]
    print('BEST FEASIBLE MINIMUM', [(r['quantity'],r['minimum_cash'],r['mean_cash']) for r in sorted(feasible,key=lambda r:(r['minimum_cash'],r['mean_cash']),reverse=True)[:10]])

if __name__ == '__main__':
    main()
