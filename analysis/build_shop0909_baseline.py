"""Reproduce inspected notebook files without executing notebook cells."""
import argparse
import ast
import base64
import gzip
import hashlib
import json
from pathlib import Path
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def literal(source,name):
    for node in ast.parse(source).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets):return ast.literal_eval(node.value)
    raise ValueError(name)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=ROOT/'public_candidates/shop0909_20260910');args=ap.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    archive=ROOT/'analysis/replay_csv_56139834/public_notebook_sources.zip'
    with zipfile.ZipFile(archive) as z:raw=z.read('notebooks/yhay81/shop-router-0909.ipynb')
    notebook=json.loads(raw);cells=[''.join(c['source']) for c in notebook['cells']]
    source=next(c.split('\n',1)[1] for c in cells if c.startswith('%%writefile main.py\n'))
    data=next(c for c in cells if 'data_payload = ' in c)
    files=json.loads(gzip.decompress(base64.b64decode(literal(data,'data_payload'))));files['main.py']=source
    expected=literal(next(c for c in cells if 'expected_hashes = ' in c),'expected_hashes')
    if set(files)!=set(expected) or set(files)!={'main.py','actions.json','LICENSE.txt'}:raise ValueError('Unexpected files')
    actual={name:hashlib.sha256(content.encode('utf-8')).hexdigest() for name,content in files.items()}
    if actual!=expected:raise ValueError({'expected':expected,'actual':actual})
    plans=json.loads(files['actions.json']);assert len(plans)==13 and all(len(p)==719 for p in plans)
    compile(source,'main.py','exec');args.output.mkdir(parents=True)
    for name,content in files.items():(args.output/name).write_bytes(content.encode('utf-8'))
    metadata={'source':'https://www.kaggle.com/code/yhay81/shop-router-0909','snapshot':'2026-09-10','notebook_sha256':hashlib.sha256(raw).hexdigest(),'members':actual,'unchanged':True}
    (args.output/'provenance.json').write_text(json.dumps(metadata,indent=2)+'\n');print(json.dumps(metadata,indent=2))

if __name__=='__main__':main()
