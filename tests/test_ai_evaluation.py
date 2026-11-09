import json
import hashlib
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from commercelens_ai.evaluation import run_evaluation, deterministic_checks, _ragas, _strip_known_citations


CASE = dict(id='one', question='Who owns stock?', mode='ask', reference='Inventory owns stock.',
            expected_services=['inventory-service'], required_facts=['stock'],
            required_considerations=[], forbidden_assumptions=[], reference_evidence=[])
RESULT = dict(answer='Inventory owns stock. [c1]', selected_services=['inventory-service'],
              citations=[dict(id='c1', source_url='https://example.com/wiki')],
              retrieved_ids=['c1'], retrieved_contexts=['Inventory owns stock.'],
              status='ok', latency_seconds=0.2, model_calls=2, tool_calls=3, trace=[])


class EvaluationTests(unittest.TestCase):
    def evaluate(self, assistant=None, **kwargs):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as directory:
            path = Path(directory) / 'golden.jsonl'
            path.write_text(json.dumps(CASE)+'\n', encoding='utf-8')
            summary = run_evaluation(assistant or Mock(run=Mock(return_value=RESULT)), path, directory, **kwargs)
            rows = [json.loads(x) for x in (Path(directory)/'runs.jsonl').read_text().splitlines()]
            self.assertEqual(json.loads((Path(directory)/'summary.json').read_text()), summary)
            return summary, rows

    def test_repetitions_continue_after_failure_and_aggregate_valid_only(self):
        assistant = Mock(run=Mock(side_effect=[RuntimeError('secret'), RESULT]))
        summary, rows = self.evaluate(assistant, repetitions=2)
        self.assertEqual(summary['run_count'], 2)
        self.assertEqual(summary['failure_count'], 1)
        self.assertEqual(summary['metrics']['service_recall']['count'], 1)
        self.assertEqual(summary['metrics']['service_recall']['mean'], 1)
        self.assertEqual(rows[0]['error'], 'RuntimeError')
        self.assertEqual(rows[1]['judge']['status'], 'skipped')

    def test_citation_must_match_retrieval_and_answer(self):
        bad = dict(RESULT, citations=[dict(id='invented', source_url='https://example.com/wiki')])
        self.assertEqual(deterministic_checks(CASE, bad)['citation_validity'], 0)
        self.assertEqual(deterministic_checks(CASE, RESULT)['citation_validity'], 1)

    def test_missing_retrieval_ids_not_claimed_as_verified(self):
        result = dict(RESULT)
        del result['retrieved_ids']
        self.assertIsNone(deterministic_checks(CASE, result)['citation_validity'])

    def test_invalid_judge_json_is_error_not_zero_score(self):
        summary, rows = self.evaluate(judge=Mock(complete=Mock(return_value='not json')))
        self.assertEqual(rows[0]['judge']['status'], 'error')
        self.assertEqual(summary['judge']['error'], 1)
        self.assertNotIn('judge_groundedness', summary['metrics'])

    def test_valid_judge_scores_and_ask_plan_quality_null(self):
        scores=dict(groundedness=1, completeness=0.5, plan_quality=None, uncertainty=1)
        summary, rows = self.evaluate(judge=Mock(complete=Mock(return_value=json.dumps(scores))))
        self.assertEqual(summary['metrics']['judge_completeness']['mean'], 0.5)
        self.assertEqual(rows[0]['judge']['status'], 'ok')

    def test_ragas_requires_explicit_models(self):
        summary, rows = self.evaluate(ragas=True)
        self.assertEqual(rows[0]['ragas']['status'], 'missing_configuration')

    def test_langsmith_uploads_dataset_linked_experiment_and_feedback(self):
        client=Mock()
        client.create_dataset.return_value=SimpleNamespace(id='dataset')
        client.create_example.return_value=SimpleNamespace(id='example')
        client.create_project.return_value=SimpleNamespace(id='project')
        summary, rows=self.evaluate(langsmith=True, langsmith_client=client)
        self.assertEqual(summary['langsmith']['status'], 'ok')
        self.assertEqual(client.create_project.call_args.kwargs['reference_dataset_id'], 'dataset')
        self.assertEqual(client.create_run.call_args.kwargs['reference_example_id'], 'example')
        self.assertTrue(client.create_feedback.called)
        self.assertEqual(client.update_project.call_args.kwargs['project_id'], 'project')

    def test_ragas_filters_nan_and_keeps_metric_failure_visible(self):
        evaluate=Mock(return_value=SimpleNamespace(scores=[{'faithfulness':float('nan'), 'answer_relevancy':0.75}]))
        modules={'ragas':SimpleNamespace(EvaluationDataset=SimpleNamespace(from_list=lambda rows:rows),evaluate=evaluate),
                 'ragas.metrics._faithfulness':SimpleNamespace(Faithfulness=Mock),
                 'ragas.metrics._answer_relevance':SimpleNamespace(AnswerRelevancy=Mock),
                 'ragas.metrics._context_precision':SimpleNamespace(LLMContextPrecisionWithReference=Mock),
                 'ragas.metrics._factual_correctness':SimpleNamespace(FactualCorrectness=Mock),
                 'ragas.metrics._context_recall':SimpleNamespace(LLMContextRecall=Mock)}
        with patch.dict('sys.modules',modules):
            summary, rows=self.evaluate(ragas=True, ragas_llm=object(), ragas_embeddings=object())
        self.assertEqual(rows[0]['ragas']['status'], 'partial')
        self.assertEqual(rows[0]['ragas']['missing_metrics'], ['faithfulness'])
        self.assertEqual(summary['metrics']['ragas_answer_relevancy']['mean'], 0.75)

    def test_ragas_factual_suite_uses_references_and_all_five_metrics(self):
        names=['faithfulness','answer_relevancy','llm_context_recall',
               'llm_context_precision_with_reference','factual_correctness']
        evaluate=Mock(return_value=SimpleNamespace(scores=[dict.fromkeys(names,1.0)]))
        def metric(name): return lambda:SimpleNamespace(name=name)
        modules={'ragas':SimpleNamespace(EvaluationDataset=SimpleNamespace(from_list=lambda rows:rows),evaluate=evaluate),
                 'ragas.metrics._faithfulness':SimpleNamespace(Faithfulness=metric(names[0])),
                 'ragas.metrics._answer_relevance':SimpleNamespace(AnswerRelevancy=metric(names[1])),
                 'ragas.metrics._context_recall':SimpleNamespace(LLMContextRecall=metric(names[2])),
                 'ragas.metrics._context_precision':SimpleNamespace(LLMContextPrecisionWithReference=metric(names[3])),
                 'ragas.metrics._factual_correctness':SimpleNamespace(FactualCorrectness=metric(names[4]))}
        llm,embeddings=object(),object()
        with patch.dict('sys.modules',modules):
            result=_ragas(CASE,RESULT,True,llm,embeddings)
        self.assertEqual(result['status'],'ok')
        self.assertEqual({m.name for m in evaluate.call_args.kwargs['metrics']},set(names))
        self.assertEqual(evaluate.call_args.args[0][0]['reference'],CASE['reference'])
        self.assertNotIn('[c1]',evaluate.call_args.args[0][0]['response'])
        self.assertIn('[c1]',RESULT['answer'])
        self.assertIs(evaluate.call_args.kwargs['llm'],llm)
        self.assertIs(evaluate.call_args.kwargs['embeddings'],embeddings)

    def test_ragas_plan_skips_proposals_even_without_models(self):
        result=_ragas(dict(CASE,mode='plan',reference=None),RESULT,True,None,None)
        self.assertEqual(result['status'],'skipped')
        self.assertIn('proposed',result['reason'])
        self.assertNotIn('scores',result)

    def test_reported_assistant_failure_is_not_scored(self):
        summary,rows=self.evaluate(Mock(run=Mock(return_value=dict(RESULT,status='error'))))
        self.assertEqual(summary['failure_count'],1)
        self.assertNotIn('service_recall',summary['metrics'])
        self.assertNotIn('citation_validity',summary['metrics'])
        self.assertEqual(summary['metrics']['latency_seconds']['mean'],0.2)
        self.assertEqual(summary['metrics']['model_calls']['mean'],2)
        self.assertEqual(summary['metrics']['tool_calls']['mean'],3)

    def test_strip_known_citations_preserves_unrelated_brackets_and_links(self):
        text='[c1] Inventory stock [c2]. Keep [unknown], [1, 2] and [c1](https://example.com).'
        cleaned=_strip_known_citations(text,{'c1','c2'})
        self.assertEqual(cleaned,'Inventory stock . Keep [unknown], [1, 2] and [c1](https://example.com).')
        self.assertEqual(_strip_known_citations('[unknown]',set()),'[unknown]')

    def test_ragas_cleans_context_ids_without_mutating_original_context(self):
        evaluate=Mock(return_value=SimpleNamespace(scores=[{'faithfulness':1.0}]))
        modules={'ragas':SimpleNamespace(EvaluationDataset=SimpleNamespace(from_list=lambda rows:rows),evaluate=evaluate),
                 'ragas.metrics._faithfulness':SimpleNamespace(Faithfulness=Mock),
                 'ragas.metrics._answer_relevance':SimpleNamespace(AnswerRelevancy=Mock),
                 'ragas.metrics._context_precision':SimpleNamespace(LLMContextPrecisionWithReference=Mock),
                 'ragas.metrics._factual_correctness':SimpleNamespace(FactualCorrectness=Mock),
                 'ragas.metrics._context_recall':SimpleNamespace(LLMContextRecall=Mock)}
        original=dict(RESULT,retrieved_contexts=['[c1] Inventory has [reserved] stock.'])
        with patch.dict('sys.modules',modules):
            result=_ragas(CASE,original,True,object(),object())
        self.assertEqual(result['status'],'ok')
        self.assertEqual(evaluate.call_args.args[0][0]['retrieved_contexts'],['Inventory has [reserved] stock.'])
        self.assertEqual(original['retrieved_contexts'],['[c1] Inventory has [reserved] stock.'])

    def test_snapshot_validation_rejects_stale_evidence_before_running(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as directory:
            root=Path(directory)
            evidence=root/'source.md'
            evidence.write_text('original evidence',encoding='utf-8')
            case=dict(CASE,reference_evidence=[{'path':'source.md','sha256':hashlib.sha256(evidence.read_bytes()).hexdigest()}])
            dataset=root/'subset.jsonl'
            dataset.write_text(json.dumps(case)+'\n',encoding='utf-8')
            assistant=Mock(run=Mock(return_value=RESULT))
            summary=run_evaluation(assistant,dataset,root/'valid',evidence_root=root)
            self.assertEqual(summary['reference_snapshot_status']['status'],'validated')
            self.assertEqual(summary['reference_snapshot_status']['checked_files'],1)
            assistant.reset_mock()
            evidence.write_text('changed documentation',encoding='utf-8')
            with self.assertRaisesRegex(ValueError,'snapshot.*source.md'):
                run_evaluation(assistant,dataset,root/'stale',evidence_root=root)
            assistant.run.assert_not_called()
            self.assertFalse((root/'stale'/'runs.jsonl').exists())
            preflight=json.loads((root/'stale'/'summary.json').read_text())
            self.assertEqual(preflight['reference_snapshot_status']['mismatches'][0]['reason'],'hash_mismatch')

    def test_snapshot_validation_reports_not_checked_when_root_omitted(self):
        summary,_=self.evaluate()
        self.assertEqual(summary['reference_snapshot_status']['status'],'not_checked')

    def test_snapshot_validation_rejects_missing_evidence(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as directory:
            root=Path(directory)
            case=dict(CASE,reference_evidence=[{'path':'missing.md','sha256':'0'*64}])
            dataset=root/'subset.jsonl'
            dataset.write_text(json.dumps(case)+'\n',encoding='utf-8')
            assistant=Mock()
            with self.assertRaisesRegex(ValueError,'snapshot.*missing.md'):
                run_evaluation(assistant,dataset,root/'output',evidence_root=root)
            assistant.run.assert_not_called()

    def test_golden_cases_have_versioned_evidence(self):
        path=Path(__file__).resolve().parents[1]/'evals/golden.jsonl'
        cases=[json.loads(line) for line in path.read_text().splitlines()]
        self.assertGreaterEqual(len(cases), 12)
        self.assertEqual(len({c['id'] for c in cases}), len(cases))
        for case in cases:
            self.assertTrue(case['reference_evidence'])
            self.assertTrue(all(len(e['sha256']) == 64 for e in case['reference_evidence']))
            if case['mode']=='ask': self.assertTrue(case['reference'])
            else: self.assertEqual(case['reference_kind'], 'proposed_plan_rubric')


if __name__=='__main__': unittest.main()
