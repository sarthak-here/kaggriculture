"""Original-seed branch diagnostics; recorded opponents are not adaptive agents."""
import gzip,json
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from run_w13_isolated import play
ROOT=Path(__file__).resolve().parents[1]
def execute(job):
    ep,arm,agent,opponent,seed,seat,expected=job
    return dict(episode=ep,arm=arm,expected=expected,**play(str(agent),str(opponent),seed,seat))
def main():
    out=ROOT/'analysis/late_yarn_probe_20260914';out.mkdir(exist_ok=False)
    corpus=ROOT/'analysis/shop0909_full_20260913';manifest=json.loads((corpus/'manifest.json').read_text(encoding='utf-8'));labels={r['episode_id']:r for r in manifest['episodes']};jobs=[]
    for ep in (108358878,108143468):
        label=labels[ep];seat=label['seat'];r=json.loads(gzip.decompress((corpus/f'replays/episode-{ep}-replay.json.gz').read_bytes()));folder=out/str(ep);folder.mkdir()
        (folder/'tape.json').write_text(json.dumps([s[1-seat]['action'] for s in r['steps'][1:]]))
        opponent=folder/'main.py';opponent.write_text('import json\nfrom pathlib import Path\nTAPE=None\ndef agent(obs,config=None):\n global TAPE\n if TAPE is None: TAPE=json.loads((Path(agent.__code__.co_filename).resolve().parent/"tape.json").read_text())\n return TAPE[obs["step"]]\n')
        for arm,path in [('opening','variants/shop0909_opening_net/main.py'),('submitted','variants/shop0909_tomato432/main.py'),('yarn','variants/late_yarn_20260914/main.py')]:
            jobs.append((ep,arm,ROOT/path,opponent,r['info']['seed'],seat,[label['ours'],label['theirs']]))
    rows=[]
    with ProcessPoolExecutor(max_workers=3) as pool:
        for f in as_completed([pool.submit(execute,j) for j in jobs]):
            row=f.result();rows.append(row);(out/'results.json').write_text(json.dumps(rows,indent=2)+'\n');print(row['episode'],row['arm'],row.get('a'),row.get('b'),flush=True)
    assert len(rows)==6 and all(r['status']=='DONE' for r in rows)
    assert all([r['a'],r['b']]==r['expected'] for r in rows if r['arm']=='opening')
if __name__=='__main__':main()
