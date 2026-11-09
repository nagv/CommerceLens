"""Lexical retrieval and explicit, incremental Pinecone vector retrieval.

PineconeRetriever(index, embed, namespace=..., index_name=..., embedding_model=...)
accepts an SDK-compatible index and embed(list[str]) -> list[list[float]].
No provider errors are converted into local search results.
"""
import hashlib
import json
import math
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path


def _tokens(text):
    return re.findall(r'[a-z0-9]+(?:[._/-][a-z0-9]+)*',text.lower())


class LocalRetriever:
    def __init__(self,chunks):
        self.chunks=list(chunks)
        self.terms=[Counter(_tokens(c['text']+' '+c['metadata'].get('service_id',''))) for c in self.chunks]
        self.df=Counter(t for terms in self.terms for t in terms)

    def search(self,query,service_ids=None,level=None,limit=6):
        if limit<=0 or service_ids==[]: return []
        terms=set(_tokens(query)); results=[]
        for chunk,counts in zip(self.chunks,self.terms):
            meta=chunk['metadata']
            if service_ids is not None and meta.get('service_id') not in service_ids: continue
            if level and meta.get('level')!=level: continue
            score=sum((1+math.log(counts[t]))*math.log(1+len(self.chunks)/(1+self.df[t])) for t in terms if counts[t])
            if score: results.append(dict(chunk,score=score))
        return sorted(results,key=lambda c:(-c['score'],c['id']))[:limit]


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        return None


class PineconeHTTPIndex:
    """Minimal vector data-plane adapter (host must be a trusted HTTPS URL)."""
    def __init__(self,host,api_key):
        if not isinstance(host,str) or any(c.isspace() for c in host): raise ValueError('Invalid Pinecone host')
        parsed=urllib.parse.urlsplit(host)
        if (parsed.scheme!='https' or not parsed.hostname or parsed.username is not None
                or parsed.password is not None or parsed.path not in {'','/'} or parsed.query
                or parsed.fragment or parsed.port not in {None,443}):
            raise ValueError('Pinecone host must be an HTTPS origin without credentials, path, query or fragment')
        self.host=host.rstrip('/')
        if not api_key: raise ValueError('Pinecone API key required')
        self.api_key=api_key
        self.opener=urllib.request.build_opener(_NoRedirect())

    def _post(self,path,body):
        request=urllib.request.Request(self.host+path,data=json.dumps(body).encode(),headers={'Api-Key':self.api_key,'Content-Type':'application/json','X-Pinecone-Api-Version':'2025-10'})
        try:
            with self.opener.open(request,timeout=60) as response: return json.load(response)
        except urllib.error.HTTPError as error:
            detail={401:'authentication failed',403:'access denied',429:'quota or rate limit reached'}.get(error.code,'redirect refused' if 300<=error.code<400 else 'data-plane request failed')
            raise RuntimeError(f'Pinecone HTTP {error.code}: {detail}') from None
        except (urllib.error.URLError,TimeoutError,OSError):
            raise RuntimeError('Pinecone data-plane connection failed') from None
        except (ValueError,UnicodeError):
            raise RuntimeError('Pinecone returned invalid JSON') from None

    def upsert(self,**kwargs): return self._post('/vectors/upsert',kwargs)
    def delete(self,**kwargs): return self._post('/vectors/delete',kwargs)
    def query(self,**kwargs):
        for a,b in [('top_k','topK'),('include_metadata','includeMetadata')]:
            if a in kwargs: kwargs[b]=kwargs.pop(a)
        return self._post('/query',kwargs)


def _dict(value):
    return value if isinstance(value,dict) else value.to_dict()


