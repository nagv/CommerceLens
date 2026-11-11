import json
import tempfile
import unittest
import urllib.error
from unittest.mock import patch
from pathlib import Path

from commercelens_ai.knowledge import build_corpus, build_relationships, get_dependencies
from commercelens_ai.retrieval import LocalRetriever, PineconeRetriever, PineconeHTTPIndex


class KnowledgeTests(unittest.TestCase):
    def test_monorepo_source_and_relationship_links_include_service_path(self):
        import yaml
        path=self.root/'services.example.yaml'
        manifest=yaml.safe_load(path.read_text())
        for service in manifest['services']:
            service['repository']='https://github.com/example/app.git'
            service['repository_path']='services/'+service['id']
        path.write_text(yaml.safe_dump(manifest))
        chunks=build_corpus(self.root)
        order=next(c for c in chunks if c['metadata']['service_id']=='orders')
        self.assertEqual(order['metadata']['source_url'],'https://github.com/example/app/blob/main/services/orders/openwiki/details.md')
        self.assertEqual(order['metadata']['source_path'],'services/orders/openwiki/details.md')
        graph=build_relationships(self.root)
        edge=next(e for e in graph['edges'] if e['from']=='orders')
        self.assertEqual(edge['evidence_url'],'https://github.com/example/app/blob/main/services/orders/openwiki/details.md')

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'services.example.yaml').write_text('application: {id: demo}\nservices:\n- {id: orders, path: orders, aliases: [Orders API]}\n- {id: mail, path: mail}\n')
        (self.root/'openwiki').mkdir()
        (self.root/'openwiki/overview.md').write_text('# Overview\nApplication overview.')
        for sid in ['orders', 'mail']:
            (self.root / sid / 'openwiki').mkdir(parents=True)
            (self.root / sid / 'openwiki/details.md').write_text('---\nsecret: hidden\n---\n# Overview\n## Delivery\nUses order.confirmed delivery.\n## Retry\nRetries safely.\n')
            (self.root / sid / 'openwiki/INSTRUCTIONS.md').write_text('Never index this')
        (self.root / 'catalog/service-cards').mkdir(parents=True)
        for sid, deps in [('orders', [{'target':'RabbitMQ','kind':'publishes','interface':'order.confirmed queue, order.confirmed.dead DLQ','evidence':'openwiki/details.md'}]), ('mail', [{'target':'rabbitmq','kind':'consumes','interface':'Queue order.confirmed (DLX to order.confirmed.dead)','evidence':'openwiki/details.md'}, {'target':'Orders API','kind':'http','interface':'GET orders','evidence':'openwiki/details.md'}, {'target':'Mystery Provider','kind':'external','interface':'email','evidence':'openwiki/details.md'}])]:
            (self.root / f'catalog/service-cards/{sid}.json').write_text(json.dumps({'id':sid,'summary':{'dependencies':deps}}))

    def test_docs_are_bounded_versioned_and_not_instructions(self):
        chunks = build_corpus(self.root)
        self.assertTrue(chunks)
        self.assertFalse(any('hidden' in c['text'] or 'Never index' in c['text'] for c in chunks))
        self.assertEqual(chunks, build_corpus(self.root))
        self.assertTrue(all(c['metadata']['source_version'] for c in chunks))
        p = self.root / 'orders/openwiki/details.md'
        old = {c['id'] for c in chunks if c['metadata']['service_id']=='orders'}
        p.write_text('# Changed\nNew body')
        self.assertTrue(old.isdisjoint({c['id'] for c in build_corpus(self.root)}))
        (p.parent/'remaining.md').write_text('# Remaining\nOther documentation.')
        deleted_ids={c['id'] for c in build_corpus(self.root) if c['metadata']['service_id']=='orders' and c['metadata']['source_path'].endswith('details.md')}
        p.unlink()
        self.assertTrue(deleted_ids.isdisjoint({c['id'] for c in build_corpus(self.root)}))

    def test_queue_direction_aliases_unknowns_and_hop_bound(self):
        graph = build_relationships(self.root)
        self.assertTrue(any(e['from']=='mail' and e['to']=='orders' for e in graph['edges']))
        self.assertTrue(any(n['id']=='Mystery Provider' for n in graph['nodes']))
        self.assertTrue(graph['warnings'])
        self.assertIn('mail', get_dependencies(graph,'orders','outbound',1)['services'])
        self.assertEqual([],get_dependencies(graph,'orders',max_hops=0)['services'])
        self.assertFalse(any(e['type']=='consumes' and e['from']=='queue:order.confirmed.dead' for e in graph['edges']))

    def test_lexical_filters(self):
        results = LocalRetriever(build_corpus(self.root)).search('order.confirmed',service_ids=['mail'],level='service')
        self.assertTrue(results)
        self.assertTrue(all(c['metadata']['service_id']=='mail' for c in results))

    def test_simple_queue_names_and_inbound_direction(self):
        for sid in ['orders','mail']:
            path=self.root / f'catalog/service-cards/{sid}.json'
            card=json.loads(path.read_text())
            card['summary']['dependencies']=card['summary']['dependencies'][:1]
            card['summary']['dependencies'][0]['interface']='Queue checkout-events (durable)'
            path.write_text(json.dumps(card))
        graph=build_relationships(self.root)
        self.assertIn('queue:checkout-events',[n['id'] for n in graph['nodes']])
        self.assertEqual(['orders'],get_dependencies(graph,'mail','inbound')['services'])
        self.assertEqual([],get_dependencies(graph,'mail','outbound')['services'])

    def test_large_section_has_bounded_chunks(self):
        (self.root/'orders/openwiki/details.md').write_text('# Context\n## Large\n'+('words '*3000))
        chunks=build_corpus(self.root)
        self.assertTrue(all(len(c['text'])<=5000 for c in chunks))
        self.assertTrue(all(c['text'].startswith('Context > Large') for c in chunks if c['metadata']['service_id']=='orders'))

    def test_http_consumption_points_from_client_to_service(self):
        path=self.root/'catalog/service-cards/mail.json'
        path.write_text(json.dumps({'summary':{'dependencies':[{'target':'orders','kind':'consumes','interface':'HTTP /api/orders','evidence':'openwiki/details.md'}]}}))
        graph=build_relationships(self.root)
        self.assertTrue(any(e['from']=='mail' and e['to']=='orders' and e['type']=='http' for e in graph['edges']))

    def test_master_citations_are_shareable_and_paths_relative(self):
        manifest=self.root/'services.example.yaml'
        manifest.write_text(manifest.read_text().replace('id: demo','id: demo, repository: https://github.com/example/demo.git'))
        (self.root/'openwiki/overview.md').write_text('# Overview\nMaster documentation')
        chunks=build_corpus(self.root)
        master=next(c for c in chunks if c['metadata']['level']=='master')
        self.assertEqual(master['metadata']['source_url'],'https://github.com/example/demo/blob/main/openwiki/overview.md')
        self.assertTrue(all(not Path(c['metadata']['source_path']).is_absolute() for c in chunks))

    def test_missing_or_empty_wiki_rejects_incomplete_corpus(self):
        path=self.root/'mail/openwiki/details.md'
        path.unlink()
        with self.assertRaisesRegex(ValueError,'mail.*substantive'): build_corpus(self.root)
        (self.root/'mail/openwiki/INSTRUCTIONS.md').unlink()
        (self.root/'mail/openwiki').rmdir()
        with self.assertRaisesRegex(ValueError,'mail.*missing'): build_corpus(self.root)

    def test_graph_evidence_has_repository_link_and_recorded_version(self):
        path=self.root/'catalog/service-cards/orders.json'
        card=json.loads(path.read_text())
        card.update(repository='https://github.com/example/orders.git',page_hashes={'openwiki/details.md':'recorded-version'})
        path.write_text(json.dumps(card))
        edge=next(e for e in build_relationships(self.root)['edges'] if e['from']=='orders')
        self.assertEqual(edge['evidence_url'],'https://github.com/example/orders/blob/main/openwiki/details.md')
        self.assertEqual(edge['evidence_version'],'recorded-version')


