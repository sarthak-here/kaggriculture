"""Original feedback-controlled crop planner. No replay tables or route imports.

Prototype: price-impact-aware crop allocation and deadline-aware worker dispatch.
Animal investment is deliberately not implemented in this first baseline.
"""
import math
from collections import Counter

# Official engine1.32.7 crop rules: cost, first yield, full yield, interval, units.
CROPS={'WHEAT':(10,2,4,0,6),'CARROT':(20,2,3,0,4),
       'TOMATO':(50,8,8,1,4),'STRAWBERRY':(100,10,10,2,4),'MELON':(80,10,12,0,6)}
PRICES={'WHEAT':(25,400,'sqrt',.8,'log',.2),'CARROT':(35,450,'hinge',1,'sqrt',.7),
        'TOMATO':(60,200,'hinge',.4,'sqrt',.6),'STRAWBERRY':(120,100,'sqrt',.7,'linear',1.6),
        'MELON':(250,300,'log',.2,'sq',3.6)}
SHOPS={'BAKERY':['EGG','WHEAT'],'PIZZA_SHOP':['MILK','TOMATO','WHEAT'],
       'BRUNCH_SPOT':['EGG','WHEAT','STRAWBERRY'],'YARN_STORE':['WOOL'],
       'ICE_CREAM_SHOP':['STRAWBERRY','MILK','WHEAT'],'PET_CAFE':['CARROT'],
       'SMOOTHIE_SHOP':['STRAWBERRY','MILK'],'FARMERS_MARKET':['WHEAT','CARROT','TOMATO','STRAWBERRY']}

def shape(name,x,t):
    x=max(0,x)
    if name=='hinge':
        u=x/t;return u+8*max(0,u-1)**2
    return {'sqrt':math.sqrt,'log':math.log1p,'linear':lambda v:v,'sq':lambda v:v*v}[name](x)

def price(item,inventory,overrides=None):
    base,t,below,bt,above,at=PRICES[item];p=(overrides or {}).get(item,{})
    base=p.get('base',base);t=p.get('T',t);center=p.get('I0',10000)
    below=p.get('below_func',below);above=p.get('above_func',above)
    bt=p.get('below_target',bt);at=p.get('above_target',at)
    scarce=inventory<center;f=below if scarce else above
    delta=base*(bt if scarce else at)*shape(f,abs(inventory-center),t)/shape(f,t,t)
    return max(1,round(base+(delta if scarce else -delta)))

def distance(a,b):return abs(a[0]-b[0])+abs(a[1]-b[1])

def daily_demand(shops):
    out=Counter({p:1 for p in CROPS})
    for shop in shops:
        items=SHOPS.get(shop,[])
        for item in items:out[item]+=12 if len(items)==1 else 6
    return out

