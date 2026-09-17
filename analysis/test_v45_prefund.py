import ast,unittest
from build_v45_prefund import WRAPPER
class Prefund(unittest.TestCase):
    def setUp(self):
        fn=next(n for n in ast.parse(WRAPPER.replace('LOCAL_QUANTITY','20')).body if isinstance(n,ast.FunctionDef) and n.name=='_local_prefund_action')
        self.ns={'_LOCAL_PREFUND_REPORT':{'prefund_openings':0,'prefund_held_feed':0}}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'<prefund>','exec'),self.ns)
        self.fn=self.ns['_local_prefund_action']
        self.action={'farmer':['MOVE','NORTH'],'hands':[], 'market':[['SELL','WHEAT',13],['BUY_PRODUCT','WHEAT',5],['HIRE'],['BUY_ANIMAL','COW',2]]}
    def test_preserves_inventory_and_order_slots(self):
        result=self.fn({'step':1,'private':{'shed':{'WHEAT':5}}},self.action)
        self.assertEqual(result['market'][:2],[['SELL','WHEAT',0],['BUY_PRODUCT','WHEAT',0]])
        for key in ('farmer','hands'):self.assertEqual(result[key],self.action[key])
        self.assertEqual(result['market'][2:],self.action['market'][2:])
        self.assertEqual(self.action['market'][0][2],13)
    def test_insufficient_feed_fallback(self):
        self.assertIs(self.fn({'step':1,'private':{'shed':{'WHEAT':4}}},self.action),self.action)
    def test_unexpected_stock_fallback(self):
        self.assertIs(self.fn({'step':1,'private':{'shed':{'WHEAT':6}}},self.action),self.action)
    def test_nonstandard_fallback(self):
        self.assertIs(self.fn({'step':1},self.action,{'shedCapacity':50}),self.action)
    def test_later_turn_noop(self):self.assertIs(self.fn({'step':2},self.action),self.action)
    def test_opening_retains_five(self):
        result=self.fn({'step':0},{'market':[['BUY_PRODUCT','WHEAT',70],['SELL','WHEAT',70]]})
        self.assertEqual(result['market'],[['BUY_PRODUCT','WHEAT',20],['SELL','WHEAT',15]])
if __name__=='__main__':unittest.main()
