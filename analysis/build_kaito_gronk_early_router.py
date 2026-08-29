"""Use Gronk's market-only opening, then retain its suffix only for PIZZA/YARN."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from build_kaito_gronk_router import BRANCH_STEP, ROUTER, encoded
from extract_kaito_v46 import assignment, decode_json
from mine_compatible_routes import route_of


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "variants" / "kaito_soil_router" / "main.py"
REPLAY = ROOT / "loss_analysis" / "kaito_soil_router_current" / "episode-102674510-replay.json"
TARGET = ROOT / "variants" / "kaito_gronk_early_router" / "main.py"


def main() -> int:
    source = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source)
    node = assignment(tree, "_V44_ROUTES")
    routes = decode_json(node)
    replay = json.loads(REPLAY.read_text(encoding="utf-8"))
    gronk = route_of(replay, 0)

    # Unit actions are identical through BRANCH_STEP.  Only the purchase timing
    # changes, so every route can safely share Gronk's cheaper opening market plan.
    early_routes = {name: gronk[:BRANCH_STEP] + route[BRANCH_STEP:]
                    for name, route in routes.items()}
    gronk_routes = {name: gronk for name in routes}

    lines = source.splitlines(keepends=True)
    newline = "\r\n" if lines[node.lineno - 1].endswith("\r\n") else "\n"
    lines[node.lineno - 1:node.end_lineno] = [encoded("_V44_ROUTES", early_routes) + newline]
    source = "".join(lines)
    policy_start = source.index("_V44_POLICY = _v44_build(_V44_ROUTES, _V44_CONFIG)")
    entrypoint = source.index("def _kaggle_submission_entrypoint", policy_start)
    patched = (source[:policy_start]
               + encoded("_V44_GRONK_ROUTES", gronk_routes)
               + "\n\n" + ROUTER + "\n\n" + source[entrypoint:])
    compile(patched, str(TARGET), "exec")
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(patched, encoding="utf-8")
    print(TARGET.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
