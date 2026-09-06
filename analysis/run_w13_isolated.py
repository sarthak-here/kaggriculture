"""Paired games with each bundled agent in its own process.

Records actual engine fills, per-seat action hashes and explicit failures.
Unlike the historical harness, this cannot share v44/v23 sys.modules between
agents. Use engine 1.32.7. Each JSON output is exclusive to one experiment.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import importlib.metadata
import inspect
import json
import multiprocessing as mp
from pathlib import Path
import time
import traceback

def child(connection, path):
    namespace = {'__name__':'w13_isolated_agent', '__file__':path}
    try:
        exec(compile(Path(path).read_text(),path,'exec'),namespace)
        # Audit mode must expose errors rather than silently PASS.
        fn=namespace.get('_V44_POLICY', namespace.get('agent'))
        params=list(inspect.signature(fn).parameters.values())
        accepts_config=(len([p for p in params if p.kind in (p.POSITIONAL_ONLY,p.POSITIONAL_OR_KEYWORD)])>=2
                        or any(p.kind==p.VAR_POSITIONAL for p in params))
        while True:
            request=connection.recv()
            if request is None: break
            if request=='telemetry':
                connection.send(getattr(fn,'delay_telemetry',{}));continue
            obs, config=request
            connection.send(('ok',fn(obs,config) if accepts_config else fn(obs)))
    except BaseException:
        connection.send(('error',traceback.format_exc()))
    finally: connection.close()

def play(a,b,seed,order):
    from kaggle_environments import make
    from kaggle_environments.envs.kaggriculture import kaggriculture as engine
    ctx=mp.get_context('spawn'); processes=[]; connections=[]
    paths=[a,b] if order==0 else [b,a]
    hashes=[hashlib.sha256(),hashlib.sha256()]
    fills=[collections.Counter(),collections.Counter()]
    action_errors=[]; market_count=[0,0]; timeline=[]
    active_farms={}; active_step=0
    original_commit=engine._commit_unit; original_market=engine._process_market
    def market(state,env):
        nonlocal active_step,active_farms
        active_step=state[0].observation.step
        active_farms={id(f):i for i,f in enumerate(state[0].observation.farms)}
        return original_market(state,env)
    def commit(op,item,price,farm,private,market,shed_capacity=100):
        ok=original_commit(op,item,price,farm,private,market,shed_capacity)
        if ok:
            seat=active_farms[id(farm)]
            fills[seat][op+':'+item+':units']+=1
            fills[seat][op+':'+item+':value']+=price
            if op=='SELL' and item=='STRAWBERRY':timeline.append([active_step,seat,price])
        return ok
    engine._commit_unit=commit;engine._process_market=market
    try:
        policies=[]
        for seat,path in enumerate(paths):
            parent,kid=ctx.Pipe();p=ctx.Process(target=child,args=(kid,path));p.start();kid.close()
            processes.append(p);connections.append(parent)
            def policy(obs,config,seat=seat,conn=parent):
                conn.send((obs,config))
                if not conn.poll(5):
                    action_errors.append([seat,obs.step,'timeout']);raise TimeoutError('agent IPC exceeded 5 seconds')
                status,value=conn.recv()
                if status!='ok':
                    action_errors.append([seat,obs.step,value]);raise RuntimeError(value)
                hashes[seat].update(json.dumps({k:v for k,v in value.items() if k!='market'},sort_keys=True).encode())
                market_count[seat]+=len(value.get('market',[]))
                return value
            # Core introspects required positional parameters, so expose exactly two.
            def bind(fn):
                def wrapped(obs,config):return fn(obs,config)
                return wrapped
            policies.append(bind(policy))
        env=make('kaggriculture',configuration={'seed':seed},debug=False)
        env.run(policies)
        rewards=[s.reward for s in env.state];statuses=[s.status for s in env.state]
        if action_errors or any(s!='DONE' for s in statuses) or any(not isinstance(x,(int,float)) for x in rewards):
            raise RuntimeError(str({'statuses':statuses,'rewards':rewards,'errors':action_errors}))
        ai=order;bi=1-order
        def farm_summary(seat):
            farm=env.state[0].observation.farms[seat]
            animals=collections.Counter(tile.get('animal') for row in farm['tiles'] for tile in row
                                        if isinstance(tile,dict) and tile.get('animal'))
            return {'quadrants':len(farm.get('unlocked_quadrants',[])),'animals':dict(animals)}
        agent_telemetry=[]
        for conn in connections:
            conn.send('telemetry')
            agent_telemetry.append(conn.recv() if conn.poll(5) else {'error':'telemetry timeout'})
        return {'seed':seed,'order':order,'status':'DONE','a':rewards[ai],'b':rewards[bi],
                'a_final_farm':farm_summary(ai),'b_final_farm':farm_summary(bi),
                'a_telemetry':agent_telemetry[ai],'b_telemetry':agent_telemetry[bi],
                'a_fills':dict(fills[ai]),'b_fills':dict(fills[bi]),
                'a_workers_sha256':hashes[ai].hexdigest(),'b_workers_sha256':hashes[bi].hexdigest(),
                'strawberry_fills':timeline,'shops':list(env.state[0].observation.town.unlocked_shops)}
    except BaseException:
        return {'seed':seed,'order':order,'status':'FAILED','error':traceback.format_exc()}
    finally:
        engine._commit_unit=original_commit;engine._process_market=original_market
        for c in connections:
            try:c.send(None)
            except (EOFError,BrokenPipeError,OSError):pass
            c.close()
        for p in processes:
            p.join(1)
            if p.is_alive():p.terminate();p.join()

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('a');parser.add_argument('b');parser.add_argument('--seed',type=int,required=True)
    parser.add_argument('--pairs',type=int,default=5);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True)
    if importlib.metadata.version('kaggle-environments')!='1.32.7':
        raise RuntimeError('This experiment is pinned to kaggle-environments 1.32.7')
    if args.output.exists():raise FileExistsError(args.output)
    rows=[];start=time.monotonic()
    provenance={'a_sha256':hashlib.sha256(Path(args.a).read_bytes()).hexdigest(),
                'b_sha256':hashlib.sha256(Path(args.b).read_bytes()).hexdigest(),
                'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    for seed in range(args.seed,args.seed+args.pairs):
        for order in (0,1):
            row=play(str(Path(args.a).resolve()),str(Path(args.b).resolve()),seed,order);rows.append(row)
            args.output.write_text(json.dumps({'a':args.a,'b':args.b,'engine':'1.32.7',**provenance,'rows':rows},indent=2)+'\n')
            print({k:v for k,v in row.items() if k in ('seed','order','status','a','b','error')},flush=True)
    wins=sum(r.get('a',0)>r.get('b',0) for r in rows if r['status']=='DONE')
    losses=sum(r.get('a',0)<r.get('b',0) for r in rows if r['status']=='DONE')
    ties=sum(r['a']==r['b'] for r in rows if r['status']=='DONE')
    print({'wins':wins,'losses':losses,'ties':ties,'failures':len(rows)-wins-losses-ties,'seconds':time.monotonic()-start},flush=True)

if __name__=='__main__':main()
