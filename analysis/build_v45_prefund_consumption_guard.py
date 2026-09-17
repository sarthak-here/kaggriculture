"""Apply the prior town-consumption sale gate on the corrected prefund world."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE_SHA='1a9c3a3ef6902d958d6269421a196aa683492e927f660f566c3029698498bf04'
HELPER='''
def _local_consumption_covers(obs, item, due, quantity):
    state = _RACE_STATE.get(int(obs['player']), {})
    if due <= int(obs['step']) + 8 or not _local_strict_clone(obs, state):
        return False
    shops = obs['town'].get('unlocked_shops', [])
    consumed = sum(_race_town(t, shops).get(item, 0)
                   for t in range(int(obs['step']), due))
    return quantity > 0 and consumed >= quantity

'''
def main():
    base=ROOT/'variants/v45_prefund_10_exported/main.py';raw=base.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==BASE_SHA
    source=raw.decode().replace('\r\n','\n')
    anchor='            if amount:\n                reservations.append((due_step,amount));available-=amount'
    assert source.count(anchor)==1
    source=source.replace(anchor,'            if amount and _local_consumption_covers(obs, item, due_step, amount):\n                amount = 0\n'+anchor)
    strict='def _local_strict_clone(observation, state):'
    assert source.count(strict)==1
    source=source.replace(strict,HELPER+strict)
    compile(source,'main.py','exec')
    out=ROOT/'variants/v45_prefund_consumption_guard';out.mkdir(exist_ok=False)
    encoded=source.encode();(out/'main.py').write_bytes(encoded)
    (out/'provenance.json').write_text(json.dumps({'base_sha256':BASE_SHA,'main_sha256':hashlib.sha256(encoded).hexdigest(),'hypothesis':'Keep corrected prefund opening; decline >8-turn strict-clone reservations when known town consumption covers an equal competing batch.'},indent=2)+'\n')
if __name__=='__main__':main()