class FakeIndex:
    def __init__(self): self.records={}; self.fail=False; self.last_query=None
    def upsert(self, vectors, namespace):
        if self.fail: raise RuntimeError('network')
        self.records.update({v['id']:v for v in vectors})
        return {'upserted_count':len(vectors)}
    def delete(self, ids, namespace):
        for key in ids: self.records.pop(key,None)
    def query(self, **kwargs):
        self.last_query=kwargs
        return {'matches':[dict(v,score=0.9) for v in self.records.values()]}


class PineconeTests(unittest.TestCase):
    def test_http_index_rejects_unsafe_hosts(self):
        for host in ['http://index.example','https://user:pass@index.example','https://index.example/path',
                     'https://index.example?key=secret','https://index.example#part','https://','https://index.example:444']:
            with self.assertRaises(ValueError): PineconeHTTPIndex(host,'secret')

    def test_sync_rejects_unsupported_metadata_before_writes(self):
        with tempfile.TemporaryDirectory() as folder:
            index=FakeIndex()
            r=PineconeRetriever(index,lambda texts:[[1.] for t in texts],namespace='test',index_name='test',embedding_model='embed')
            for value in [None,{'nested':'value'},[1,2]]:
                with self.assertRaisesRegex(ValueError,'metadata'):
                    r.sync([{'id':'one','text':'doc','metadata':{'invalid':value}}],Path(folder)/'manifest.json')
            self.assertEqual(index.records,{})

    @patch('commercelens_ai.retrieval.urllib.request.build_opener')
    def test_http_index_refuses_redirects_and_sanitizes_errors(self,build):
        index=PineconeHTTPIndex('https://index.example','secret')
        handler=build.call_args.args[0]
        self.assertIsNone(handler.redirect_request(None,None,302,'redirect',{},'https://other.example'))
        for status in [302,401,429,500]:
            build.return_value.open.side_effect=urllib.error.HTTPError('url',status,'secret provider payload',{},None)
            with self.assertRaises(RuntimeError) as caught: index.query(vector=[1.],namespace='test')
            self.assertIn(str(status),str(caught.exception))
            self.assertNotIn('secret',str(caught.exception))

    def test_upserts_split_by_serialized_payload_size(self):
        with tempfile.TemporaryDirectory() as folder:
            index=FakeIndex(); original=index.upsert; sizes=[]
            def bounded(**kwargs):
                sizes.append(len(json.dumps(kwargs).encode('utf-8')))
                return original(**kwargs)
            index.upsert=bounded
            r=PineconeRetriever(index,lambda texts:[[0.12345678901234567]*4096 for t in texts],namespace='test',index_name='test',embedding_model='embed')
            chunks=[{'id':str(i),'text':'doc','metadata':{}} for i in range(64)]
            r.sync(chunks,Path(folder)/'manifest.json',batch_size=64)
            self.assertGreater(len(sizes),1)
            self.assertTrue(all(size<=1_900_000 for size in sizes))

    def test_failed_partial_sync_is_cleaned_on_different_retry(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'manifest.json'; index=FakeIndex()
            r=PineconeRetriever(index,lambda texts:[[1.] for t in texts],namespace='test',index_name='test',embedding_model='embed')
            chunk={'id':'one','text':'payment','metadata':{}}
            r.sync([chunk],path)
            original=index.upsert
            def partial(vectors,namespace):
                original(vectors,namespace)
                raise RuntimeError('response lost after write')
            index.upsert=partial
            with self.assertRaises(RuntimeError): r.sync([dict(chunk,id='two')],path)
            index.upsert=original
            r.sync([dict(chunk,id='three')],path)
            self.assertEqual(set(index.records),{'three'})

    def test_incremental_deletes_and_partial_failure_preserves_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'manifest.json'; index=FakeIndex(); calls=[]
            def embed(texts): calls.extend(texts); return [[1.,0.] for t in texts]
            r=PineconeRetriever(index,embed,namespace='test',index_name='test',embedding_model='embed')
            chunk={'id':'one','text':'payment','metadata':{'service_id':'payment','level':'service','content_hash':'a'}}
            r.sync([chunk],path)
            r.sync([chunk],path)
            self.assertEqual(calls,['payment'])
            before=path.read_text(); index.fail=True
            with self.assertRaises(RuntimeError): r.sync([dict(chunk,id='two')],path)
            self.assertEqual(path.read_text(),before)
            self.assertIn('one',index.records)
            index.fail=False; r.sync([dict(chunk,id='two')],path)
            self.assertEqual(set(index.records),{'two'})
            self.assertEqual(r.search('payment',service_ids=['payment'],level='service')[0]['text'],'payment')
            self.assertEqual(index.last_query['namespace'],'test')
            self.assertIn('$and',index.last_query['filter'])
            other=PineconeRetriever(index,embed,namespace='other',index_name='test',embedding_model='embed')
            with self.assertRaises(ValueError): other.sync([chunk],path)


if __name__ == '__main__': unittest.main()
