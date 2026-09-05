import copy
import unittest
from w13_sales_delay import wrap_sales_delay

class DelayTests(unittest.TestCase):
    def setup_policy(self, gate=False, config=None):
        self.routes={'default':[{'farmer':['PASS'],'hands':[],'market':[]} for _ in range(719)]}
        self.routes['default'][200]['market']=[['SELL','STRAWBERRY',5],['SELL','MILK',2]]
        def base(obs,cfg):return copy.deepcopy(self.routes['default'][obs['step']])
        self.policy=wrap_sales_delay(base,self.routes,lambda item,inv:20000-inv,{'TEST':['STRAWBERRY']},gate)
        self.obs={'step':200,'player':0,'farms':[{'money':1000}],
                  'private':{'shed':{'STRAWBERRY':5,'MILK':2}},
                  'market':{'inventory':{'STRAWBERRY':10000}},'town':{'unlocked_shops':['TEST']}}
        self.config=config or {}
    def test_exact_two_turn_delay_and_order_slots(self):
        self.setup_policy();a=self.policy(self.obs,{})
        self.assertEqual(a['market'],[['SELL','STRAWBERRY',0],['SELL','MILK',2]])
        self.obs['step']=201;self.assertEqual(self.policy(self.obs,{})['market'],[])
        self.obs['step']=202;self.assertEqual(self.policy(self.obs,{})['market'],[['SELL','STRAWBERRY',5]])
        self.obs['step']=203;self.assertEqual(self.policy(self.obs,{})['market'],[])
    def test_purchase_obligation_veto(self):
        self.setup_policy();self.routes['default'][201]['market']=[['BUY_SEED','WHEAT',1]]
        self.assertEqual(self.policy(self.obs,{})['market'][0][2],5)
    def test_deposit_veto(self):
        self.setup_policy();self.routes['default'][201]['farmer']=['DROP']
        self.assertEqual(self.policy(self.obs,{})['market'][0][2],5)
    def test_future_batch_veto(self):
        self.setup_policy();self.routes['default'][204]['market']=[['SELL','STRAWBERRY',1]]
        self.assertEqual(self.policy(self.obs,{})['market'][0][2],5)
    def test_recovery_requires_history(self):
        self.setup_policy(True);self.assertEqual(self.policy(self.obs,{})['market'][0][2],5)
    def test_recovery_can_activate(self):
        self.setup_policy(True);self.obs['step']=199;self.policy(self.obs,{})
        self.obs['step']=200;self.assertEqual(self.policy(self.obs,{})['market'][0][2],0)
    def test_no_double_sale_if_unexpected_baseline_sale(self):
        self.setup_policy();self.policy(self.obs,{})
        self.routes['default'][202]['market']=[['SELL','STRAWBERRY',5]]
        self.obs['step']=202;rows=self.policy(self.obs,{})['market']
        self.assertEqual(sum(r[2] for r in rows if r[:2]==['SELL','STRAWBERRY']),5)
    def test_reset_drops_previous_game_queue(self):
        self.setup_policy();self.policy(self.obs,{})
        self.obs['step']=0;self.policy(self.obs,{})
        self.obs['step']=202;self.assertEqual(self.policy(self.obs,{})['market'],[])
    def test_terminal_uses_original_liquidation(self):
        self.setup_policy();self.policy(self.obs,{})
        self.routes['default'][718]['market']=[['SELL','STRAWBERRY',5]]
        self.obs['step']=718;self.assertEqual(self.policy(self.obs,{})['market'],[['SELL','STRAWBERRY',5]])

if __name__=='__main__':unittest.main()
