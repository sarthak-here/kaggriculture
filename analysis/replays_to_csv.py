"""Export JSON/JSON.gz Kaggriculture replays to relational, audited CSV tables.

Action at replay record i+1 executes against observation i. Opponent code is
never loaded. Optional engine reconstruction labels fills with cash agreement.
"""
import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
import copy
import csv
import gzip
import hashlib
import json
from pathlib import Path
import traceback

PRODUCTS=('WHEAT','CARROT','TOMATO','STRAWBERRY','MELON','EGG','MILK','WOOL','FERTILIZER')
ANIMALS=('COW','SHEEP','GOOSE')
TABLES=('episodes','turns','actions','orders','fills','days')


def load_replay(path):
    data=Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if data[:2]==b'\x1f\x8b' else data)


def safe_cell(value):
    # Names and user-supplied text must not become executable Excel formulas.
    if isinstance(value,str) and value.lstrip().startswith(('=','+','-','@')):
        return "'"+value
    return value


def write_table(path, rows):
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        for row in rows:writer.writerow({k:safe_cell(v) for k,v in row.items()})


def farm_stats(obs,seat):
    farm=obs['farms'][seat];private=obs.get('private')
    tiles=[t for row in farm['tiles'] for t in row if isinstance(t,dict)]
    crops=Counter(t['crop'] for t in tiles if t.get('kind')=='PLANT' and t.get('crop'))
    animals=Counter(t['animal'] for t in tiles if t.get('animal'))
    result=dict(money=farm['money'],hands=len(farm.get('hands',[])),
                quadrants=len(farm.get('unlocked_quadrants',[])),
                weeds=sum(t.get('kind')=='WEED' for t in tiles),
                crop_yield_on_tiles=sum(t.get('yield_units',0) for t in tiles if t.get('kind')=='PLANT'),
                unfed_animals=sum(not t.get('fed_today',False) for t in tiles if t.get('animal')),
                private_available=isinstance(private,dict))
    for item in PRODUCTS:
        result['plants_'+item]=crops[item]
        result['shed_'+item]=private.get('shed',{}).get(item,0) if isinstance(private,dict) else None
        result['carried_'+item]=sum(i.get(item,0) for i in private.get('inventories',[])) if isinstance(private,dict) else None
    for item in ANIMALS:result[item.lower()]=animals[item]
    return result


def observations(record):
    shared=record[0].get('observation',{})
    result=[]
    for seat in (0,1):
        obs=dict(record[seat].get('observation') or {})
        for key in ('farms','market','town','step'):
            if key not in obs and key in shared:obs[key]=shared[key]
        result.append(obs)
    return result


