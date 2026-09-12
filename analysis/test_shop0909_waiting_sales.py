import copy,unittest
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
class WaitingTests(unittest.TestCase):
    def setUp(self):
        path=ROOT/'variants/shop0909_waiting_h3/main.py';self.n={'__name__':'waiting_test','__file__':str(path)}
        exec(compile(path.read_text(),str(path),'exec'),self.n)
        self.view=SimpleNamespace(shed={'WOOL':6,'WHEAT':9},positions=[],prices={'WOOL':100,'WHEAT':40})
        self.tape=[{'market':[]} for _ in range(719)]
        self.tape[148]['market']=[['SELL','WOOL',4],['SELL','WHEAT',9]]
        self.action={'farmer':['PASS'],'hands':[],'market':[]}
    def test_only_held_eligible_stock(self):
        self.n['sell_waiting_stock'](self.action,self.view,self.tape,145)
        self.assertEqual(self.action['market'],[['SELL','WOOL',4]])
        self.assertEqual(self.action['farmer'],['PASS']);self.assertEqual(self.view.shed['WOOL'],6)
        self.assertEqual(self.tape[148]['market'][0],['SELL','WOOL',4])
    def test_buying_turn_untouched(self):
        self.action['market']=[['BUY_SEED','WHEAT',1]];before=copy.deepcopy(self.action)
        self.n['sell_waiting_stock'](self.action,self.view,self.tape,145);self.assertEqual(self.action,before)
    def test_opening_and_boundary_untouched(self):
        for step in (0,23,143,144,167,647,648,718):
            action=copy.deepcopy(self.action)
            self.n['sell_waiting_stock'](action,self.view,self.tape,step)
            self.assertEqual(action,self.action)
    def test_no_room_or_no_stock(self):
        self.action['market']=[['PASS'] for _ in range(10)]
        self.n['sell_waiting_stock'](self.action,self.view,self.tape,145)
        self.assertEqual(len(self.action['market']),10)
        self.action['market']=[];self.view.shed['WOOL']=0
        self.n['sell_waiting_stock'](self.action,self.view,self.tape,145)
        self.assertEqual(self.action['market'],[])
if __name__=='__main__':unittest.main()
