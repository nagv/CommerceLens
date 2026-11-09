import importlib.util,tempfile,unittest,json
from unittest.mock import patch
from pathlib import Path
spec=importlib.util.spec_from_file_location('catalog_refresh',Path(__file__).resolve().parents[1]/'scripts/refresh-catalog.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class RefreshTests(unittest.TestCase):
 def test_fingerprint_ignores_commit_but_detects_content(self):
  self.assertEqual(m.fingerprint({'a.md':'same'}),m.fingerprint({'a.md':'same'}))
  self.assertNotEqual(m.fingerprint({'a.md':'same'}),m.fingerprint({'a.md':'changed'}))
 def test_unchanged_service_skips_model(self):
  old={'input_hash':'abc','pipeline_version':m.VERSION,'model':'test'}
  self.assertFalse(m.needs_refresh(old,'abc','test'))
  self.assertTrue(m.needs_refresh(old,'new','test'))
  self.assertTrue(m.needs_refresh(old,'abc','other'))
 def test_empty_model_output_is_explicit_failure(self):
  with self.assertRaisesRegex(ValueError,"length"):
   m.parse_response({"choices":[{"finish_reason":"length","message":{"content":None}}]})
 def test_unknown_evidence_rejected(self):
  card={'purpose':'x','stack':'x','interfaces':[],'data':[],'events':[],'flow':[],'dependencies':[],'unknowns':[],'evidence':['invented.md']}
  with self.assertRaises(ValueError):m.validate_summary(card,{'real.md'})
 def test_summary_must_be_bounded(self):
  card={'purpose':'x'*12001,'stack':'x','interfaces':[],'data':[],'events':[],'flow':[],'dependencies':[],'unknowns':[],'evidence':['real.md']}
  with self.assertRaises(ValueError):m.validate_summary(card,{'real.md'})
 def test_unrelated_doc_change_preserves_summary_but_records_drift(self):
  selected={'overview.md':'same'}
  before={'overview.md':'same','detail.md':'old'}
  after={'overview.md':'same','detail.md':'new'}
  self.assertEqual(m.fingerprint(selected),m.fingerprint(selected))
  self.assertNotEqual(m.fingerprint(before),m.fingerprint(after))
class PipelineTests(unittest.TestCase):
 def test_incremental_refresh_and_service_removal(self):
  with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]/".context-work") as tmp:
   root=Path(tmp);manifest=root/'services.yaml'
   services=[]
   for name in ['one','two']:
    wiki=root/name/'openwiki';wiki.mkdir(parents=True)
    (wiki/'quickstart.md').write_text('Overview '+name)
    services.append({'id':name,'path':name,'repository':'https://github.com/demo/'+name+'.git'})
   manifest.write_text(m.yaml.safe_dump({'services':services}))
   def summary(service,inputs,previous,model):
    return {'purpose':'Purpose '+service['id'],'stack':'Demo','interfaces':[],'data':[],'events':[],'flow':[],'dependencies':[],'unknowns':[],'evidence':list(inputs)}
   def run(command):
    with patch('sys.argv',['refresh',command,'--manifest',str(manifest)]):m.main()
   with patch.object(m,'ROOT',root),patch.object(m,'summarize',side_effect=summary) as gen:
    run('refresh');self.assertEqual(gen.call_count,2)
    run('refresh');self.assertEqual(gen.call_count,2)
    run('check')
    (root/'one/openwiki/quickstart.md').write_text('Changed overview')
    with self.assertRaisesRegex(SystemExit,'Stale'):run('check')
    run('refresh');self.assertEqual(gen.call_count,3)
    manifest.write_text(m.yaml.safe_dump({'services':[services[0]]}))
    with self.assertRaisesRegex(SystemExit,'membership'):run('check')
    run('refresh');self.assertEqual(gen.call_count,3)
    self.assertNotIn('## two',(root/'openwiki/service-catalog.md').read_text())
    run('check')
if __name__=='__main__':unittest.main()
