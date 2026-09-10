"""Exporter contract checks, using a real public replay only as an input fixture."""
import copy
import csv
import gzip
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from replays_to_csv import load_replay, safe_cell, farm_stats, observations, export_one, reconstruct

CORPUS=Path(__file__).resolve().parent/'replay_csv_56139834'
FIXTURE='replays/episode-107405585-replay.json.gz'


class ExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if (CORPUS/FIXTURE).exists():cls.replay=load_replay(CORPUS/FIXTURE)
        else:
            with zipfile.ZipFile(CORPUS/'replay_corpus.zip') as z:cls.replay=json.loads(gzip.decompress(z.read(FIXTURE)))

    def test_formula_escape(self):
        self.assertEqual(safe_cell(' =1+1'),"' =1+1")
        self.assertEqual(safe_cell(-21),-21)
        self.assertEqual(safe_cell('normal'),'normal')

    def test_missing_private_is_unknown(self):
        obs=copy.deepcopy(observations(self.replay['steps'][0])[0]);obs.pop('private')
        self.assertIsNone(farm_stats(obs,0)['shed_WHEAT'])
        self.assertFalse(farm_stats(obs,0)['private_available'])

    def test_shared_state_does_not_invent_private(self):
        record=copy.deepcopy(self.replay['steps'][0]);record[1]['observation']={}
        obs=observations(record)
        self.assertEqual(obs[1]['farms'],obs[0]['farms'])
        self.assertNotIn('private',obs[1])

    def test_action_alignment_and_plain_or_gzip(self):
        replay=copy.deepcopy(self.replay);replay['steps']=replay['steps'][:2]
        replay['steps'][1][0]['action']['farmer']=['PASS','alignment-marker']
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);path=root/'episode-123-replay.json'
            path.write_text(json.dumps(replay),encoding='utf-8')
            packed=root/'compressed';packed.write_bytes(gzip.compress(path.read_bytes()))
            self.assertEqual(load_replay(path),load_replay(packed))
            result=export_one((str(path),[],str(root/'out'),False))
            self.assertEqual(result['status'],'DONE',result)
            with (root/'out/_parts/123/actions.csv').open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
            self.assertEqual(json.loads(rows[0]['requested_action']),['PASS','alignment-marker'])
            self.assertEqual(rows[0]['step'],'0')
            self.assertEqual(rows[0]['cash_verified'],'')

    def test_corrupt_replay_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'episode-123-replay.json';path.write_text('{}')
            result=export_one((str(path),[],tmp,False))
            self.assertEqual(result['status'],'FAILED')
            self.assertIn('KeyError',result['error'])

    def test_successful_cash_ledger_includes_atomic_orders(self):
        from kaggle_environments.envs.kaggriculture import kaggriculture as eng
        before=observations(self.replay['steps'][0]);after=observations(self.replay['steps'][1])
        actions=[r['action'] for r in self.replay['steps'][1]]
        fills,_,verified=reconstruct(before,actions,after,self.replay['configuration'],eng)
        self.assertEqual(verified,[True,True])
        for seat in (0,1):
            delta=sum(v*(1 if op=='SELL' else -1) for (s,op,item,metric),v in fills.items() if s==seat and metric=='value')
            self.assertEqual(delta,after[seat]['farms'][seat]['money']-before[seat]['farms'][seat]['money'])

    def test_requested_quantity_is_not_filled_quantity(self):
        from kaggle_environments.envs.kaggriculture import kaggriculture as eng
        before=observations(copy.deepcopy(self.replay['steps'][0]));after=observations(self.replay['steps'][1])
        before[0]['private']['shed']={'WHEAT':3}
        actions=[{'farmer':['PASS'],'market':[['SELL','WHEAT',99999]]},{'farmer':['PASS']}]
        originals=eng._commit_unit,eng._do_hire,eng._do_buy_land
        fills,_,_=reconstruct(before,actions,after,self.replay['configuration'],eng)
        self.assertEqual(fills[0,'SELL','WHEAT','units'],3)
        self.assertEqual(originals,(eng._commit_unit,eng._do_hire,eng._do_buy_land))


if __name__=='__main__':unittest.main()
