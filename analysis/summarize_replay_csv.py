"""Descriptive loss attribution from exported CSV; no counterfactual claims."""
import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path
from replays_to_csv import PRODUCTS, write_table


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,required=True)
    ap.add_argument('--csv-subdir',default='csv_audited')
    args=ap.parse_args();root=args.directory
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    def rows(name):
        with (root/args.csv_subdir/f'{name}.csv').open(encoding='utf-8-sig',newline='') as f:yield from csv.DictReader(f)
    def key(r):return int(r['episode_id']),int(r['seat'])
    def num(v):return float(v) if v else 0
    eps={key(r):r for r in rows('episodes')};totals=defaultdict(Counter);cash=defaultdict(dict);shops={};maxima=defaultdict(Counter)
    for r in rows('fills'):
        if r['cash_verified']!='True':continue
        t=totals[key(r)];op,item=r['operation'],r['item']
        t[f'{op}_{item}_units']+=num(r['units']);t[f'{op}_{item}_value']+=num(r['value'])
        t['revenue' if op=='SELL' else 'expense']+=num(r['value'])
    for r in rows('days'):
        k=key(r);cash[k][int(r['day'])]=num(r['closing_money'])
        for f in ('cow','sheep','goose','hands','quadrants','weeds','plants_STRAWBERRY','plants_CARROT'):
            maxima[k][f]=max(maxima[k][f],num(r['max_'+f]))
    for r in rows('turns'):
        if int(r['step'])==144:shops[key(r)]=json.loads(r['shops'])[:2]
    for r in rows('actions'):
        t=totals[key(r)];a=json.loads(r['requested_action']);op=a[0] if a else 'PASS'
        t['requested_'+op]+=1
        if op=='HARVEST' and r['engine_harvest_units']:
            item=r['tile_crop'] or {'COW':'MILK','SHEEP':'WOOL','GOOSE':'EGG'}.get(r['tile_animal'],'UNKNOWN')
            t['engine_harvest_'+item]+=num(r['engine_harvest_units'])
            t['zero_harvest_requests']+=num(r['engine_harvest_units'])==0
        if op=='FEED' and r['tile_animal'] and r['tile_fed_today']=='False' and num(r['carried_wheat'])==0:
            t['feed_without_wheat']+=1
        if op in ('PLANT','BUILD_PASTURE','BUILD_COOP') and r['tile_kind']=='WEED':t['weed_blocked_work']+=1
    summaries=[];top=[]
    def describe(ep,seat,label):
        ours=(ep,seat);other=(ep,1-seat);a,b=eps[ours],eps[other];ta,tb=totals[ours],totals[other]
        row=dict(episode_id=ep,seat=seat,team=a['team'],opponent=b['team'],cohort=label,
                 margin=num(a['final_reward'])-num(b['final_reward']),shops_at_144=json.dumps(shops.get(ours,[])),
                 worker_agreement=num(a['worker_agreement']),
                 own_cash_mismatches=int(a['mismatched_transitions']),opp_cash_mismatches=int(b['mismatched_transitions']))
        components={}
        for prefix,k in [('own',ours),('opp',other)]:
            t=totals[k];e=eps[k]
            for f in ('revenue','expense','feed_without_wheat','weed_blocked_work','zero_harvest_requests'):
                row[prefix+'_'+f]=t[f]
            for f,v in maxima[k].items():row[prefix+'_max_'+f]=v
            for f in ('money','crop_yield_on_tiles'):row[prefix+'_final_'+f]=num(e[f])
            row[prefix+'_terminal_stock_units']=sum(num(e['shed_'+p])+num(e['carried_'+p]) for p in PRODUCTS)
            for p in PRODUCTS:
                for suffix in ('units','value'):row[f'{prefix}_sold_{p}_{suffix}']=t[f'SELL_{p}_{suffix}']
                row[f'{prefix}_engine_harvest_{p}']=t['engine_harvest_'+p]
            for d in (0,1,5,10,15,20,25,29):row[f'{prefix}_cash_day_{d}']=cash[k].get(d)
        # Net product trading before comparing productive farm income. Wheat and
        # fertilizer purchases serve both inventory/trading and farm inputs;
        # this is cash attribution, not a causal profit estimate.
        for p in PRODUCTS:
            own_net=ta[f'SELL_{p}_value']-ta[f'BUY_PRODUCT_{p}_value']
            opp_net=tb[f'SELL_{p}_value']-tb[f'BUY_PRODUCT_{p}_value']
            components[p+'_net_receipts']=own_net-opp_net
            row['own_net_'+p]=own_net;row['opp_net_'+p]=opp_net
        own_capital=ta['expense']-sum(ta[f'BUY_PRODUCT_{p}_value'] for p in PRODUCTS)
        opp_capital=tb['expense']-sum(tb[f'BUY_PRODUCT_{p}_value'] for p in PRODUCTS)
        row['own_other_expenses']=own_capital;row['opp_other_expenses']=opp_capital
        components['other_expenses']=opp_capital-own_capital
        row['largest_negative_component']=min(components,key=components.get)
        row['largest_negative_value']=min(components.values())
        row['cash_decomposition_residual']=row['margin']-sum(components.values())
        sheep=maxima[other]['sheep'];cow=maxima[other]['cow'];goose=maxima[other]['goose']
        row['opponent_structure']='sheep-heavy' if sheep>=10 and sheep>=cow else 'cattle-heavy' if cow>=10 else 'goose-heavy' if goose>=10 else 'mixed/small'
        return row
    for r in manifest['replays']:
        for label in r['labels']:
            row=describe(label['episode_id'],label['seat'],label['cohort'])
            if label['cohort']=='top10':row['rank']=label['rank'];top.append(row)
            else:summaries.append(row)
    write_table(root/'match_summary.csv',summaries);write_table(root/'top10_summary.csv',top)
    write_table(root/'ladder_record.csv',manifest['episodes'])
    aggregate={}
    for cohort in ('submission_loss','submission_win_control'):
        group=[r for r in summaries if r['cohort']==cohort]
        aggregate[cohort]={'n':len(group),'opponent_structures':dict(Counter(r['opponent_structure'] for r in group)),
            'largest_negative_components':dict(Counter(r['largest_negative_component'] for r in group)),
            'near_worker_clone_ge_90pct':sum(r['worker_agreement']>=.9 for r in group),
            'any_cash_mismatch':sum(r['own_cash_mismatches']+r['opp_cash_mismatches']>0 for r in group),
            'means':{f:sum(r[f] for r in group)/len(group) for f in ('margin','own_feed_without_wheat','opp_feed_without_wheat','own_weed_blocked_work','opp_weed_blocked_work','own_terminal_stock_units','opp_terminal_stock_units')}}
    (root/'summary.json').write_text(json.dumps(aggregate,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(aggregate,indent=2))


if __name__=='__main__':main()
