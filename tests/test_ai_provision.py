import io
import json
import unittest
import urllib.error
from unittest.mock import patch

from commercelens_ai.provision import ensure_index


class Reply(io.BytesIO):
    def __init__(self,value): super().__init__(json.dumps(value).encode())


class ProvisionTests(unittest.TestCase):
    def existing(self,**overrides):
        return dict({'name':'demo','dimension':4096,'metric':'cosine','vector_type':'dense','host':'demo.svc.pinecone.io','status':{'ready':True}},**overrides)

    @patch('commercelens_ai.provision.urllib.request.build_opener')
    def test_existing_index_is_validated_without_mutation(self,build):
        build.return_value.open.return_value=Reply(self.existing())
        result=ensure_index('secret','demo',4096)
        self.assertFalse(result['created'])
        self.assertEqual(result['host'],'demo.svc.pinecone.io')
        self.assertEqual(build.return_value.open.call_count,1)
        request=build.return_value.open.call_args.args[0]
        self.assertEqual(request.get_method(),'GET')

    @patch('commercelens_ai.provision.urllib.request.build_opener')
    def test_404_creates_serverless_with_deletion_protection(self,build):
        missing=urllib.error.HTTPError('url',404,'missing',{},None)
        build.return_value.open.side_effect=[missing,Reply(self.existing(status={'ready':False}))]
        result=ensure_index('secret','demo',4096)
        self.assertTrue(result['created'])
        request=build.return_value.open.call_args.args[0]
        body=json.loads(request.data)
        self.assertEqual(body['dimension'],4096)
        self.assertEqual(body['deletion_protection'],'enabled')
        self.assertEqual(body['spec'],{'serverless':{'cloud':'aws','region':'us-east-1'}})
        self.assertEqual(request.get_method(),'POST')

    @patch('commercelens_ai.provision.urllib.request.build_opener')
    def test_mismatch_never_recreates(self,build):
        for changes in [{'dimension':1536},{'metric':'dotproduct'},{'vector_type':'sparse'}]:
            build.return_value.open.reset_mock()
            build.return_value.open.return_value=Reply(self.existing(**changes))
            with self.assertRaisesRegex(ValueError,'mismatch'): ensure_index('secret','demo',4096)
            self.assertEqual(build.return_value.open.call_count,1)

    @patch('commercelens_ai.provision.urllib.request.build_opener')
    def test_http_failures_are_sanitized_and_status_preserved(self,build):
        for status in [401,403,429,500,302]:
            build.return_value.open.side_effect=urllib.error.HTTPError('url',status,'secret leaked',{},io.BytesIO(b'secret leaked'))
            with self.assertRaises(RuntimeError) as caught: ensure_index('secret','demo',4096)
            self.assertIn(str(status),str(caught.exception))
            self.assertNotIn('secret',str(caught.exception))

    def test_invalid_parameters_do_not_make_requests(self):
        for name,dim in [('BAD',4096),('../bad',4096),('demo',0),('demo',True)]:
            with self.assertRaises(ValueError): ensure_index('secret',name,dim)


if __name__=='__main__': unittest.main()
