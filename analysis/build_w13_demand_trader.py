"""Reproducible demand-trading probes; no incumbent writes or submissions."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

WRAPPER = '''
from v24 import market_maker as _dt_mm

def _dt_demand(obs, configuration, item):
    step = int(_dt_mm.get(obs, "step", 0))
    shops = _dt_mm.get(_dt_mm.get(obs, "town", {}), "unlocked_shops", [])
    si = max(1, int(_dt_mm.get(configuration, "townShopSellInterval", 4)))
    ci = max(1, int(_dt_mm.get(configuration, "townCenterSellInterval", 24)))
    demand = sum((2 if len(_dt_mm.SHOP_PRODUCTS[s]) == 1 else 1)
                 for s in shops if item in _dt_mm.SHOP_PRODUCTS.get(s, ())) if step % si == 0 else 0
    return demand + int(item != "FERTILIZER" and step % ci == 0)

class _DemandTrader:
    def __init__(self, base, actions, gated):
        self.base, self.gated = base, gated
        self.expert = _dt_mm.MarketMakerExpert(actions, _dt_mm.MarketMakerConfig(
            max_batch=40, minimum_cash_reserve=5000, shed_headroom=30,
            minimum_expected_profit=5, mirror_minimum_expected_profit=5))
        self.history = {0: [], 1: []}
        self.delay_telemetry = self.expert.telemetry
        self.delay_telemetry.update(supply_blocks=0, boundary_blocks=0)

    def __call__(self, obs, configuration=None):
        action = self.base(obs, configuration)
        step = int(_dt_mm.get(obs, "step", 0))
        seat = int(_dt_mm.get(obs, "player", 0))
        inv = int(_dt_mm.get(_dt_mm.get(_dt_mm.get(obs, "market", {}), "inventory", {}), "WHEAT", 10000))
        hist = self.history[seat]
        if step == 0 or (hist and step <= hist[-1][0]):
            hist.clear()
        # Inventory deltas contain both players' trades. This is a conservative
        # public net-supply gate, not an estimate of private opponent inventory.
        recent = [max(0, inv - hist[-1][1])] if hist else []
        hist.append((step, inv, recent[0] if recent else 0))
        del hist[:-24]
        state = self.expert.states[seat]
        if step == 0 or step < state.get("last_step", -1):
            state = self.expert._reset(seat, step)
        # Open positions must always reach the exit logic, including blocked ticks.
        if not state.get("open_units", 0):
            tpd = max(1, int(_dt_mm.get(configuration, "turnsPerDay", 24)))
            if step % tpd == tpd - 1:
                self.delay_telemetry["boundary_blocks"] += 1
                return action
            demand = _dt_demand(obs, configuration, "WHEAT")
            if self.gated and demand and len(hist) >= 12:
                supply = sum(row[2] for row in hist) / len(hist)
                if supply >= demand:
                    self.delay_telemetry["supply_blocks"] += 1
                    return action
        return self.expert.apply(obs, action, configuration)

# Match the installed official engine's flat town-center consumption.
_dt_mm.demand_on_step = _dt_demand
_V44_POLICY = _DemandTrader(_V44_POLICY, _V44_ROUTES["default"], GATED_VALUE)
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=ROOT/'variants/w13_zero_replay/main.py')
    parser.add_argument('--output-root', type=Path, default=ROOT/'variants')
    args = parser.parse_args()
    source = args.source.read_text()
    marker = '\ndef agent(obs, configuration=None):'
    assert source.count(marker) == 1
    manifest = {}
    for label, gated in [('gated', True), ('ungated', False)]:
        target = args.output_root/f'w13_demand_{label}/main.py'
        candidate = source.replace(marker, '\n'+WRAPPER.replace('GATED_VALUE', repr(gated))+marker)
        compile(candidate, str(target), 'exec')
        if target.exists() and target.read_text() != candidate:
            raise FileExistsError(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(candidate)
        manifest[label] = {'path': str(target.resolve().relative_to(ROOT)),
                           'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
    print(json.dumps({'source_sha256': hashlib.sha256(args.source.read_bytes()).hexdigest(),
                      'variants': manifest}, indent=2))


if __name__ == '__main__':
    main()
