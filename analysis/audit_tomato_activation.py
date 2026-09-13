"""Activation coverage on saved observations, not counterfactual game results."""
import importlib.util,json
from collections import Counter
from pathlib import Path
from replays_to_csv import load_replay,observations
ROOT=Path(__file__).resolve().parents[1]
def main():
    root=ROOT/'analysis/shop0909_full_20260913';folder=ROOT/'variants/shop0909_tomato432'
    spec=importlib.util.spec_from_file_location('tomato_probe',folder/'main.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'));rows=[]
    for entry in manifest['replays']:
        label=entry['labels'][0]
        if not label['cohort'].startswith('submission_') or label['self_play']:continue
        replay=load_replay(root/entry['path']);policy=module.Policy(folder);seat=label['seat']
        prefix_mismatches=0
        for step in range(433):
            obs=observations(replay['steps'][step])[seat];obs['player']=seat
            action=policy.act(obs)
            if step<432 and action!=replay['steps'][step+1][seat]['action']:prefix_mismatches+=1
        rows.append(dict(episode=label['episode_id'],result=label['result'],margin=label['margin'],
            active=policy.players[seat].tomato_active,prefix_action_mismatches=prefix_mismatches))
    result=dict(total=len(rows),eligible_by_result=dict(Counter(r['result'] for r in rows if r['active'])),
        total_by_result=dict(Counter(r['result'] for r in rows)),prefix_action_mismatches=sum(r['prefix_action_mismatches'] for r in rows),rows=rows)
    (root/'tomato_activation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
if __name__=='__main__':main()
