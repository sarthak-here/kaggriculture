"""Original-seed counterfactuals against recorded actions, not live rival policies."""
import gzip,hashlib,json
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from run_w13_isolated import play
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/v45_loss_controls_20260916'
ARMS={'submitted':'variants/v45_proactive/main.py','original':'public_candidates/cloning_v45_20260916/main.py'}
def run(job):
    ep,arm,opponent,seed,seat,expected=job
    return dict(episode=ep,arm=arm,expected=expected,**play(str(ROOT/ARMS[arm]),opponent,seed,seat))
def main():
    corpus=ROOT/'analysis/v45_live_20260916';m=json.loads((corpus/'manifest.json').read_text(encoding='utf-8'))
    OUT.mkdir(exist_ok=False);jobs=[];hashes={}
    for entry in m['replays']:
        label=next((l for l in entry['labels'] if l['submission']==56278443 and l['result']=='L' and not l['self_play']),None)
        if not label:continue
        r=json.loads(gzip.decompress((corpus/entry['path']).read_bytes()));seat=label['seat'];ep=label['episode_id']
        folder=OUT/str(ep);folder.mkdir()
        (folder/'tape.json').write_text(json.dumps([s[1-seat]['action'] for s in r['steps'][1:]]))
        opponent=folder/'main.py'
        opponent.write_text('import json\nfrom pathlib import Path\nTAPE=None\ndef agent(obs,config=None):\n global TAPE\n if TAPE is None: TAPE=json.loads((Path(agent.__code__.co_filename).resolve().parent/"tape.json").read_text())\n return TAPE[obs["step"]]\n')
        hashes[entry['path']]=hashlib.sha256((corpus/entry['path']).read_bytes()).hexdigest()
        for arm in ARMS:jobs.append((ep,arm,str(opponent),r['info']['seed'],seat,[label['ours'],label['theirs']]))
    (OUT/'protocol.json').write_text(json.dumps(dict(jobs=jobs,replay_hashes=hashes,
        agent_hashes={k:hashlib.sha256((ROOT/v).read_bytes()).hexdigest() for k,v in ARMS.items()},
        runner_hash=hashlib.sha256((ROOT/'analysis/run_w13_isolated.py').read_bytes()).hexdigest()),indent=2)+'\n')
    rows=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for f in as_completed([pool.submit(run,j) for j in jobs]):
            r=f.result();rows.append(r);(OUT/'results.json').write_text(json.dumps(rows)+'\n')
            print(len(rows),r['episode'],r['arm'],r['status'],r.get('a'),r.get('b'),flush=True)
    assert len(rows)==40 and all(r['status']=='DONE' for r in rows)
    submitted={r['episode']:r for r in rows if r['arm']=='submitted'}
    original={r['episode']:r for r in rows if r['arm']=='original'}
    summary=dict(reproduced=sum([r['a'],r['b']]==r['expected'] for r in submitted.values()),
        expected_reproductions=20,original_wins=sum(r['a']>r['b'] for r in original.values()),
        original_ties=sum(r['a']==r['b'] for r in original.values()),
        comparisons=[dict(episode=e,submitted=s['a']-s['b'],original=original[e]['a']-original[e]['b'],
            reproduced=[s['a'],s['b']]==s['expected']) for e,s in submitted.items()])
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (OUT/'results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
    print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()
