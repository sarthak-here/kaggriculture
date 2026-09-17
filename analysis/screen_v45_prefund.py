"""Independent feed-prefunding arm on the preregistered loss/win diagnostic set."""
import gzip,hashlib,importlib.metadata,json
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from run_w13_isolated import play
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis/v45_prefund_10_screen_20260917'
AGENT=ROOT/'variants/v45_prefund_10/main.py'
def run(job):
    ep,opp,seed,seat,expected=job
    return dict(episode=ep,expected=expected,**play(str(AGENT),opp,seed,seat))
def main():
    assert importlib.metadata.version('kaggle-environments')=='1.32.7'
    jobs=json.loads((ROOT/'analysis/v45_consumption_guard_screen_20260917/protocol.json').read_text())['jobs']
    OUT.mkdir(exist_ok=False);rows=[]
    fingerprint=hashlib.sha256(AGENT.read_bytes()).hexdigest()
    (OUT/'protocol.json').write_text(json.dumps({'jobs':jobs,'agent_sha256':fingerprint,'selection':'Same 20 external losses plus 10 narrow wins; fixed rival actions; quantity10 selected on setup cash, not game outcomes'},indent=2))
    with ProcessPoolExecutor(max_workers=4) as pool:
        for f in as_completed([pool.submit(run,j) for j in jobs]):
            row=f.result();rows.append(row);(OUT/'results.json').write_text(json.dumps(rows))
            print(len(rows),row['episode'],row['status'],row.get('a'),row.get('b'),flush=True)
    assert hashlib.sha256(AGENT.read_bytes()).hexdigest()==fingerprint
    (OUT/'results.json.gz').write_bytes(gzip.compress(json.dumps(rows).encode(),mtime=0))
    summary={'games':len(rows),'failed':sum(r['status']!='DONE' for r in rows),'comparisons':[{'episode':r['episode'],'before':r['expected'][0]-r['expected'][1],'after':r['a']-r['b']} for r in rows if r['status']=='DONE']}
    (OUT/'summary.json').write_text(json.dumps(summary,indent=2))
    assert summary['failed']==0
if __name__=='__main__':main()
