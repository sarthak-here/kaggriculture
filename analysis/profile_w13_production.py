"""Selected-game production diagnostics, with full crop state and unit positions."""
import copy
import profile_w13_herd as profiler

_base_snapshot = profiler._farm_snapshot


def production_snapshot(obs, seat):
    result = _base_snapshot(obs, seat)
    farm = obs.farms[seat]
    result['units'] = [list(farm['farmer']), *[list(p) for p in farm['hands']]]
    result['plants'] = [dict(xy=[x,y], **copy.deepcopy(tile))
                        for y,row in enumerate(farm['tiles'])
                        for x,tile in enumerate(row)
                        if isinstance(tile,dict) and tile.get('kind') == 'PLANT']
    return result


if __name__ == '__main__':
    profiler._farm_snapshot = production_snapshot
    profiler.main()
