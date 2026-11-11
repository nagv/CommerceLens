import unittest
import http.client
import json
import threading

from commercelens_ai.engine import Assistant


class Retriever:
    def search(self, query, service_ids=None, level=None, limit=6):
        ids = service_ids or ['order', 'payment']
        return [{'id': f'{s}-{level}', 'text': f'{s} documented behavior',
                 'metadata': {'service_id': s, 'level': level,
                              'source_url': 'https://example.test/' + s}} for s in ids][:limit]


class Model:
    def __init__(self, answer):
        self.answer = answer
        self.messages = []

    def complete(self, messages):
        self.messages.append(messages)
        return self.answer


GRAPH = {'nodes': [{'id': 'order', 'name': 'Order', 'type': 'service'}, {'id': 'payment', 'name': 'Payment', 'type': 'service'}],
         'edges': [{'from': 'order', 'to': 'payment', 'type': 'calls'}]}


class AssistantTests(unittest.TestCase):
    def test_ask_returns_only_cited_evidence(self):
        result = Assistant(Retriever(), Model('Orders work [order-master].'), GRAPH).run('What is order?')
        self.assertEqual(result['status'], 'ok')
        self.assertEqual([c['id'] for c in result['citations']], ['order-master'])
        self.assertEqual(result['tool_calls'], 1)

    def test_rejects_invented_citations(self):
        result = Assistant(Retriever(), Model('Claim [nonexistent].'), GRAPH).run('What is order?')
        self.assertEqual(result['status'], 'invalid_citations')
        self.assertEqual(result['citations'], [])
        self.assertNotIn('Claim', result['answer'])

    def test_missing_citation_is_not_grounded_success(self):
        result = Assistant(Retriever(), Model('A confident undocumented claim'), GRAPH).run('What is order?')
        self.assertEqual(result['status'], 'invalid_citations')

    def test_global_question_includes_each_service_summary(self):
        result = Assistant(Retriever(), Model('Both [order-master] [payment-master]'), GRAPH).run('Explain the entire application')
        self.assertEqual(set(result['selected_services']), {'order', 'payment'})
        self.assertTrue(any('payment documented' in s for s in result['retrieved_contexts']))

    def test_plan_expands_impacts_and_requests_high_level_sections(self):
        model = Model('Current documented behavior [order-master]. Proposed changes. Unknowns.')
        result = Assistant(Retriever(), model, GRAPH).run('Change order behavior', 'plan')
        self.assertIn('payment', result['selected_services'])
        self.assertTrue(any('payment documented' in s for s in result['retrieved_contexts']))
        prompt = model.messages[-1][0]['content']
        self.assertIn('ordered implementation stages', prompt)
        self.assertIn('risks and validation', prompt)
        self.assertIn('untrusted', prompt)
        self.assertIn('filenames', prompt)

    def test_budget_stops_retrieval_and_returns_explicit_status(self):
        result = Assistant(Retriever(), Model('Claim [order-master]'), GRAPH, max_tool_calls=1).run('Change order behavior', 'plan')
        self.assertLessEqual(result['tool_calls'], 1)
        self.assertEqual(result['status'], 'budget_exceeded')

    def test_invalid_input_never_reaches_model(self):
        model = Model('unused')
        with self.assertRaises(ValueError):
            Assistant(Retriever(), model, GRAPH).run('hello', 'execute')
        self.assertEqual(model.messages, [])

    def test_long_master_chunks_do_not_crowd_out_service_evidence(self):
        class LongRetriever(Retriever):
            def search(self, query, service_ids=None, level=None, limit=6):
                rows = super().search(query, service_ids, level, limit)
                for row in rows:
                    row['text'] = row['metadata']['service_id'] + ' detail ' * 2000
                return rows
        result = Assistant(LongRetriever(), Model('Evidence [order-master]'), GRAPH,
                           max_context_chars=3000).run('Change order flow', 'plan')
        self.assertTrue(any(s.startswith('[payment-service]') for s in result['retrieved_contexts']))

    def test_global_plan_does_not_exhaust_default_budget(self):
        graph = {'nodes': [{'id': f'service{i}', 'type': 'service'} for i in range(6)], 'edges': []}
        result = Assistant(Retriever(), Model('Evidence [order-master]'), graph).run('Change the entire application', 'plan')
        self.assertEqual(result['status'], 'ok')

    def test_retrieved_ids_and_usage_are_reported(self):
        model = Model('Orders [order-master]')
        model.usage = {'prompt_tokens': 10, 'completion_tokens': 5, 'total_tokens': 15}
        result = Assistant(Retriever(), model, GRAPH).run('What is order?')
        self.assertEqual(result['retrieved_ids'], ['order-master', 'payment-master'])
        self.assertEqual(result['token_usage']['total_tokens'], 15)

    def test_obvious_help_needs_no_retrieval_or_citations(self):
        result = Assistant(Retriever(), Model('unused'), GRAPH).run('/help')
        self.assertEqual(result['answer_type'], 'help')
        self.assertEqual(result['tool_calls'], 0)
        self.assertEqual(result['model_calls'], 0)
        self.assertEqual(result['status'], 'ok')

    def test_failure_reports_type_and_stage_without_secret(self):
        class FailedModel:
            def complete(self, messages):
                raise RuntimeError('secret-key')
        result = Assistant(Retriever(), FailedModel(), GRAPH).run('What is order?')
        failure = result['trace'][-1]
        self.assertEqual(failure['error_type'], 'RuntimeError')
        self.assertEqual(failure['stage'], 'model:answer')
        self.assertNotIn('secret-key', str(result))

    def test_service_limit_is_visible_in_answer(self):
        result = Assistant(Retriever(), Model('Orders [order-master]'), GRAPH,
                           max_services=1).run('Explain the entire application')
        self.assertIn('Coverage limited', result['answer'])
        self.assertIn('payment', result['answer'])

    def test_global_plan_above_service_cap_keeps_partial_answer_with_warning(self):
        graph = {'nodes': [{'id': f'service{i}', 'type': 'service'} for i in range(7)], 'edges': []}
        result = Assistant(Retriever(), Model('Evidence [order-master]'), graph).run('Change entire application', 'plan')
        self.assertEqual(result['status'], 'ok')
        self.assertIn('Coverage limited', result['answer'])
        self.assertEqual(result['tool_calls'], 7)

    def test_routes_endpoints_and_status_questions_retrieve_details(self):
        for question in ('List order API routes', 'Which payment statuses exist?', 'List order endpoints'):
            with self.subTest(question=question):
                result = Assistant(Retriever(), Model('Evidence [order-master]'), GRAPH).run(question)
                self.assertTrue(any(step.get('level') == 'service' for step in result['trace']))

    def test_short_model_citations_normalize_to_canonical_ids(self):
        model = Model('Orders [S1], payments [S2].')
        result = Assistant(Retriever(), model, GRAPH).run('What is order?')
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['answer'], 'Orders [order-master], payments [payment-master].')
        evidence = json.loads(model.messages[-1][1]['content'])['evidence']
        self.assertEqual([item['id'] for item in evidence], ['S1', 'S2'])
        self.assertEqual([item['id'] for item in result['citations']], ['order-master', 'payment-master'])

    def test_unknown_alias_or_abbreviation_still_fails(self):
        for answer in ('Claim [S999]', 'Claim [order-m...]'):
            result = Assistant(Retriever(), Model(answer), GRAPH).run('What is order?')
            self.assertEqual(result['status'], 'invalid_citations')

    def test_timeout_agreement_question_expands_to_connected_service(self):
        result = Assistant(Retriever(), Model('Evidence [S1]'), GRAPH).run('What state follows a payment timeout, and do docs agree?')
        self.assertEqual(set(result['selected_services']), {'order', 'payment'})
        self.assertIn('order-service', result['retrieved_ids'])


