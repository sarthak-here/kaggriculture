import ast,unittest
from pathlib import Path
from kaggle_environments.agent import get_last_callable
ROOT=Path(__file__).resolve().parents[1]
class CombinedGuard(unittest.TestCase):
    def test_kaggle_selects_agent(self):
        p=ROOT/'variants/v45_prefund_consumption_guard/main.py'
        self.assertEqual(get_last_callable(p.read_text(),path=str(p)).__name__,'agent')
    def test_worker_and_funding_functions_unchanged(self):
        def nodes(path,name):return [ast.dump(n) for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name]
        base=ROOT/'variants/v45_prefund_10_exported/main.py';candidate=ROOT/'variants/v45_prefund_consumption_guard/main.py'
        for name in ('_r124_seed_budget','_r124_atomic','_r97_supply','_r97_budget','_local_prefund_action'):
            self.assertEqual(nodes(base,name),nodes(candidate,name))
if __name__=='__main__':unittest.main()
