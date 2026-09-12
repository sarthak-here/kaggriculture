"""Candidate contract tests use saved observations, not whole-game claims."""
import copy, gzip, json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'public_candidates/shop0909_20260910'
NEW=ROOT/'variants/shop0909_opening_net'
def namespace(folder):
    n={'__name__':'contract_test','__file__':str(folder/'main.py')}
    exec(compile((folder/'main.py').read_text(),str(folder/'main.py'),'exec'),n);return n
class OpeningTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=namespace(BASE);cls.new=namespace(NEW)
        cls.replay=json.loads(gzip.decompress((ROOT/'analysis/shop0909_all_losses_20260911/replays/episode-107774237-replay.json.gz').read_bytes()))
    def test_only_exact_step0_market_changes(self):
        from replays_to_csv import observations
        b=self.base['Policy'](BASE);n=self.new['Policy'](NEW)
        obs=observations(self.replay['steps'][0])[0];before=copy.deepcopy(obs)
        x=b.act(obs);y=n.act(obs)
        self.assertEqual(y['market'],[['BUY_PRODUCT','WHEAT',13]])
        self.assertEqual({k:v for k,v in x.items() if k!='market'},{k:v for k,v in y.items() if k!='market'})
        self.assertEqual(obs,before)
    def test_later_policy_outputs_and_state_match_on_saved_observations(self):
        from replays_to_csv import observations
        b=self.base['Policy'](BASE);n=self.new['Policy'](NEW)
        for i in range(719):
            obs=observations(self.replay['steps'][i])[0]
            x=b.act(obs);y=n.act(obs)
            if i:self.assertEqual(x,y,(i,x,y))
    def test_unexpected_opening_is_not_overridden(self):
        from replays_to_csv import observations
        b=self.base['Policy'](BASE);n=self.new['Policy'](NEW)
        for p in (b,n):p.tapes[0][0]['market']=[['BUY_PRODUCT','WHEAT',12]]
        obs=observations(self.replay['steps'][0])[0]
        self.assertEqual(b.act(obs),n.act(obs))
    def test_actions_and_license_unchanged(self):
        for f in ('actions.json','LICENSE.txt'):self.assertEqual((BASE/f).read_bytes(),(NEW/f).read_bytes())
    def test_last_function_contract(self):
        import ast
        defs=[n for n in ast.parse((NEW/'main.py').read_text()).body if isinstance(n,ast.FunctionDef)]
        self.assertEqual(defs[-1].name,'agent')
        self.assertEqual(defs[-1].args.args[0].arg,'observation')
if __name__=='__main__':unittest.main()
