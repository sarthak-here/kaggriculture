"""Compact evidence, retaining initial failures and identifying shop-sequence drift."""
import gzip,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    folder=ROOT/'analysis/v45_prefund_10_screen_20260917'
    initial=json.loads((folder/'results.json').read_text());retry=json.loads((folder/'retry_results.json').read_text())
    resolved={r['episode']:r for r in initial}
    for r in retry:
        assert resolved[r['episode']]['status']!='DONE'
        resolved[r['episode']]=r
    corpus=ROOT/'analysis/v45_live_20260916';manifest=json.loads((corpus/'manifest.json').read_text(encoding='utf-8'))
    comparisons=[]
    for ep,r in resolved.items():
        assert r['status']=='DONE'
        entry=next(e for e in manifest['replays'] if any(l['episode_id']==ep for l in e['labels']))
        label=next(l for l in entry['labels'] if l['submission']==56278443)
        replay=json.loads(gzip.decompress((corpus/entry['path']).read_bytes()))
        shops=replay['steps'][-1][0]['observation']['town']['unlocked_shops']
        comparisons.append({'episode':ep,'opponent':label['opponent'],'before':r['expected'][0]-r['expected'][1],
                            'after':r['a']-r['b'],'shops_changed':shops!=r['shops'],
                            'melon_units_sold':r['a_fills'].get('SELL:MELON:units',0)})
    summary={'initial_attempts':len(initial),'initial_failures':[r for r in initial if r['status']!='DONE'],
             'retry_count':len(retry),'completed_after_retry':len(comparisons),'wins':sum(r['after']>0 for r in comparisons),
             'repairs':sum(r['before']<0 and r['after']>0 for r in comparisons),
             'regressions':sum(r['before']>0 and r['after']<=0 for r in comparisons),
             'changed_shop_sequences':sum(r['shops_changed'] for r in comparisons),'comparisons':comparisons}
    (folder/'resolved_summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
