"""Build a state-compatible day-18 tomato continuation; keep baseline fallback."""
import gzip,hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HELPER='''
def tomato_compatible(observation, state, reference):
    if state.plan != 0 or any(state.queues.values()):
        return False
    farm = observation["farms"][observation["player"]]
    shops = observation["town"]["unlocked_shops"]
    if sum(s in ("FARMERS_MARKET", "PIZZA_SHOP") for s in shops) < 2:
        return False
    if farm["money"] < 10000:
        return False
    if {k:v for k,v in farm.items() if k != "money"} != reference["farm"]:
        return False
    return observation["private"] == reference["private"]

'''
def main():
    out=ROOT/'variants/shop0909_tomato432'
    if out.exists():raise FileExistsError(out)
    archive=ROOT/'analysis/shop0909_opening_panel_20260912/candidate.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='a63d56e478203b281b9560df3224abef322f34fcb81dee812f707720593758fb'
    with zipfile.ZipFile(archive) as z:files={n:z.read(n) for n in z.namelist()}
    path=ROOT/'analysis/shop0909_full_20260913/replays/episode-108145550-replay.json.gz'
    replay=json.loads(gzip.decompress(path.read_bytes()));obs=replay['steps'][432][0]['observation']
    reference=dict(farm={k:v for k,v in obs['farms'][0].items() if k!='money'},private=obs['private'])
    assert all(reference['farm'][k]==obs['farms'][1][k] for k in reference['farm'])
    assert reference['private']==replay['steps'][432][1]['observation']['private']
    route=[r[0]['action'] for r in replay['steps'][1:]]
    source=files['main.py'].decode()
    source=source.replace('class Policy:',HELPER+'class Policy:')
    source=source.replace('        self.players = {}','        self.players = {}\n        self.tomato = json.loads((Path(folder) / "tomato.json").read_text())')
    source=source.replace('        self.plan = 0','        self.plan = 0\n        self.tomato_active = False')
    anchor='        if step == FINAL_PLAN_STEP:'
    source=source.replace(anchor,'        if step == 432:\n            state.tomato_active = tomato_compatible(observation, state, self.tomato["reference"])\n'+anchor)
    source=source.replace('        tape = self.tapes[state.plan]','        tape = self.tomato["route"] if state.tomato_active else self.tapes[state.plan]')
    source=source.replace('        advance_sales(action, view, state, tape, step)','        if not state.tomato_active:\n            advance_sales(action, view, state, tape, step)')
    compile(source,'main.py','exec');files['main.py']=source.encode()
    files['tomato.json']=json.dumps(dict(reference=reference,route=route),separators=(',',':')).encode()
    out.mkdir(parents=True)
    for n,data in files.items():(out/n).write_bytes(data)
    (out/'provenance.json').write_text(json.dumps(dict(base_submission=56182426,episode=108145550,seat=0,switch_step=432,replay_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),files={n:hashlib.sha256(v).hexdigest() for n,v in files.items()}),indent=2)+'\n')
    print(out)
if __name__=='__main__':main()
