"""Profile W13 animal placement, feeding, and escapes on one paired game.

The normal isolated runner records final farms and successful market fills.  This
diagnostic keeps the same per-agent process isolation, while adding compact
per-step state and nightly animal escape events.  It is intended for selected
loss seeds, not broad tournament runs.
"""
from __future__ import annotations

import argparse
import collections
import importlib.metadata
import inspect
import json
import multiprocessing as mp
from pathlib import Path
import traceback


def child(connection, path):
    namespace = {"__name__": "w13_profile_agent", "__file__": path}
    try:
        exec(compile(Path(path).read_text(), path, "exec"), namespace)
        fn = namespace.get("_V44_POLICY", namespace.get("agent"))
        params = list(inspect.signature(fn).parameters.values())
        accepts_config = (
            len(
                [
                    p
                    for p in params
                    if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
                ]
            )
            >= 2
            or any(p.kind == p.VAR_POSITIONAL for p in params)
        )
        while True:
            request = connection.recv()
            if request is None:
                break
            obs, config = request
            connection.send(("ok", fn(obs, config) if accepts_config else fn(obs)))
    except BaseException:
        connection.send(("error", traceback.format_exc()))
    finally:
        connection.close()


def _counter(items):
    return dict(sorted(collections.Counter(items).items()))


def _farm_snapshot(obs, seat):
    farm = obs.farms[seat]
    private = obs.private
    animals = []
    empty_structures = []
    crops = collections.Counter()
    weeds = 0
    for y, row in enumerate(farm.get("tiles", []) or []):
        for x, tile in enumerate(row):
            if not isinstance(tile, dict):
                continue
            if tile.get("animal"):
                animals.append(
                    {
                        "xy": [x, y],
                        "type": tile["animal"],
                        "fed": bool(tile.get("fed_today")),
                        "unfed": int(tile.get("consecutive_unfed", 0) or 0),
                        "yield": int(tile.get("yield_units", 0) or 0),
                    }
                )
            elif tile.get("kind") in ("PASTURE", "COOP"):
                empty_structures.append([x, y, tile["kind"]])
            elif tile.get("kind") == "PLANT":
                crops[tile.get("crop", "?")] += 1
            elif tile.get("kind") == "WEED":
                weeds += 1
    return {
        "money": farm.get("money", 0),
        "hands": len(farm.get("hands", []) or []),
        "animals": animals,
        "animal_counts": _counter(a["type"] for a in animals),
        "empty_structures": empty_structures,
        "crops": dict(sorted(crops.items())),
        "weeds": weeds,
        "shed": dict(private.get("shed", {}) or {}),
        "seeds": dict(private.get("seeds", {}) or {}),
        "inventories": [dict(x or {}) for x in private.get("inventories", []) or []],
    }


