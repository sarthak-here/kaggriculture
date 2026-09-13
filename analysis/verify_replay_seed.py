"""Check info.seed by replaying both action streams through the pinned engine."""
import argparse,json
from pathlib import Path
from replays_to_csv import load_replay,observations
def main():
    p=argparse.ArgumentParser();p.add_argument('replay',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    from kaggle_environments import make
    replay=load_replay(a.replay);seed=replay.get('info',{}).get('seed')
    assert isinstance(seed,int)
    cfg=dict(replay['configuration']);cfg['seed']=seed
    env=make('kaggriculture',configuration=cfg)
    def bind(seat):
        def agent(obs,config):return replay['steps'][obs.step+1][seat]['action']
        return agent
    env.run([bind(0),bind(1)])
    mismatches=[]
    for step,(left,right) in enumerate(zip(replay['steps'],env.steps)):
        lhs=observations(left);rhs=observations(right)
        for seat in (0,1):
            for field in ('farms','market','town','private'):
                if lhs[seat].get(field)!=rhs[seat].get(field):
                    mismatches.append(dict(step=step,seat=seat,field=field))
    result=dict(seed=seed,expected_steps=len(replay['steps']),actual_steps=len(env.steps),
        expected_rewards=[r['reward'] for r in replay['steps'][-1]],actual_rewards=[r.reward for r in env.steps[-1]],
        mismatch_count=len(mismatches),first_mismatches=mismatches[:10])
    a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
