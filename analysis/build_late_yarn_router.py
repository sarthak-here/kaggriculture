"""Experimental full-state-gated sheep continuations for two-Yarn markets."""
import gzip,hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HELPER='''
def select_yarn(observation, state, branches):
    if any(state.queues.values()):
        return None
    if observation["town"]["unlocked_shops"].count("YARN_STORE") < 2:
        return None
    farm = observation["farms"][observation["player"]]
    if farm["money"] < 10000:
        return None
    noncash = {k:v for k,v in farm.items() if k != "money"}
    for index, branch in enumerate(branches):
        if noncash == branch["farm"] and observation["private"] == branch["private"]:
            return index
    return None

'''
def main():
    archive=ROOT/'analysis/tomato_panel_20260913/candidate.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='6675155bf551cdeb547028cd226ed7d6c935c6bfeda636dec7c202495cf08195'
    with zipfile.ZipFile(archive) as z:files={n:z.read(n) for n in z.namelist()}
    corpus=ROOT/'analysis/shop0909_full_20260913';manifest=json.loads((corpus/'manifest.json').read_text(encoding='utf-8'));labels={r['episode_id']:r for r in manifest['episodes']};branches=[]
    for ep in (108358878,108143468):
        r=json.loads(gzip.decompress((corpus/f'replays/episode-{ep}-replay.json.gz').read_bytes()));seat=1-labels[ep]['seat'];o=r['steps'][288][seat]['observation'];farms=r['steps'][288][0]['observation']['farms']
        farm={k:v for k,v in farms[seat].items() if k!='money'}
        assert farm=={k:v for k,v in farms[1-seat].items() if k!='money'}
        assert o['private']==r['steps'][288][1-seat]['observation']['private']
        branches.append(dict(episode=ep,seat=seat,farm=farm,private=o['private'],route=[s[seat]['action'] for s in r['steps'][1:]]))
    source=files['main.py'].decode();source=source.replace('class Policy:',HELPER+'class Policy:')
    source=source.replace('        self.tomato_active = False','        self.tomato_active = False\n        self.yarn_branch = None')
    source=source.replace('        self.players = {}','        self.players = {}\n        self.yarn = json.loads((Path(folder) / "yarn.json").read_text())')
    source=source.replace('        if step == 432:','        if step == 288:\n            state.yarn_branch = select_yarn(observation, state, self.yarn)\n        if step == 432 and state.yarn_branch is None:')
    source=source.replace('        action = copy.deepcopy(tape[step])','        if state.yarn_branch is not None:\n            tape = self.yarn[state.yarn_branch]["route"]\n        action = copy.deepcopy(tape[step])')
    source=source.replace('        if not state.tomato_active:','        if not state.tomato_active and state.yarn_branch is None:')
    compile(source,'main.py','exec');files['main.py']=source.encode();files['yarn.json']=json.dumps(branches,separators=(',',':')).encode()
    out=ROOT/'variants/late_yarn_20260914';out.mkdir(exist_ok=False)
    for n,b in files.items():(out/n).write_bytes(b)
    (out/'provenance.json').write_text(json.dumps(dict(base_submission=56226432,step=288,episodes=[108358878,108143468],files={n:hashlib.sha256(b).hexdigest() for n,b in files.items()}),indent=2)+'\n')
    print(out)
if __name__=='__main__':main()
