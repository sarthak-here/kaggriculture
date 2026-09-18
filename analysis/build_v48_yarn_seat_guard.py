"""Build a narrow V48 probe for seat-1 YARN market-priority reversals."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public_candidates/v48_clear_queue_20260918/main.py"
OUT = ROOT / "variants/v48_yarn_seat_guard/main.py"

WRAPPER = r'''

# EXP336 probe: V48 queue compaction can reverse one YARN-first game in seat 1.
# Preserve the V47 queue for that observable market-priority condition only.
_E336_V48 = _e335_agent
_E336_REPORT = {'fallback_turns': 0, 'errors': 0}

def agent(observation, configuration=None):
    try:
        shops = list((observation.get('town') or {}).get('unlocked_shops', []) or [])
        if int(observation.get('player', 0)) == 1 and shops[:1] == ['YARN_STORE']:
            _E336_REPORT['fallback_turns'] += 1
            return _E334_BASE(observation, configuration)
    except Exception:
        _E336_REPORT['errors'] += 1
    return _E336_V48(observation, configuration)

agent.telemetry = _E336_REPORT
agent = globals().pop('agent')
'''


def main():
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(raw + WRAPPER.encode("utf-8"))
    provenance = {
        "parent": str(SOURCE.relative_to(ROOT)),
        "parent_sha256": hashlib.sha256(raw).hexdigest(),
        "candidate_sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
        "hypothesis": "Disable V48 queue compaction only for seat 1 while YARN_STORE is the first unlocked shop.",
        "status": "probe; not promoted",
    }
    (OUT.parent / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(provenance)


if __name__ == "__main__":
    main()
