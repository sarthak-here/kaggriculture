"""Create an immutable-source Shop0909 step-zero purchase candidate."""
import argparse, hashlib, json, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
EXPECTED='9fa78bee25ec86381f59c10025b1713bb5f37294320ca009eb3ab91a99851dde'
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'variants/shop0909_opening_net');a=ap.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    archive=ROOT/'analysis/shop0909_panel/agent.zip'
    assert hashlib.sha256(archive.read_bytes()).hexdigest()==EXPECTED
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist())=={'main.py','actions.json','LICENSE.txt'}
        files={name:z.read(name) for name in z.namelist()}
    old='        return liquidate(view) if step == LAST_STEP else action'
    new='''        # Only net the exact initial round-trip. All worker commands, later
        # market orders, route selection and repair state remain unchanged.
        if step == 0 and action.get("market") == [
                ["BUY_PRODUCT", "WHEAT", 13], ["SELL", "WHEAT", 13],
                ["BUY_PRODUCT", "WHEAT", 13]]:
            action["market"] = [["BUY_PRODUCT", "WHEAT", 13]]
        return liquidate(view) if step == LAST_STEP else action'''
    source=files['main.py'].decode('utf-8');assert source.count(old)==1
    files['main.py']=source.replace(old,new).encode('utf-8')
    compile(files['main.py'],'main.py','exec')
    a.output.mkdir(parents=True)
    for name,data in files.items():(a.output/name).write_bytes(data)
    (a.output/'provenance.json').write_text(json.dumps(dict(base_archive_sha256=EXPECTED,
        change='Exact step0 BUY13/SELL13/BUY13 WHEAT -> BUY13 WHEAT only',
        files={name:hashlib.sha256(data).hexdigest() for name,data in files.items()}),indent=2)+'\n')
    print(a.output)
if __name__=='__main__':main()
