import unittest, tempfile, json
from pathlib import Path
from unittest.mock import patch
from commercelens_ai.cli import prepare_knowledge
class CliTests(unittest.TestCase):
 def test_ragas_clients_have_bounded_network_timeouts(self):
  from unittest.mock import Mock
  from types import SimpleNamespace
  from commercelens_ai.cli import main
  llm=Mock();emb=Mock()
  with patch.dict('sys.modules',{'langchain_openai':SimpleNamespace(ChatOpenAI=llm,OpenAIEmbeddings=emb)}),patch('commercelens_ai.cli.make_assistant'),patch('commercelens_ai.evaluation.run_evaluation',return_value={}):
   self.assertEqual(main(['evaluate','--ragas']),0)
  for client in (llm,emb):
   self.assertEqual(client.call_args.kwargs['timeout'],60)
   self.assertEqual(client.call_args.kwargs['max_retries'],1)

 def test_json_mode_keeps_error_exit_status(self):
  from commercelens_ai.cli import main
  from unittest.mock import Mock
  assistant=Mock();assistant.run.return_value={"status":"error","answer":"failed"}
  with patch("commercelens_ai.cli.make_assistant",return_value=assistant):
   self.assertEqual(main(["--backend","local","ask","test","--json"]),2)
 def test_prepare_writes_chunks_and_relationships(self):
  tmpbase=Path(__file__).resolve().parents[1]/'.context-work';tmpbase.mkdir(exist_ok=True)
  with tempfile.TemporaryDirectory(dir=tmpbase) as d:
   root=Path(d);chunk={'id':'x','text':'docs','metadata':{'service_id':'test'}};graph={'nodes':[],'edges':[]}
   with patch('commercelens_ai.cli.build_corpus',return_value=[chunk]),patch('commercelens_ai.cli.build_relationships',return_value=graph):
    result=prepare_knowledge(root,None)
   self.assertEqual(result['chunks'],1)
   self.assertEqual(json.loads((root/'catalog/relationships.json').read_text()),graph)
   self.assertEqual(json.loads((root/'.data/corpus.jsonl').read_text()),chunk)
if __name__=='__main__':unittest.main()
