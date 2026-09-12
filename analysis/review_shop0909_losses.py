"""Review a frozen loss cohort using audited CSV and full replay action traces."""
import argparse, ast, csv, json
from collections import Counter, defaultdict
from pathlib import Path
from replays_to_csv import PRODUCTS, load_replay, observations, write_table

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--directory',type=Path,required=True)
    ap.add_argument('--agent',type=Path,required=True)
    a=ap.parse_args(); root=a.directory
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    def rows(name):
        with (root/'csv_audited'/f'{name}.csv').open(encoding='utf-8-sig',newline='') as f:
            yield from csv.DictReader(f)
    def key(r):return int(r['episode_id']),int(r['seat'])
    def num(v):return float(v) if v else 0
    with (root/'match_summary.csv').open(encoding='utf-8-sig',newline='') as f:
        summary={key(r):r for r in csv.DictReader(f)}
    turns=defaultdict(dict)
    for r in rows('turns'):turns[key(r)][int(r['step'])]=r
    eps={key(r):r for r in rows('episodes')}
    assert all(int(r['mismatched_transitions'])==0 and int(r['verified_transitions'])==719 for r in eps.values())
    fills=defaultdict(list)
    for r in rows('fills'):
        assert r['cash_verified']=='True'
        fills[key(r)].append(r)
    tree=ast.parse(a.agent.read_text(encoding='utf-8'))
    plans=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign)
               and any(isinstance(t,ast.Name) and t.id=='SHOP_PLANS' for t in n.targets))
    output=[]; details=[]
    for entry in manifest['replays']:
        label=entry['labels'][0]; ep=label['episode_id']; seat=label['seat']; k=(ep,seat)
        r=summary[k]; replay=load_replay(root/entry['path'])
        commands=[[(record[s].get('action') or {}) for record in replay['steps'][1:]] for s in (0,1)]
        def workers(act):return [act.get('farmer',['PASS']),*(act.get('hands') or [])]
        worker_diff=[i for i,(x,y) in enumerate(zip(*commands)) if workers(x)!=workers(y)]
        market_diff=[i for i,(x,y) in enumerate(zip(*commands)) if x.get('market',[])!=y.get('market',[])]
        own=turns[k]; opp=turns[(ep,1-seat)]
        shops=json.loads(own[144]['shops'])
        fullshops=json.loads(own[718]['shops'])
        result=dict(episode_id=ep,opponent=label['opponent'],seat=seat,result=label['result'],
            margin=label['margin'],cohort=label['cohort'],shop_pair=' / '.join(shops[:2]),
            shops=json.dumps(fullshops),inferred_plan=plans.get(tuple(shops[:2]),0),
            exact_worker_agreement=1-len(worker_diff)/719,
            different_market_steps=len(market_diff),first_worker_difference=worker_diff[0] if worker_diff else None,
            first_market_difference=market_diff[0] if market_diff else None)
        for step in (1,2,17,23,24,25,48,72,144):
            for field in ('money','hands','cow','sheep','quadrants'):
                result[f'own_{field}_step{step}']=num(own[step][field])
        result['step24_hires_filled']=sum(num(f['units']) for f in fills[k] if f['step']=='24' and f['operation']=='HIRE')
        result['day0_wheat_seeds_bought']=sum(num(f['units']) for f in fills[k] if f['day']=='0' and f['operation']=='BUY_SEED' and f['item']=='WHEAT')
        result['day1_wheat_bought']=sum(num(f['units']) for f in fills[k] if f['day']=='1' and f['operation']=='BUY_PRODUCT' and f['item']=='WHEAT')
        result['step0_orders']=json.dumps(commands[seat][0].get('market',[]))
        result['step0_opponent_orders']=json.dumps(commands[1-seat][0].get('market',[]))
        result['own_final_stock_units']=num(r['own_terminal_stock_units'])
        result['own_final_crop_yield']=num(r['own_final_crop_yield_on_tiles'])
        result['cash_residual']=num(r['cash_decomposition_residual'])
        assert abs(result['cash_residual'])<.001
        components=[]
        for p in PRODUCTS:
            qa=num(r[f'own_sold_{p}_units']);qb=num(r[f'opp_sold_{p}_units'])
            va=num(r[f'own_sold_{p}_value']);vb=num(r[f'opp_sold_{p}_value'])
            pa=va/qa if qa else None;pb=vb/qb if qb else None
            result[f'own_sold_{p}']=qa;result[f'opp_sold_{p}']=qb
            result[f'own_avg_price_{p}']=pa;result[f'opp_avg_price_{p}']=pb
            result[f'net_receipts_gap_{p}']=num(r['own_net_'+p])-num(r['opp_net_'+p])
            result[f'own_harvested_{p}']=num(r['own_engine_harvest_'+p])
            result[f'opp_harvested_{p}']=num(r['opp_engine_harvest_'+p])
            components.append((p,result[f'net_receipts_gap_{p}']))
        result['other_expenses_gap']=num(r['opp_other_expenses'])-num(r['own_other_expenses'])
        result['same_product_sale_quantities']=all(result[f'own_sold_{p}']==result[f'opp_sold_{p}'] for p in PRODUCTS)
        # Disjoint descriptive groups. Not counterfactual attribution.
        core=('MILK','WOOL','EGG','CARROT','TOMATO','MELON')
        core_equal=all(result[f'own_sold_{p}']==result[f'opp_sold_{p}'] for p in core)
        if result['day0_wheat_seeds_bought']<7:
            result['review_group']='Opening cash/seed shortfall'
        elif result['exact_worker_agreement']>=.97 and core_equal:
            result['review_group']='Near-clone sale-price/timing'
        else:
            result['review_group']='Different production mix'
        result['opening_no_day1_hands']=num(own[25]['hands'])==0
        result['opening_understaffed_day1']=num(own[25]['hands'])<3
        result['own_feed_without_wheat_requests']=num(r['own_feed_without_wheat'])
        result['own_weed_blocked_requests']=num(r['own_weed_blocked_work'])
        components.append(('other_expenses',result['other_expenses_gap']))
        components.sort(key=lambda x:x[1])
        result['largest_cash_gap']=components[0][0];result['largest_cash_gap_coins']=components[0][1]
        result['replay_url']=eps[k]['replay_url']
        output.append(result)
        details.append(dict(episode_id=ep,seat=seat,worker_difference_steps=worker_diff,
            market_difference_steps=market_diff,cash_components=components,
            final_status=[x.get('status') for x in replay['steps'][-1]],
            opening_checkpoints=[dict(step=s,ours={f:own[s][f] for f in ('money','hands','cow','sheep','quadrants')},
                 opponent={f:opp[s][f] for f in ('money','hands','cow','sheep','quadrants')}) for s in (1,2,17,24,25,48,144)]))
    output.sort(key=lambda r:r['margin'])
    write_table(root/'loss_review.csv',[r for r in output if r['result']=='L'])
    write_table(root/'control_review.csv',[r for r in output if r['result']=='W'])
    external=[r for r in manifest['episodes'] if not r['self_play']]
    losses=[r for r in output if r['result']=='L']
    assert {r['episode_id'] for r in losses}=={r['episode_id'] for r in external if r['result']=='L'}
    stats=dict(as_of=manifest['retrieved_at'],record=dict(Counter(r['result'] for r in external)),
        audited_replays=len(output),verified_cash_transitions=sum(int(r['verified_transitions']) for r in eps.values()),
        mismatches=0,losses=len(losses),controls=len(output)-len(losses),
        loss_margin_sum=sum(r['margin'] for r in losses),
        loss_opening_no_hands=sum(r['opening_no_day1_hands'] for r in losses),
        loss_opening_understaffed=sum(r['opening_understaffed_day1'] for r in losses),
        same_sale_quantity_losses=sum(r['same_product_sale_quantities'] for r in losses),
        loss_seats=dict(Counter(r['seat'] for r in losses)),
        loss_plans=dict(Counter(r['inferred_plan'] for r in losses)),
        descriptive_groups=dict(Counter(r['review_group'] for r in losses)),
        control_opening_seed_shortfalls=sum(r['day0_wheat_seeds_bought']<7 for r in output if r['result']=='W'),
        details=details)
    (root/'review_details.json').write_text(json.dumps(stats,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in stats.items() if k!='details'},indent=2))
    for r in output:
        print(r['episode_id'],r['opponent'],r['margin'],'hands25',r['own_hands_step25'],
              'cow48',r['own_cow_step48'],'equalqty',r['same_product_sale_quantities'],
              'worker',round(r['exact_worker_agreement'],3),'plan',r['inferred_plan'])

if __name__=='__main__':main()
