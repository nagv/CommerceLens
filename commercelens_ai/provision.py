"""Explicit Pinecone index provisioning; never deletes or recreates indexes."""
import json
import re
import urllib.error
import urllib.request


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        return None


def _http_error(status):
    reason={401:'authentication failed; check PINECONE_API_KEY',
            403:'access denied; check project permissions',
            404:'index not found',
            409:'index name conflict; retry to inspect the existing index',
            429:'quota or rate limit reached; check Pinecone limits'}
    detail=reason.get(status,'redirect refused' if 300<=status<400 else 'control-plane request failed')
    return RuntimeError(f'Pinecone HTTP {status}: {detail}')


def ensure_index(api_key,name,dimension,cloud='aws',region='us-east-1') -> dict:
    """Inspect an index, or create it once on HTTP 404. No readiness polling.

    Returns the control-plane index description plus ``created``. Existing
    dimension, cosine metric and dense vector type must match exactly.
    """
    if not isinstance(name,str) or not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,43}[a-z0-9])?',name):
        raise ValueError('Index name must be 1..45 lowercase letters, digits or internal hyphens')
    if type(dimension) is not int or dimension<=0: raise ValueError('dimension must be a positive integer')
    if not isinstance(api_key,str) or not api_key.strip(): raise ValueError('PINECONE_API_KEY is required')
    if cloud not in {'aws','gcp','azure'}: raise ValueError('Unsupported Pinecone cloud')
    if not isinstance(region,str) or not re.fullmatch(r'[a-z0-9-]+',region): raise ValueError('Invalid region')
    opener=urllib.request.build_opener(_NoRedirect())
    headers={'Api-Key':api_key,'Content-Type':'application/json','X-Pinecone-Api-Version':'2025-10'}

    def request(path,body=None):
        req=urllib.request.Request('https://api.pinecone.io/indexes'+path,
                                   data=json.dumps(body).encode() if body is not None else None,
                                   headers=headers)
        try:
            with opener.open(req,timeout=60) as response:
                value=json.load(response)
        except urllib.error.HTTPError:
            raise
        except (urllib.error.URLError,TimeoutError,OSError):
            raise RuntimeError('Pinecone control-plane connection failed; check network connectivity') from None
        except (ValueError,UnicodeError):
            raise RuntimeError('Pinecone returned an invalid index description') from None
        if not isinstance(value,dict): raise RuntimeError('Pinecone returned an invalid index description')
        return value

    created=False
    try:
        try:
            value=request('/'+name)
        except urllib.error.HTTPError as error:
            if error.code!=404: raise
            value=request('',{'name':name,'dimension':dimension,'metric':'cosine','vector_type':'dense',
                              'spec':{'serverless':{'cloud':cloud,'region':region}},
                              'deletion_protection':'enabled','tags':{'application':'commercelens'}})
            created=True
    except urllib.error.HTTPError as error:
        raise _http_error(error.code) from None
    for key,expected in [('dimension',dimension),('metric','cosine'),('vector_type','dense')]:
        if value.get(key)!=expected: raise ValueError(f'Existing Pinecone index {key} mismatch; choose a compatible index name')
    return dict(value,created=created)
