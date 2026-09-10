import unittest
from summarize_w13_opening_net import stats, compare


class SummaryTests(unittest.TestCase):
    def row(self, seed, a, b, status='DONE'):
        return dict(seed=seed, order=0, a=a, b=b, status=status, shops=[])

    def test_ties_and_failures_stay_in_total(self):
        r = stats({'rows':[self.row(0,2,1),self.row(1,1,2),self.row(2,1,1),
                          self.row(3,0,0,'FAILED')]})
        self.assertEqual(r['wins_over_total'], .25)
        self.assertEqual(r['decisive_win_rate'], .5)
        self.assertEqual((r['ties'],r['failures']), (1,1))

    def test_paired_outcomes_not_just_margin(self):
        c = {'rows':[self.row(0,2,1),self.row(1,20,10),self.row(2,0,0,'FAILED')]}
        b = {'rows':[self.row(0,1,2),self.row(1,2,1),self.row(2,1,2)]}
        r = compare(c,b)
        self.assertEqual(r['improved_outcomes'],1)
        self.assertEqual(r['worsened_outcomes'],0)
        self.assertEqual(r['failed_pairs'],1)
        self.assertEqual(r['mean_margin_delta'],5.5)

    def test_missing_pair_rejected(self):
        with self.assertRaises(AssertionError):
            compare({'rows':[self.row(1,1,2)]},{'rows':[self.row(2,1,2)]})


if __name__ == '__main__':
    unittest.main()
