"""Freeze completed opening experiments and a reproducible candidate archive."""
import gzip,hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'analysis/shop0909_opening_panel_20260912'
    summary=json.loads((out/'summary.json').read_text());assert summary['complete']
    raw=json.loads(gzip.decompress((out/'raw_results.json.gz').read_bytes()))
    protocol=json.loads((out/'protocol.json').read_text())
    for path,digest in protocol['hashes'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    diagdir=ROOT/'analysis/shop0909_opening_diagnostics_20260912'
    diagnostic=json.loads(gzip.decompress((diagdir/'results.json.gz').read_bytes()))
    assert len(diagnostic)==10 and all(r['status']=='DONE' for r in diagnostic)
    step0=json.loads((diagdir/'one_turn.json').read_text(encoding='utf-8'))
    assert len(step0)==29 and all(r['net_wheat']==13 and r['gain']>=0 for r in step0)
    stats={}
    for family,comp in summary['comparisons'].items():
        cr=raw['candidate_'+family]['rows'];br=raw['base_'+family]['rows']
        c={(r['seed'],r['order']):r for r in cr};b={(r['seed'],r['order']):r for r in br}
        assert set(c)==set(b) and len(c)==20
        comp['identical_rewards']=sum((c[k]['a'],c[k]['b'])==(b[k]['a'],b[k]['b']) for k in c)
        comp['identical_opening_checkpoints']=sum(c[k]['a_checkpoints']==b[k]['a_checkpoints'] for k in c)
    folder=ROOT/'variants/shop0909_opening_net';archive=out/'candidate.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name in ('main.py','actions.json','LICENSE.txt'):
            info=zipfile.ZipInfo(name,date_time=(2026,9,12,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,(folder/name).read_bytes())
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None and set(z.namelist())=={'main.py','actions.json','LICENSE.txt'}
    metadata=json.loads((folder/'provenance.json').read_text());metadata.update(archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),submitted=False)
    (out/'candidate_manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    text=['# Shop0909 opening-net evaluation — September 12, 2026','',
        'Only the exact step0 BUY13/SELL13/BUY13 wheat sequence becomes BUY13.',
        'Every later rule, action tape and license is preserved. The base is the exact',
        'Shop0909 submission56159253 archive. Original pf_all is used, never pf_all2.',
        'Ten contract tests pass across baseline and candidate. No Kaggle submission.','',
        '## Fresh paired panel','',
        'Seeds39119000–39119009, both seats,180 full games. Process-isolated agents.',
        'All planned games completed with zero failures. Ties remain in the denominator.','',
        '| Matchup | Wins | Losses | Ties | Games |','| --- | ---: | ---: | ---: | ---: |']
    for r in summary['results']:
        text.append(f"| {r['job']} | {r['wins']} | {r['losses']} | {r['ties']} | {r['completed']} |")
    text+=['','| Family | Gained wins | Lost wins | Changed shops | Identical reward pairs | Mean margin delta |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    for n,c in summary['comparisons'].items():
        text.append(f"| {n} | {c['gained_wins']} | {c['lost_wins']} | {c['changed_shops']} | {c['identical_rewards']}/20 | {c['mean_margin_delta']:.1f} |")
    text+=['','Retained candidate losses against the top2 fixed tape:',
        '| Seed | Seat | Deficit | Milk ours/opponent | Strawberries ours/opponent |',
        '| --- | ---: | ---: | --- | --- |']
    for r in raw['candidate_top2_fixed']['rows']:
        if r['a']<r['b']:
            af,bf=r['a_fills'],r['b_fills']
            text.append(f"| {r['seed']} | {r['order']} | {r['b']-r['a']:.0f} | {af.get('SELL:MILK:units',0)}/{bf.get('SELL:MILK:units',0)} | {af.get('SELL:STRAWBERRY:units',0)}/{bf.get('SELL:STRAWBERRY:units',0)} |")
    text+=['','Kaito means the existing submit_v46_three_suffix panel opponent. Suliman',
        'and top2 are recorded-route reconstructions, not their live policies.',
        'Source and runner hashes are frozen in protocol.json. A source hash alone',
        'does not substitute for comparing actual outputs.','',
        '## Saved-opening audit and full-game fixed-tape diagnostics','',
        'Across29 saved first transitions: five improve cash,24 are unchanged,',
        'none worsen, and all preserve13 net wheat. The maximum saving is52 coins.',
        'These one-turn checks use the original market state and recorded opponent action.','',
        'Five affected opponent tapes then run against both builds at seed39120000,',
        'in their original seats. The original live seeds are absent, so these are',
        'new seeded diagnostics, not exact live replay reruns or held-out strength tests.','',
        '| Source episode | Arm | Our reward | Opponent reward | Day1 hands | Cows at step48 |',
        '| --- | --- | ---: | ---: | ---: | ---: |']
    for r in diagnostic:
        text.append(f"| {r['episode_id']} | {r['arm']} | {r['a']:.0f} | {r['b']:.0f} | {r['a_checkpoints']['25']['hands']} | {r['a_checkpoints']['48']['herd'].get('COW',0)} |")
    text+=['','Baseline0–5 becomes candidate2–3. Both severe zero-hire/cow-loss cases',
        'reverse. The two way-to-you cases and infamemconculcemus remain losses.',
        'Their fresh seeded shop sequences can change when farming changes weed RNG',
        'consumption; final margin improvements are not isolated price/cash effects.','',
        '## Decision','',
        'This is a narrowly supported opening-resilience change, not proof of broad',
        'dominance or top10 strength. Direct games against the unchanged upload tie.',
        'Retain the candidate separately. Do not claim that cash savings reverse every',
        'loss or infer leaderboard improvement from fixed-tape counterfactuals.',
        'No further model changes are bundled. No submission without explicit approval.','',
        '## Reproduction','',
        'Run build_shop0909_opening_net.py to reconstruct from the tracked original archive.',
        'Run test_shop0909_baseline.py and test_shop0909_opening_net.py.',
        'run_shop0909_opening_panel.py freezes a new seed protocol and refuses an existing output.',
        'run_shop0909_opening_diagnostics.py generates tapes from the archived loss corpus.',
        'audit_shop0909_step0.py audits the first transitions. This finalizer checks',
        'all source hashes and packages candidate.zip with deterministic ZIP timestamps.',
        'Raw results are stored as gzip, including checkpoints, fills, worker hashes',
        'and shop sequences. candidate_manifest.json contains exact archive/member hashes.','']
    (out/'REPORT.md').write_text('\n'.join(text),encoding='utf-8')
    print(json.dumps(summary,indent=2))
    print(json.dumps(metadata,indent=2))
if __name__=='__main__':main()
