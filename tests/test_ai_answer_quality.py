import json,unittest
from unittest.mock import Mock
from test_ai_engine import Retriever,GRAPH
from commercelens_ai.engine import Assistant

PLAN={'strategy':'Proposed bounded change. Current owner [S1].','service_changes':'- Order: proposed change with failure handling.','implementation_order':'1. Confirm contract.\n2. Implement and validate.','requirement_coverage':'- Requested outcome: supplied by the change.','alternatives':'- Alternative: different trade-off.','recommendation':'Prefer this approach because it preserves existing boundaries.','validation':'Check success, retries and failure paths.'}
def envelope(answer='Draft [S1].',**kwargs):return json.dumps(dict(behavior='answer',factual_claims=True,answer=answer,**kwargs))
class AnswerQualityTests(unittest.TestCase):
 def test_structured_plan_is_rendered_in_required_sections(self):
  from commercelens_ai.response_contract import decode_response
  p=decode_response(envelope(plan=PLAN))
  for heading in ['Overall strategy','Service changes','Implementation order','How this meets the request','Alternatives','Why this approach','Validation']:
   self.assertIn('## '+heading,p['answer'])
  self.assertIn('[S1]',p['answer'])
 def test_incomplete_plan_is_rejected(self):
  from commercelens_ai.response_contract import decode_response
  with self.assertRaises(ValueError):decode_response(envelope(plan={'strategy':'Too little'}))
 def test_behavioral_response_cannot_smuggle_plan(self):
  from commercelens_ai.response_contract import decode_response
  with self.assertRaises(ValueError):decode_response(json.dumps(dict(behavior='uncertain',factual_claims=True,answer='Investigate [S1]',plan=PLAN)))
 def test_editor_preserves_citations_and_updates_answer(self):
  model=Mock(complete=Mock(side_effect=[envelope('Technical draft [S1].'),envelope('Order Service owns this behavior [S1].')]))
  r=Assistant(Retriever(),model,GRAPH).run('What does order do?')
  self.assertEqual(r['status'],'ok');self.assertIn('owns this behavior',r['answer'])
  self.assertTrue(any(t.get('purpose')=='quality_review' for t in r['trace']))
 def test_invalid_editor_does_not_destroy_valid_draft(self):
  model=Mock(complete=Mock(side_effect=[envelope(),'{bad']))
  r=Assistant(Retriever(),model,GRAPH).run('What does order do?')
  self.assertEqual(r['status'],'ok');self.assertIn('Draft',r['answer'])
  self.assertTrue(any(t['step']=='quality_review_rejected' for t in r['trace']))
 def test_editor_respects_existing_model_budget(self):
  model=Mock(complete=Mock(return_value=envelope()))
  r=Assistant(Retriever(),model,GRAPH,max_model_calls=1).run('What does order do?')
  self.assertEqual(r['status'],'ok');self.assertEqual(model.complete.call_count,1)
 def test_unknown_response_needs_no_editor(self):
  model=Mock(complete=Mock(return_value=json.dumps(dict(behavior='unknown',factual_claims=False,answer='I do not have this information.'))))
  r=Assistant(Retriever(),model,GRAPH).run('What is the live order status?')
  self.assertEqual(r['status'],'ok');self.assertEqual(model.complete.call_count,1)

 def test_router_adds_services_without_discarding_named_service(self):
  model=Mock(complete=Mock(side_effect=[json.dumps({'service_ids':['payment'],'intent':'retrieve','response':''}),'Current behavior [S1].']))
  r=Assistant(Retriever(),model,GRAPH).run('Change order processing','plan')
  self.assertEqual(set(r['selected_services']),{'order','payment'})
  self.assertTrue(any(t.get('purpose')=='route' for t in r['trace']))

 def test_provider_sends_requested_response_schema(self):
  from commercelens_ai.providers import OpenAICompatibleModel
  from test_ai_providers import Response
  from unittest.mock import patch
  schema={'type':'object','properties':{'answer':{'type':'string'}},'required':['answer'],'additionalProperties':False}
  with patch('urllib.request.OpenerDirector.open',return_value=Response({'choices':[{'message':{'content':'{"answer":"ok"}'},'finish_reason':'stop'}]})) as op:
   OpenAICompatibleModel('key','https://example.test','model').complete_structured([],schema)
  self.assertEqual(json.loads(op.call_args.args[0].data)['response_format']['json_schema']['schema'],schema)

 def test_semantic_selection_does_not_pull_unrelated_neighbors(self):
  graph={'nodes':GRAPH['nodes']+[{'id':'unrelated','name':'Unrelated','type':'service'}],
         'edges':GRAPH['edges']+[{'from':'order','to':'unrelated','type':'calls'}]}
  model=Mock(complete=Mock(side_effect=[json.dumps({'service_ids':['order','payment'],'service_queries':{'payment':'payment existing contract'},'intent':'retrieve','response':''}),'Current behavior [S1].']))
  retriever=Mock(wraps=Retriever())
  r=Assistant(retriever,model,graph).run('Change order processing','plan')
  self.assertNotIn('unrelated',r['selected_services'])
  self.assertTrue(any(c.args[0]=='payment existing contract' for c in retriever.search.call_args_list))

 def test_editor_invented_citation_preserves_valid_draft(self):
  model=Mock(complete=Mock(side_effect=[envelope('Valid draft [S1].'),envelope('Revised [S999].')]))
  r=Assistant(Retriever(),model,GRAPH).run('What does order do?')
  self.assertEqual(r['status'],'ok');self.assertIn('Valid draft',r['answer'])
