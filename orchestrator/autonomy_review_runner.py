"""M0 durable one-invocation runner. Never imports archived review automation."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from orchestrator import private_records
import signal
import subprocess
import time
from orchestrator import autonomy_review as review, review_inspection
from orchestrator.job_store import Store
from orchestrator.manual_executor import lock


class ReviewQueue(Store):
    def __init__(self, folder):
        self.folder=Path(folder)
        if any(p.is_symlink() for p in [self.folder.absolute(),*self.folder.absolute().parents]):
            raise ValueError('REVIEW_STATE_ALIAS')
        private_records.mkdir(self.folder,parents=True,exist_ok=True,mode=0o700)
        super().__init__(self.folder/'jobs.sqlite',connection_factory=private_records.Connection)
        self.db.execute("""CREATE TABLE IF NOT EXISTS autonomy_calls(
          id TEXT PRIMARY KEY, kind TEXT NOT NULL, change_id TEXT NOT NULL,
          round INTEGER NOT NULL, day TEXT NOT NULL, status TEXT NOT NULL,
          binding TEXT NOT NULL, receipt TEXT)""")

    def status(self, ident):
        row=self.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(ident,)).fetchone()
        return dict(row) if row else {'id':ident,'status':'NOT_RESERVED','charged_calls':0}

    def reserve(self, manifest, preflight):
        ident=review.sha(review.canonical(manifest));day=datetime.now(timezone.utc).date().isoformat()
        self.db.execute('BEGIN IMMEDIATE')
        try:
            if (self.folder/'HALT').exists():raise ValueError('OPERATOR_HALT_NO_REVIEW_CALL')
            old=self.status(ident)
            if old['status']!='NOT_RESERVED':
                self.db.execute('COMMIT');return old,False
            from orchestrator.administrative_terminal import administrative_exceptions
            reconciled_scientific=administrative_exceptions(self.db,self.folder.parent/'scientific-terminal')
            if self.db.execute('SELECT count(*) FROM autonomy_calls WHERE day=?',(day,)).fetchone()[0]>=20:
                raise ValueError('AUTONOMY_DAILY_CALL_LIMIT')
            rows=self.db.execute('SELECT * FROM autonomy_calls WHERE change_id=? ORDER BY round',(manifest['change_id'],)).fetchall()
            if len(rows)>=2 or manifest['round']!=len(rows)+1:raise ValueError('REVIEW_TWO_ROUND_LIMIT_OR_MISSING_PREDECESSOR')
            if rows:
                prior=manifest['predecessor'];prior_folder=self.folder/rows[0]['id']
                if prior.get('kind') in ('known_terminal_30_turn_exhaustion','known_terminal_60_turn_exhaustion'):
                    saved=json.loads(rows[0]['receipt']) if rows[0]['receipt'] else {}
                    if (rows[0]['status']!='FAILED' or saved.get('uncertain') is not False or
                        saved.get('exit_code')!=0 or saved.get('reason')!='REVIEW_INCOMPLETE_NO_RETRY' or
                        saved.get('native_stream_sha256')!=prior['native_stream_sha256'] or
                        review.verify_turn_exhaustion(prior_folder)!=prior):
                        raise ValueError('TURN_EXHAUSTION_LEDGER_BINDING')
                    # Historical 30-turn receipts retain their original shape, but
                    # every new completion must bind the original candidate too.
                    original=json.loads(rows[0]['binding'])['manifest']
                    if review.sha(review.canonical(original))!=prior['packet_sha256'] or rows[0]['id']!=prior['packet_sha256']:
                        raise ValueError('TURN_EXHAUSTION_ORIGINAL_MANIFEST_BINDING')
                    review.verify_completion_scope(manifest,original)
                elif prior.get('kind')=='provider_refusal':
                    saved=json.loads(rows[0]['receipt']) if rows[0]['receipt'] else {}
                    original=json.loads(rows[0]['binding'])['manifest']
                    if (rows[0]['status']!='FAILED' or saved.get('uncertain') is not False or
                        saved.get('exit_code')!=1 or saved.get('reason') not in
                        ('REVIEW_INCOMPLETE_NO_RETRY','PROVIDER_REFUSAL_NO_VERDICT') or
                        saved.get('native_stream_sha256')!=prior['native_stream_sha256'] or
                        review.provider_refusal_evidence(prior_folder)!=prior or
                        review.sha(review.canonical(original))!=prior['packet_sha256'] or
                        rows[0]['id']!=prior['packet_sha256']):
                        raise ValueError('PROVIDER_REFUSAL_LEDGER_BINDING')
                    review.verify_provider_retry_scope(manifest,original)
                    review.provider_permit(manifest)
                    if manifest.get('evidence_selection') is not None:
                        original_packet = (review.PROVIDER_RETRY_ROOT / prior['packet_sha256'] /
                                           'original-packet')
                        if review.verify_packet(original_packet) != original:
                            raise ValueError('PROVIDER_RETRY_PRESERVED_ORIGINAL_CHANGED')
                else:
                    if rows[0]['status']!='COMPLETE':raise ValueError('INCOMPLETE_REVIEW_NO_SUCCESSOR')
                    previous=review.verify_result(prior_folder)
                    if (previous['verdict'] not in ('CHANGES REQUIRED','REVISE') or
                        prior['receipt_sha256']!=review.sha((prior_folder/'receipt.json').read_bytes()) or
                        prior['report_sha256']!=previous['report_sha256']):raise ValueError('REVIEW_PREDECESSOR_BINDING')
            from orchestrator import connectivity
            preflight={**preflight,'connectivity':connectivity.require(['claude'], self.folder/'connectivity.json')}
            binding={'manifest':manifest,'preflight':preflight,'administrative_only_reconciliations':reconciled_scientific,'accounting_unit':'one native Claude invocation',
                     'scope':'implementation review; excluded from 30 M2-M6 scientific acceptance calls','daily_limit':20,'max_rounds':2}
            raw=json.dumps(binding,sort_keys=True)
            self.db.execute("INSERT INTO jobs(id,binding,phase,status) VALUES(?,?,'dispatch','RUNNING')",(ident,raw))
            self.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,NULL)',
                            (ident,'implementation_review',manifest['change_id'],manifest['round'],day,'RUNNING',raw))
            self.db.execute('INSERT INTO events VALUES(?,?,?)',(ident+':reserved',ident,json.dumps({'kind':'MODEL_CALL_RESERVED','charged_units':1,'binding_sha256':review.sha(raw.encode())})))
            self.db.execute('COMMIT');return self.status(ident),True
        except BaseException:self.db.execute('ROLLBACK');raise

    def finish(self, ident, status, receipt):
        if status not in {'COMPLETE','FAILED','UNCERTAIN'}:raise ValueError('REVIEW_OUTCOME')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.status(ident)
            if old['status']!='RUNNING':
                if old['status']!=status or json.loads(old['receipt'])!=receipt:raise ValueError('REVIEW_FINAL_OUTCOME_CHANGED')
                self.db.execute('COMMIT');return
            raw=json.dumps(receipt,sort_keys=True)
            self.db.execute('UPDATE autonomy_calls SET status=?,receipt=? WHERE id=?',(status,raw,ident))
            self.db.execute('UPDATE jobs SET status=? WHERE id=?',(status,ident))
            self.db.execute('INSERT INTO events VALUES(?,?,?)',(ident+':finished',ident,raw))
            self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise


def _preflight(packet, work):
    from orchestrator import manual_runtime, manual_auth, manual_host_guard, manual_isolation
    if manual_runtime.login_root().name!='autonomy-review-login':raise ValueError('SEPARATE_IMPLEMENTATION_REVIEW_LOGIN_REQUIRED')
    manual_auth.check('claude')
    if not manual_runtime.settings().get('host_guard'):raise ValueError('SERVER_REVIEW_HOST_GUARD_REQUIRED')
    host=manual_host_guard.before_call(work);outer=manual_isolation.probe(work,'claude');manifest=review.verify_packet(packet)
    if manifest.get('prompt_version') != 6:
        raise ValueError('FRESH_REVIEW_INSPECTION_VERSION_REQUIRED')
    view=review_inspection.prepare(packet,work/'inspection')
    from orchestrator.review_submission import prepare_administrative
    submission=prepare_administrative(work,manifest,work/'inspection')
    return {'host':host,'outer':outer,'inspection':view,'submission':submission,'reviewer_runtime_sha256':manual_runtime.identity(),
            'runner_sha256':review.sha(Path(__file__).read_bytes()),'protocol_sha256':review.sha(Path(review.__file__).read_bytes())}


def _native(packet, work, folder):
    from orchestrator import manual_isolation
    home,_=manual_isolation.credential_home(work,'claude')
    try:
        reserved=json.loads(review.regular(folder/'packet-manifest.json').read_text())
        if review.verify_packet(packet)!=reserved:raise ValueError('REVIEW_PACKET_CHANGED_BEFORE_SEND')
        view=review_inspection.verify(packet,work/'inspection')
        if json.loads(review.regular(folder/'inspection-binding.json').read_text())!=view:
            raise ValueError('INSPECTION_RESERVATION_BINDING_CHANGED')
        prompt=(packet/'prompt.txt').read_bytes();argv=review.readonly_command(work,home,packet,mode='exec',inspection=work/'inspection')
        with private_records.open_file(folder/'native-stream.jsonl','xb') as stdout, private_records.open_file(folder/'native-stderr.log','xb') as stderr:
            process=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=stdout,stderr=stderr,start_new_session=True,close_fds=True)
            review.write_once(folder/'process.json',review.canonical({'pid':process.pid,'started_at':time.time(),'prompt_sha256':review.sha(prompt),'inspection_manifest_sha256':view['inspection_manifest_sha256']}))
            try:process.communicate(prompt,timeout=900)
            except BaseException:
                try:os.killpg(process.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:process.wait(timeout=5)
                except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
                raise
        from orchestrator import review_submission as rs
        if reserved.get('prompt_version')==6 and (work/rs.RECORD).exists():
            raw=rs.regular(work/rs.RECORD).read_bytes()
            review.write_once(folder/'submission.json',raw)
        return process.returncode
    finally:
        cleanup=manual_isolation.discard_claude_copy(home)
        review.write_once(folder/'credential-cleanup.json',review.canonical({'status':cleanup}))


def reconcile(queue, ident):
    """Recover completed captured output only; never infer completion from a PID."""
    row=queue.status(ident)
    if row['status']=='NOT_RESERVED':return row
    folder=queue.folder/ident
    if row['status']!='RUNNING':
        if row['status']=='COMPLETE':review.verify_result(folder)
        return row
    exit_path=folder/'process-exit.json'
    if not exit_path.exists():return {**row,'next_action':'Inspect actual process/service handle; no launch or charge permitted'}
    exit_record=json.loads(review.regular(exit_path).read_text())
    manifest=json.loads(review.regular(folder/'packet-manifest.json').read_text())
    receipt={k:manifest[k] for k in ('source_sha','runtime_sha256','change_id','round')}
    receipt.update(exit_record,accounting_units=1)
    stream=folder/'native-stream.jsonl';raw=review.regular(stream).read_bytes() if stream.exists() else b''
    receipt['native_stream_sha256']=review.sha(raw)
    if exit_record.get('uncertain'):
        receipt['reason']='UNCERTAIN_MODEL_CALL_NO_RETRY';queue.finish(ident,'UNCERTAIN',receipt);return queue.status(ident)
    try:
        native=[json.loads(x) for x in raw.decode().splitlines() if x.strip()]
        final=[x for x in native if x.get('type')=='result']
        if len(final)==1 and isinstance(final[0].get('result'),str):
            report=final[0]['result'].encode();path=folder/('final-prose.txt' if manifest.get('prompt_version')==6 else 'report.md')
            if path.exists():
                if review.regular(path).read_bytes()!=report:raise ValueError('GENUINE_REPORT_CHANGED')
            else:review.write_once(path,report)
        if (exit_record['exit_code']==1 and len(final)==1 and final[0].get('is_error') is True and
            isinstance(final[0].get('result'),str) and final[0]['result'].startswith(review.PROVIDER_REFUSAL_PREFIX)):
            refusal=review.provider_refusal_evidence(folder)
            receipt.update(reason='PROVIDER_REFUSAL_NO_VERDICT',outcome='PROVIDER_REFUSAL',
                           verdict=None,provider_evidence=refusal)
            queue.finish(ident,'FAILED',receipt)
            return queue.status(ident)
        submission_raw=None
        if manifest.get('prompt_version')==6:
            if not (folder/'submission.json').exists():raise ValueError('ACCEPTED_SUBMISSION_REQUIRED')
            submission_raw=review.regular(folder/'submission.json').read_bytes()
            if not (folder/'final-prose.txt').is_file():raise ValueError('GENUINE_NATIVE_FINAL_TEXT_FIELD_REQUIRED')
            receipt.update(submission_sha256=review.sha(submission_raw),final_prose_sha256=review.sha(review.regular(folder/'final-prose.txt').read_bytes()))
        result=review.extract_result(raw.decode(),manifest,exit_record['exit_code'],submission_raw)
        if manifest.get('prompt_version')==6:
            report=result['report'].encode();path=folder/'report.md'
            if path.exists():
                if review.regular(path).read_bytes()!=report:raise ValueError('GENUINE_REPORT_CHANGED')
            else:review.write_once(path,report)
        receipt.update({k:v for k,v in result.items() if k!='report'},report_sha256=review.sha(result['report'].encode()))
        dest=folder/'receipt.json'
        if dest.exists():
            if json.loads(review.regular(dest).read_text())!=receipt:raise ValueError('REVIEW_RECEIPT_CHANGED')
        else:review.write_once(dest,review.canonical(receipt))
        review.verify_result(folder)
    except (ValueError,KeyError,TypeError,UnicodeError) as error:
        receipt['reason']=str(error);queue.finish(ident,'FAILED',receipt);return queue.status(ident)
    queue.finish(ident,'COMPLETE',receipt);return queue.status(ident)


@private_records.private_umask
def run(packet, state):
    from orchestrator import manual_auth
    packet=Path(packet);queue=ReviewQueue(state);manifest=review.verify_packet(packet);ident=review.sha(review.canonical(manifest))
    with lock(queue.folder/'review.lock'):
        from orchestrator.manual_isolation import cleanup_stale_claude_copies
        removed=cleanup_stale_claude_copies(queue.folder/'preflights')
        if removed:review.write_once(queue.folder/('startup-cleanup-'+str(time.time_ns())+'.json'),review.canonical({'removed_runtime_homes':removed,'original_login_unchanged':True}))
        if queue.status(ident)['status']!='NOT_RESERVED':return reconcile(queue,ident)
        folder=queue.folder/ident
        if folder.exists():raise ValueError('PARTIAL_REVIEW_PREPARATION_PRESERVED')
        with manual_auth.guard('implementation_review'):
            probes=queue.folder/'preflights';private_records.mkdir(probes,mode=0o700,exist_ok=True)
            work=probes/str(time.time_ns());private_records.mkdir(work,mode=0o700)
            try:preflight=_preflight(packet,work)
            except Exception as error:
                review.write_once(work/'refusal.json',review.canonical({'reason':str(error),'charged_calls':0}))
                raise
            if review.verify_packet(packet)!=manifest:raise ValueError('REVIEW_PACKET_CHANGED_BEFORE_RESERVATION')
            prepared=work/'prepared';private_records.mkdir(prepared,mode=0o700)
            review.write_once(prepared/'packet-manifest.json',review.canonical(manifest))
            if 'inspection' in preflight:
                review.write_once(prepared/'inspection-binding.json',review.canonical(preflight['inspection']))
            row,new=queue.reserve(manifest,preflight)
            if not new:return reconcile(queue,ident)
            try:
                prepared.rename(folder)  # same filesystem; no invocation folder on admission refusal
                rc=_native(packet,work,folder);exit_record={'exit_code':rc,'uncertain':False,'completed_at':time.time()}
            except BaseException as error:
                exit_record={'exit_code':None,'uncertain':True,'completed_at':time.time(),'error_type':type(error).__name__}
            if not folder.exists():
                queue.finish(ident,'UNCERTAIN',{'accounting_units':1,'reason':'PREPARED_INVOCATION_ADOPTION_FAILED_NO_RETRY',**exit_record})
                return queue.status(ident)
            review.write_once(folder/'process-exit.json',review.canonical(exit_record))
            return reconcile(queue,ident)


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['run','status'])
    parser.add_argument('--packet',required=True);parser.add_argument('--state',required=True);args=parser.parse_args()
    if args.action=='run':value=run(args.packet,args.state)
    else:
        m=review.verify_packet(args.packet);q=ReviewQueue(args.state);value=q.status(review.sha(review.canonical(m)))
    print(json.dumps(value,sort_keys=True));return 0 if value['status']=='COMPLETE' else 2

if __name__=='__main__':raise SystemExit(main())
