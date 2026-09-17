"""Counterfactual arms against Shawn404's fixed episode-110040845 actions."""
import gzip,hashlib,importlib.metadata,json
from pathlib import Path
from run_w13_isolated import play
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/shawn404_110040845_controls_20260917'
REPLAY=ROOT/'analysis/v45_prefund_exported_live_20260917/replays/episode-110040845-replay.json.gz'
ARMS={
    'corrected_prefund':'variants/v45_prefund_10_exported/main.py',
    'v45_proactive':'variants/v45_proactive/main.py',
    'v45_original':'public_candidates/cloning_v45_20260916/main.py',
    'consumption_guard':'variants/v45_consumption_guard/main.py',
}
def main():
    assert importlib.metadata.version('kaggle-environments')=='1.32.7'
    replay=json.loads(gzip.decompress(REPLAY.read_bytes()));seed=replay['info']['seed'];seat=0
    OUT.mkdir(exist_ok=False)
    (OUT/'tape.json').write_text(json.dumps([step[1]['action'] for step in replay['steps'][1:]])+'\n')
    opponent=OUT/'main.py'
    opponent.write_text('import json\nfrom pathlib import Path\nTAPE=None\ndef agent(obs,config=None):\n global TAPE\n if TAPE is None:TAPE=json.loads((Path(agent.__code__.co_filename).resolve().parent/"tape.json").read_text())\n return TAPE[obs["step"]]\n')
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ARMS.values()}
    hashes['replay']=hashlib.sha256(REPLAY.read_bytes()).hexdigest()
    (OUT/'protocol.json').write_text(json.dumps({'episode':110040845,'seed':seed,'seat':seat,'arms':ARMS,'hashes':hashes,'limitation':'Opponent actions fixed; valid causal diagnostic, not a reactive-policy ranking.'},indent=2)+'\n')
    rows=[]
    for name,path in ARMS.items():
        row=dict(arm=name,**play(str(ROOT/path),str(opponent),seed,seat));rows.append(row)
        print(name,row['status'],row.get('a'),row.get('b'),flush=True)
    (OUT/'results.json').write_text(json.dumps(rows)+'\n')
    assert all(r['status']=='DONE' for r in rows)
    assert all(hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h for p,h in hashes.items() if p!='replay')
if __name__=='__main__':main()
