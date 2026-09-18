"""Build a V48-default router with a state-compatible prefund specialist.

V48 runs at step 0. On a verified MINGXI-family opening, prefund takes over at
step 1, the final observation where its own physical state is proven identical
to V48's on the source loss. The unused specialist is never evaluated.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import zlib


ROOT = Path(__file__).resolve().parents[1]
V48 = ROOT / "public_candidates/v48_clear_queue_20260918/main.py"
PREFUND = ROOT / "variants/v45_prefund_10_exported/main.py"
OUTPUT = ROOT / "variants/v48_mingxi_prefund_router/main.py"
HASHES = {
    "v48": "4b5402888feeb4170dce38f34bebe56788b62ca287139fce7db72df8eb89bb96",
    "prefund": "1a9c3a3ef6902d958d6269421a196aa683492e927f660f566c3029698498bf04",
}


def packed(source: bytes) -> str:
    return base64.b85encode(zlib.compress(source, 9)).decode("ascii")


def main() -> int:
    v48 = V48.read_bytes()
    prefund = PREFUND.read_bytes()
    assert hashlib.sha256(v48).hexdigest() == HASHES["v48"]
    assert hashlib.sha256(prefund).hexdigest() == HASHES["prefund"]
    source = f'''# EXP337: V48 default with a step-1 state-compatible prefund specialist.
import base64 as _e337_b64,zlib as _e337_z
_E337_V48_NS={{'__name__':'_e337_v48','__file__':'<v48>'}}
_E337_PREFUND_NS={{'__name__':'_e337_prefund','__file__':'<prefund>'}}
exec(compile(_e337_z.decompress(_e337_b64.b85decode({packed(v48)!r})).decode('utf-8'),'<v48>','exec'),_E337_V48_NS)
exec(compile(_e337_z.decompress(_e337_b64.b85decode({packed(prefund)!r})).decode('utf-8'),'<prefund>','exec'),_E337_PREFUND_NS)
_E337_V48=[v for v in _E337_V48_NS.values() if callable(v)][-1]
_E337_PREFUND=[v for v in _E337_PREFUND_NS.values() if callable(v)][-1]
_E337_LATCH={{}}
_E337_LAST={{}}
_E337_REPORT={{'checks':0,'activations':0,'specialist_steps':0,'errors':0}}

def _e337_get(obj,key,default=None):
    return obj.get(key,default) if isinstance(obj,dict) else getattr(obj,key,default)

def _e337_match(obs,seat):
    farms=list(_e337_get(obs,'farms',[]) or [])
    if len(farms)!=2:return False
    rival=farms[1-seat]
    return (float(_e337_get(rival,'money',-1)) in {2445.0,2455.0,2461.0,2467.0}
            and len(_e337_get(rival,'hands',[]) or [])==0
            and len(_e337_get(rival,'unlocked_quadrants',[]) or [])==1
            and list(_e337_get(rival,'farmer',[]) or [])==[4,4])

def agent(observation,configuration=None):
    seat=1 if int(_e337_get(observation,'player',0) or 0)==1 else 0
    step=int(_e337_get(observation,'step',0) or 0)
    try:
        if step==0 or step<=_E337_LAST.get(seat,-1):
            _E337_LATCH[seat]=False
            _E337_REPORT.update(checks=0,activations=0,specialist_steps=0,errors=0)
        _E337_LAST[seat]=step
        if step==0:
            # Do not warm the unused specialist. The policies share imported
            # module objects inside one submission process; evaluating prefund
            # here can perturb V48 even when the detector never activates.
            return _E337_V48(observation,configuration)
        if step==1:
            base=_E337_V48(observation,configuration)
            _E337_REPORT['checks']+=1
            _E337_LATCH[seat]=_e337_match(observation,seat)
            if _E337_LATCH[seat]:
                _E337_REPORT['activations']+=1
                _E337_REPORT['specialist_steps']+=1
                result=_E337_PREFUND(observation,configuration)
                agent.telemetry=dict(_E337_REPORT)
                return result
            agent.telemetry=dict(_E337_REPORT)
            return base
        if _E337_LATCH.get(seat,False):
            _E337_REPORT['specialist_steps']+=1
            result=_E337_PREFUND(observation,configuration)
        else:
            result=_E337_V48(observation,configuration)
        agent.telemetry=dict(_E337_REPORT)
        return result
    except Exception as exc:
        _E337_REPORT['errors']+=1
        _E337_REPORT['last_error']=repr(exc)
        agent.telemetry=dict(_E337_REPORT)
        farm=list(_e337_get(observation,'farms',[]) or [{{}}])[seat]
        return {{'farmer':['PASS'],'hands':[['PASS'] for _ in (_e337_get(farm,'hands',[]) or [])],'market':[]}}

agent.telemetry=_E337_REPORT
agent=globals().pop('agent')
'''
    encoded = source.encode("utf-8")
    compile(source, str(OUTPUT), "exec")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(encoded)
    manifest = {
        "experiment": 337,
        "v48_sha256": HASHES["v48"],
        "prefund_sha256": HASHES["prefund"],
        "main_sha256": hashlib.sha256(encoded).hexdigest(),
        "activation": "step 1 rival money in {2445,2455,2461,2467}, no hands, one quadrant, farmer=[4,4]",
        "compatibility": "V48 and prefund own physical state equal through observation step 1 on episode 110380424",
    }
    (OUTPUT.parent / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
