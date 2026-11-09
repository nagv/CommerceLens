"""CLI for documentation preparation, Pinecone ingestion, chat and evaluation."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
from .knowledge import build_corpus, build_relationships, get_dependencies
ROOT=Path(__file__).resolve().parents[1]


def atomic_write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(text,encoding='utf-8');temp.replace(path)


def prepare_knowledge(root,manifest=None):
    chunks=build_corpus(root,manifest)
    graph=build_relationships(root,manifest)
    atomic_write(root/'.data/corpus.jsonl',''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in chunks))
    atomic_write(root/'catalog/relationships.json',json.dumps(graph,indent=2,ensure_ascii=False)+'\n')
    return {'chunks':len(chunks),'nodes':len(graph['nodes']),'relationships':len(graph['edges'])}


@contextmanager
def ingest_lock(root):
    lock=root/'.data/ingest.lock';lock.parent.mkdir(parents=True,exist_ok=True)
    try:fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY)
    except FileExistsError:raise RuntimeError('Another ingestion holds .data/ingest.lock. Remove a stale lock only after checking no ingestion is running.') from None
    try:
        os.write(fd,str(os.getpid()).encode());os.close(fd);yield
    finally:lock.unlink(missing_ok=True)


def make_retriever(root,settings,backend,manifest=None):
    from .retrieval import LocalRetriever,PineconeHTTPIndex,PineconeRetriever
    if backend=='local':return LocalRetriever(build_corpus(root,manifest))
    from .providers import OpenAICompatibleEmbeddings
    if not settings.pinecone_host or not settings.pinecone_api_key:
        raise ValueError('Configure PINECONE_API_KEY and PINECONE_HOST, or explicitly select --backend local.')
    embeddings=OpenAICompatibleEmbeddings(settings.embedding_api_key,settings.embedding_base_url,settings.embedding_model)
    return PineconeRetriever(PineconeHTTPIndex(settings.pinecone_host,settings.pinecone_api_key),embeddings.embed,
        namespace=settings.pinecone_namespace,index_name=settings.pinecone_index,embedding_model=settings.embedding_model)


def make_assistant(root,settings,backend,manifest=None,trace=False):
    from .engine import Assistant
    from .providers import OpenAICompatibleModel
    graph=build_relationships(root,manifest)
    assistant=Assistant(make_retriever(root,settings,backend,manifest),
        OpenAICompatibleModel(settings.chat_api_key,settings.chat_base_url,settings.chat_model),graph)
    if trace:
        if not settings.langsmith_api_key:raise ValueError('LANGSMITH_API_KEY is required for --trace')
        import langsmith
        os.environ['LANGSMITH_TRACING']='true'
        os.environ['LANGSMITH_API_KEY']=settings.langsmith_api_key
        os.environ['LANGSMITH_PROJECT']=settings.langsmith_project
        assistant.run=langsmith.traceable(name='CommerceLens ask/plan',run_type='chain')(assistant.run)
    return assistant


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--env-file',type=Path,help='Explicit configuration file; defaults to CommerceLens/.env')
    parser.add_argument('--manifest',type=Path)
    parser.add_argument('--backend',choices=['local','pinecone'],default='pinecone',help='No silent fallback; local is lexical retrieval')
    parser.add_argument('--trace',action='store_true',help='Send assistant runs to LangSmith')
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('build',help='Build local chunks and consolidated relationships; no network')
    sub.add_parser('setup',help='Create or verify a dedicated Pinecone index matching the embedding dimensions')
    sub.add_parser('status',help='Show non-secret configuration and local artifact status')
    p=sub.add_parser('dependencies');p.add_argument('service');p.add_argument('--direction',choices=['inbound','outbound','both'],default='both');p.add_argument('--hops',type=int,default=1)
    p=sub.add_parser('search');p.add_argument('question');p.add_argument('--service',action='append');p.add_argument('--level',choices=['master','service']);p.add_argument('--limit',type=int,default=6)
    p=sub.add_parser('ingest');p.add_argument('--batch-size',type=int,default=16)
    for mode in ['ask','plan']:
        p=sub.add_parser(mode);p.add_argument('question');p.add_argument('--json',action='store_true');p.add_argument('--output',type=Path)
    p=sub.add_parser('serve');p.add_argument('--port',type=int,default=8090)
    p=sub.add_parser('evaluate');p.add_argument('--dataset',type=Path,default=ROOT/'evals/golden.jsonl');p.add_argument('--output',type=Path)
    p.add_argument('--repetitions',type=int,default=1);p.add_argument('--judge',action='store_true');p.add_argument('--ragas',action='store_true');p.add_argument('--langsmith',action='store_true')
    args=parser.parse_args(argv)
    from .config import Settings
    settings=Settings.from_env(ROOT,args.env_file)
    if args.command=='build':result=prepare_knowledge(ROOT,args.manifest)
    elif args.command=='status':
        result={'backend':args.backend,'chat_model':settings.chat_model,'chat_configured':bool(settings.chat_api_key),'embedding_model':settings.embedding_model,
            'pinecone_configured':bool(settings.pinecone_api_key and settings.pinecone_host),'pinecone_index':settings.pinecone_index,'pinecone_namespace':settings.pinecone_namespace,
            'langsmith_configured':bool(settings.langsmith_api_key),'corpus_exists':(ROOT/'.data/corpus.jsonl').exists()}
    elif args.command=='setup':
        from .provision import ensure_index
        from .providers import OpenAICompatibleEmbeddings
        embeddings=OpenAICompatibleEmbeddings(settings.embedding_api_key,settings.embedding_base_url,settings.embedding_model)
        dimension=len(embeddings.embed(['CommerceLens embedding dimension check'])[0])
        index=ensure_index(settings.pinecone_api_key,settings.pinecone_index,dimension)
        host='https://'+index['host'].removeprefix('https://')
        env_path=args.env_file or ROOT/'.env'
        lines=env_path.read_text(encoding='utf-8').splitlines() if env_path.exists() else []
        lines=[line for line in lines if not line.strip().startswith('PINECONE_HOST=')]
        lines.append('PINECONE_HOST='+host)
        atomic_write(env_path,'\n'.join(lines)+'\n')
        result={'index':settings.pinecone_index,'dimension':dimension,'created':index['created'],'ready':index.get('status',{}).get('ready',False),'host':host,'namespace':settings.pinecone_namespace}
    elif args.command=='dependencies':result=get_dependencies(build_relationships(ROOT,args.manifest),args.service,args.direction,args.hops)
    elif args.command=='search':result=make_retriever(ROOT,settings,args.backend,args.manifest).search(args.question,args.service,args.level,args.limit)
    elif args.command=='ingest':
        if args.backend!='pinecone':raise ValueError('Ingest requires --backend pinecone. Use build for local artifacts.')
        with ingest_lock(ROOT):
            prepare_knowledge(ROOT,args.manifest)
            chunks=[json.loads(line) for line in (ROOT/'.data/corpus.jsonl').read_text(encoding='utf-8').splitlines()]
            result=make_retriever(ROOT,settings,'pinecone',args.manifest).sync(chunks,ROOT/'.data/pinecone-manifest.json',args.batch_size)
    else:
        assistant=make_assistant(ROOT,settings,args.backend,args.manifest,args.trace)
        if args.command=='serve':
            from .server import serve
            print(f'CommerceLens assistant: http://127.0.0.1:{args.port} (retrieval={args.backend})',flush=True)
            serve(assistant,port=args.port);return 0
        if args.command=='evaluate':
            from .evaluation import run_evaluation
            from .providers import OpenAICompatibleModel
            kwargs={}
            if args.ragas:
                # Imports are explicit: optional missing evaluator dependencies never silently disappear.
                from langchain_openai import ChatOpenAI,OpenAIEmbeddings
                kwargs['ragas_llm']=ChatOpenAI(model=settings.chat_model,api_key=settings.chat_api_key,base_url=settings.chat_base_url,temperature=0)
                kwargs['ragas_embeddings']=OpenAIEmbeddings(model=settings.embedding_model,api_key=settings.embedding_api_key,base_url=settings.embedding_base_url,check_embedding_ctx_length=False)
            if args.langsmith:
                if not settings.langsmith_api_key:raise ValueError('LANGSMITH_API_KEY is required for experiment upload')
                from langsmith import Client
                kwargs['langsmith_client']=Client(api_key=settings.langsmith_api_key)
            output=args.output or ROOT/'evals/results'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            result=run_evaluation(assistant,args.dataset,output,repetitions=args.repetitions,
                judge=OpenAICompatibleModel(settings.chat_api_key,settings.chat_base_url,settings.chat_model) if args.judge else None,
                ragas=args.ragas,langsmith=args.langsmith,evidence_root=ROOT,**kwargs)
            print(json.dumps(result,indent=2,ensure_ascii=False));print('Results: '+str(output))
            return 0 if result.get('failure_count',0)==0 and result.get('langsmith',{}).get('status')!='error' and not any(result.get('judge',{}).get(k,0) or result.get('ragas',{}).get(k,0) for k in ['error','missing_configuration','missing_dependency']) else 2
        result=assistant.run(args.question,mode=args.command);result['retrieval_backend']=args.backend
        if args.output:atomic_write(args.output,json.dumps(result,indent=2,ensure_ascii=False)+'\n')
        if not args.json:
            print(result['answer'])
            print(f"\nStatus: {result['status']}; retrieval: {args.backend}; latency: {result['latency_seconds']}s")
            return 0 if result['status']=='ok' else 2
    print(json.dumps(result,indent=2,ensure_ascii=False))
    if args.command in ('ask','plan'):return 0 if result['status']=='ok' else 2
    return 0


def entrypoint():
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,"reconfigure"):stream.reconfigure(encoding="utf-8",errors="replace")
    try:return main()
    except KeyboardInterrupt:return 130
    except Exception as exc:
        # Provider exceptions may contain keys; only safe, actionable configuration errors are displayed.
        if isinstance(exc,(ValueError,FileNotFoundError)):print(f'{type(exc).__name__}: {exc}',file=sys.stderr)
        else:print(f'{type(exc).__name__}: operation failed; inspect configuration and service availability.',file=sys.stderr)
        return 1
