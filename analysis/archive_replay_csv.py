"""Archive reproducible evidence without expanded CSV parts or transient logs."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--directory',type=Path,required=True);args=ap.parse_args();root=args.directory
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    for r in manifest['replays']:r['path']='replays/'+Path(r['path']).name
    (root/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    groups={'replay_corpus.zip':list((root/'replays').glob('*.gz'))+[root/'manifest.json',root/'episode_service_snapshot.json',root/'leaderboard/kaggriculture.zip'],
            'csv_tables.zip':list((root/'csv_audited').glob('*.csv'))+[root/'csv_audited/export_status.json'],
            'public_notebook_sources.zip':list((root/'notebooks').rglob('*'))}
    index={}
    for name,paths in groups.items():
        if not any(p.is_file() for p in paths):
            continue
        target=root/name
        if target.exists():raise FileExistsError(target)
        with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for p in paths:
                if p.is_file():z.write(p,p.relative_to(root).as_posix())
        with zipfile.ZipFile(target) as z:
            if z.testzip() is not None:raise ValueError('Archive verification failed')
        index[name]={'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size}
    (root/'archive_index.json').write_text(json.dumps(index,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(index,indent=2))


if __name__=='__main__':main()
