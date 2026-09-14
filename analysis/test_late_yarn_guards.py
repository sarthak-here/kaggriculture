import copy,importlib.util,json,unittest
from pathlib import Path
from collections import deque
ROOT=Path(__file__).resolve().parents[1]
class YarnGuards(unittest.TestCase):
    def setUp(self):
        folder=ROOT/'variants/late_yarn_20260914';spec=importlib.util.spec_from_file_location('yarn_test',folder/'main.py');self.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.m)
        self.branches=json.loads((folder/'yarn.json').read_text());self.state=self.m.DayState()
        self.obs=dict(player=0,farms=[dict(copy.deepcopy(self.branches[0]['farm']),money=20000)],private=copy.deepcopy(self.branches[0]['private']),town=dict(unlocked_shops=['YARN_STORE','YARN_STORE']))
    def test_matching(self):self.assertEqual(self.m.select_yarn(self.obs,self.state,self.branches),0)
    def test_cash(self):
        self.obs['farms'][0]['money']=9999;self.assertIsNone(self.m.select_yarn(self.obs,self.state,self.branches))
    def test_position(self):
        self.obs['farms'][0]['farmer'][0]+=1;self.assertIsNone(self.m.select_yarn(self.obs,self.state,self.branches))
    def test_inventory(self):
        self.obs['private']['seeds']['WHEAT']+=1;self.assertIsNone(self.m.select_yarn(self.obs,self.state,self.branches))
    def test_demand(self):
        self.obs['town']['unlocked_shops']=['YARN_STORE'];self.assertIsNone(self.m.select_yarn(self.obs,self.state,self.branches))
    def test_queue(self):
        self.state.queues[0]=deque([['EAST']]);self.assertIsNone(self.m.select_yarn(self.obs,self.state,self.branches))
if __name__=='__main__':unittest.main()
