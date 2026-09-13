"""Validate completed tomato panel, freeze artifact, and report without rerunning."""
import gzip,hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    root=ROOT/'analysis/tomato_panel_20260913'
    summary=json.loads((root/'summary.json').read_text());assert summary['complete']
    protocol=json.loads((root/'protocol.json').read_text())
    for path,digest in protocol['hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    raw=json.loads(gzip.decompress((root/'raw_results.json.gz').read_bytes()))
    assert len(raw)==9
    for data in raw.values():
        assert len(data['rows'])==20 and all(r['status']=='DONE' for r in data['rows'])
        assert len({r['seed'] for r in data['rows']})==10
    direct=raw['direct']['rows']
    checks=dict(total_games=180,failures=0,
        direct_mean_margin=sum(r['a']-r['b'] for r in direct)/20,
        direct_tomato_production_games=sum(r['a_fills'].get('SELL:TOMATO:units',0)>0 for r in direct),
        direct_margins=[dict(seed=r['seed'],seat=r['order'],margin=r['a']-r['b'],tomatoes=r['a_fills'].get('SELL:TOMATO:units',0)) for r in direct],
        opponents={})
    for name in summary['comparisons']:
        c={(r['seed'],r['order']):r for r in raw['candidate_'+name]['rows']}
        b={(r['seed'],r['order']):r for r in raw['base_'+name]['rows']}
        checks['opponents'][name]=dict(tomato_production_games=sum(r['a_fills'].get('SELL:TOMATO:units',0)>0 for r in c.values()),
            own_mean_cash_gain=sum(c[k]['a']-b[k]['a'] for k in c)/20,
            own_mean_tomato_units_gain=sum(c[k]['a_fills'].get('SELL:TOMATO:units',0)-b[k]['a_fills'].get('SELL:TOMATO:units',0) for k in c)/20,
            changed_outcomes=[dict(seed=k[0],seat=k[1],candidate=c[k]['a']-c[k]['b'],base=b[k]['a']-b[k]['b']) for k in c
                if (c[k]['a']>c[k]['b'])!=(b[k]['a']>b[k]['b'])])
    (root/'audit.json').write_text(json.dumps(checks,indent=2)+'\n')
    target=root/'candidate.zip';assert not target.exists()
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for name in ('main.py','actions.json','tomato.json','LICENSE.txt'):
            z.write(ROOT/'variants/shop0909_tomato432'/name,name)
    with zipfile.ZipFile(target) as z:assert z.testzip() is None
    digest=hashlib.sha256(target.read_bytes()).hexdigest()
    lines=['# Tomato432 fresh paired panel','',
        'Ten new seeds39131000–39131009, both seats. 180 completed games, zero failures. Candidate built before this panel. No Kaggle submission.','',
        '| Matchup | Candidate W–L–T | Baseline W–L–T | Mean margin change |',
        '|---|---:|---:|---:|']
    results={r['job']:r for r in summary['results']}
    def record(r):return f"{r['wins']}–{r['losses']}–{r['ties']}"
    lines.append(f"| Direct vs baseline | {record(results['direct'])} | — | {checks['direct_mean_margin']:+.2f} |")
    for name,comparison in summary['comparisons'].items():
        lines.append(f"| {name} | {record(results['candidate_'+name])} | {record(results['base_'+name])} | {comparison['mean_margin_delta']:+.2f} |")
    gained=sum(r['gained_wins'] for r in summary['comparisons'].values());lost=sum(r['lost_wins'] for r in summary['comparisons'].values())
    lines+=['',f'Distinct-opponent matched games: **{gained} gained wins, {lost} lost wins**. Counts include all games; decisive win rate must not silently exclude ties.',
        '',f"The candidate sells tomatoes in {checks['direct_tomato_production_games']}/20 direct games. Fallback games can still be seat-asymmetric; the ±160 pair must not be attributed to the tomato branch.",
        '', 'Actual-loss diagnostics: ten original seeds, three arms,30 valid games. All baseline final scores reproduce exactly. Tomato reverses2/10 selected losses; h3 reverses2 different losses. Recorded opponents cannot react to changed candidate observations.',
        '', 'The live rank-one model was not available. Separate fixed-route reconstructions lost20/20 discovery games and are rejected; the historical Suliman/top2 panel agents are recordings too, not live leaderboard policies.',
        '', 'Do not infer a rank or guaranteed ladder gain. The candidate targets compatible default-route tomato demand; it does not address all sheep-heavy or near-clone timing failures.',
        '',f'Frozen ZIP SHA256: `{digest}`. Root files: main.py, actions.json, tomato.json, LICENSE.txt.',
        '', 'Eight state-compatibility tests pass. Protocol hashes cover source, action tables, tomato continuation and harness. `audit.json` records production and outcome flips; `raw_results.json.gz` retains all game results.']
    (root/'REPORT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(dict(artifact_sha256=digest,checks=checks,summary=summary),indent=2))
if __name__=='__main__':main()
