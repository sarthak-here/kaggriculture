import copy,importlib.util,unittest
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
class RecoveryTests(unittest.TestCase):
    def setUp(self):
        p=ROOT/'variants/protected_portfolio/main.py';s=importlib.util.spec_from_file_location('protected_test',p);self.m=importlib.util.module_from_spec(s);s.loader.exec_module(self.m)
        self.obs=dict(step=24,player=0,farms=[dict(money=0)])
        self.action=dict(farmer=['PASS'],hands=[],market=[['HIRE']]*3)
        self.view=SimpleNamespace(shed={'WHEAT':2},positions=[],prices={'WHEAT':30})
    def test_recovery(self):
        self.m.recover_day_one(self.action,self.view,self.obs);self.assertEqual(self.action['market'],[['SELL','WHEAT',1],['HIRE'],['HIRE'],['HIRE']])
    def test_cash_sufficient(self):
        self.obs['farms'][0]['money']=4;self.m.recover_day_one(self.action,self.view,self.obs);self.assertEqual(len(self.action['market']),3)
    def test_preserves_wheat_reserve(self):
        self.view.shed['WHEAT']=1;self.m.recover_day_one(self.action,self.view,self.obs);self.assertEqual(len(self.action['market']),3)
    def test_other_steps(self):
        self.obs['step']=25;self.m.recover_day_one(self.action,self.view,self.obs);self.assertEqual(len(self.action['market']),3)
    def test_unexpected_orders(self):
        self.action['market'].append(['BUY_PRODUCT','WHEAT',1]);old=copy.deepcopy(self.action);self.m.recover_day_one(self.action,self.view,self.obs);self.assertEqual(self.action,old)
    def test_sales_disabled_through_routing(self):
        tape=[dict(market=[['SELL','WOOL',4]]) for _ in range(719)];self.view.shed={'WOOL':9};self.view.prices={'WOOL':100}
        for step in range(433):
            action=dict(farmer=['PASS'],hands=[],market=[]);self.m.sell_waiting_stock(action,self.view,tape,step);self.assertEqual(action['market'],[])
    def test_sales_enabled_after_routing(self):
        tape=[dict(market=[['SELL','WOOL',4]]) for _ in range(719)];self.view.shed={'WOOL':9};self.view.prices={'WOOL':100}
        action=dict(farmer=['PASS'],hands=[],market=[]);self.m.sell_waiting_stock(action,self.view,tape,433);self.assertEqual(action['market'],[['SELL','WOOL',8]])
if __name__=='__main__':unittest.main()
