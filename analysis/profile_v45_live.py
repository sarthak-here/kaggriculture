"""Per-label farm milestones; top-v-top replays retain both competitors' labels."""
import json
from pathlib import Path
from replays_to_csv import load_replay,observations,farm_stats
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'analysis/v45_live_20260916'
def main():
    manifest=json.loads((FOLDER/'manifest.json').read_text(encoding='utf-8'));rows=[]
    for entry in manifest['replays']:
        replay=load_replay(FOLDER/entry['path'])
        for label in entry['labels']:
            if label['submission']==56278443 and label['result']!='L':continue
            seat=label['seat'];profile=dict(label,milestones={})
            for step in (1,24,144,288,432,576,719):
                ob=observations(replay['steps'][step]);own=farm_stats(ob[seat],seat);opp=farm_stats(ob[1-seat],1-seat)
                profile['milestones'][str(step)]=dict(own=own,opponent=opp)
            profile['opening_market']=replay['steps'][1][seat]['action'].get('market',[])
            profile['opponent_opening_market']=replay['steps'][1][1-seat]['action'].get('market',[])
            rows.append(profile)
    (FOLDER/'milestones.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('profiled labels',len(rows))
    for r in rows:
        if r['submission']==56278443:
            m=r['milestones']['432'];print(r['episode_id'],r['opponent'],r['margin'],
                'd18',m['own']['money']-m['opponent']['money'],
                'opening',r['opponent_opening_market'])
if __name__=='__main__':main()
