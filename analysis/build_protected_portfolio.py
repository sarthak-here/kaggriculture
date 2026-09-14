"""Separate day-one recovery and protected production/sales portfolio probes."""
import hashlib,json,zipfile
from pathlib import Path
from build_shop0909_waiting_sales import HELPER
ROOT=Path(__file__).resolve().parents[1]
CASH='''
def recover_day_one(action, view, observation):
    if int(observation["step"]) != 24:
        return
    if action["market"] != [["HIRE"], ["HIRE"], ["HIRE"]]:
        return
    cash = observation["farms"][observation["player"]]["money"]
    if cash < 4 and view.prices.get("WHEAT",0) >= 4 and projected_shed(action,view).get("WHEAT",0) >= 2:
        action["market"].insert(0,["SELL","WHEAT",1])

'''
def main():
    archive=ROOT/'analysis/tomato_panel_20260913/candidate.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='6675155bf551cdeb547028cd226ed7d6c935c6bfeda636dec7c202495cf08195'
    with zipfile.ZipFile(archive) as z:base={n:z.read(n) for n in z.namelist()}
    for name in ('day1_recovery','protected_portfolio'):
        if name=='day1_recovery':files=dict(base)
        else:
            folder=ROOT/'variants/late_yarn_20260914'
            provenance=json.loads((folder/'provenance.json').read_text())
            files={n:(folder/n).read_bytes() for n in provenance['files']}
            assert all(hashlib.sha256(v).hexdigest()==provenance['files'][n] for n,v in files.items())
        source=files['main.py'].decode();source=source.replace('class Policy:',CASH+'class Policy:')
        source=source.replace('        action["market"] = action["market"][:MAX_ORDERS]','        recover_day_one(action, view, observation)\n        action["market"] = action["market"][:MAX_ORDERS]')
        if name=='protected_portfolio':
            helper=HELPER.replace('144 <= step < 648','433 <= step < 648')
            source=source.replace('class Policy:',helper+'class Policy:')
            anchor='            advance_sales(action, view, state, tape, step)';assert source.count(anchor)==1
            source=source.replace(anchor,anchor+'\n            sell_waiting_stock(action, view, tape, step)')
        compile(source,'main.py','exec');files['main.py']=source.encode();out=ROOT/'variants'/name;out.mkdir(exist_ok=False)
        for n,b in files.items():(out/n).write_bytes(b)
        (out/'provenance.json').write_text(json.dumps(dict(base_submission=56226432,files={n:hashlib.sha256(v).hexdigest() for n,v in files.items()}),indent=2)+'\n')
        print(out)
if __name__=='__main__':main()
