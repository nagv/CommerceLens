import json
import tempfile
import unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import Mock
from commercelens_ai.evaluation import _judge, run_evaluation

DIMENSIONS=('strategy','service_impacts','service_details','implementation_order','requirement_coverage','alternatives','recommendation_rationale','grounding')

def assessment():
    return {'dimensions':{k:{'score':2,'reason':'The plan gives concrete service-level steps supported by the supplied evidence.'} for k in DIMENSIONS},'critical_issues':[]}

CASE={'id':'shipping','mode':'plan','question':'Introduce destination-based shipping.', 'reference':None,
      'alternatives_policy':'conditional','reference_kind':'proposed_plan_rubric'}

class PlanEvaluationTests(unittest.TestCase):
    def grade(self, payload, case=CASE):
        return _judge(Mock(complete=Mock(return_value=json.dumps(payload))),case,{'answer':'Proposed plan'})

    def test_dimensions_and_reasons_retained(self):
        result=self.grade(assessment())
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result['scores']['plan_service_details'],2)
        self.assertEqual(result['scores']['plan_quality'],1)
        self.assertTrue(result['rationale']['service_details'])

    def test_missing_dimension_is_error_not_partial_success(self):
        payload=assessment();del payload['dimensions']['grounding']
        self.assertEqual(self.grade(payload)['status'],'error')

    def test_scores_require_zero_one_two_not_booleans_or_fractional(self):
        for value in [True,3,-1,0.7,None]:
            with self.subTest(value=value):
                payload=assessment();payload['dimensions']['strategy']['score']=value
                self.assertEqual(self.grade(payload)['status'],'error')

    def test_conditional_alternatives_can_be_not_applicable(self):
        payload=assessment();payload['dimensions']['alternatives']={'score':None,'reason':'A cosmetic wording-only change has no meaningful architectural variation.'}
        result=self.grade(payload)
        self.assertEqual(result['status'],'ok')
        self.assertIsNone(result['scores']['plan_alternatives'])
        self.assertEqual(result['applicable_dimensions'],7)
        self.assertEqual(result['scores']['plan_quality'],1)
        self.assertEqual(self.grade(payload,dict(CASE,alternatives_policy='required'))['status'],'error')

    def test_unsupported_facts_remain_visible_despite_good_structure(self):
        payload=assessment();payload['dimensions']['grounding']={'score':0,'reason':'The plan invents an existing provider quote endpoint.'};payload['critical_issues']=['Invented current provider capability']
        result=self.grade(payload)
        self.assertEqual(result['scores']['groundedness'],0)
        self.assertEqual(result['scores']['plan_grounding'],0)
        self.assertEqual(result['critical_issues'],payload['critical_issues'])
        self.assertLess(result['scores']['plan_quality'],1)

    def test_missing_reason_is_rejected(self):
        payload=assessment();payload['dimensions']['alternatives']['reason']=''
        self.assertEqual(self.grade(payload)['status'],'error')

    def test_dimension_scores_flow_into_experiment_summary(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as d:
            p=Path(d)/'cases.jsonl';p.write_text(json.dumps(CASE)+'\n')
            result={'status':'ok','answer':'Proposed plan','retrieved_ids':[],'citations':[]}
            payload=assessment();payload['dimensions']['alternatives']['score']=None
            summary=run_evaluation(Mock(run=Mock(return_value=result)),p,Path(d)/'out',judge=Mock(complete=Mock(return_value=json.dumps(payload))))
            self.assertEqual(summary['metrics']['judge_plan_strategy']['mean'],2)
            self.assertEqual(summary['metrics']['judge_plan_alternatives']['count'],0)
            self.assertIsNone(summary['metrics']['judge_plan_alternatives']['mean'])

    def test_langsmith_feedback_includes_dimension_reason(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as d:
            p=Path(d)/'cases.jsonl';p.write_text(json.dumps(CASE)+'\n')
            client=Mock();client.create_dataset.return_value=SimpleNamespace(id='dataset');client.create_example.return_value=SimpleNamespace(id='example');client.create_project.return_value=SimpleNamespace(id='project')
            payload=assessment()
            summary=run_evaluation(Mock(run=Mock(return_value={'status':'ok','answer':'Plan'})),p,Path(d)/'out',judge=Mock(complete=Mock(return_value=json.dumps(payload))),langsmith=True,langsmith_client=client)
            self.assertEqual(summary['langsmith']['status'],'ok')
            feedback=next(c.kwargs for c in client.create_feedback.call_args_list if c.kwargs['key']=='judge_plan_strategy')
            self.assertEqual(feedback.get('comment'),payload['dimensions']['strategy']['reason'])

if __name__=='__main__':unittest.main()
