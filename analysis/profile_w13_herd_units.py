"""Run the herd profiler while also recording globally indexed unit positions."""
from __future__ import annotations

import profile_w13_herd as profiler

_base_snapshot = profiler._farm_snapshot


def snapshot_with_units(obs, seat):
    result = _base_snapshot(obs, seat)
    farm = obs.farms[seat]
    result["units"] = [
        list(farm.get("farmer", [0, 0]) or [0, 0]),
        *[list(position or [0, 0]) for position in farm.get("hands", []) or []],
    ]
    return result


if __name__ == "__main__":
    profiler._farm_snapshot = snapshot_with_units
    profiler.main()
