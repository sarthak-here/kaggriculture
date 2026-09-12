"""Full-game fixed-tape diagnostics for five observed opening shortfalls.
The replay seeds are unknown; these are new seeded games, not exact live reruns.
"""
import gzip,hashlib,json,subprocess,sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    from run_w13_isolated import play
    out=ROOT/'analysis/shop0909_opening_diagnostics_20260912';out.mkdir(exist_ok=False)
    corpus=ROOT/'analysis/shop0909_all_losses_20260911'
    manifest=json.loads((corpus/'manifest.json').read_text(encoding='utf-8'))
    selected={107774237,107764291,107779199,107788563,107784173}
    results=[]
    for entry in manifest['replays']:
        label=entry['labels'][0];ep=label['episode_id'];seat=label['seat']
        if ep not in selected:continue
        raw=(corpus/entry['path']).read_bytes();replay=json.loads(gzip.decompress(raw))
        folder=out/str(ep);folder.mkdir()
        tape=[record[1-seat].get('action') or {} for record in replay['steps'][1:]]
        (folder/'actions.json').write_text(json.dumps(tape),encoding='utf-8')
        # Generated fixture is only a recorded action tape, never downloaded code.
        (folder/'main.py').write_text("import json,copy\nfrom pathlib import Path\nA=json.loads(Path(__file__).with_name('actions.json').read_text())\ndef agent(observation, configuration=None):\n    return copy.deepcopy(A[int(observation['step'])])\n")
        for arm,path in [('base','public_candidates/shop0909_20260910/main.py'),('candidate','variants/shop0909_opening_net/main.py')]:
            row=play(str(ROOT/path),str(folder/'main.py'),39120000,seat)
            row.update(episode_id=ep,arm=arm,original_seat=seat,opponent=label['opponent'],source_sha256=hashlib.sha256(raw).hexdigest())
            results.append(row)
            (out/'results.json').write_text(json.dumps(results,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
            print({k:row.get(k) for k in ('episode_id','arm','status','a','b')},flush=True)
    assert len(results)==10 and all(r['status']=='DONE' for r in results)
    (out/'results.json.gz').write_bytes(gzip.compress(json.dumps(results).encode(),mtime=0))
if __name__=='__main__':main()
