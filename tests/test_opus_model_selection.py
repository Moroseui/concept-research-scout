"""No model calls: actual command assembly differs only in the selected model."""
import hashlib,inspect,json,os,tempfile,unittest
from pathlib import Path
from orchestrator import manual_stage,autonomy_review

class ModelSelection(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.work=Path(self.temp.name)/'workspace';self.work.mkdir(mode=0o700)
        raw=b'synthetic evidence only\n';(self.work/'evidence.txt').write_bytes(raw)
        (self.work/'input-measurement.json').write_text(json.dumps({'workspace_files':[{'id':'synthetic','path':'evidence.txt','sha256':hashlib.sha256(raw).hexdigest()}]}))
        for p in self.work.iterdir():p.chmod(0o600)
    def tearDown(self):self.temp.cleanup()
    def compare(self,module,name,*args):
        fn=getattr(module,name);source=inspect.getsource(fn)
        self.assertEqual(source.count('claude-opus-4-8'),1)
        old=source.replace('claude-opus-4-8','claude-fable-5')
        space=dict(vars(module));exec(compile(old,'synthetic-predecessor-command','exec'),space)
        before=space[name](*args);after=fn(*args)
        i=before.index('--model')+1
        self.assertEqual(before[i],'claude-fable-5');self.assertEqual(after[i],'claude-opus-4-8')
        before[i]=after[i];self.assertEqual(before,after)
        return after
    def test_run_spec_review_only_model_changes(self):
        a=self.compare(manual_stage,'reviewer_command',self.work,'run_spec_review')
        self.assertEqual(a[a.index('--max-turns')+1],'30')
    def test_interpretation_review_only_model_changes(self):
        a=self.compare(manual_stage,'reviewer_command',self.work,'result_interpretation_review')
        self.assertEqual(a[a.index('--max-turns')+1],'60')
    def test_administrative_review_only_model_changes(self):
        a=self.compare(autonomy_review,'claude_argv')
        self.assertEqual(a[a.index('--max-turns')+1],'60')
        # The separately authorized ExitPlanMode correction selects default
        # with exactly the same restricted tools; the model-only comparison above remains.
        self.assertEqual(a[a.index('--permission-mode')+1],'default')
    def test_scientific_tools_and_mcp_unchanged(self):
        a=manual_stage.reviewer_command(self.work,'result_interpretation_review')
        self.assertEqual(a[a.index('--tools')+1],'Read,Write')
        config=json.loads(a[a.index('--mcp-config')+1]);self.assertEqual(set(config['mcpServers']),{'evidence'})
        self.assertEqual(a[a.index('--allowedTools')+1],'Read(./**),Edit(./review.json),mcp__evidence__evidence_search,mcp__evidence__evidence_glob')
    def test_author_and_historical_retry_contract_unchanged(self):
        self.assertIn("'--model','gpt-6-astra'",inspect.getsource(manual_stage._invoke))
        # Existing specific historical permit is preserved, not reinterpreted.
        self.assertIn("'model':'claude-fable-5'",inspect.getsource(autonomy_review.provider_permit))

if __name__=='__main__':unittest.main()