def play(a, b, seed, order):
    from kaggle_environments import make
    from kaggle_environments.envs.kaggriculture import kaggriculture as engine

    ctx = mp.get_context("spawn")
    paths = [a, b] if order == 0 else [b, a]
    processes = []
    connections = []
    snapshots = [dict(), dict()]
    actions = [dict(), dict()]
    fills = []
    nights = []
    active_step = 0
    active_farms = {}

    original_market = engine._process_market
    original_commit = engine._commit_unit
    original_refresh = engine._daily_refresh_animals

    def market(state, env):
        nonlocal active_step, active_farms
        active_step = int(state[0].observation.step)
        active_farms = {
            id(farm): seat for seat, farm in enumerate(state[0].observation.farms)
        }
        return original_market(state, env)

    def commit(op, item, price, farm, private, market_state, shed_capacity=100):
        ok = original_commit(
            op, item, price, farm, private, market_state, shed_capacity
        )
        if ok:
            fills.append(
                {
                    "step": active_step,
                    "seat": active_farms[id(farm)],
                    "op": op,
                    "item": item,
                    "value": price,
                }
            )
        return ok

    def refresh_animals(farm, day):
        seat = active_farms.get(id(farm), -1)
        before = {}
        for y, row in enumerate(farm.get("tiles", []) or []):
            for x, tile in enumerate(row):
                if isinstance(tile, dict) and tile.get("animal"):
                    before[(x, y)] = {
                        "type": tile["animal"],
                        "fed": bool(tile.get("fed_today")),
                        "unfed": int(tile.get("consecutive_unfed", 0) or 0),
                    }
        original_refresh(farm, day)
        after_positions = {
            (x, y)
            for y, row in enumerate(farm.get("tiles", []) or [])
            for x, tile in enumerate(row)
            if isinstance(tile, dict) and tile.get("animal")
        }
        escaped = [
            {"xy": list(xy), **detail}
            for xy, detail in before.items()
            if xy not in after_positions
        ]
        nights.append(
            {
                "day": int(day),
                "seat": seat,
                "before_counts": _counter(x["type"] for x in before.values()),
                "unfed_before": _counter(
                    x["type"] for x in before.values() if not x["fed"]
                ),
                "escaped": escaped,
            }
        )

    engine._process_market = market
    engine._commit_unit = commit
    engine._daily_refresh_animals = refresh_animals
    try:
        policies = []
        for seat, path in enumerate(paths):
            parent, kid = ctx.Pipe()
            process = ctx.Process(target=child, args=(kid, path))
            process.start()
            kid.close()
            processes.append(process)
            connections.append(parent)

            def policy(obs, config, seat=seat, connection=parent):
                step = int(obs.step)
                snapshots[seat][step] = _farm_snapshot(obs, seat)
                connection.send((obs, config))
                if not connection.poll(5):
                    raise TimeoutError("agent IPC exceeded 5 seconds")
                status, value = connection.recv()
                if status != "ok":
                    raise RuntimeError(value)
                actions[seat][step] = value
                return value

            def bind(fn):
                def wrapped(obs, config):
                    return fn(obs, config)

                return wrapped

            policies.append(bind(policy))

        env = make("kaggriculture", configuration={"seed": seed}, debug=False)
        env.run(policies)
        rewards = [state.reward for state in env.state]
        statuses = [state.status for state in env.state]
        if any(status != "DONE" for status in statuses):
            raise RuntimeError({"statuses": statuses, "rewards": rewards})
        ai = order
        bi = 1 - order
        return {
            "seed": seed,
            "order": order,
            "paths_by_seat": paths,
            "rewards_by_seat": rewards,
            "a_reward": rewards[ai],
            "b_reward": rewards[bi],
            "shops": list(env.state[0].observation.town.unlocked_shops),
            "snapshots_by_seat": snapshots,
            "actions_by_seat": actions,
            "fills": fills,
            "nights": nights,
        }
    finally:
        engine._process_market = original_market
        engine._commit_unit = original_commit
        engine._daily_refresh_animals = original_refresh
        for connection in connections:
            try:
                connection.send(None)
            except (EOFError, BrokenPipeError, OSError):
                pass
            connection.close()
        for process in processes:
            process.join(1)
            if process.is_alive():
                process.terminate()
                process.join()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("a")
    parser.add_argument("b")
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--order", type=int, choices=(0, 1), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if importlib.metadata.version("kaggle-environments") != "1.32.7":
        raise RuntimeError("This diagnostic is pinned to kaggle-environments 1.32.7")
    if args.output.exists():
        raise FileExistsError(args.output)
    result = play(
        str(Path(args.a).resolve()),
        str(Path(args.b).resolve()),
        args.seed,
        args.order,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        {
            "a": result["a_reward"],
            "b": result["b_reward"],
            "margin": result["a_reward"] - result["b_reward"],
            "shops": result["shops"],
            "escapes": [x for x in result["nights"] if x["escaped"]],
        },
        flush=True,
    )


if __name__ == "__main__":
    main()
