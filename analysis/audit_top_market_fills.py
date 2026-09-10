"""Replay each observed actor/market transition; verify cash before counting fills.

Never runs opponent code. Both seats' saved private states are historical audit
data only, never inputs to a deployed policy. No RNG or inferred seed is needed.
"""
import argparse
from collections import Counter, defaultdict
import copy
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit(entry):
    from kaggle_environments.envs.kaggriculture import kaggriculture as eng
    from kaggle_environments.utils import structify
    path = ROOT/'replays_top'/f"episode-{entry['episode_id']}-replay.json.gz"
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        replay = json.load(f)
    cfg = replay['configuration']
    fills = [Counter(), Counter()]
    mismatches = []
    requests = Counter()
    original = eng._commit_unit
    farm_ids = {}
    def commit(op, item, price, farm, private, market, shed_capacity=100):
        ok = original(op, item, price, farm, private, market, shed_capacity)
        if ok:
            target = fills[farm_ids[id(farm)]]
            target[f'{op}:{item}:units'] += 1
            target[f'{op}:{item}:value'] += price
        return ok
    eng._commit_unit = commit
    try:
        for index in range(len(replay['steps'])-1):
            before = replay['steps'][index]
            after = replay['steps'][index+1]
            state = structify([{'observation': copy.deepcopy(before[s]['observation']),
                                'action': after[s]['action']} for s in (0, 1)])
            obs = state[0].observation
            state[1].observation.farms = obs.farms
            state[1].observation.market = obs.market
            farm_ids = {id(farm): s for s, farm in enumerate(obs.farms)}
            step = int(obs.get('step', index))
            for s in (0, 1):
                action = state[s].action or {}
                units = [action.get('farmer', ['PASS']), *(action.get('hands') or [])]
                private = state[s].observation.private
                plants = Counter(a[1] for a in units if a and len(a)>1 and a[0]=='PLANT')
                blocked = {c for c,n in plants.items() if n>private.get('seeds',{}).get(c,0)}
                for unit, act in enumerate(units):
                    if act and len(act)>1 and act[0]=='PLANT' and act[1] in blocked:
                        act = ['PASS']
                    eng._apply_unit_action(obs.farms[s], private, unit, act,
                                           cfg['boardSize'], step//cfg['turnsPerDay'],
                                           cfg['turnsPerDay'], cfg['shedCapacity'])
            for order in (state[int(entry['seat'])].action or {}).get('market', []):
                if len(order)>=3 and order[0]=='BUY_PRODUCT':
                    requests[order[1]] += max(0, int(order[2]))
            eng._process_market(state, structify({'configuration': cfg}))
            for s in (0,1):
                expected = after[0]['observation']['farms'][s]['money']
                actual = obs.farms[s]['money']
                if abs(expected-actual)>0.001:
                    mismatches.append({'step': step, 'seat': s, 'expected': expected, 'actual': actual})
        return {'episode': entry['episode_id'], 'team': entry['team_name'],
                'seat': entry['seat'], 'transitions': len(replay['steps'])-1,
                'cash_mismatches': mismatches,
                'requested_buy_products': dict(requests),
                'successful_fills': dict(fills[int(entry['seat'])]),
                'replay_sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    finally:
        eng._commit_unit = original


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=50)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    entries = json.loads((ROOT/'replays_top/manifest.json').read_text())[:args.limit]
    rows = []
    for entry in entries:
        row = audit(entry)
        rows.append(row)
        print(json.dumps({k:row[k] for k in ('episode','team','transitions')})+
              f" cash_mismatches={len(row['cash_mismatches'])}", flush=True)
    from kaggle_environments.envs.kaggriculture import kaggriculture as eng
    result = {'rows': rows, 'engine_sha256': hashlib.sha256(Path(eng.__file__).read_bytes()).hexdigest(),
              'valid': all(not row['cash_mismatches'] for row in rows)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    if not result['valid']:
        raise SystemExit('Cash transitions did not reproduce; do not trust fill totals.')


if __name__=='__main__':
    main()
