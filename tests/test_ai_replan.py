import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock
from commercelens_ai.engine import Assistant
from commercelens_ai.evaluation import run_evaluation

CONTEXT=dict(original_request='Change shipping prices',previous_plan='Use regional rules.',selected_alternative='Provider quotes',instruction='No regional fallback.')

class ReplanTests(unittest.TestCase):
    def test_evaluation_dispatches_structured_context(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as directory:
            path=Path(directory)/'cases.jsonl'
            path.write_text(json.dumps(dict(id='revision',mode='plan',question='Replan',replan_context=CONTEXT,reference=None))+'\n')
            assistant=Mock(replan=Mock(return_value=dict(status='ok',answer='Revised plan')))
            summary=run_evaluation(assistant,path,Path(directory)/'out')
            assistant.replan.assert_called_once_with(**CONTEXT)
            assistant.run.assert_not_called()
            self.assertEqual(summary['failure_count'],0)

    def test_replan_retrieves_fresh_evidence_and_passes_context(self):
        retriever=Mock(search=Mock(return_value=[dict(id='fresh',text='Current shipping facts',metadata={'source_url':'https://example.test/wiki'})]))
        model=Mock(complete=Mock(return_value=json.dumps(dict(behavior='answer',factual_claims=True,answer='Current facts [S1]. Proposed provider quotes.'))))
        result=Assistant(retriever,model,{'nodes':[]}).replan(**CONTEXT)
        self.assertEqual(result['status'],'ok')
        self.assertEqual(result['request_type'],'replan')
        self.assertEqual(result['original_request'],CONTEXT['original_request'])
        self.assertIn('Provider quotes',retriever.search.call_args.args[0])
        payload=json.loads(model.complete.call_args.args[0][1]['content'])
        self.assertEqual(payload['replan_context'],CONTEXT)
        self.assertEqual(result['retrieved_ids'],['fresh'])

    def test_invalid_context_rejected_before_retrieval(self):
        retriever=Mock()
        assistant=Assistant(retriever,Mock(),{'nodes':[]})
        for field,value in [('previous_plan',''),('selected_alternative',''),('instruction',5),('previous_plan','x'*32001)]:
            with self.subTest(field=field):
                with self.assertRaises(ValueError):assistant.replan(**dict(CONTEXT,**{field:value}))
        retriever.search.assert_not_called()

if __name__=='__main__':unittest.main()
