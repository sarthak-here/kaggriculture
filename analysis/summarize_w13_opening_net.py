"""Validate and archive the explicitly listed opening-net experiments."""
import collections
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT/'analysis'
RUNS = {
    'mirror': 'opening_net_vs_combined_318000',
    'suliman': 'opening_net_suliman_318100',
    'suliman_control': 'combined_suliman_318100',
    'kaito': 'opening_net_kaito_318200',
    'kaito_control': 'combined_kaito_318200',
    'suliman_confirm': 'opening_net_suliman_319000',
    'suliman_confirm_control': 'combined_suliman_319000',
    'pfall': 'opening_net_pfall_319100',
    'pfall_control': 'combined_pfall_319100',
    'top2': 'opening_net_top2_319200',
    'top2_control': 'combined_top2_319200',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stats(run):
    rows = run['rows']
    done = [r for r in rows if r['status'] == 'DONE']
    counts = collections.Counter('wins' if r['a'] > r['b'] else
                                 'losses' if r['a'] < r['b'] else 'ties' for r in done)
    return dict(total=len(rows), completed=len(done), failures=len(rows)-len(done),
                wins=counts['wins'], losses=counts['losses'], ties=counts['ties'],
                wins_over_total=counts['wins']/len(rows),
                decisive_win_rate=counts['wins']/(counts['wins']+counts['losses'])
                if counts['wins']+counts['losses'] else None,
                mean_margin=sum(r['a']-r['b'] for r in done)/len(done) if done else None)


def compare(candidate, control):
    ca = {(r['seed'],r['order']):r for r in candidate['rows']}
    co = {(r['seed'],r['order']):r for r in control['rows']}
    assert ca.keys() == co.keys()
    improved = worsened = changed_shops = failed_pairs = 0
    deltas = []
    for key,c in ca.items():
        b = co[key]
        if c['status'] != 'DONE' or b['status'] != 'DONE':
            failed_pairs += 1
            continue
        outcome = lambda r: (r['a'] > r['b'])-(r['a'] < r['b'])
        improved += outcome(c) > outcome(b)
        worsened += outcome(c) < outcome(b)
        changed_shops += c['shops'] != b['shops']
        deltas.append((c['a']-c['b'])-(b['a']-b['b']))
    return dict(improved_outcomes=improved, worsened_outcomes=worsened,
                failed_pairs=failed_pairs, compared_pairs=len(deltas),
                changed_shop_sequences=changed_shops,
                mean_margin_delta=sum(deltas)/len(deltas) if deltas else None)


def main():
    archive = ANALYSIS/'w13_opening_net_raw.json.gz'
    runs = json.loads(gzip.decompress(archive.read_bytes())) if archive.exists() else {}
    for label,name in RUNS.items():
        path = ANALYSIS/(name+'.json')
        if path.exists():
            run = json.loads(path.read_text())
            assert len(run['rows']) == 20, (label, 'incomplete')
            assert len({(r['seed'],r['order']) for r in run['rows']}) == 20
            seeds = {r['seed'] for r in run['rows']}
            assert len(seeds) == 10
            assert all({r['order'] for r in run['rows'] if r['seed']==s} == {0,1} for s in seeds)
            for side in ('a','b'):
                assert digest(ROOT/run[side]) == run[side+'_sha256']
            if label in runs:
                assert runs[label] == run, (label, 'archive conflict')
            runs[label] = run
        assert label in runs, (label, 'missing experiment')
    summary = {k:stats(v) for k,v in runs.items()}
    matched = {k:compare(runs[k],runs[k+'_control'])
               for k in ('suliman','kaito','suliman_confirm','pfall','top2')}
    result = dict(experiments=summary, matched=matched,
                  total_games=sum(s['total'] for s in summary.values()))
    archive.write_bytes(gzip.compress(json.dumps(runs,separators=(',',':')).encode(),mtime=0))
    (ANALYSIS/'w13_opening_net_results.json').write_text(json.dumps(result,indent=2)+'\n')
    profiles = {}
    for label,name in [('control','suliman_production_317002'),
                       ('candidate','suliman_opening_net_317002'),
                       ('remaining_top2_loss','opening_net_top2_profile_319204')]:
        path = ANALYSIS/(name+'.json')
        if path.exists():
            profiles[label] = json.loads(path.read_text())
            profiles[label]['policy_sha256_by_seat'] = [digest(Path(p)) for p in profiles[label]['paths_by_seat']]
    if profiles:
        assert len(profiles) == 3
        target = ANALYSIS/'w13_opening_net_profiles.json.gz'
        content = gzip.compress(json.dumps(profiles,separators=(',',':')).encode(),mtime=0)
        if target.exists():
            assert target.read_bytes() == content, 'profile archive conflict'
        target.write_bytes(content)
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
