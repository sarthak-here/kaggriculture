"""Matched comparisons from the durable archive; no untracked inputs needed."""
from pathlib import Path
import gzip
import json
import statistics

ROOT=Path(__file__).resolve().parents[1]

def compare(base,candidate):
    a={(r['seed'],r['order']):r for r in base['rows']}
    b={(r['seed'],r['order']):r for r in candidate['rows']}
    if a.keys()!=b.keys():raise ValueError('Mismatched seed/seat sets')
    if base['b']!=candidate['b'] or base.get('b_sha256')!=candidate.get('b_sha256'):
        raise ValueError('Mismatched opponent')
    pairs=[(a[k],b[k]) for k in sorted(a) if a[k]['status']==b[k]['status']=='DONE']
    def score(rows):
        return {'wins':sum(r['a']>r['b'] for r in rows),'losses':sum(r['a']<r['b'] for r in rows),
                'ties':sum(r['a']==r['b'] for r in rows),
                'mean_margin':statistics.mean(r['a']-r['b'] for r in rows) if rows else None}
    def outcome(r):return (r['a']>r['b'])-(r['a']<r['b'])
    def sheep(r):
        animals=r.get('b_final_farm',{}).get('animals',{})
        return animals.get('COW',0)<=6 and animals.get('SHEEP',0)>=9
    groups={}
    for name,subset in [('all',pairs),('both_runs_sheep_heavy',[(x,y) for x,y in pairs if sheep(x) and sheep(y)])]:
        groups[name]={'matched_games':len(subset),'base':score([x for x,y in subset]),
                      'candidate':score([y for x,y in subset]),
                      'outcome_flips':sum(outcome(x)!=outcome(y) for x,y in subset),
                      'worker_hash_matches':sum(x['a_workers_sha256']==y['a_workers_sha256'] for x,y in subset),
                      'shop_sequence_matches':sum(x['shops']==y['shops'] for x,y in subset)}
    return {'expected_matches':len(a),'failed_or_incomplete_matches':len(a)-len(pairs),'groups':groups}

def main():
    experiments=json.loads(gzip.decompress((ROOT/'analysis/w13_sales_raw_runs.json.gz').read_bytes()))
    output={}
    for label,base,candidate in [
        ('kaito_142000','review_base_142000.json','review_strawberry_142000.json'),
        ('gronk_230300','review_base_gronk_230300.json','review_strawberry_gronk_230300.json')]:
        output[label]=compare(experiments[base],experiments[candidate])
    (ROOT/'analysis/w13_review_matched_results.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2))

if __name__=='__main__':main()
