import pfall_impl as _PF
import kaito_impl as _KAITO


def agent(obs):
    step = int(obs.get("step", 0) if isinstance(obs, dict) else getattr(obs, "step", 0))
    return _PF.agent(obs) if step == 0 else _KAITO.agent(obs)
