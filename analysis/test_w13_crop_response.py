import copy
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
NS = runpy.run_path(str(ROOT/'variants/w13_crop_response/main.py'))


def observation(step, carrot_inventory=9000):
    return {'step':step,'player':0,'farms':[{'money':6000,'farmer':[0,0], 'hands':[],
        'tiles':[[None for _ in range(10)] for _ in range(10)]}],
        'private':{'seeds':{'CARROT':1,'WHEAT':1},'shed':{}},
        'market':{'inventory':{'CARROT':carrot_inventory,'WHEAT':10000}}}

def base(obs, configuration):
    return {'farmer':['PLANT','WHEAT'] if obs['step']==301 else ['PASS'],
            'hands':[], 'market':[]}


class CropResponseTests(unittest.TestCase):
    def test_seed_purchase_precedes_plant(self):
        policy = NS['_CropResponse'](base, {'301':[[0,0,0]]})
        self.assertIn(['BUY_SEED','CARROT',1],policy(observation(300))['market'])
        self.assertEqual(policy(observation(301))['farmer'],['PLANT','CARROT'])
        self.assertEqual(policy.delay_telemetry['planted'],1)

    def test_position_mismatch_preserves_original_action(self):
        policy = NS['_CropResponse'](base, {'301':[[0,0,0]]})
        policy(observation(300));obs=observation(301);obs['farms'][0]['farmer']=[1,0]
        self.assertEqual(policy(obs)['farmer'],['PLANT','WHEAT'])

    def test_no_seed_and_existing_crop_are_vetoes(self):
        for veto in ('seed','tile'):
            policy = NS['_CropResponse'](base, {'301':[[0,0,0]]})
            policy(observation(300));obs=observation(301)
            if veto=='seed':obs['private']['seeds']['CARROT']=0
            else:obs['farms'][0]['tiles'][0][0]={'crop':'WHEAT','kind':'PLANT'}
            self.assertEqual(policy(obs)['farmer'],['PLANT','WHEAT'])

    def test_unprofitable_and_poor_states_do_not_buy(self):
        for poor in (False,True):
            policy=NS['_CropResponse'](base, {'301':[[0,0,0]]})
            obs=observation(300,9000 if poor else 10000)
            if poor:obs['farms'][0]['money']=4999
            self.assertEqual(policy(obs)['market'],[])

    def test_preserves_seed_reserve_for_original_carrot_orders(self):
        def mixed(obs,cfg):return {'farmer':['PLANT','WHEAT'],'hands':[['PLANT','CARROT']],'market':[]}
        policy=NS['_CropResponse'](mixed, {})
        policy.pending[301]=[[0,0,0]]
        obs=observation(301);obs['farms'][0]['hands']=[[1,0]]
        self.assertEqual(policy(obs)['farmer'],['PLANT','WHEAT'])


if __name__=='__main__':unittest.main()
