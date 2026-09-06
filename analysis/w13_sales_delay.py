"""Conservative, experimental strawberry-only delay. No opponent identity input.

Only one batch can be pending. Entry requires an otherwise quiet two-turn
window; the baseline policy still runs every turn. No new entries near endgame.
This is a causal experiment, not a proven price predictor or promotion candidate.
"""
import copy

def wrap_sales_delay(base, routes, price_fn, shop_products, require_recovery=True):
    states = {}
    telemetry = {'entries':0, 'units':0, 'released':0, 'slot_waits':0, 'shortfalls':0}
    def policy(obs, configuration=None):
        cfg=configuration or {};step=int(obs.get('step',0));seat=int(obs.get('player',0))
        state=states.get(seat)
        if state is None or step==0 or step<state['step']:
            state={'step':step,'pending':None,'previous_inventory':None};states[seat]=state
        state['step']=step
        result=copy.deepcopy(base(obs,configuration))
        base_terminal_result=copy.deepcopy(result)
        market=result.setdefault('market',[])
        private=obs.get('private',{});shed=private.get('shed',{})
        farms=obs.get('farms',[]);farm=farms[seat]
        cap=int(cfg.get('maxMarketOrdersPerTurn',10));end=int(cfg.get('episodeSteps',720))-2
        inventory=int(obs.get('market',{}).get('inventory',{}).get('STRAWBERRY',10000))
        preempt=getattr(base,'preemption',None)
        ps=preempt.states[seat] if preempt is not None else {}
        route=routes.get(ps.get('route','default'),routes['default'])
        pending=state['pending']
        if pending is not None:
            # Reserve held inventory against an unexpected new baseline SELL.
            available=max(0,int(shed.get('STRAWBERRY',0))-pending['qty'])
            for row in market:
                if len(row)>=3 and row[:2]==['SELL','STRAWBERRY']:
                    original=max(0,int(row[2]));row[2]=min(original,available);available-=row[2]
            if step>=pending['due']:
                if len(market)<cap:
                    quantity=min(pending['qty'],max(0,int(shed.get('STRAWBERRY',0))))
                    if quantity<pending['qty']:telemetry['shortfalls']+=1
                    # Successful SELL is guaranteed for current shed stock: no
                    # cash requirement and no other strawberry sale consumes it.
                    market.append(['SELL','STRAWBERRY',quantity])
                    telemetry['released']+=quantity;state['pending']=None
                else:telemetry['slot_waits']+=1
            # Preserve baseline's terminal liquidation rather than carrying debt.
            if step==end:
                result=copy.deepcopy(base_terminal_result)
                state['pending']=None
            # Keep the controller's own-flow estimator synchronized with emitted orders.
            if preempt is not None:ps['last_emitted_market']=copy.deepcopy(result['market'])
            state['previous_inventory']=inventory
            return result

        previous=state['previous_inventory'];state['previous_inventory']=inventory
        if not (160<=step<end-6):return result
        tpd=int(cfg.get('turnsPerDay',24))
        if step//tpd!=(step+2)//tpd:return result
        if any(int(d.get('STRAWBERRY',0)) for d in ps.get('due',{}).values()):return result
        window=route[step:step+3]
        # No purchases/hiring/land or deposits/pickups can depend on today's sale.
        for action in window:
            if any(row and row[0]!='SELL' for row in action.get('market',[])):return result
            if any(row and row[0] in ('DROP','PLACE','PICKUP') for row in [action.get('farmer',[]),*action.get('hands',[])]):return result
        if any(row and row[0]!='SELL' for row in market):return result
        if any(row and row[0] in ('DROP','PLACE','PICKUP') for row in [result.get('farmer',[]),*result.get('hands',[])]):return result
        if float(farm.get('money',0))<500:return result
        if sum(shed.values())>int(cfg.get('shedCapacity',100))-20:return result
        # Leave room for the controller's at-most-four product preemptions plus release.
        if any(len(a.get('market',[]))>cap-5 for a in route[step+1:step+3]):return result
        # No overlapping scheduled batches or future preemption targets.
        if any(len(row)>=2 and row[:2]==['SELL','STRAWBERRY']
               for a in route[step+1:step+6] for row in a.get('market',[])):return result
        candidates=[(i,row) for i,row in enumerate(market[:cap]) if len(row)>=3 and row[:2]==['SELL','STRAWBERRY'] and int(row[2])>0]
        if len(candidates)!=1:return result
        index,row=candidates[0];quantity=int(row[2])
        if quantity>int(shed.get('STRAWBERRY',0)):return result
        if require_recovery:
            interval=int(cfg.get('townShopSellInterval',4))
            demand=sum((2 if len(shop_products.get(s,[]))==1 else 1)
                       for s in obs.get('town',{}).get('unlocked_shops',[])
                       if 'STRAWBERRY' in shop_products.get(s,[]))
            drain=demand*sum(t%interval==0 for t in (step,step+1))
            # Public trend is supporting evidence only; unseen future opponent
            # supply can still erase this forecast. Never use replay lookahead.
            if previous is None or inventory>previous or drain<=0:return result
            now=sum(price_fn('STRAWBERRY',inventory+i) for i in range(quantity))
            later=sum(price_fn('STRAWBERRY',inventory-drain+i) for i in range(quantity))
            if later<=now:return result
        # Zero-quantity placeholder preserves every other order's original slot.
        market[index]=['SELL','STRAWBERRY',0]
        state['pending']={'qty':quantity,'due':step+2}
        telemetry['entries']+=1;telemetry['units']+=quantity
        if preempt is not None:ps['last_emitted_market']=copy.deepcopy(market)
        return result
    policy.delay_telemetry=telemetry
    return policy
