import unittest
from run_w13_isolated import submission_entrypoint

class EntryTests(unittest.TestCase):
    def test_router_not_internal_policy(self):
        source = 'def agent(obs): return "router"\ndef entry(obs): return agent(obs)\n'
        ns = {'_V44_POLICY': lambda obs: 'wrong base'}
        exec(source, ns)
        self.assertEqual(submission_entrypoint(ns, source)({}), 'router')

    def test_nested_definition_not_selected(self):
        source = 'def agent(obs):\n def nested(): return 9\n return 3\n'
        ns = {}
        exec(source, ns)
        self.assertEqual(submission_entrypoint(ns, source)({}), 3)

    def test_no_function_rejected(self):
        with self.assertRaises(ValueError):
            submission_entrypoint({}, 'x=1')

if __name__ == '__main__':
    unittest.main()
