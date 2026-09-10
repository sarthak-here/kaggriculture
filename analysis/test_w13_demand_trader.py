"""Compare demand/price assumptions with the installed official engine."""
import contextlib
import io
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    from kaggle_environments.envs.kaggriculture import kaggriculture as engine
    from kaggle_environments.utils import structify
NS = runpy.run_path(str(ROOT/'variants/w13_demand_gated/main.py'))


class DemandTraderTests(unittest.TestCase):
    def test_demand_matches_official_engine(self):
        for ci in (12, 24):
            for step in (0, 4, 12, 23, 24, 240, 480, 716):
                config = dict(townCenterSellInterval=ci, townShopSellInterval=4)
                obs = dict(step=step, town={'unlocked_shops': ['BAKERY', 'BAKERY', 'PET_CAFE']},
                           market={'inventory': dict.fromkeys(engine.PRODUCTS, 10000), 'prices': {}})
                state = structify([{'observation': obs}])
                engine._town_consume(structify({'configuration': config}), state, step)
                for item in engine.PRODUCTS:
                    self.assertEqual(NS['_dt_demand'](obs, config, item),
                                     10000-state[0].observation.market.inventory[item])

    def test_prices_match_official_engine(self):
        for inventory in (0, 9500, 9999, 10000, 10001, 10500):
            self.assertEqual(NS['_dt_mm'].market_price('WHEAT', inventory),
                             engine.market_price('WHEAT', inventory))

    def test_supply_gate_and_open_position_exit(self):
        trader = NS['_DemandTrader'](lambda obs, cfg: {'market': []}, [{}]*719, True)
        trader.history[0] = [(s, 10000+s*10, 10) for s in range(348, 360)]
        trader.expert.apply = lambda obs, act, cfg: {'reached_expert': True}
        obs = {'step': 360, 'player': 0, 'market': {'inventory': {'WHEAT': 13600}},
               'town': {'unlocked_shops': ['BAKERY']}}
        self.assertEqual(trader(obs), {'market': []})
        self.assertEqual(trader.delay_telemetry['supply_blocks'], 1)
        trader.expert.states[0]['open_units'] = 10
        obs['step'] = 364
        self.assertTrue(trader(obs)['reached_expert'])

    def test_game_reset_clears_history_and_position(self):
        trader = NS['_DemandTrader'](lambda obs, cfg: {'market': []}, [{}]*719, True)
        trader.history[0] = [(700, 9000, 10)]
        trader.expert.states[0] = {'last_step': 700, 'open_units': 20}
        trader({'step': 0, 'player': 0})
        self.assertEqual(len(trader.history[0]), 1)
        self.assertEqual(trader.expert.states[0]['open_units'], 0)


if __name__ == '__main__':
    unittest.main()
