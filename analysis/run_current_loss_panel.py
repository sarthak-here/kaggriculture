"""All current loss recordings plus recent winning controls, exact original seeds."""
import gzip,hashlib,json
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from run_w13_isolated import play
ROOT=Path(__file__).resolve().parents[1]
def execute(job):
    ep,arm,path,opponent,seed,seat,expected=job
    return dict(episode=ep,arm=arm,expected=expected,**play(str(path),str(opponent),seed,seat))
def main():
    corpus=ROOT/'analysis/tomato_losses_20260914';out=ROOT/'analysis/current_loss_panel_20260914';out.mkdir(exist_ok=False)
    manifest=json.loads((corpus/'manifest.json').read_text(encoding='utf-8'));jobs=[]
    for entry in manifest['replays']:
        label=entry['labels'][0];ep=label['episode_id'];seat=label['seat'];r=json.loads(gzip.decompress((corpus/entry['path']).read_bytes()));folder=out/str(ep);folder.mkdir()
        (folder/'tape.json').write_text(json.dumps([s[1-seat]['action'] for s in r['steps'][1:]]))
        opponent=folder/'main.py';opponent.write_text('import json\nfrom pathlib import Path\nTAPE=None\ndef agent(obs,config=None):\n global TAPE\n if TAPE is None: TAPE=json.loads((Path(agent.__code__.co_filename).resolve().parent/"tape.json").read_text())\n return TAPE[obs["step"]]\n')
        arms=[('base','variants/shop0909_tomato432/main.py'),('portfolio','variants/protected_portfolio/main.py')]
        if ep==108886864:arms.append(('recovery','variants/day1_recovery/main.py'))
        for arm,path in arms:jobs.append((ep,arm,ROOT/path,opponent,r['info']['seed'],seat,[label['ours'],label['theirs']]))
    paths={str(j[2].relative_to(ROOT)) for j in jobs}|{'analysis/run_w13_isolated.py'}
    for name in ('protected_portfolio','day1_recovery','shop0909_tomato432'):
        paths.update(str(p.relative_to(ROOT)) for p in (ROOT/'variants'/name).glob('*.json'))
    (out/'protocol.json').write_text(json.dumps(dict(jobs=len(jobs),hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)}),indent=2)+'\n')
    rows=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        for f in as_completed([pool.submit(execute,j) for j in jobs]):
            row=f.result();rows.append(row);(out/'results.json').write_text(json.dumps(rows)+'\n');print(row['episode'],row['arm'],row.get('a'),row.get('b'),flush=True)
    assert len(rows)==len(jobs) and all(r['status']=='DONE' for r in rows)
    assert all([r['a'],r['b']]==r['expected'] for r in rows if r['arm']=='base'),'Baseline did not reproduce actual rewards'
    (out/'results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
if __name__=='__main__':main()