class ServerTests(unittest.TestCase):
    def test_replan_endpoint_and_invalid_context(self):
        payload=dict(original_request='Change order workflow',previous_plan='Use a Portal action.',selected_alternative='Operational command',instruction='No Portal changes')
        self.client.request('POST','/api/replan',json.dumps(payload),{'Content-Type':'application/json'})
        response=self.client.getresponse()
        self.assertEqual(response.status,200)
        result=json.loads(response.read())
        self.assertEqual(result['request_type'],'replan')
        self.assertEqual(result['original_request'],payload['original_request'])
        self.client.request('POST','/api/replan',json.dumps(dict(payload,previous_plan='')))
        response=self.client.getresponse()
        self.assertEqual(response.status,400)
        response.read()

    def setUp(self):
        from commercelens_ai.server import create_server
        self.server = create_server(Assistant(Retriever(), Model('Orders [order-master]'), GRAPH), port=0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.client = http.client.HTTPConnection('127.0.0.1', self.server.server_port)

    def tearDown(self):
        self.client.close()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def test_chat_and_ui_are_served(self):
        self.client.request('POST', '/api/chat', json.dumps({'question': 'What is order?', 'mode': 'ask'}), {'Content-Type': 'application/json'})
        response = self.client.getresponse()
        self.assertEqual(response.status, 200)
        self.assertEqual(json.loads(response.read())['status'], 'ok')
        self.client.request('GET', '/')
        response = self.client.getresponse()
        self.assertEqual(response.status, 200)
        self.assertIn(b'<form', response.read())

    def test_foreign_origin_is_rejected(self):
        self.client.request('POST', '/api/chat', '{}', {'Origin': 'https://attacker.example'})
        response = self.client.getresponse()
        self.assertEqual(response.status, 403)
        response.read()

    def test_invalid_request_is_safe(self):
        self.client.request('POST', '/api/chat', '{malformed')
        response = self.client.getresponse()
        self.assertEqual(response.status, 400)
        self.assertNotIn(b'Traceback', response.read())


if __name__ == '__main__':
    unittest.main()
