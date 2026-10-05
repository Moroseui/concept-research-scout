"""Synthetic decisions only; no native/model invocation in these tests."""
import copy, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
from orchestrator import review_submission as s, scientific_search as search, autonomy_review as review

class SubmissionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name);self.root.chmod(0o700)
        self.bindings={'call_id':'c'*64,'run_id':'synthetic-run','stage':'run_spec_review','source_sha':'a'*40,'runtime_sha256':'b'*64,'input_sha256':'d'*64}
        self.pins=s.prepare(self.root,'scientific',self.bindings);self.pin=self.pins['config_sha256']
        self.config=s.load(self.root,self.pin)
        self.payload={'verdict':'APPROVE','findings':[],'rationale':'Synthetic only','bindings':self.bindings}
    def tearDown(self):self.tmp.cleanup()
    def finding(self):return {'id':'B1','category':'budget','text':'Exceeded','evidence':'Synthetic','resolution':'Fix cap'}
    def events(self,payload,ack):
        return [{'type':'assistant','message':{'content':[{'type':'tool_use','name':s.TOOL,'id':'submit1','input':payload}]}},
            {'type':'user','message':{'content':[{'type':'tool_result','tool_use_id':'submit1','content':[{'type':'text','text':json.dumps(ack)}]}]}}]
    def test_one_accepted_record_and_native_binding(self):
        ack=s.submit(self.root,self.pin,self.payload);raw=(self.root/s.RECORD).read_bytes()
        self.assertEqual((self.root/s.RECORD).stat().st_mode&0o777,0o600)
        self.assertEqual(s.verify_native(raw,self.config,self.pin,self.events(self.payload,ack))['verdict'],'APPROVE')
        with self.assertRaisesRegex(ValueError,'SECOND_SUBMISSION_REFUSED'):s.submit(self.root,self.pin,self.payload)
        self.assertEqual(raw,(self.root/s.RECORD).read_bytes())
    def test_invalid_then_corrected_in_same_process(self):
        for damage in ['missing','extra','verdict','binding','findings','category','empty','duplicate','listed']:
            v=copy.deepcopy(self.payload)
            if damage=='missing':v.pop('findings')
            elif damage=='extra':v['unused']='ignore'
            elif damage=='verdict':v['verdict']='APPROVE or REJECT'
            elif damage=='binding':v['bindings']['call_id']='wrong'
            elif damage=='findings':v['findings']='None'
            elif damage=='category':v.update(verdict='REVISE',findings=[dict(self.finding(),category='other')])
            elif damage=='empty':v['rationale']=' '
            elif damage=='duplicate':v.update(verdict='REVISE',findings=[self.finding(),self.finding()])
            else:v['findings']=[self.finding()]
            with self.subTest(damage=damage):
                with self.assertRaises(ValueError):s.submit(self.root,self.pin,v)
                self.assertFalse((self.root/s.RECORD).exists())
        s.submit(self.root,self.pin,self.payload)
    def test_reject_and_findings_preserved(self):
        self.payload.update(verdict='REJECT',findings=[self.finding()]);ack=s.submit(self.root,self.pin,self.payload)
        result=s.verify_native((self.root/s.RECORD).read_bytes(),self.config,self.pin,self.events(self.payload,ack))
        self.assertEqual(result['findings'],[self.finding()]);self.assertEqual(result['verdict'],'REJECT')
    def test_forged_missing_duplicate_native_proof_refuses(self):
        ack=s.submit(self.root,self.pin,self.payload);raw=(self.root/s.RECORD).read_bytes()
        for damage in ['none','payload','ack','duplicate','error']:
            e=self.events(copy.deepcopy(self.payload),copy.deepcopy(ack))
            if damage=='none':e=[]
            elif damage=='payload':e[0]['message']['content'][0]['input']['rationale']='changed'
            elif damage=='ack':e[1]['message']['content'][0]['content'][0]['text']='{}'
            elif damage=='duplicate':e+=copy.deepcopy(e)
            else:e[1]['message']['content'][0]['is_error']=True
            with self.subTest(damage=damage):
                with self.assertRaises(ValueError):s.verify_native(raw,self.config,self.pin,e)
    def test_prose_never_replaces_submission(self):
        for text in ['APPROVE','{"verdict":"APPROVE","findings":[]}','No BLOCKER[budget]']:
            with self.assertRaises(ValueError):s.verify_record(text.encode(),self.config,self.pin)
    def test_changed_config_and_unsafe_record_refuse(self):
        with self.assertRaisesRegex(ValueError,'CONFIG_CHANGED'):s.submit(self.root,'0'*64,self.payload)
        (self.root/s.RECORD).symlink_to(self.root/'outside')
        with self.assertRaisesRegex(ValueError,'SECOND'):s.submit(self.root,self.pin,self.payload)
        self.assertFalse((self.root/'outside').exists())
    def test_unsafe_preexisting_config_refuses(self):
        (self.root/s.CONFIG).chmod(0o644)
        with self.assertRaisesRegex(ValueError,'FILE_IDENTITY'):s.prepare(self.root,'scientific',self.bindings)
    def test_real_stdio_schema_correction_acceptance_and_second_refusal(self):
        (self.root/'input-measurement.json').write_text('{"workspace_files":[]}');(self.root/'input-measurement.json').chmod(0o600)
        ev=search.prepare(self.root)
        requests=[{'jsonrpc':'2.0','id':1,'method':'tools/list'}]
        for i,v in enumerate([dict(self.payload,verdict='maybe'),self.payload,self.payload],2):
            requests.append({'jsonrpc':'2.0','id':i,'method':'tools/call','params':{'name':'submit_review','arguments':v}})
        p=subprocess.run([sys.executable,'-I','-B',str(self.root/search.SERVER),ev['manifest_sha256'],self.pin,self.pins['module_sha256'],self.pins['contract_sha256']],cwd=self.root,
            input=''.join(json.dumps(v)+'\n' for v in requests),text=True,capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr)
        replies=[json.loads(line) for line in p.stdout.splitlines()]
        self.assertEqual(replies[0]['result']['tools'][-1]['inputSchema'],s.schema(self.config))
        self.assertTrue(replies[1]['result']['isError']);self.assertFalse(replies[2]['result']['isError'])
        self.assertEqual(replies[3]['error']['message'],'SECOND_SUBMISSION_REFUSED')
    def test_terminal_exhaustion_is_failed_but_unproven_stream_is_not(self):
        event={'type':'result','subtype':'error_max_turns','is_error':False,'session_id':'synthetic'}
        self.assertTrue(s.terminal_without_submission(self.root,json.dumps(event)))
        self.assertFalse(s.terminal_without_submission(self.root,''))
        self.assertFalse(s.terminal_without_submission(self.root,json.dumps(event)+'\n'+json.dumps(event)))
        self.assertFalse(s.terminal_without_submission(self.root,json.dumps({'type':'system','session_id':'other'})+'\n'+json.dumps(event)))

    def test_native_no_submission_is_terminal_failed_not_approval(self):
        console=json.dumps({'type':'result','subtype':'success','is_error':False,'session_id':'synthetic','result':'APPROVE'})
        with self.assertRaisesRegex(s.TerminalSubmissionFailure,'ACCEPTED_SUBMISSION_REQUIRED'):s.collect_scientific(self.root,console)
    def test_native_scientific_materializes_only_server_decision(self):
        ack=s.submit(self.root,self.pin,self.payload);e=self.events(self.payload,ack)
        e.append({'type':'result','subtype':'success','is_error':False,'session_id':'synthetic','result':'REJECT in prose is not a submitted decision'})
        s.collect_scientific(self.root,'\n'.join(json.dumps(x) for x in e))
        self.assertEqual(json.loads((self.root/'review.json').read_bytes()),{k:self.payload[k] for k in ('verdict','findings','rationale')})
    def test_scientific_command_has_no_write_or_execute_tool(self):
        from orchestrator.manual_stage import reviewer_command
        (self.root/'input-measurement.json').write_text('{"workspace_files":[]}');(self.root/'input-measurement.json').chmod(0o600)
        args=reviewer_command(self.root,'run_spec_review')
        self.assertEqual(args[args.index('--tools')+1],'Read')
        self.assertEqual(args[args.index('--allowedTools')+1],'Read(./**),'+','.join((*s.SEARCH_TOOLS,s.TOOL)))
        self.assertIn(self.pin,args[args.index('--mcp-config')+1])
    def test_administrative_command_keeps_confinement(self):
        args=review.claude_argv(s.mcp_config('e'*64,self.pins))
        self.assertEqual(args[args.index('--tools')+1],'Read,Glob,Grep')
        self.assertEqual(args[args.index('--disallowedTools')+1],'Bash,Write,Edit,NotebookEdit,Task')
        self.assertIn(s.TOOL,args[args.index('--allowedTools')+1])

if __name__=='__main__':unittest.main()