def reconstruct(before, actions, after, cfg, eng):
    from kaggle_environments.utils import structify
    state=structify([dict(observation=copy.deepcopy(before[s]),action=actions[s]) for s in (0,1)])
    obs=state[0].observation
    state[1].observation.farms=obs.farms;state[1].observation.market=obs.market
    ids={id(f):s for s,f in enumerate(obs.farms)}
    fills=Counter(); harvests={}; original=eng._commit_unit
    original_hire=eng._do_hire;original_land=eng._do_buy_land
    def atomic(operation,fn,farm,*args):
        cash=farm['money'];result=fn(farm,*args);cost=cash-farm['money']
        if cost>0:
            fills[ids[id(farm)],operation,'', 'units']+=1
            fills[ids[id(farm)],operation,'', 'value']+=cost
        return result
    def commit(op,item,price,farm,private,market,shed_capacity=100):
        ok=original(op,item,price,farm,private,market,shed_capacity)
        if ok:
            fills[ids[id(farm)],op,item,'units']+=1
            fills[ids[id(farm)],op,item,'value']+=price
        return ok
    eng._commit_unit=commit
    eng._do_hire=lambda farm,*args:atomic('HIRE',original_hire,farm,*args)
    eng._do_buy_land=lambda farm,*args:atomic('BUY_LAND',original_land,farm,*args)
    try:
        for s in (0,1):
            private=state[s].observation.private
            units=[actions[s].get('farmer',['PASS']),*actions[s].get('hands',[])]
            demands=Counter(a[1] for a in units if len(a)>1 and a[0]=='PLANT')
            blocked={c for c,n in demands.items() if n>private.get('seeds',{}).get(c,0)}
            for u,act in enumerate(units):
                inv=private.get('inventories',[])
                initial=dict(inv[u]) if u<len(inv) else {}
                effective=['PASS'] if len(act)>1 and act[0]=='PLANT' and act[1] in blocked else act
                eng._apply_unit_action(obs.farms[s],private,u,effective,cfg.get('boardSize',10),
                    int(obs.get('step',0))//cfg.get('turnsPerDay',24),cfg.get('turnsPerDay',24),cfg.get('shedCapacity',100))
                if act and act[0]=='HARVEST':
                    final=private['inventories'][u] if u<len(private['inventories']) else {}
                    harvests[s,u]=sum(max(0,final.get(k,0)-initial.get(k,0)) for k in PRODUCTS)
        eng._process_market(state,structify({'configuration':cfg}))
        verified=[abs(obs.farms[s]['money']-after[s]['farms'][s]['money'])<.001 for s in (0,1)]
        return fills,harvests,verified
    finally:
        eng._commit_unit=original;eng._do_hire=original_hire;eng._do_buy_land=original_land


def export_one(job):
    path,labels,output,audit=job
    try:
        replay=load_replay(path);steps=replay['steps'];cfg=replay.get('configuration',{})
        episode=int(labels[0]['episode_id']) if labels else int(Path(path).name.split('-')[1])
        target=Path(output)/'_parts'/str(episode);target.mkdir(parents=True,exist_ok=True)
        tables={k:[] for k in TABLES};daily={};matched=Counter();hashes=[hashlib.sha256(),hashlib.sha256()]
        opening=[hashlib.sha256(),hashlib.sha256()];engine_hash='';eng=None
        if audit:
            from kaggle_environments.envs.kaggriculture import kaggriculture as eng
            engine_hash=hashlib.sha256(Path(eng.__file__).read_bytes()).hexdigest()
        provenance=hashlib.sha256(Path(path).read_bytes()).hexdigest()
        for i in range(len(steps)-1):
            before=observations(steps[i]);after=observations(steps[i+1])
            step=int(before[0].get('step',i));day=step//cfg.get('turnsPerDay',24)
            actions=[steps[i+1][s].get('action') or {} for s in (0,1)]
            fills=Counter();harvests={};verified=[None,None]
            if eng and all(isinstance(o.get('private'),dict) for o in before):
                fills,harvests,verified=reconstruct(before,actions,after,cfg,eng)
            normalized=[]
            for seat in (0,1):
                key=dict(episode_id=episode,seat=seat,step=step,day=day)
                stats=farm_stats(before[seat],seat)
                for item in PRODUCTS:stats['price_'+item]=before[seat].get('market',{}).get('prices',{}).get(item)
                delta=after[seat]['farms'][seat]['money']-stats['money']
                tables['turns'].append(dict(key,**stats,cash_delta=delta,cash_verified=verified[seat],
                    shops=json.dumps(before[seat].get('town',{}).get('unlocked_shops',[]),separators=(',',':'))))
                dkey=(seat,day)
                if dkey not in daily:daily[dkey]=dict(episode_id=episode,seat=seat,day=day,
                    opening_money=stats['money'],cash_delta=0,verified_transitions=0,mismatched_transitions=0)
                d=daily[dkey];d['closing_money']=after[seat]['farms'][seat]['money'];d['cash_delta']+=delta
                d['verified_transitions']+=verified[seat] is True;d['mismatched_transitions']+=verified[seat] is False
                for k in ('hands','quadrants','weeds','cow','sheep','goose','plants_STRAWBERRY','plants_CARROT'):
                    d['max_'+k]=max(d.get('max_'+k,0),stats[k])
                farm=before[seat]['farms'][seat];positions=[farm['farmer'],*farm.get('hands',[])]
                acts=[actions[seat].get('farmer',['PASS']),*actions[seat].get('hands',[])]
                canonical=[a[:2] for a in acts];normalized.append(canonical)
                hashes[seat].update(json.dumps(canonical).encode())
                if step<24:opening[seat].update(json.dumps(canonical).encode())
                for u,a in enumerate(acts):
                    pos=positions[u] if u<len(positions) else [None,None]
                    tile=farm['tiles'][pos[1]][pos[0]] if pos[0] is not None else None
                    tile=tile if isinstance(tile,dict) else {}
                    inventories=(before[seat].get('private') or {}).get('inventories',[])
                    inv=inventories[u] if u<len(inventories) else {}
                    tables['actions'].append(dict(key,unit=u,x=pos[0],y=pos[1],
                        requested_action=json.dumps(a,separators=(',',':')),tile_crop=(tile or {}).get('crop'),
                        tile_animal=(tile or {}).get('animal'),tile_yield=(tile or {}).get('yield_units'),
                        tile_kind=tile.get('kind'),planted_day=tile.get('planted_day'),
                        tile_fed_today=tile.get('fed_today'),carried_wheat=inv.get('WHEAT') if inventories else None,
                        engine_harvest_units=harvests.get((seat,u)),cash_verified=verified[seat]))
                for order_idx,o in enumerate(actions[seat].get('market',[])):
                    tables['orders'].append(dict(key,order_index=order_idx,requested_order=json.dumps(o,separators=(',',':'))))
                for s,op,item,metric in list(fills):
                    if s!=seat or metric!='units':continue
                    n=fills[s,op,item,'units'];value=fills[s,op,item,'value']
                    tables['fills'].append(dict(key,operation=op,item=item,units=n,value=value,cash_verified=verified[seat]))
                    # Only cash-reconciled transactions enter the verified daily totals.
                    if verified[seat]:
                        for suffix,val in [('units',n),('value',value)]:
                            name=op+'_'+item+'_'+suffix;d[name]=d.get(name,0)+val
            matched['steps']+=1;matched['equal_worker_steps']+=normalized[0]==normalized[1]
        tables['days']=list(daily.values())
        final=observations(steps[-1])
        for seat in (0,1):
            ownlabels=[r for r in labels if r['seat']==seat]
            peerlabels=[r for r in labels if r['seat']!=seat]
            team=ownlabels[0].get('team') if ownlabels else peerlabels[0].get('opponent') if peerlabels else ''
            days=[r for r in daily.values() if r['seat']==seat]
            tables['episodes'].append(dict(episode_id=episode,seat=seat,team=team,
                cohorts=';'.join(r['cohort'] for r in ownlabels),rank=next((r['rank'] for r in ownlabels if 'rank' in r),None),
                final_reward=steps[-1][seat].get('reward'),**farm_stats(final[seat],seat),
                worker_agreement=matched['equal_worker_steps']/matched['steps'],
                worker_sha256=hashes[seat].hexdigest(),opening_sha256=opening[seat].hexdigest(),
                verified_transitions=sum(r['verified_transitions'] for r in days),
                mismatched_transitions=sum(r['mismatched_transitions'] for r in days),
                replay_sha256=provenance,engine_sha256=engine_hash,
                replay_url=f'https://www.kaggle.com/competitions/kaggriculture/episodes/{episode}'))
        for name,rows in tables.items():write_table(target/(name+'.csv'),rows)
        return dict(episode_id=episode,status='DONE',rows={k:len(v) for k,v in tables.items()})
    except Exception:
        return dict(path=path,status='FAILED',error=traceback.format_exc())


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('inputs',nargs='*',type=Path)
    ap.add_argument('--manifest',type=Path)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--audit-fills',action='store_true')
    ap.add_argument('--workers',type=int,default=1)
    args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    records=json.loads(args.manifest.read_text(encoding='utf-8'))['replays'] if args.manifest else [dict(path=str(p),labels=[]) for p in args.inputs]
    if args.manifest:
        records=[dict(r,path=str(Path(r['path']) if Path(r['path']).is_absolute() else args.manifest.parent/r['path'])) for r in records]
    if not records:raise ValueError('No replays supplied')
    identifiers=[int(r['labels'][0]['episode_id']) if r.get('labels') else int(Path(r['path']).name.split('-')[1]) for r in records]
    if len(set(identifiers))!=len(identifiers):raise ValueError('Duplicate episode IDs supplied')
    args.output.mkdir(parents=True)
    jobs=[(r['path'],r.get('labels',[]),str(args.output),args.audit_fills) for r in records]
    results=[]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for future in as_completed([pool.submit(export_one,job) for job in jobs]):
            row=future.result();results.append(row);print(json.dumps(row),flush=True)
            (args.output/'export_status.json').write_text(json.dumps(results,indent=2)+'\n')
    for name in TABLES:
        files=sorted((args.output/'_parts').glob('*/'+name+'.csv'))
        fields=[]
        for p in files:
            with p.open(encoding='utf-8-sig',newline='') as f:
                fields.extend(k for k in (csv.DictReader(f).fieldnames or []) if k not in fields)
        with (args.output/(name+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
            for p in files:
                with p.open(encoding='utf-8-sig',newline='') as src:writer.writerows(csv.DictReader(src))
    if any(r['status']=='FAILED' for r in results):raise SystemExit('Some exports failed; see export_status.json')


if __name__=='__main__':main()
