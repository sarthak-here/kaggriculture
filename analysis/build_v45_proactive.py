"""Build a separate strict-clone anticipatory sale-reservation experiment."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HELPER='''
# Local experiment: advance the existing reservation horizon only on strict clones.
def _local_strict_clone(observation, state):
    history = state.get('hist', [])
    return len(history) == 6 and all(history) and _r37_similarity(observation) == 1.0

'''
def main():
    base=ROOT/'public_candidates/cloning_v45_20260916/main.py'
    original=base.read_bytes()
    assert hashlib.sha256(original).hexdigest()=='2536d41ed5a00c75204b6350f1c76c54259c774cb065ba2a3a0072eedf210d94'
    s=original.decode();anchor="            _RACE_REPORT['race_clone_turns']+=1"
    assert s.count(anchor)==1
    s=s.replace('def _race_positions_equal(farms,player):',HELPER+'def _race_positions_equal(farms,player):')
    s=s.replace(anchor,anchor+"\n            if state['level'] < _RACE_HORIZON_ESCALATED and _local_strict_clone(observation, state):\n                state['level'] = _RACE_HORIZON_ESCALATED\n                _RACE_REPORT['local_proactive_escalations'] = _RACE_REPORT.get('local_proactive_escalations', 0) + 1")
    compile(s,'main.py','exec');out=ROOT/'variants/v45_proactive';out.mkdir(exist_ok=False)
    (out/'main.py').write_bytes(s.encode())
    (out/'provenance.json').write_text(json.dumps(dict(base_sha256=hashlib.sha256(original).hexdigest(),
        main_sha256=hashlib.sha256(s.encode()).hexdigest(),change='strict six-observation clones use existing24-turn reservations proactively'),indent=2)+'\n')
    print(out)
if __name__=='__main__':main()
