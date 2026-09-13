"""Actual-seed counterfactuals against recorded opponents, not adaptive policies."""
import argparse,json,sys
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from replays_to_csv import load_replay
from run_w13_isolated import play
ROOT=Path(__file__).resolve().parents[1]
IDS=[108145550,108365255,108358878,108214006,108202824,108187759,108207436,108244520,108158623,108331733]
def execute(job):
    ep,arm,path,opp,seed,seat,expected=job
    row=play(str(ROOT/path),str(opp.resolve()),seed,seat)
    return dict(episode=ep,arm=arm,expected=expected,**row)
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    root=ROOT/'analysis/shop0909_full_20260913';manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    labels={r['episode_id']:r for r in manifest['episodes']};jobs=[]
    for ep in IDS:
        label=labels[ep];seat=label['seat'];replay=load_replay(root/f'replays/episode-{ep}-replay.json.gz')
        folder=a.output/str(ep);folder.mkdir();tape=[r[1-seat]['action'] for r in replay['steps'][1:]]
        (folder/'tape.json').write_text(json.dumps(tape))
        opp=folder/'main.py'
        opp.write_text('import json\nfrom pathlib import Path\nTAPE=None\ndef agent(obs,config=None):\n global TAPE\n if TAPE is None: TAPE=json.loads((Path(agent.__code__.co_filename).resolve().parent/"tape.json").read_text())\n return TAPE[obs["step"]]\n')
        expected=[label['ours'],label['theirs']]
        for arm,path in [('base','variants/shop0909_opening_net/main.py'),('tomato','variants/shop0909_tomato432/main.py'),('h3','variants/shop0909_waiting_h3/main.py')]:
            jobs.append((ep,arm,path,opp,replay['info']['seed'],seat,expected))
    rows=[]
    with ProcessPoolExecutor(max_workers=3) as pool:
        for f in as_completed([pool.submit(execute,j) for j in jobs]):
            row=f.result();rows.append(row)
            (a.output/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
            print(json.dumps({k:row.get(k) for k in ('episode','arm','status','a','b','expected')}),flush=True)
    assert len(rows)==len(jobs) and all(r['status']=='DONE' for r in rows)
    assert all([r['a'],r['b']]==r['expected'] for r in rows if r['arm']=='base'),'Baseline replay did not reproduce'
if __name__=='__main__':main()
