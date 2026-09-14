import copy,importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('adaptive',ROOT/'adaptive_agent/main.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def fixture():
    farm=dict(money=3000,farmer=[4,4],hands=[],hires_today=0,unlocked_quadrants=['NW'],tiles=[[None if x<5 and y<5 else 'LOCKED' for x in range(10)] for y in range(10)])
    return dict(step=0,player=0,farms=[farm,copy.deepcopy(farm)],private=dict(inventories=[{}],seeds={p:0 for p in m.CROPS},shed={p:0 for p in m.CROPS}),town=dict(unlocked_shops=[]),market=dict(inventory={p:10000 for p in m.CROPS},prices={p:m.price(p,10000) for p in m.CROPS}))
class AdaptiveTests(unittest.TestCase):
    def test_exact_engine_prices(self):
        from kaggle_environments.envs.kaggriculture import kaggriculture as engine
        for p in m.CROPS:
            for inv in (8000,9500,9999,10000,10001,10200,12000):self.assertEqual(m.price(p,inv),engine.market_price(p,inv))
    def test_demand_response(self):
        obs=fixture();a=m.crop_values(obs)['CARROT'];obs['town']['unlocked_shops']=['PET_CAFE']*3
        self.assertGreater(m.crop_values(obs)['CARROT'],a)
    def test_supply_response(self):
        obs=fixture();obs['step']=240;obs['town']['unlocked_shops']=['FARMERS_MARKET']*2;a=m.crop_values(obs)['CARROT']
        for y in range(5):
            for x in range(5):obs['farms'][1]['tiles'][y][x]=dict(crop='CARROT',planted_day=9,yield_units=1)
        self.assertLess(m.crop_values(obs)['CARROT'],a)
    def test_season_deadline(self):
        obs=fixture();obs['step']=27*24;self.assertEqual(m.crop_values(obs)['TOMATO'],-float('inf'))
    def test_input_pure_and_valid_shape(self):
        obs=fixture();original=copy.deepcopy(obs);action=m.agent(obs);self.assertEqual(obs,original)
        self.assertEqual(set(action),{'farmer','hands','market'});self.assertLessEqual(len(action['market']),10)
    def test_cash_reserve(self):
        obs=fixture();obs['farms'][0]['money']=60;self.assertFalse(any(o[0].startswith('BUY') or o[0]=='HIRE' for o in m.agent(obs)['market']))
if __name__=='__main__':unittest.main()
