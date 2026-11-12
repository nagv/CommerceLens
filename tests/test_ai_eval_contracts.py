import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock
from commercelens_ai.evaluation import _judge, deterministic_checks

CASE={'mode':'ask','question':'Who owns stock?','reference':'Inventory Service.',
      'expected_behavior':'answer','evaluation_contract':{'version':'v3','must_pass':{'owner':'Identify Inventory Service.'},'evidence_topics':{'ownership':'Product and stock ownership'}}}

class ContractTests(unittest.TestCase):
    def test_code_verification_drift_blocks_reference_preflight(self):
        from commercelens_ai.evaluation import _reference_snapshot
        with tempfile.TemporaryDirectory() as directory:
            Path(directory,'service.py').write_text('changed implementation',encoding='utf-8')
            case=dict(CASE,id='drift',expected_behavior='clarify',reference_kind='behavior_rubric',
                      verification_evidence=[{'path':'service.py','sha256':'0'*64}])
            result=_reference_snapshot([case],directory)
            self.assertEqual(result['status'],'mismatch')
            self.assertEqual(result['mismatches'][0]['reason'],'hash_mismatch')

    def payload(self):
        from commercelens_ai.eval_contracts import dimensions_for
        return {'dimensions':{k:{'score':2,'reason':'Supported by the answer.'} for k in dimensions_for(CASE)},
                'requirements':{'owner':{'status':'fail','reason':'Wrong owner.','answer_quote':'Order Service'}},
                'evidence_topics':{'ownership':{'status':'covered','evidence_ids':['c1'],'reason':'States ownership.'}},
                'documentation_gap':{'status':'none','reason':'No conflict identified.'}}

    def grade(self,payload):
        return _judge(Mock(complete=Mock(return_value=json.dumps(payload))),CASE,{'answer':'Order Service owns stock.','retrieved_ids':['c1']})

    def test_long_evidence_ids_use_short_aliases_and_restore_validation(self):
        cid='a'*64
        payload=self.payload();payload['evidence_topics']['ownership']['evidence_ids']=['E1']
        payload['requirements']['owner']['answer_quote']='Order Service [E1]'
        model=Mock(complete=Mock(return_value=json.dumps(payload)))
        result=_judge(model,CASE,{'answer':'Order Service ['+cid+'] owns stock.','retrieved_ids':[cid]})
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result['evidence_topics']['ownership']['evidence_ids'],[cid])
        self.assertNotIn(cid,model.complete.call_args.args[0][1]['content'])

    def test_validation_failure_keeps_safe_reason_and_attempts(self):
        payload=self.payload();payload['requirements']['owner']['answer_quote']='fabricated'
        result=self.grade(payload)
        self.assertEqual(result['validation_errors'],['Fabricated answer quotation']*2)
        self.assertEqual(result['scoring_attempts'],2)

    def test_quote_selection_resolves_exact_original_excerpt(self):
        payload=self.payload();item=payload['requirements']['owner'];item.pop('answer_quote');item['quote_id']='Q1'
        r=self.grade(payload)
        self.assertEqual(r['status'],'ok')
        self.assertEqual(r['requirements']['owner']['answer_quote'],'Order Service owns stock.')

    def test_unknown_quote_selection_stays_error(self):
        payload=self.payload();item=payload['requirements']['owner'];item.pop('answer_quote');item['quote_id']='Q999'
        self.assertEqual(self.grade(payload)['status'],'error')

    def test_failed_requirement_cannot_be_hidden_by_perfect_scores(self):
        result=self.grade(self.payload())
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result['gate_status'],'fail')
        self.assertEqual(result['scores']['critical_gate_pass'],0)
        self.assertEqual(result['scores']['quality'],1)

    def test_unknown_requirement_is_review_not_pass(self):
        p=self.payload();p['requirements']['owner']['status']='unknown'
        r=self.grade(p);self.assertEqual(r['gate_status'],'needs_review');self.assertIsNone(r['scores']['critical_gate_pass'])

    def test_invalid_assessment_is_corrected_once_and_recorded(self):
        invalid=self.payload();invalid['requirements']['owner']['answer_quote']='fabricated'
        model=Mock(complete=Mock(side_effect=[json.dumps(invalid),json.dumps(self.payload())]))
        result=_judge(model,CASE,{'answer':'Order Service owns stock.','retrieved_ids':['c1']})
        self.assertEqual(result['scoring_attempts'],2)
        self.assertEqual(result['validation_errors'],['Fabricated answer quotation'])
        self.assertEqual(result['gate_status'],'fail')
        self.assertEqual(model.complete.call_count,2)

    def test_missing_requirements_or_fabricated_quotes_and_sources_rejected(self):
        for mutate in [lambda p:p['requirements'].clear(),lambda p:p['requirements']['owner'].update(answer_quote='Invented quotation'),lambda p:p['evidence_topics']['ownership'].update(evidence_ids=['not-retrieved'])]:
            p=self.payload();mutate(p);self.assertEqual(self.grade(p)['status'],'error')

    def test_task_specific_dimensions(self):
        from commercelens_ai.eval_contracts import dimensions_for
        debug=dict(CASE,mode='plan',response_policy='investigation_leads')
        self.assertIn('discriminating_checks',dimensions_for(debug))
        self.assertNotIn('plan_strategy',dimensions_for(debug))
        replan=dict(CASE,mode='plan',replan_context={'previous_plan':'old'})
        self.assertIn('replan_exclusions',dimensions_for(replan))

    def test_service_precision_penalizes_unnecessary_selection(self):
        r=deterministic_checks({'expected_services':['inventory']},{'selected_services':['inventory','orders'],'answer':''})
        self.assertEqual(r['service_recall'],1)
        self.assertEqual(r['service_precision'],0.5)
        self.assertAlmostEqual(r['service_f1'],2/3)

if __name__=='__main__':unittest.main()
