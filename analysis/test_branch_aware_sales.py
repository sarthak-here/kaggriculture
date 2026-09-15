import ast,importlib.util,unittest
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]

class Windows(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p=ROOT/'variants/branch_aware_sales/main.py'
        spec=importlib.util.spec_from_file_location('branch_sales_test',p)
        cls.m=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.m)
    def state(self,plan=0,**kwargs):
        return SimpleNamespace(plan=plan,tomato_active=kwargs.get('tomato',False),yarn_branch=kwargs.get('yarn'))
    def test_no_early_changes(self):
        for plan in range(13):
            for step in range(289):self.assertFalse(self.m.sale_window_open(self.state(plan),step))
    def test_default_protected(self):
        for step in range(433):self.assertFalse(self.m.sale_window_open(self.state(),step))
        self.assertTrue(self.m.sale_window_open(self.state(),433))
    def test_nondefault_released(self):
        for plan in range(1,13):self.assertTrue(self.m.sale_window_open(self.state(plan),289))
    def test_active_specialists_unchanged(self):
        for step in (289,432,433,647):
            self.assertFalse(self.m.sale_window_open(self.state(1,yarn=0),step))
            self.assertFalse(self.m.sale_window_open(self.state(1,tomato=True),step))
    def test_terminal_no_change(self):
        self.assertFalse(self.m.sale_window_open(self.state(1),648))
    def test_critical_functions_identical(self):
        def funcs(path):return {n.name:ast.dump(n) for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef)}
        a=funcs(ROOT/'variants/protected_portfolio/main.py');b=funcs(ROOT/'variants/branch_aware_sales/main.py')
        for name in ('tomato_compatible','select_yarn','recover_day_one','repair_weeds'):
            self.assertEqual(a[name],b[name])
if __name__=='__main__':unittest.main()
