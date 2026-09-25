"""Build a transparent adaptive-flow layer on the frozen demand_timing agent.

The layer source is extracted literally (never executed) from the public
Pioneers notebook and appended to our audited incumbent. Existing license and
provenance notices remain intact in the generated file.
"""

import ast
from pathlib import Path

from audit_agent_safety import unwrap_exec_arg


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "public_candidates/current_20260924/demand_timing/main.py"
SOURCE = ROOT / "public_candidates/current_20260925/pioneers2/main.py"
OUT = ROOT / "variants/adaptive_flow_20260925/main.py"


def layer_source():
    text = SOURCE.read_text(encoding="utf-8-sig")
    tree = ast.parse(text)
    aliases = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                aliases[alias.asname or alias.name] = alias.name
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = node.func.id if isinstance(node.func, ast.Name) else ""
        if name != "exec" or not node.args:
            continue
        decoded = unwrap_exec_arg(node.args[0], aliases)
        if decoded and "class FlowLayer" in decoded and "class QuietOpening" in decoded:
            return decoded
    raise RuntimeError("adaptive layer literal not found")


WRAPPER = r'''

# Adaptive rival-supply experiment, 2026-09-25.
# The parent policy above is frozen. This transparent layer replaces only
# premium-product sale quantities and the opening wheat round-trip. It uses
# public observations, bounded simulations, and falls back exactly on error.
_AF_PARENT = agent
_AF_LAYER = FlowLayer(flow=True, reserve=True, planner="model", floor_frac=0.3)
_AF_QUIET = QuietOpening(buy=6, sell=5)
_AF_REPORT = _AF_LAYER.telemetry


def _af_tape_future(player, step, horizon=24):
    chassis = _IMPL.chassis
    native = chassis.players.get(player) or {}
    route = native.get("route", 0)
    out = []
    for turn in range(step + 1, min(719, step + 1 + horizon)):
        tape = chassis.routes.get(2 if turn >= 648 else route) or chassis.routes.get(route)
        action = tape[turn] if tape and turn < len(tape) and isinstance(tape[turn], dict) else {}
        out.append(action.get("market") or [])
    return out


def adaptive_flow_agent(observation, configuration=None):
    original = _AF_PARENT(observation, configuration)
    action = original
    try:
        player = int(observation["player"])
        step = int(observation["step"])
        action = _AF_QUIET.apply(observation, action)
        projected = _IMPL.chassis._projected_shed(
            action, FarmView(observation)
        ) if hasattr(_IMPL.chassis, "_projected_shed") else projected_shed(
            action, FarmView(observation)
        )
        action = _AF_LAYER.apply(
            observation, action, projected, _af_tape_future(player, step)
        )
        if action is not original:
            state = _RACE_STATE.get(player)
            if state and state.get("step") == step and state.get("prev_action") is not None:
                state["prev_action"] = action
    except Exception:
        _AF_LAYER.telemetry["errors"] += 1
        return original
    return action


adaptive_flow_agent.telemetry = _AF_REPORT
agent = adaptive_flow_agent
kaggle_submission_agent = adaptive_flow_agent
'''


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    result = BASE.read_text(encoding="utf-8-sig").rstrip() + "\n\n" + layer_source().rstrip() + WRAPPER
    OUT.write_text(result, encoding="utf-8")
    print(OUT)
    print(f"{len(result)} characters")


if __name__ == "__main__":
    main()
