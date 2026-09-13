"""Build coherent rank-one replay probes, not a reconstruction of its live policy.

Keep each complete route together. No cross-farm branch splicing is performed.
Frozen Shop0909 supplies weed repair and final liquidation, but its advance-sales
rule is disabled because the recorded route already contains sale decisions.
"""
import argparse, gzip, hashlib, json, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--corpus',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    manifest=json.loads((a.corpus/'manifest.json').read_text(encoding='utf-8'))
    archive=ROOT/'analysis/shop0909_opening_panel_20260912/candidate.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='a63d56e478203b281b9560df3224abef322f34fcb81dee812f707720593758fb'
    with zipfile.ZipFile(archive) as z:
        source=z.read('main.py').decode();license=z.read('LICENSE.txt')
    source=source.replace('        advance_sales(action, view, state, tape, step)',
        '        # Replay already records its original market decisions.')
    compile(source,'main.py','exec')
    a.output.mkdir(parents=True,exist_ok=False);index=[]
    for entry in manifest['replays']:
        labels=[r for r in entry['labels'] if r['cohort']=='top10' and r['rank']==1]
        for label in labels:
            data=(a.corpus/entry['path']).read_bytes();replay=json.loads(gzip.decompress(data))
            seat=label['seat'];ep=label['episode_id'];steps=replay['steps']
            assert len(steps)==720 and all(r[seat].get('action') is not None for r in steps[1:])
            tape=[r[seat]['action'] for r in steps[1:]]
            target=a.output/str(ep);target.mkdir()
            (target/'main.py').write_text(source,encoding='utf-8')
            (target/'actions.json').write_text(json.dumps([tape]*13,separators=(',',':')))
            (target/'LICENSE.txt').write_bytes(license)
            index.append(dict(episode=ep,seat=seat,team=label['team'],submission=label['submission'],
                replay_sha256=hashlib.sha256(data).hexdigest(),reported_seed=replay.get('info',{}).get('seed'),
                path=(target/'main.py').as_posix(),
                shops=steps[-1][0]['observation']['town']['unlocked_shops'],
                caveat='Recorded route with Shop0909 guards, not the live rank-one policy'))
    assert len(index)==5
    (a.output/'index.json').write_text(json.dumps(index,indent=2)+'\n')
    print(json.dumps(index,indent=2))
if __name__=='__main__':main()
