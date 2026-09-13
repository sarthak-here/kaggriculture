import copy,importlib.util,json,unittest
from collections import deque
from pathlib import Path
from replays_to_csv import load_replay,observations
ROOT=Path(__file__).resolve().parents[1]
class Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.folder=ROOT/'variants/shop0909_tomato432'
        spec=importlib.util.spec_from_file_location('tomato_candidate',cls.folder/'main.py')
        cls.mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.mod)
        cls.ref=json.loads((cls.folder/'tomato.json').read_text())['reference']
        cls.replay=load_replay(ROOT/'analysis/shop0909_full_20260913/replays/episode-108145550-replay.json.gz')
    def setUp(self):
        self.obs=copy.deepcopy(observations(self.replay['steps'][432])[1]);self.obs['player']=1
        self.state=self.mod.DayState()
    def test_matching_state(self):self.assertTrue(self.mod.tomato_compatible(self.obs,self.state,self.ref))
    def test_cash(self):
        self.obs['farms'][1]['money']=9999
        self.assertFalse(self.mod.tomato_compatible(self.obs,self.state,self.ref))
    def test_inventory(self):
        self.obs['private']['seeds']['WHEAT']=1
        self.assertFalse(self.mod.tomato_compatible(self.obs,self.state,self.ref))
    def test_position(self):
        self.obs['farms'][1]['farmer'][0]+=1
        self.assertFalse(self.mod.tomato_compatible(self.obs,self.state,self.ref))
    def test_queue(self):
        self.state.queues[0]=deque([['NORTH']])
        self.assertFalse(self.mod.tomato_compatible(self.obs,self.state,self.ref))
    def test_route(self):
        self.state.plan=5
        self.assertFalse(self.mod.tomato_compatible(self.obs,self.state,self.ref))
    def test_demand(self):
        self.obs['town']['unlocked_shops']=['YARN_STORE']*6
        self.assertFalse(self.mod.tomato_compatible(self.obs,self.state,self.ref))
    def test_prefix_activation(self):
        policy=self.mod.Policy(self.folder)
        for step in range(434):
            obs=observations(self.replay['steps'][step])[1];obs['player']=1
            action=policy.act(obs)
        self.assertTrue(policy.players[1].tomato_active)
        self.assertIn(['BUY_SEED','TOMATO',10],action['market'])
if __name__=='__main__':unittest.main()
