"""Terminal crop maturity and worker-only similarity to sampled top-ten traces."""
import argparse
from collections import Counter
import json
from pathlib import Path
from replays_to_csv import load_replay, observations, write_table


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,required=True);args=ap.parse_args()
    from kaggle_environments.envs.kaggriculture.kaggriculture import CROPS
    root=args.directory;manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    terminal=[];traces={};leaders=[];losses=[]
    for entry in manifest['replays']:
        path=Path(entry['path']);path=path if path.is_absolute() else root/path
        replay=load_replay(path);ep=entry['labels'][0]['episode_id'];final=observations(replay['steps'][-1])
        for seat in (0,1):
            seq=[]
            for record in replay['steps'][1:]:
                a=record[seat].get('action') or {}
                seq.append(json.dumps([a.get('farmer',['PASS']),*(a.get('hands') or [])],sort_keys=True,separators=(',',':')))
            traces[ep,seat]=seq
            day=int(final[seat].get('step',719))//replay['configuration'].get('turnsPerDay',24)
            for y,row in enumerate(final[seat]['farms'][seat]['tiles']):
                for x,t in enumerate(row):
                    if not isinstance(t,dict) or not t.get('yield_units',0):continue
                    crop=t.get('crop');animal=t.get('animal')
                    ready=(day-t['planted_day']>=CROPS[crop]['first_yield_day']) if crop else bool(animal)
                    terminal.append(dict(episode_id=ep,seat=seat,x=x,y=y,crop=crop,animal=animal,
                        day=day,planted_day=t.get('planted_day'),yield_units=t['yield_units'],harvest_ready=ready))
        leaders.extend(x for x in entry['labels'] if x['cohort']=='top10')
        losses.extend(x for x in entry['labels'] if x['cohort']=='submission_loss')
    family=[]
    for loss in losses:
        if not leaders:
            break
        opponent=traces[loss['episode_id'],1-loss['seat']]
        def agreement(top):
            other=traces[top['episode_id'],top['seat']]
            return sum(a==b for a,b in zip(opponent,other))/max(len(opponent),len(other))
        leader=max(leaders,key=agreement)
        family.append(dict(episode_id=loss['episode_id'],opponent=loss['opponent'],
            closest_sampled_top_team=leader['team'],top_rank=leader['rank'],top_episode=leader['episode_id'],
            exact_worker_action_agreement=agreement(leader)))
    write_table(root/'terminal_tiles.csv',terminal);write_table(root/'opponent_trace_neighbors.csv',family)
    ownkeys={(x['episode_id'],x['seat']) for x in losses}
    print('Our loss terminal tiles:',Counter((r['crop'] or r['animal'],r['harvest_ready']) for r in terminal if (r['episode_id'],r['seat']) in ownkeys))
    print('Loss opponents >=90% worker agreement with sampled top10:',sum(r['exact_worker_action_agreement']>=.9 for r in family))


if __name__=='__main__':main()
