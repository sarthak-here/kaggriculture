"""Repair only the Kaggle callable export of the frozen broken submission."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BROKEN_SHA='baeffa728ffdad24db7799d8962e2328ae606d87c77032bcac33654d13fc18a0'
def main():
    base=ROOT/'variants/v45_prefund_10/main.py';raw=base.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BROKEN_SHA
    source=raw.decode()
    assert source.endswith('agent.telemetry=_LOCAL_PREFUND_REPORT\n')
    source += "agent=globals().pop('agent')\n"
    compile(source,'main.py','exec')
    out=ROOT/'variants/v45_prefund_10_exported';out.mkdir(exist_ok=False)
    encoded=source.encode();(out/'main.py').write_bytes(encoded)
    (out/'provenance.json').write_text(json.dumps({
        'base_sha256':BROKEN_SHA,'main_sha256':hashlib.sha256(encoded).hexdigest(),
        'change':"append agent=globals().pop('agent') so Kaggle selects the policy instead of _local_prefund_action",
        'broken_submission':56294314},indent=2)+'\n')
if __name__=='__main__':main()
