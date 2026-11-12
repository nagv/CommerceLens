"""Reproducible quality run with isolated, bounded RAGAS and parallel feedback upload."""
import sys,json,subprocess,argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from commercelens_ai.config import Settings
from commercelens_ai import evaluation as ev
from commercelens_ai.cli import make_assistant
from commercelens_ai.providers import OpenAICompatibleModel
settings=Settings.from_env(root)
if sys.argv[1:2]==['--ragas-child']:
 from langchain_openai import ChatOpenAI,OpenAIEmbeddings
 request=Path(sys.argv[2]);payload=json.loads(request.read_text())
 llm=ChatOpenAI(model=settings.chat_model,api_key=settings.chat_api_key,base_url=settings.chat_base_url,temperature=0,timeout=60,max_retries=1)
 emb=OpenAIEmbeddings(model=settings.embedding_model,api_key=settings.embedding_api_key,base_url=settings.embedding_base_url,check_embedding_ctx_length=False,timeout=60,max_retries=1)
 result=ev._ragas(payload['case'],payload['result'],True,llm,emb)
 request.with_suffix('.result.json').write_text(json.dumps(result));sys.exit(0)
original=ev._ragas
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--repetitions',type=int,choices=range(1,4),default=1)
args=parser.parse_args()
output=args.output.resolve()
if output.exists() and any(output.iterdir()):raise SystemExit('Output must be new or empty; existing results are never overwritten.')
output.mkdir(parents=True,exist_ok=True)
def bounded(case,result,enabled,llm,emb):
 if not enabled or case['mode']=='plan' or case.get('expected_behavior','answer')!='answer' or result.get('behavior','answer')!='answer':return original(case,result,enabled,llm,emb)
 import uuid
 request=output/('ragas-'+case['id']+'-'+uuid.uuid4().hex[:8]+'.json');request.write_text(json.dumps({'case':case,'result':result}))
 try:
  with request.with_suffix('.log').open('w') as log:
   subprocess.run([sys.executable,__file__,'--ragas-child',str(request)],timeout=180,stdout=log,stderr=log,check=True,cwd=root)
  answer=json.loads(request.with_suffix('.result.json').read_text())
 except subprocess.TimeoutExpired:answer={'status':'error','error':'TimeoutError','reason':'Isolated RAGAS process exceeded 180 seconds; application answer preserved.'}
 except Exception as exc:answer={'status':'error','error':type(exc).__name__}
 print('RAGAS',case['id'],answer['status'],flush=True);return answer
ev._ragas=bounded
oldjudge=ev._judge
def progress(judge,case,result):
 answer=oldjudge(judge,case,result);print('Judge',case['id'],answer['status'],flush=True);return answer
ev._judge=progress
from langsmith import Client
class ParallelFeedback:
 def __init__(self):self.client=Client(api_key=settings.langsmith_api_key,auto_batch_tracing=False);self.pool=ThreadPoolExecutor(max_workers=4);self.pending=[];self.project=None
 def __getattr__(self,key):return getattr(self.client,key)
 def create_project(self,**kwargs):
  result=self.client.create_project(**kwargs);self.project=result.id;return result
 def create_feedback(self,**kwargs):
  kwargs['session_id']=self.project;self.pending.append(self.pool.submit(self.client.create_feedback,**kwargs))
 def update_project(self,**kwargs):
  for future in self.pending:future.result()
  self.pool.shutdown();return self.client.update_project(**kwargs)
client=ParallelFeedback()
summary=ev.run_evaluation(make_assistant(root,settings,'pinecone',None,True),root/'evals/baselines/v1-20261111/golden.jsonl',output,repetitions=args.repetitions,judge=OpenAICompatibleModel(settings.chat_api_key,settings.chat_base_url,settings.chat_model,max_tokens=8000,timeout=120),ragas=True,langsmith=True,ragas_llm=True,ragas_embeddings=True,langsmith_client=client,evidence_root=root,workers=3)
client.pool.shutdown(wait=True)
print(json.dumps(summary),flush=True)
