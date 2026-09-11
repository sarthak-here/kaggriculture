"""Contract checks for the inspected, unchanged public baseline."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'public_candidates/shop0909_20260910'

class ShopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ns={'__name__':'tested_shop0909','__file__':str(FOLDER/'main.py')}
        exec(compile((FOLDER/'main.py').read_text(),str(FOLDER/'main.py'),'exec'),cls.ns)
        with zipfile.ZipFile(ROOT/'analysis/replay_csv_56139834/replay_corpus.zip') as z:
            replay=json.loads(gzip.decompress(z.read('replays/episode-107405585-replay.json.gz')))
        cls.observation=replay['steps'][0][0]['observation']

    def test_published_hashes(self):
        expected=json.loads((FOLDER/'provenance.json').read_text())['members']
        for name,digest in expected.items():self.assertEqual(hashlib.sha256((FOLDER/name).read_bytes()).hexdigest(),digest)

    def test_plan_shapes(self):
        policy=self.ns['Policy'](FOLDER)
        self.assertEqual(len(policy.tapes),13)
        self.assertTrue(all(len(t)==719 for t in policy.tapes))

    def test_reset_and_no_observation_mutation(self):
        policy=self.ns['Policy'](FOLDER);obs=copy.deepcopy(self.observation);saved=copy.deepcopy(obs)
        first=policy.act(obs);second=policy.act(obs)
        self.assertEqual(first,second);self.assertEqual(obs,saved)

    def test_shop_selection_and_seat_isolation(self):
        policy=self.ns['Policy'](FOLDER)
        obs=copy.deepcopy(self.observation);obs['step']=144;obs['player']=0
        obs['town']['unlocked_shops']=['BAKERY','YARN_STORE'];policy.act(obs)
        self.assertEqual(policy.players[0].plan,3)
        obs['player']=1;obs['town']['unlocked_shops']=['PET_CAFE','BRUNCH_SPOT'];policy.act(obs)
        self.assertEqual(policy.players[1].plan,0);self.assertEqual(policy.players[0].plan,3)

    def test_shared_final_continuation(self):
        policy=self.ns['Policy'](FOLDER);obs=copy.deepcopy(self.observation);obs['step']=648
        action=policy.act(obs)
        self.assertEqual(policy.players[obs['player']].plan,2)
        self.assertLessEqual(len(action['market']),10)

if __name__=='__main__':unittest.main()
