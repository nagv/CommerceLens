import json,unittest,urllib.error
from unittest.mock import patch
from test_ai_engine import Retriever,Model,GRAPH
from test_ai_providers import Response
from commercelens_ai.engine import Assistant
from commercelens_ai.providers import OpenAICompatibleModel,ProviderError
class ReliabilityTests(unittest.TestCase):
 def test_grouped_citations_resolve_individually(self):
  r=Assistant(Retriever(),Model('Documented [S1, S2].'),GRAPH).run('What is order?')
  self.assertEqual(r['status'],'ok');self.assertEqual(len(r['citations']),2)
 def test_unknown_in_group_is_still_rejected(self):
  r=Assistant(Retriever(),Model('Documented [S1, S999].'),GRAPH).run('What is order?')
  self.assertEqual(r['status'],'invalid_citations')
 def test_context_label_is_not_a_source(self):
  r=Assistant(Retriever(),Model('Your [replan_context] is a proposal. Current fact [S1].'),GRAPH).run('What is order?')
  self.assertEqual(r['status'],'ok');self.assertEqual(len(r['citations']),1)
 def test_invalid_envelope_gets_one_repair(self):
  model=Model('');responses=iter(['{"behavior":"answer","factual_claims":"yes","answer":"Fact [S1]"}',json.dumps({'behavior':'answer','factual_claims':True,'answer':'Fact [S1]'})])
  model.complete=lambda messages:next(responses)
  r=Assistant(Retriever(),model,GRAPH).run('What is order?')
  self.assertEqual(r['status'],'ok');self.assertEqual(r['model_calls'],2)
 def test_invalid_repair_stays_failure(self):
  r=Assistant(Retriever(),Model('{"answer":"bad"}'),GRAPH).run('What is order?')
  self.assertEqual(r['status'],'error');self.assertEqual(r['model_calls'],2)
  self.assertEqual(r['trace'][-1]['error_category'],'response_schema')
 def test_transient_http_retried_once(self):
  good=Response({'choices':[{'message':{'content':'ok'},'finish_reason':'stop'}]})
  with patch('urllib.request.OpenerDirector.open',side_effect=[urllib.error.HTTPError('https://example.test',429,'secret',{},None),good]) as op,patch('time.sleep'):
   m=OpenAICompatibleModel('secret','https://example.test','chat');self.assertEqual(m.complete([]),'ok');self.assertEqual(op.call_count,2)
 def test_auth_error_not_retried_and_sanitized(self):
  with patch('urllib.request.OpenerDirector.open',side_effect=urllib.error.HTTPError('https://example.test',401,'secret',{},None)) as op:
   with self.assertRaises(ProviderError) as caught:OpenAICompatibleModel('secret','https://example.test','chat').complete([])
  self.assertEqual(op.call_count,1);self.assertEqual(caught.exception.category,'authentication');self.assertEqual(caught.exception.http_status,401);self.assertNotIn('secret',str(caught.exception))

 def test_repair_explains_mode_is_not_behavior(self):
  model=Model('{"behavior":"plan","factual_claims":true,"answer":"Fact [S1]"}')
  Assistant(Retriever(),model,GRAPH).run('What is order?')
  instruction=model.messages[-1][-1]['content']
  self.assertIn('plan is a mode, not a behavior',instruction)
  self.assertIn('answer, partial_answer, uncertain, unknown, clarify, redirect',instruction)
