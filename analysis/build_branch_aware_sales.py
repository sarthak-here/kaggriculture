"""Release sale protection once all reachable production decisions have passed."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

HELPER='''
def sale_window_open(state, step):
    # Yarn choice is made at288; a nonzero shop plan cannot enter tomato at432.
    # Active specialist tapes retain their existing complete market schedule.
    if state.tomato_active or state.yarn_branch is not None:
        return False
    return 289 <= step < 648 and (state.plan != 0 or step > 432)

'''

def main():
    base=ROOT/'variants/protected_portfolio';out=ROOT/'variants/branch_aware_sales'
    provenance=json.loads((base/'provenance.json').read_text())
    files={n:(base/n).read_bytes() for n in provenance['files']}
    assert all(hashlib.sha256(v).hexdigest()==provenance['files'][n] for n,v in files.items())
    source=files['main.py'].decode()
    assert source.count('if not 433 <= step < 648')==1
    source=source.replace('if not 433 <= step < 648','if not 289 <= step < 648')
    anchor='            sell_waiting_stock(action, view, tape, step)'
    assert source.count(anchor)==1
    source=source.replace(anchor,'            if sale_window_open(state, step):\n    '+anchor)
    assert source.count('class Policy:')==1
    source=source.replace('class Policy:',HELPER+'class Policy:')
    compile(source,'main.py','exec');files['main.py']=source.encode()
    out.mkdir(exist_ok=False)
    for n,v in files.items():(out/n).write_bytes(v)
    (out/'provenance.json').write_text(json.dumps(dict(base='protected_portfolio',
        change='Start h3 at289 only on nonzero plans after yarn decision; strict branch checks unchanged',
        files={n:hashlib.sha256(v).hexdigest() for n,v in files.items()}),indent=2)+'\n')
    print(out)
if __name__=='__main__':main()
