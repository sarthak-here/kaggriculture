import copy
import unittest
from build_w13_opening_net import WRAPPER


class OpeningNetTests(unittest.TestCase):
    def policy(self, action):
        namespace = {'_V44_POLICY': lambda obs, configuration=None: action}
        exec(WRAPPER, namespace)
        return namespace['_V44_POLICY']

    def test_net_preserves_workers_and_input(self):
        a = dict(farmer=['NORTH'], hands=[['FEED']], market=[
            ['SELL','WHEAT',3], ['HIRE'], ['BUY_PRODUCT','WHEAT',5]])
        before = copy.deepcopy(a)
        out = self.policy(a)({'step':5})
        self.assertEqual(out['market'], [['HIRE'], ['BUY_PRODUCT','WHEAT',2]])
        self.assertEqual(out['hands'], a['hands'])
        self.assertEqual(out['farmer'], a['farmer'])
        self.assertEqual(a, before)

    def test_split_orders_preserve_other_products(self):
        a = dict(market=[['SELL','WHEAT',1], ['SELL','WHEAT',4],
                        ['BUY_PRODUCT','WHEAT',3], ['SELL','MILK',2]])
        self.assertEqual(self.policy(a)({'step':23})['market'],
                         [['SELL','WHEAT',2], ['SELL','MILK',2]])

    def test_opening_and_later_days_untouched(self):
        a = dict(market=[['SELL','WHEAT',1], ['BUY_PRODUCT','WHEAT',1]])
        policy = self.policy(a)
        for step in (0,1,24,300,718):
            self.assertIs(policy({'step':step}), a)

    def test_unmatched_purchase_untouched(self):
        a = dict(market=[['BUY_PRODUCT','WHEAT',5]])
        self.assertIs(self.policy(a)({'step':5}), a)


if __name__ == '__main__':
    unittest.main()
