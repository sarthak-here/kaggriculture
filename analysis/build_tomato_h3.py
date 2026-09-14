"""Combine complementary experimental mechanisms; never modify the submitted ZIP."""
import hashlib,json,zipfile
from pathlib import Path
from build_shop0909_waiting_sales import HELPER
ROOT=Path(__file__).resolve().parents[1]
def main():
    archive=ROOT/'analysis/tomato_panel_20260913/candidate.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()=='6675155bf551cdeb547028cd226ed7d6c935c6bfeda636dec7c202495cf08195'
    with zipfile.ZipFile(archive) as z:files={n:z.read(n) for n in z.namelist()}
    source=files['main.py'].decode();anchor='            advance_sales(action, view, state, tape, step)'
    assert source.count(anchor)==1 and source.count('class Policy:')==1
    source=source.replace('class Policy:',HELPER+'class Policy:')
    source=source.replace(anchor,anchor+'\n            sell_waiting_stock(action, view, tape, step)')
    compile(source,'main.py','exec');files['main.py']=source.encode()
    out=ROOT/'variants/tomato_h3_20260914';out.mkdir(exist_ok=False)
    for n,b in files.items():(out/n).write_bytes(b)
    (out/'provenance.json').write_text(json.dumps(dict(base_submission=56226432,
        change='h3 market additions only while tomato branch is inactive; compatibility guard unchanged',
        files={n:hashlib.sha256(b).hexdigest() for n,b in files.items()}),indent=2)+'\n')
    print(out)
if __name__=='__main__':main()
