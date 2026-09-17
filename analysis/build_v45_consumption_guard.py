"""Experimental long-reservation gate, preserving the submitted opening and workers."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HELPER='''
def _local_consumption_covers(obs, item, due, quantity):
    # Same-shop window is enforced by the existing reservation scheduler.
    # Strict clones suggest a competing batch of similar size, not certainty.
    state = _RACE_STATE.get(int(obs['player']), {})
    if due <= int(obs['step']) + 8 or not _local_strict_clone(obs, state):
        return False
    shops = obs['town'].get('unlocked_shops', [])
    consumed = sum(_race_town(t, shops).get(item, 0)
                   for t in range(int(obs['step']), due))
    return quantity > 0 and consumed >= quantity

'''
def main():
    base=ROOT/'variants/v45_proactive/main.py'
    raw=base.read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='831dcc2cba277f12947966a38e25f04fb7854c3116f9669a04c0d00cf611b87f'
    source=raw.decode().replace('\r\n','\n')
    anchor='            if amount:\n                reservations.append((due_step,amount));available-=amount'
    assert source.count(anchor)==1
    source=source.replace(anchor, '            if amount and _local_consumption_covers(obs, item, due_step, amount):\n                amount = 0\n'+anchor)
    source=source.replace('def _local_strict_clone(observation, state):',HELPER+'def _local_strict_clone(observation, state):')
    compile(source,'main.py','exec')
    out=ROOT/'variants/v45_consumption_guard';out.mkdir(exist_ok=False)
    (out/'main.py').write_bytes(source.encode())
    (out/'provenance.json').write_text(json.dumps({'base_sha256':hashlib.sha256(raw).hexdigest(), 'main_sha256':hashlib.sha256(source.encode()).hexdigest(), 'hypothesis':'Decline >8-turn strict-clone reservations if known town consumption covers a same-size competing batch.'},indent=2))

if __name__=='__main__':main()
