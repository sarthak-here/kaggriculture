import ast
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ConsumptionGuard(unittest.TestCase):
    def setUp(self):
        source=(ROOT/'variants/v45_consumption_guard/main.py').read_text(encoding='utf-8')
        fn=next(n for n in ast.parse(source).body if isinstance(n,ast.FunctionDef) and n.name=='_local_consumption_covers')
        self.ns={'_RACE_STATE':{0:{}},'_local_strict_clone':lambda obs,state:obs['clone'],
                 '_race_town':lambda step,shops:{'MILK':int(step%4==0)}}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'<guard>','exec'),self.ns)
        self.obs={'player':0,'step':216,'town':{'unlocked_shops':[]},'clone':True}
    def gate(self,due,quantity):return self.ns['_local_consumption_covers'](self.obs,'MILK',due,quantity)
    def test_short_unchanged(self):self.assertFalse(self.gate(224,1))
    def test_absorbed_batch(self):self.assertTrue(self.gate(228,3))
    def test_large_batch_still_early(self):self.assertFalse(self.gate(228,4))
    def test_no_zero_reservation(self):self.assertFalse(self.gate(228,0))
    def test_non_clone_unchanged(self):
        self.obs['clone']=False
        self.assertFalse(self.gate(228,1))
    def test_worker_and_funding_functions_unchanged(self):
        def nodes(path,name):return [ast.dump(n) for n in ast.parse(path.read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name==name]
        for name in ('_r124_seed_budget','_r124_atomic','_r97_supply','_r97_budget'):
            self.assertEqual(nodes(ROOT/'variants/v45_proactive/main.py',name),nodes(ROOT/'variants/v45_consumption_guard/main.py',name))
if __name__=='__main__':unittest.main()
