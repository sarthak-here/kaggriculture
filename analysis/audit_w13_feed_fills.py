"""Instrument actual order-index fills without changing either policy's actions."""
import argparse
import ast
import json
from pathlib import Path

from run_w13_isolated import play


def audit(a, b, seed, order):
    from kaggle_environments.envs.kaggriculture import kaggriculture as engine
    original_market, original_parse, original_commit = engine._process_market, engine._parse_order, engine._commit_unit
    original_unit = engine._apply_unit_action
    tree=ast.parse(Path(a).read_text())
    nodes=[n for n in tree.body if isinstance(n,ast.Assign) and isinstance(n.value,ast.Call)
           and isinstance(n.value.func,ast.Name) and n.value.func.id=='_CropResponse']
    eligible=ast.literal_eval(nodes[-1].value.args[1]) if nodes else {}
    crops={'successful_plants':0,'successful_harvests':0,'harvested_units':0}
    planted=set();last_market_step=-1;actor_seat=-1
    context = {}; records = []
    def unit(farm,private,idx,action,board_size,day,turns_per_day,shed_capacity=100):
        nonlocal actor_seat
        if idx==0:actor_seat+=1
        step=last_market_step+1
        position=farm['farmer'] if idx==0 else farm['hands'][idx-1] if idx<=len(farm['hands']) else None
        target=tuple(position) if position is not None else None
        old_tile=farm['tiles'][target[1]][target[0]] if target is not None else None
        inventories=private.get('inventories',[])
        old_count=inventories[idx].get('CARROT',0) if idx<len(inventories) else 0
        result=original_unit(farm,private,idx,action,board_size,day,turns_per_day,shed_capacity)
        if actor_seat==order and target is not None:
            tile=farm['tiles'][target[1]][target[0]]
            if (action==['PLANT','CARROT'] and old_tile is None and isinstance(tile,dict)
                and tile.get('crop')=='CARROT' and [idx,*target] in eligible.get(str(step),[])):
                planted.add(target);crops['successful_plants']+=1
            if action==['HARVEST'] and target in planted and isinstance(old_tile,dict) and old_tile.get('crop')=='CARROT' and tile is None:
                planted.remove(target);crops['successful_harvests']+=1
                crops['harvested_units']+=private['inventories'][idx].get('CARROT',0)-old_count
        return result
    def market(state, env):
        nonlocal last_market_step,actor_seat
        step = state[0].observation.step
        last_market_step=step;actor_seat=-1
        context.clear()
        context.update(step=step, farms={id(f):s for s,f in enumerate(state[0].observation.farms)},
                       orders={}, active={}, rows={})
        for seat in (0,1):
            for idx, raw in enumerate((state[seat].action or {}).get('market',[])[:env.configuration.maxMarketOrdersPerTurn]):
                context['orders'][id(raw)] = (seat,idx)
                if len(raw)>=3 and raw[:2]==['BUY_PRODUCT','WHEAT'] and seat==order:
                    row={'step':step,'order_index':idx,'requested':int(raw[2]),'filled':0,'cost':0}
                    context['rows'][seat,idx]=row;records.append(row)
        return original_market(state, env)
    def parse(raw):
        key = context['orders'].get(id(raw))
        if key is not None:context['active'][key[0]]=key[1]
        return original_parse(raw)
    def commit(op,item,price,farm,private,market,shed_capacity=100):
        ok=original_commit(op,item,price,farm,private,market,shed_capacity)
        if ok and op=='BUY_PRODUCT' and item=='WHEAT':
            seat=context['farms'][id(farm)]
            key=(seat,context['active'].get(seat))
            if key in context['rows']:
                row=context['rows'][key];row['filled']+=1;row['cost']+=price
        return ok
    engine._process_market=market;engine._parse_order=parse;engine._commit_unit=commit;engine._apply_unit_action=unit
    try:
        result=play(str(Path(a).resolve()),str(Path(b).resolve()),seed,order)
    finally:
        engine._process_market=original_market;engine._parse_order=original_parse;engine._commit_unit=original_commit
        engine._apply_unit_action=original_unit
    late=[r for r in records if r['step']>=300]
    result['wheat_order_audit']={'late_requested':sum(r['requested'] for r in late),
        'late_filled':sum(r['filled'] for r in late),
        'late_unfilled_orders':[r for r in late if r['filled']!=r['requested']], 'orders':records}
    result['crop_execution_audit']={**crops,'unharvested_tracked_plots':len(planted)}
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('a');p.add_argument('b')
    p.add_argument('--seed',type=int,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    rows=[]
    for order in (0,1):
        r=audit(args.a,args.b,args.seed,order);rows.append(r)
        w=r['wheat_order_audit']
        print({'seed':args.seed,'order':order,'status':r['status'],
               'late_requested':w['late_requested'],'late_filled':w['late_filled'],
               'unfilled_orders':len(w['late_unfilled_orders'])},flush=True)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({'a':args.a,'b':args.b,'rows':rows},indent=2)+'\n')
    if any(r['status']!='DONE' for r in rows):raise SystemExit(1)


if __name__=='__main__':main()