def crop_values(obs,extra=None):
    """Conservative marginal value, accounting for visible competing crop output.

    Forecast uses known shops only. Future shops, perfect harvests and sale timing
    are uncertain; this is an approximation, not a guaranteed profit estimate.
    """
    day=int(obs['step'])//24;left=29-day;demand=daily_demand(obs['town']['unlocked_shops'])
    fields=[]
    for farm in obs['farms']:
        fields.extend(t for row in farm['tiles'] for t in row if isinstance(t,dict) and t.get('crop') in CROPS)
    values={}
    for crop,(cost,first,mature,interval,units) in CROPS.items():
        if mature>left:values[crop]=-float('inf');continue
        horizon=min(left,mature+4);supply=0
        for tile in fields:
            if tile['crop']!=crop:continue
            wait=max(0,tile['planted_day']+mature-day)
            if wait<=horizon:
                if interval:
                    elapsed=max(0,1+(day-tile['planted_day']-mature)//interval)
                    supply+=tile.get('yield_units',0)+max(0,min(4-elapsed,1+(horizon-wait)//interval))
                else:supply+=units
        future_units=min(4,1+(horizon-mature)//interval) if interval else units
        supply+=(extra or {}).get(crop,0)*future_units
        inv=obs['market']['inventory'][crop]+supply-demand[crop]*horizon
        projected=sum(price(crop,inv+i,obs['market'].get('params')) for i in range(units))/units
        # Saturation is modeled before any additional planting decision.
        cycles=min(4,1+(left-mature)//interval) if interval else 1
        output_units=cycles if interval else units
        life=mature+(cycles-1)*interval if interval else mature
        work=life*2.5+cycles*2+3
        values[crop]=(output_units*projected*.7-cost)/work
    return values

def move_toward(pos,target):
    if pos[0]!=target[0]:return ['EAST' if pos[0]<target[0] else 'WEST']
    if pos[1]!=target[1]:return ['SOUTH' if pos[1]<target[1] else 'NORTH']
    return ['PASS']

def hire_cost(n):
    a,b=1,1
    for _ in range(n):a,b=b,a+b
    return a

def agent(observation,configuration=None):
    obs=observation;farm=obs['farms'][obs['player']];private=obs['private']
    step=int(obs['step']);day,hour=divmod(step,24);tiles=farm['tiles'];size=len(tiles)
    positions=[farm['farmer'],*farm['hands']];inventories=private['inventories']
    access=[(x,y) for x in (size//2-1,size//2) for y in (size//2-1,size//2)]
    values=crop_values(obs);cash=farm['money'];orders=[];seeds=dict(private['seeds'])
    stock=dict(private['shed']);free=[(x,y) for y,row in enumerate(tiles) for x,t in enumerate(row) if t is None]
    plants=[(x,y,t) for y,row in enumerate(tiles) for x,t in enumerate(row) if isinstance(t,dict) and t.get('crop') in CROPS]
    # Budget predictable daily labour before optional purchases. Sales are not
    # treated as cash until they have actually filled in a later observation.
    reserve=max(60,hire_cost(5)*3)
    for item,quantity in stock.items():
        if item in CROPS and quantity>0:orders.append(['SELL',item,quantity])
    if hour<3:
        desired=min(7,max(2,math.ceil((len(plants)*3+len(free))/18)))
        hired=len(farm['hands']);n=farm['hires_today']
        while hired<desired and len(orders)<8 and cash-hire_cost(n)>=reserve:
            cost=hire_cost(n);orders.append(['HIRE']);cash-=cost;hired+=1;n+=1
    if hour<16 and day<27 and free and len(orders)<9:
        planned=Counter();capacity=min(len(free),max(0,8-sum(seeds.values())))
        for _ in range(capacity):
            marginal=crop_values(obs,planned);crop=max(marginal,key=marginal.get);cost=CROPS[crop][0]
            if marginal[crop]<=0 or cash-cost<reserve:break
            planned[crop]+=1;cash-=cost
        for crop,quantity in planned.items():
            if len(orders)<9:orders.append(['BUY_SEED',crop,quantity])
    # Expand only when useful jobs can pay for land and spare crew capacity exists.
    land_cost=[1000,2000,4000]
    if len(farm['unlocked_quadrants'])<4 and len(free)<2 and day<17 and len(orders)<10:
        cost=land_cost[len(farm['unlocked_quadrants'])-1]
        if cash>cost+1500 and max(values.values())>20:orders.append(['BUY_LAND'])
    jobs=[]
    for x,y,tile in plants:
        crop=tile['crop'];cost,first,mature,interval,units=CROPS[crop];age=day-tile['planted_day'];yield_now=tile.get('yield_units',0)
        need_water=not tile.get('watered_today',False)
        water_grows=not interval and (mature+1)//2<=age<=mature and yield_now<units
        if need_water and (day<29 or water_grows):
            urgency=3 if tile.get('consecutive_unwatered',0)>=1 else 1
            jobs.append(((x,y),['WATER'],max(20,values[crop])*urgency+hour*3))
        if age>=first and yield_now>0 and (interval or age>=mature or day==29) and not (need_water and water_grows):
            jobs.append(((x,y),['HARVEST'],yield_now*obs['market']['prices'][crop]))
    available={c:q for c,q in seeds.items() if q>0 and values.get(c,-1)>0}
    for pos in free:
        for crop in available:jobs.append((pos,['PLANT',crop],max(0,values[crop])*3))
    if available:
        for y,row in enumerate(tiles):
            for x,t in enumerate(row):
                if isinstance(t,dict) and t.get('kind')=='WEED':jobs.append(((x,y),['DIG'],max(values.values())))
    workers=[];claimed=set();seed_used=Counter()
    for worker,pos in enumerate(positions):
        inv=inventories[worker] if worker<len(inventories) else {};held=sum(inv.values());shed=min(access,key=lambda p:distance(pos,p));back=distance(pos,shed)
        if held and (tuple(pos) in access or (day==29 and 718-step<=back+1) or held>=12 or cash<reserve):
            workers.append(['DROP'] if back==0 else move_toward(pos,shed));continue
        best=None;best_score=0
        for target,action,value in jobs:
            if target in claimed:continue
            if action[0]=='PLANT' and seed_used[action[1]]>=available[action[1]]:continue
            travel=distance(pos,target)
            if travel>=24-hour:continue
            if action[0]=='HARVEST' and day==29 and travel+1+min(distance(target,p) for p in access)+1>719-step:continue
            score=value/(travel+1)
            if score>best_score:best_score=score;best=(target,action,travel)
        if best is None:workers.append(['DROP'] if held and back==0 else ['PASS']);continue
        target,action,travel=best;claimed.add(target)
        if action[0]=='PLANT':seed_used[action[1]]+=1
        workers.append(action if travel==0 else move_toward(pos,target))
    # Worker drops precede markets. Project just those additions, respecting cap.
    total=sum(stock.values())
    for i,action in enumerate(workers):
        if action==['DROP']:
            for item,qty in inventories[i].items():
                added=min(qty,max(0,100-total));stock[item]=stock.get(item,0)+added;total+=added
    sold={o[1] for o in orders if o[0]=='SELL'}
    for o in orders:
        if o[0]=='SELL':o[2]=stock.get(o[1],0)
    for item,qty in stock.items():
        if item in CROPS and qty>0 and item not in sold and len(orders)<10:orders.append(['SELL',item,qty])
    return dict(farmer=workers[0],hands=workers[1:],market=orders[:10])