class PineconeRetriever:
    def __init__(self,index,embed,*,namespace,index_name,embedding_model):
        if not all([namespace,index_name,embedding_model]): raise ValueError('Explicit namespace, index and embedding model required')
        self.index=index; self.embed=embed; self.namespace=namespace
        self.config={'namespace':namespace,'index':index_name,'embedding_model':embedding_model,
                     'host':getattr(index,'host',None)}

    def _embed(self,texts):
        vectors=list(self.embed(texts))
        if len(vectors)!=len(texts) or any(not v or any(not math.isfinite(x) for x in v) for v in vectors):
            raise ValueError('Invalid embedding response')
        if len({len(v) for v in vectors})>1: raise ValueError('Inconsistent embedding dimensions')
        return vectors

    def search(self,query,service_ids=None,level=None,limit=6):
        if limit<=0 or service_ids==[]: return []
        filters=[]
        if service_ids is not None: filters.append({'service_id':{'$in':list(service_ids)}})
        if level: filters.append({'level':{'$eq':level}})
        kwargs={'namespace':self.namespace,'vector':self._embed([query])[0],'top_k':limit,'include_metadata':True}
        if filters: kwargs['filter']={'$and':filters} if len(filters)>1 else filters[0]
        response=_dict(self.index.query(**kwargs)); results=[]
        for item in response.get('matches',[]):
            item=_dict(item); metadata=dict(item.get('metadata',{})); text=metadata.pop('text','')
            results.append({'id':item['id'],'text':text,'metadata':metadata,'score':item['score']})
        return results

    def sync(self,chunks,manifest_path,batch_size=16):
        if not 1<=batch_size<=100: raise ValueError('batch_size must be 1..100')
        path=Path(manifest_path); chunks=list(chunks)
        for chunk in chunks:
            for key,value in chunk['metadata'].items():
                valid=isinstance(value,(str,bool)) or (type(value) in {int,float} and math.isfinite(value)) or (isinstance(value,list) and all(isinstance(v,str) for v in value))
                if not isinstance(key,str) or key.startswith('$') or not valid:
                    raise ValueError('Pinecone metadata must contain named strings, finite numbers, booleans or string lists')
        old=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'config':self.config,'chunks':{}}
        if old['config']!=self.config: raise ValueError('Index/namespace/embedding configuration differs from manifest')
        current={c['id']:hashlib.sha256(json.dumps(c,sort_keys=True).encode()).hexdigest() for c in chunks}
        if len(current)!=len(chunks): raise ValueError('Duplicate chunk IDs')
        # A separate write-ahead journal remembers possible remote writes even
        # when their response was lost. The committed manifest stays untouched.
        journal=path.with_suffix(path.suffix+'.pending')
        pending=json.loads(journal.read_text(encoding='utf-8')) if journal.exists() else {'config':self.config,'ids':[]}
        if pending['config']!=self.config: raise ValueError('Pending sync configuration differs')
        possible=set(pending['ids']) | set(old['chunks']) | set(current)
        path.parent.mkdir(parents=True,exist_ok=True)
        journal_tmp=journal.with_suffix(journal.suffix+'.tmp')
        journal_tmp.write_text(json.dumps({'config':self.config,'ids':sorted(possible)}),encoding='utf-8')
        journal_tmp.replace(journal)
        changed=[c for c in chunks if old['chunks'].get(c['id'])!=current[c['id']] or c['id'] in pending['ids']]
        for start in range(0,len(changed),batch_size):
            batch=changed[start:start+batch_size]; vectors=self._embed([c['text'] for c in batch])
            records=[{'id':c['id'],'values':v,'metadata':dict(c['metadata'],text=c['text'])} for c,v in zip(batch,vectors)]
            # The vector API caps requests at 2 MB. Measure the exact JSON form
            # used by our HTTP adapter, reserving 100 KB for SDK differences.
            groups=[]; group=[]
            for record in records:
                candidate=group+[record]
                size=len(json.dumps({'vectors':candidate,'namespace':self.namespace}).encode('utf-8'))
                if size>1_900_000:
                    if not group: raise ValueError('Single vector exceeds Pinecone request size limit')
                    groups.append(group); group=[record]
                    if len(json.dumps({'vectors':group,'namespace':self.namespace}).encode('utf-8'))>1_900_000:
                        raise ValueError('Single vector exceeds Pinecone request size limit')
                else: group=candidate
            if group: groups.append(group)
            for group in groups:
                response=_dict(self.index.upsert(vectors=group,namespace=self.namespace))
                count=response.get('upserted_count',response.get('upsertedCount'))
                if count is not None and count!=len(group): raise RuntimeError('Partial Pinecone upsert')
        obsolete=sorted(possible-set(current))
        for start in range(0,len(obsolete),1000):
            self.index.delete(ids=obsolete[start:start+1000],namespace=self.namespace)
        path.parent.mkdir(parents=True,exist_ok=True)
        temporary=path.with_suffix(path.suffix+'.tmp')
        temporary.write_text(json.dumps({'config':self.config,'chunks':current},indent=2)+'\n',encoding='utf-8')
        temporary.replace(path)
        journal.unlink()
        return {'upserted':len(changed),'deleted':len(obsolete),'unchanged':len(chunks)-len(changed)}
