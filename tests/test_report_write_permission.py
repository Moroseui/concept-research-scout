"""Report-only permission mapping; deterministic, no model invocation."""
import hashlib,inspect,json,tempfile,unittest
from pathlib import Path
from orchestrator import manual_stage

class ReportPermission(unittest.TestCase):
    def test_only_report_permission_name_changes_both_review_roles(self):
        source=inspect.getsource(manual_stage.reviewer_command)
        self.assertEqual(source.count('Edit(./review.json)'),1)
        predecessor=source.replace('Edit(./review.json)','Write(./review.json)')
        namespace=dict(vars(manual_stage));exec(compile(predecessor,'synthetic-predecessor-command','exec'),namespace)
        with tempfile.TemporaryDirectory() as tmp:
            work=Path(tmp);raw=b'Synthetic evidence only\n';p=work/'evidence.txt';p.write_bytes(raw);p.chmod(0o600)
            p=work/'input-measurement.json';p.write_text(json.dumps({'workspace_files':[{'id':'synthetic','path':'evidence.txt','sha256':hashlib.sha256(raw).hexdigest()}]}));p.chmod(0o600)
            for stage,turns in [('run_spec_review','30'),('result_interpretation_review','60')]:
                with self.subTest(stage=stage):
                    before=namespace['reviewer_command'](work,stage);after=manual_stage.reviewer_command(work,stage)
                    i=before.index('--allowedTools')+1
                    self.assertEqual(after[i],'Read(./**),Edit(./review.json),mcp__evidence__evidence_search,mcp__evidence__evidence_glob')
                    before[i]=before[i].replace('Write(./review.json)','Edit(./review.json)')
                    self.assertEqual(before,after)
                    self.assertEqual(after[after.index('--model')+1],'claude-opus-4-8')
                    self.assertEqual(after[after.index('--tools')+1],'Read,Write')
                    self.assertEqual(after[after.index('--permission-mode')+1],'default')
                    self.assertEqual(after[after.index('--max-turns')+1],turns)
                    self.assertNotIn('--dangerously-skip-permissions',after)
                    self.assertNotIn('acceptEdits',after)

if __name__=='__main__':unittest.main()
