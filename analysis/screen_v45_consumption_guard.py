"""All audited losses plus ten narrow wins. Fixed tapes, not reactive opponents."""
import gzip,hashlib,importlib.metadata,json
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from run_w13_isolated import play
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/v45_consumption_guard_screen_20260917'
AGENT=ROOT/'variants/v45_consumption_guard/main.py'
def run(job):
    ep,opp,seed,seat,expected=job
    return dict(episode=ep,expected=expected,**play(str(AGENT),opp,seed,seat))
def main():
    assert importlib.metadata.version('kaggle-environments')=='1.32.7'
    corpus=ROOT/'analysis/v45_live_20260916'
    manifest=json.loads((corpus/'manifest.json').read_text(encoding='utf-8'))
    own=[l for e in manifest['replays'] for l in e['labels'] if l['submission']==56278443 and not l['self_play']]
    chosen={l['episode_id'] for l in own if l['result']=='L'}
    chosen.update(l['episode_id'] for l in sorted((l for l in own if l['result']=='W'),key=lambda l:l['margin'])[:10])
    OUT.mkdir(exist_ok=False);jobs=[]
    for entry in manifest['replays']:
        label=next((l for l in entry['labels'] if l['submission']==56278443 and l['episode_id'] in chosen),None)
        if not label:continue
        replay=json.loads(gzip.decompress((corpus/entry['path']).read_bytes()));seat=label['seat'];ep=label['episode_id']
        folder=OUT/str(ep);folder.mkdir()
        (folder/'tape.json').write_text(json.dumps([s[1-seat]['action'] for s in replay['steps'][1:]]))
        opponent=folder/'main.py'
        opponent.write_text('import json\nfrom pathlib import Path\nTAPE=None\ndef agent(obs,config=None):\n global TAPE\n if TAPE is None: TAPE=json.loads((Path(agent.__code__.co_filename).resolve().parent/"tape.json").read_text())\n return TAPE[obs["step"]]\n')
        jobs.append((ep,str(opponent),replay['info']['seed'],seat,[label['ours'],label['theirs']]))
    assert len(jobs)==30
    fingerprint=hashlib.sha256(AGENT.read_bytes()).hexdigest()
    (OUT/'protocol.json').write_text(json.dumps({'jobs':jobs,'agent_sha256':fingerprint,'selection':'all 20 external losses and 10 narrowest external wins; exploratory only'},indent=2))
    rows=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for f in as_completed([pool.submit(run,j) for j in jobs]):
            row=f.result();rows.append(row)
            (OUT/'results.json').write_text(json.dumps(rows))
            print(len(rows),row['episode'],row['status'],row.get('a'),row.get('b'),flush=True)
    assert hashlib.sha256(AGENT.read_bytes()).hexdigest()==fingerprint
    (OUT/'results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
    summary={'games':len(rows),'failed':sum(r['status']!='DONE' for r in rows),
             'comparisons':[{'episode':r['episode'],'before':r['expected'][0]-r['expected'][1],'after':r['a']-r['b']} for r in rows if r['status']=='DONE']}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2))
    assert summary['failed']==0
if __name__=='__main__':main()
