"""Save completed independent-seed Skyspace recording check and discovery evidence."""
import gzip,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    root=ROOT/'analysis/tomato_panel_20260913';raw={}
    for arm in ('candidate','base'):
        raw[arm]=json.loads((ROOT/f'analysis/tomato_skyspace_{arm}_20260913.json').read_text())
        rows=raw[arm]['rows'];assert len(rows)==20 and all(r['status']=='DONE' for r in rows)
        assert {r['seed'] for r in rows}==set(range(39133000,39133010))
        assert len({(r['seed'],r['order']) for r in rows})==20
    by={arm:{(r['seed'],r['order']):r for r in data['rows']} for arm,data in raw.items()}
    c,b=by['candidate'],by['base']
    records={arm:dict(wins=sum(r['a']>r['b'] for r in data['rows']),losses=sum(r['a']<r['b'] for r in data['rows']),ties=sum(r['a']==r['b'] for r in data['rows'])) for arm,data in raw.items()}
    comparison=dict(gained_wins=sum(c[k]['a']>c[k]['b'] and b[k]['a']<=b[k]['b'] for k in c),lost_wins=sum(c[k]['a']<=c[k]['b'] and b[k]['a']>b[k]['b'] for k in c),mean_margin_delta=sum(c[k]['a']-c[k]['b']-b[k]['a']+b[k]['b'] for k in c)/20,
        changed_shops=sum(c[k]['shops']!=b[k]['shops'] for k in c),records=records,completed=40,failures=0)
    paths=['variants/shop0909_tomato432/main.py','variants/shop0909_tomato432/tomato.json','variants/shop0909_tomato432/actions.json','variants/shop0909_opening_net/main.py','analysis/tomato_diagnostics_20260913/108145550/main.py','analysis/tomato_diagnostics_20260913/108145550/tape.json','analysis/run_w13_isolated.py']
    comparison['hashes']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    comparison['scope']='Ten fresh seeds, both seats, fixed recorded Skyspace actions; not the live policy.'
    (root/'skyspace_summary.json').write_text(json.dumps(comparison,indent=2)+'\n')
    (root/'skyspace_raw.json.gz').write_bytes(gzip.compress(json.dumps(raw).encode(),mtime=0))
    leader=ROOT/'analysis/leader_screen_20260913'
    probes={p.name:json.loads(p.read_text()) for p in leader.glob('*.json')}
    probes['index']=json.loads((ROOT/'variants/leader_20260913/index.json').read_text())
    (leader/'raw_results.json.gz').write_bytes(gzip.compress(json.dumps(probes).encode(),mtime=0))
    print(json.dumps(comparison,indent=2))
if __name__=='__main__':main()
