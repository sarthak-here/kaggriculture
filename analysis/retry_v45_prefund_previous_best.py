"""Serially retry every preserved failure from the previous-best tournament."""
import json
from pathlib import Path
from tournament_v45_prefund_exported import OUT,run

def main():
    rows=json.loads((OUT/'results.json').read_text())
    failed=[r for r in rows if r['status']!='DONE']
    assert failed and all("[0, 0, 'timeout']" in r['error'] for r in failed)
    retries=[]
    for old in failed:
        row=run((old['opponent'],old['seed'],old['order']))
        retries.append(row)
        (OUT/'retry_results.json').write_text(json.dumps(retries)+'\n')
        print(len(retries),row['opponent'],row['seed'],row['order'],row['status'],row.get('a'),row.get('b'),flush=True)
    assert len(retries)==len(failed) and all(r['status']=='DONE' for r in retries)

if __name__=='__main__':main()
