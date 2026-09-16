"""Extract pinned source literals without executing notebook cells."""
import ast,gzip,hashlib,io,json,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('C:/Users/sarthak/Desktop/kaggriculture-cloning-agent.ipynb')
OUT=ROOT/'public_candidates/cloning_v45_20260916'
EXPECTED='2536d41ed5a00c75204b6350f1c76c54259c774cb065ba2a3a0072eedf210d94'

def main():
    raw=SOURCE.read_bytes();notebook=json.loads(raw);payloads=[]
    for cell in notebook['cells']:
        if cell['cell_type']!='code':continue
        for node in ast.parse(''.join(cell['source'])).body:
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SOURCE_BYTES' for t in node.targets):
                call=node.value
                assert isinstance(call,ast.Call) and isinstance(call.func,ast.Attribute)
                assert call.func.attr=='join' and ast.literal_eval(call.func.value)==b''
                chunks=ast.literal_eval(call.args[0]);assert all(isinstance(c,bytes) for c in chunks)
                payloads.append(b''.join(chunks))
    assert len(payloads)==1;source=payloads[0]
    assert hashlib.sha256(source).hexdigest()==EXPECTED
    compile(source,'main.py','exec')
    OUT.mkdir(exist_ok=False)
    (OUT/'source.ipynb').write_bytes(raw);(OUT/'main.py').write_bytes(source)
    notices='\n\n'.join(''.join(c['source']) for c in notebook['cells']
        if c['cell_type']=='markdown' and 'Attribution and license' in ''.join(c['source']))
    assert 'Apache' in notices
    (OUT/'UPSTREAM_NOTICES.md').write_text(notices,encoding='utf-8')
    archive=OUT/'submission_competitive_v45.tar.gz'
    with archive.open('wb') as f:
        with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as gz:
            with tarfile.open(fileobj=gz,mode='w',format=tarfile.GNU_FORMAT) as tar:
                info=tarfile.TarInfo('main.py');info.size=len(source);info.mode=0o644;info.mtime=0
                tar.addfile(info,io.BytesIO(source))
    archive_hash=hashlib.sha256(archive.read_bytes()).hexdigest()
    assert archive_hash=='b8c2f5aab88faf2332e45f721ec83e5f9e7bec3d0a995cc0dce318badd884ed0'
    imports=set();calls=set();trees=[ast.parse(source)];embedded=0
    while trees:
        tree=trees.pop()
        for n in ast.walk(tree):
            if isinstance(n,ast.Import):imports.update(a.name for a in n.names)
            elif isinstance(n,ast.ImportFrom):imports.add(n.module or '')
            elif isinstance(n,ast.Call):
                calls.add(ast.unparse(n.func))
                if isinstance(n.func,ast.Name) and n.func.id=='exec':
                    assert isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,str)
                    trees.append(ast.parse(n.args[0].value));embedded+=1
    manifest=dict(source_notebook_sha256=hashlib.sha256(raw).hexdigest(),main_sha256=EXPECTED,
        archive_sha256=archive_hash,imports=sorted(imports),embedded_sources=embedded,
        validation='Pinned source and archive verified; notebook code not executed; games not yet run')
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (OUT/'static_calls.json').write_text(json.dumps(sorted(calls),indent=2)+'\n')
    print(json.dumps(manifest,indent=2))
if __name__=='__main__':main()
