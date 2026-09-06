"""Evidence preservation regressions; all writes stay in temporary directories."""
import contextlib
import copy
import gzip
import io
import json
from pathlib import Path
import tempfile
import unittest
from summarize_w13_sales import summarize

class SummaryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.analysis=self.root/'analysis';self.analysis.mkdir()
        self.archive=self.analysis/'w13_sales_raw_runs.json.gz'
        self.summary=self.analysis/'w13_sales_results.json'
        self.row={'seed':1,'order':0,'status':'DONE','a':10,'b':5,
                  'a_workers_sha256':'same','b_workers_sha256':'same','a_fills':{},'b_fills':{}}
        self.data={'a':'a.py','b':'b.py','engine':'1.32.7','rows':[self.row]}
    def archive_data(self,data=None):
        self.archive.write_bytes(gzip.compress(json.dumps(data or {'old.json':self.data}).encode(),mtime=0))
    def local(self,name,data):
        directory=self.analysis/'w13_runs';directory.mkdir(exist_ok=True)
        (directory/name).write_text(json.dumps(data))
    def run_summary(self):
        with contextlib.redirect_stdout(io.StringIO()):summarize(self.root)
    def test_clean_checkout_retains_archive_and_is_repeatable(self):
        self.archive_data();original=self.archive.read_bytes();self.run_summary();summary=self.summary.read_bytes()
        self.run_summary();self.assertEqual(original,self.archive.read_bytes());self.assertEqual(summary,self.summary.read_bytes())
        self.assertEqual(json.loads(summary)['experiments']['old.json']['wins'],1)
    def test_local_new_experiment_merges_archive(self):
        self.archive_data();self.local('new.json',self.data);self.run_summary()
        self.assertEqual(set(json.loads(gzip.decompress(self.archive.read_bytes()))),{'old.json','new.json'})
    def test_same_experiment_extends_without_dropping_rows(self):
        self.archive_data();new=copy.deepcopy(self.data);new['rows'][0]['order']=1
        self.local('old.json',new);self.run_summary()
        self.assertEqual(len(json.loads(gzip.decompress(self.archive.read_bytes()))['old.json']['rows']),2)
    def test_conflicting_result_changes_neither_output(self):
        self.archive_data();self.run_summary();before=(self.archive.read_bytes(),self.summary.read_bytes())
        new=copy.deepcopy(self.data);new['rows'][0]['a']=99;self.local('old.json',new)
        with self.assertRaisesRegex(ValueError,'conflicting result'):self.run_summary()
        self.assertEqual(before,(self.archive.read_bytes(),self.summary.read_bytes()))
    def test_conflicting_provenance_rejected(self):
        self.archive_data();new=copy.deepcopy(self.data);new['a']='different.py';self.local('old.json',new)
        before=self.archive.read_bytes()
        with self.assertRaisesRegex(ValueError,'conflicting a'):self.run_summary()
        self.assertEqual(before,self.archive.read_bytes());self.assertFalse(self.summary.exists())
    def test_no_evidence_refuses_to_overwrite_summary(self):
        self.summary.write_text('valuable result')
        with self.assertRaisesRegex(ValueError,'No archived or local runs'):self.run_summary()
        self.assertEqual(self.summary.read_text(),'valuable result');self.assertFalse(self.archive.exists())
    def test_empty_local_run_is_not_a_replacement(self):
        self.archive_data();new=copy.deepcopy(self.data);new['rows']=[];self.local('old.json',new)
        before=self.archive.read_bytes()
        with self.assertRaisesRegex(ValueError,'nonempty'):self.run_summary()
        self.assertEqual(before,self.archive.read_bytes())
    def test_corrupt_archive_does_not_get_overwritten(self):
        self.archive.write_bytes(b'corrupt');self.local('new.json',self.data)
        with self.assertRaises(gzip.BadGzipFile):self.run_summary()
        self.assertEqual(self.archive.read_bytes(),b'corrupt')

if __name__=='__main__':unittest.main()
