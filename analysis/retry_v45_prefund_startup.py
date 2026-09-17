"""One serial diagnostic retry; preserve and report the original startup timeout."""
import json
from pathlib import Path
from screen_v45_prefund import run,OUT
def main():
    rows=json.loads((OUT/'results.json').read_text())
    failed=[r for r in rows if r['status']!='DONE']
    assert len(failed)==1 and failed[0]['episode']==109735695 and "[0, 0, 'timeout']" in failed[0]['error']
    jobs=json.loads((OUT/'protocol.json').read_text())['jobs']
    job=next(j for j in jobs if j[0]==failed[0]['episode'])
    result=run(job)
    with (OUT/'retry_results.json').open('x') as f:json.dump([result],f)
    print(result['status'],result.get('a'),result.get('b'),flush=True)
if __name__=='__main__':main()
