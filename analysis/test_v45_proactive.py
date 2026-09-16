import ast,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class StrictClone(unittest.TestCase):
    def setUp(self):
        text=(ROOT/'variants/v45_proactive/main.py').read_text()
        fn=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='_local_strict_clone')
        self.ns={'_r37_similarity':lambda o:o['similarity']}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'<strict_clone>','exec'),self.ns)
    def check(self,h,s):return self.ns['_local_strict_clone']({'similarity':s},{'hist':h})
    def test_confirmed(self):self.assertTrue(self.check([True]*6,1))
    def test_short(self):self.assertFalse(self.check([True]*5,1))
    def test_movement_mismatch(self):self.assertFalse(self.check([True]*5+[False],1))
    def test_layout_mismatch(self):self.assertFalse(self.check([True]*6,.99))
    def test_missing_history(self):self.assertFalse(self.check([],1))
    def test_reservation_guard_unchanged(self):
        def nodes(path,name):return [ast.dump(n) for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name]
        for name in ('_r36_reserve','_race_lost','_r37_similarity'):
            self.assertEqual(nodes(ROOT/'variants/v45_proactive/main.py',name),nodes(ROOT/'public_candidates/cloning_v45_20260916/main.py',name))
if __name__=='__main__':unittest.main()
