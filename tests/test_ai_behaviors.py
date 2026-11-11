import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from commercelens_ai.engine import Assistant
from commercelens_ai.evaluation import deterministic_checks, run_evaluation, _ragas, _judge


class BehaviorTests(unittest.TestCase):
    def test_debug_policy_grades_leads_without_implementation_plan(self):
        scores=dict(groundedness=1,completeness=1,plan_quality=None,uncertainty=1,correctness=1,behavior_appropriateness=1)
        judge=Mock(complete=Mock(return_value=json.dumps(scores)))
        case=dict(mode='plan',expected_behavior='uncertain',response_policy='investigation_leads',reference_kind='behavior_rubric')
        result=_judge(judge,case,dict(answer='Check the original payment outcome before concluding it failed.'))
        self.assertEqual(result['status'],'ok')
        self.assertIsNone(result['scores']['plan_quality'])
        prompt=judge.complete.call_args.args[0][0]['content']
        self.assertIn('investigation leads only',prompt)
        self.assertIn('Do not reward implementation plans',prompt)

    def test_debug_guidance_applies_even_in_plan_mode(self):
        model=Mock(complete=Mock(return_value=json.dumps(dict(behavior='uncertain',factual_claims=True,answer='Payment outcomes can be uncertain [S1]. Check the original attempt.'))))
        retriever=Mock(search=Mock(return_value=[dict(id='c1',text='Payment timeouts leave the outcome unknown.',metadata={'source_url':'https://example.test/wiki'})]))
        result=Assistant(retriever,model,{'nodes':[],'edges':[]}).run('Payment timed out, so it failed. Plan an automatic retry.',mode='plan')
        self.assertEqual(result['status'],'ok')
        self.assertIn('investigation leads only',model.complete.call_args.args[0][0]['content'])

    def test_plan_clarification_uses_behavior_scores_not_plan_dimensions(self):
        scores=dict(groundedness=1,completeness=1,plan_quality=None,uncertainty=1,correctness=1,behavior_appropriateness=1)
        judge=Mock(complete=Mock(return_value=json.dumps(scores)))
        case=dict(mode='plan',expected_behavior='clarify',reference_kind='behavior_rubric')
        result=_judge(judge,case,dict(answer='Which operation needs retries?'))
        self.assertEqual(result['status'],'ok')
        self.assertIsNone(result['scores']['plan_quality'])
        self.assertEqual(result['scores']['behavior_appropriateness'],1)
        self.assertIn('Do not require implementation sections',judge.complete.call_args.args[0][0]['content'])

    def test_plan_clarification_routes_without_retrieval(self):
        model=Mock(complete=Mock(return_value=json.dumps(dict(service_ids=[],intent='clarify',response='Which operation needs retries? Please re-ask with more details.'))))
        retriever=Mock(search=Mock(side_effect=AssertionError('Clarification needs no retrieval')))
        result=Assistant(retriever,model,{'nodes':[{'id':'orders','type':'service'}]}).run('Plan a change to improve retries in CommerceLens.',mode='plan')
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result['behavior'],'clarify')
        retriever.search.assert_not_called()

    def response(self, behavior, factual=False, answer='Which operation do you mean?'):
        model=Mock(complete=Mock(return_value=json.dumps(dict(behavior=behavior, answer=answer, factual_claims=factual))))
        retriever=Mock(search=Mock(return_value=[dict(id='c1',text='Orders reserve stock.',metadata={'source_url':'https://example.test/wiki'})]))
        return Assistant(retriever,model,{'nodes':[],'edges':[]}).run('What happens if it fails?')

    def test_nonfactual_responses_need_no_citation(self):
        for behavior in ['clarify','unknown','redirect']:
            with self.subTest(behavior=behavior):
                result=self.response(behavior)
                self.assertEqual(result['status'],'ok')
                self.assertEqual(result.get('behavior'),behavior)
                self.assertEqual(result['citations'],[])

    def test_factual_claims_still_need_citations_even_in_abstention(self):
        self.assertEqual(self.response('unknown',True)['status'],'invalid_citations')
        self.assertEqual(self.response('answer',False)['status'],'invalid_citations')
        self.assertEqual(self.response('uncertain',False)['status'],'invalid_citations')

    def test_invalid_citations_rejected_even_when_optional(self):
        self.assertEqual(self.response('clarify',False,'Which order [invented]?')['status'],'invalid_citations')

    def test_cited_structured_answer_preserves_canonical_ids(self):
        result=self.response('answer',True,'Orders reserve stock [S1].')
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result['answer'],'Orders reserve stock [c1].')

    def test_no_evidence_is_successful_abstention(self):
        result=Assistant(Mock(search=Mock(return_value=[])),Mock(),{'nodes':[]}).run('Who owns stock?')
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result.get('behavior'),'unknown')

    def test_optional_citations_not_scored_as_failure(self):
        case=dict(expected_behavior='clarify',citation_policy='optional')
        result=dict(answer='Which operation?',behavior='clarify',citations=[],retrieved_ids=[])
        checks=deterministic_checks(case,result)
        self.assertIsNone(checks['citation_validity'])
        self.assertEqual(checks.get('behavior_match'),1)
        self.assertEqual(deterministic_checks(case,dict(result,behavior='answer'))['behavior_match'],0)

    def test_behavioral_cases_skip_factual_ragas(self):
        for behavior in ['clarify','redirect','unknown','uncertain']:
            result=_ragas(dict(mode='ask',expected_behavior=behavior),{},True,None,None)
            self.assertEqual(result['status'],'skipped')

    def test_abstention_is_not_execution_failure_but_mismatch_is_visible(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as d:
            p=Path(d)/'cases.jsonl'
            cases=[dict(id='known',question='Who owns stock?',mode='ask',reference='Inventory',expected_behavior='answer'),
                   dict(id='unknown',question='Live sales?',mode='ask',reference='Unavailable',expected_behavior='unknown',citation_policy='optional')]
            p.write_text(''.join(json.dumps(c)+'\n' for c in cases))
            assistant=Mock(run=Mock(return_value=dict(status='insufficient_evidence',answer='Unavailable',citations=[],retrieved_ids=[])))
            summary=run_evaluation(assistant,p,Path(d)/'results')
            self.assertEqual(summary['failure_count'],0)
            self.assertEqual(summary['metrics']['behavior_match']['mean'],0.5)

    def test_semantic_scores_are_separate_from_keyword_matches(self):
        case=dict(mode='ask',expected_behavior='answer',reference='Duplicates are prevented.',required_facts=['duplicates'])
        result=dict(answer='Duplicates are not prevented.')
        judge=Mock(complete=Mock(return_value=json.dumps(dict(groundedness=0,completeness=0,plan_quality=None,uncertainty=0,correctness=0,behavior_appropriateness=1))))
        self.assertEqual(deterministic_checks(case,result)['lexical_required_fact_coverage'],1)
        graded=_judge(judge,case,result)
        self.assertEqual(graded['status'],'ok')
        self.assertEqual(graded['scores']['correctness'],0)

    def test_ask_only_evaluation_excludes_plans(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as d:
            path=Path(d)/'cases.jsonl'
            path.write_text('\n'.join(json.dumps(c) for c in [
                dict(id='ask',mode='ask',question='Which provider?',reference='Clarify',expected_behavior='clarify',reference_kind='behavior_rubric'),
                dict(id='plan',mode='plan',question='Change provider',reference=None)]))
            result=dict(status='ok',behavior='clarify',answer='Which integration?',citations=[],retrieved_ids=[])
            summary=run_evaluation(Mock(run=Mock(return_value=result)),path,Path(d)/'out',case_mode='ask',evidence_root=d)
            self.assertEqual(summary['case_count'],1)
            self.assertEqual(summary['failure_count'],0)

    def test_clarification_routing_happens_without_retrieval(self):
        model=Mock(complete=Mock(return_value=json.dumps({'service_ids':[], 'intent':'clarify', 'response':'Which operation do you mean?'})))
        retriever=Mock(search=Mock(side_effect=AssertionError('Do not retrieve for clarification')))
        graph={'nodes':[{'id':'orders','type':'service'}]}
        result=Assistant(retriever,model,graph).run('What happens if it fails?')
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result['behavior'],'clarify')
        self.assertEqual(result['tool_calls'],0)

    def test_scope_routing_happens_without_retrieval(self):
        model=Mock(complete=Mock(return_value=json.dumps({'service_ids':[], 'intent':'redirect', 'response':'Please ask about CommerceLens.'})))
        result=Assistant(Mock(search=Mock(side_effect=AssertionError())),model,{'nodes':[{'id':'orders','type':'service'}]}).run('Recommend a holiday destination.')
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result['behavior'],'redirect')


if __name__=='__main__':
    unittest.main()

