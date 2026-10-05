"""One explicitly supervised synthetic completion -> Astra -> Claude -> Astra cycle.

No timer integration or standing grant. Root is a setup transport, never a model
identity. Unknown/incomplete calls are blocked for reconciliation, never retried.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import pwd
import signal
import subprocess
import time

from orchestrator.remote_supervisor import Controller, checked_source, lock, PAYLOAD, identifier, validate_receipt
from orchestrator.operations_report import Queue, finalize, private_root, sanitized
from orchestrator.git_publication import scan
from orchestrator.public_export import text as public_text

SOURCE_FILES = ('orchestrator/hosted_cycle.py', 'orchestrator/remote_supervisor.py',
                'orchestrator/operations_report.py', 'orchestrator/job_store.py',
                'orchestrator/hosted_review_recovery.py', 'orchestrator/hosted_cycle_reconcile.py',
                'orchestrator/public_export.py', 'orchestrator/git_publication.py',
                'campaigns/isles24-pilot/colab/smoke.py',
                'docs/operations/REMOTE_OPERATING_DIRECTION.md',
                'docs/operations/QUEUED_SCIENTIFIC_TASKS_20260906.json')
MODELS = {'astra': 'gpt-6-astra', 'claude': 'claude-fable-5'}


def sha(raw): return hashlib.sha256(raw).hexdigest()
def encoded(value): return (json.dumps(value, sort_keys=True, indent=2)+'\n').encode()


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try: os.fsync(fd)
    finally: os.close(fd)


def immutable(path, data):
    # Private, bounded source context; public report/summary limits stay unchanged.
    path=Path(path)
    private_root(path.parent)
    scan(path.name,data);public_text(data.decode(),limit=1500000)
    try:fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    except FileExistsError:
        if path.is_symlink() or path.read_bytes()!=data:raise ValueError('IMMUTABLE_OUTPUT_CONFLICT')
        return
    with os.fdopen(fd,'wb') as stream:
        stream.write(data);stream.flush();os.fsync(stream.fileno())
    sync_dir(path.parent)


def claim(folder, binding):
    """Durable before dispatch; even crash-before-exec requires reconciliation."""
    folder = Path(folder)
    if folder.exists():
        if folder.is_symlink() or not (folder/'binding.json').is_file():
            raise ValueError('INCOMPLETE_CYCLE_RECONCILE_NO_AUTOMATIC_RETRY')
        if json.loads((folder/'binding.json').read_text()) != binding:
            raise ValueError('CYCLE_BINDING_CONFLICT')
        if (folder/'complete.json').exists(): return False
        raise ValueError('INCOMPLETE_CYCLE_RECONCILE_NO_AUTOMATIC_RETRY')
    folder.mkdir(mode=0o700)
    sync_dir(folder.parent)
    immutable(folder/'binding.json', encoded(binding))
    return True


def checked_packet(root, rows, event, config, execution_root=None, verified_events=None):
    source = {}
    for name in SOURCE_FILES:
        p = root/name
        if p.is_symlink(): raise ValueError('SOURCE_SYMLINK')
        raw = p.read_bytes(); scan(name, raw)
        source[name] = {'sha256': sha(raw), 'content': raw.decode()}
    execution = {}
    if execution_root is not None:
        pins = {r['source'] for r in rows}
        if len(pins)!=1: raise ValueError('EXECUTION_SOURCE_SET_REQUIRES_EXPLICIT_RECONCILIATION')
        checked_source(execution_root, next(iter(pins)))
        for name in SOURCE_FILES:
            p=Path(execution_root)/name
            # Adapter itself did not exist at old execution pins; say so explicitly.
            if not p.exists(): execution[name]={'status':'NOT_PRESENT_AT_EXECUTION_SOURCE'};continue
            raw=p.read_bytes();scan(name,raw)
            execution[name]={'sha256':sha(raw),'identical_to_reporting':source[name]['sha256']==sha(raw)}
            if source[name]['sha256']!=sha(raw):execution[name]['content']=raw.decode()
    packet = {'execution_implementation':execution,'verified_events':verified_events or {},
              'scope': 'Supervised operational acceptance; no scientific conclusions or grants',
              'jobs': rows, 'trigger': event, 'implementation': source,
              'deployed_service_properties': config,
              'limits': 'Three model calls maximum, 240 seconds each; no fallback or automatic retry. No patient work, publication, reset or shell instructions.'}
    scan('packet.json', encoded(packet))
    return packet


def scientific_worker_command(user, work, command):
    # Credentials retain their existing HOME. Mutable client/MCP cache belongs
    # to this already-private per-stage directory, not the reviewed auth home.
    return ['runuser', '-u', user, '--', 'env', '-i',
            'HOME='+str(Path('/home')/user), 'USER='+user,
            'XDG_CACHE_HOME='+str(Path(work)/'client-cache'),
            'PATH=/usr/local/bin:/usr/bin:/bin', *command]


def model_command(family, retrieval_runtime=None, *, output_contract=None, schema_path=None):
    """Fixed bounded client command; no caller-supplied budget or extra tools."""
    if family not in MODELS:
        raise ValueError('HOSTED_MODEL_FAMILY_REQUIRED')
    if family == 'astra':
        command = ['codex', 'exec', '--ignore-user-config', '--ignore-rules',
                   '-m', MODELS[family], '-s', 'read-only', '-c', 'approval_policy="never"',
                   '-c', 'features.shell_tool=false', '-c', 'web_search="disabled"',
                   '--skip-git-repo-check', '--json', '-']
    else:
        command = ['claude', '-p', '--model', MODELS[family], '--output-format', 'stream-json',
                   '--verbose', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
                   '--tools', '', '--permission-mode', 'dontAsk', '--max-turns', '3']
    if retrieval_runtime is not None:
        from orchestrator import scientific_evidence_runtime as retrieval
        if family == 'claude':
            # Proposed narrow operator amendment; independent review and deployment
            # gates apply before this candidate is used. Reader budgets stay fixed.
            command[command.index('--max-turns')+1] = '32'
            index = command.index('--mcp-config')
            del command[index:index+2]
        command += retrieval.client_options(retrieval_runtime, family)
    if output_contract is not None:
        from orchestrator.scientific_output import encoded as output_encoded
        schema_raw = output_encoded(output_contract['schema'])
        if len(schema_raw) > 16000:
            raise ValueError('SCIENTIFIC_OUTPUT_SCHEMA_BOUND')
        if family == 'astra':
            if schema_path is None or Path(schema_path).read_bytes() != schema_raw:
                raise ValueError('SCIENTIFIC_OUTPUT_SCHEMA_FILE_REQUIRED')
            command += ['--output-schema', str(schema_path)]
        else:
            command += ['--json-schema', schema_raw.decode()]
    return command


def model_call(folder, stage, family, prompt, output_format='markdown', prepared_prompt=False, *, timeout_seconds=240, evidence_access=None):
    if type(timeout_seconds) is not int or timeout_seconds not in (240, 600):
        raise ValueError('BOUNDED_SCIENTIFIC_MODEL_TIMEOUT_REQUIRED')
    from orchestrator.hosted_context import envelope, format_prefix, measure_input, InputTooLarge, context_bytes
    context_root=Path(__file__).resolve().parents[1]
    context_source=subprocess.check_output(['git','-c','safe.directory='+str(context_root),'rev-parse','HEAD'],cwd=context_root,text=True).strip()
    checked_source(context_root,context_source)
    if family not in MODELS:
        raise ValueError('HOSTED_MODEL_FAMILY_REQUIRED')
    envelope_options = {} if evidence_access is None else {'evidence_access': evidence_access}
    prompt,operating_context=envelope(context_root,folder,prompt,verified_source=context_source,
                                     family='codex' if family=='astra' else 'claude', **envelope_options)
    if evidence_access is not None:
        from orchestrator import scientific_evidence_runtime as retrieval
        retrieval.stage_profile(evidence_access, source=context_source,
            packet_sha256=operating_context['task_packet']['sha256'], stage=stage, family=family)
    from orchestrator import scientific_output
    packet = operating_context.get('task_state')
    selected_output = None
    if output_format == 'json':
        packet_raw = (Path(folder)/operating_context['task_packet']['name']).read_bytes()
        if sha(packet_raw) != operating_context['task_packet']['sha256']:
            raise ValueError('SCIENTIFIC_OUTPUT_PACKET_CHANGED')
        packet = scientific_output.loads(packet_raw)
        selected_output = scientific_output.contract(packet, stage)
    if selected_output is not None:
        immutable(folder/(stage+'.output-contract.json'), encoded(selected_output))
    prompt = format_prefix(prompt, prepared_prompt=prepared_prompt, output_format=output_format,
                           scientific_evidence=evidence_access is not None,
                           structured_output=selected_output is not None)
    try:
        measurement=measure_input(prompt, family, stage, task_state=packet, output_contract=selected_output)
    except InputTooLarge as error:
        context_raw=context_bytes(context_root, operating_context, context_source)
        immutable(folder/(stage+'.input-preflight-failure.json'),encoded({
            'status':'PRESERVED_FINAL_INPUT_REFUSAL_REQUIRES_RECONCILIATION',
            'measurement':error.measurement,'automatic_retry':False,'provider_calls':0,
            'input_within_existing_preservation_bound':len(prompt)<=1500000,
            'context_within_existing_preservation_bound':len(context_raw.decode())<=1500000}))
        # Keep existing original-file bounds; an oversized input still gets a
        # named refusal with its exact hash before any provider work exists.
        if len(prompt)<=1500000:immutable(folder/(stage+'.input.md'),prompt.encode())
        if len(context_raw.decode())<=1500000:immutable(folder/(stage+'.operating-context.json'),context_raw)
        raise
    context_raw=context_bytes(context_root, operating_context, context_source)
    immutable(folder/(stage+'.operating-context.json'),context_raw)
    scan('prompt.md', prompt.encode()); immutable(folder/(stage+'.input.md'), prompt.encode())
    immutable(folder/(stage+'.input-preflight.json'),encoded(measurement))
    user = 'research-driver' if family == 'astra' else 'research-reviewer'
    base=Path('/var/lib/research-system/model-work');base.mkdir(mode=0o711,exist_ok=True)
    if base.is_symlink() or base.stat().st_uid!=0 or base.stat().st_mode & 0o022:raise ValueError('PROTECTED_MODEL_WORK_ROOT_REQUIRED')
    work = base/('acceptance-'+sha(str(folder).encode())[:20]+'-'+stage)
    work.mkdir(mode=0o700)  # existing directory is ambiguous, never reused
    account = pwd.getpwnam(user); os.chown(work, account.pw_uid, account.pw_gid)
    retrieval_runtime = None
    if evidence_access is not None:
        retrieval_runtime = retrieval.prepare(evidence_access, source=context_source,
            source_root=context_root, work=work, account=account)
        immutable(folder/(stage+'.evidence-runtime.json'), encoded(retrieval_runtime))
    schema_path = None
    if selected_output is not None and family == 'astra':
        schema_path = work/'scientific-output.schema.json'
        with schema_path.open('xb') as stream:
            stream.write(scientific_output.encoded(selected_output['schema']))
        schema_path.chmod(0o444)
    command = model_command(family, retrieval_runtime, output_contract=selected_output,
                            schema_path=schema_path)
    immutable(folder/(stage+'.command.json'), encoded({'argv': command,
        'output_contract_sha256': sha(encoded(selected_output)) if selected_output else None}))
    args = scientific_worker_command(user, work, command)
    immutable(folder/(stage+'.started.json'), encoded({'stage': stage, 'requested_model': MODELS[family],
              'started_utc': datetime.now(timezone.utc).isoformat(), 'timeout_seconds': timeout_seconds}))
    start = time.monotonic()
    with (folder/(stage+'.stdout')).open('xb') as out, (folder/(stage+'.stderr')).open('xb') as err:
        process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=out, stderr=err,
                                   cwd=work, start_new_session=True)
        immutable(folder/(stage+'.process-identity.json'),encoded({'pid':process.pid,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'process_group':process.pid}))
        try: process.communicate(prompt.encode(), timeout=timeout_seconds)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL); process.wait()
            raise ValueError('MODEL_TIMEOUT_RECONCILE_PRIVATE_EVIDENCE')
        finally:
            # Stop descendants on success and on interruption before hashing evidence.
            try: os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError: pass
            process.wait()
            immutable(folder/(stage+'.ended.json'),encoded({'returncode':process.returncode,'ended_utc':datetime.now(timezone.utc).isoformat()}))
    receipt = {'stage': stage, 'requested_model': MODELS[family], 'returncode': process.returncode,
               'wall_seconds': time.monotonic()-start, 'timeout_seconds': timeout_seconds,
               'stdout_sha256': sha((folder/(stage+'.stdout')).read_bytes()),
               'stderr_sha256': sha((folder/(stage+'.stderr')).read_bytes()),
               'input_sha256': sha(prompt.encode()), 'actual_model': None, 'usage': None,
               'operating_context_sha256':sha(context_raw),
               'supplied_document_sha256':{n:v['sha256'] for n,v in operating_context['documents'].items()}}
    immutable(folder/(stage+'.process.json'), encoded(receipt))
    if process.returncode: raise ValueError('MODEL_FAILED_RECONCILE_PRIVATE_EVIDENCE')
    events = [scientific_output.loads(line) for line in (folder/(stage+'.stdout')).read_text().splitlines() if line.strip()]
    provider_output = None
    if family == 'claude':
        final = [e for e in events if e.get('type') == 'result'][-1]
        if final.get('is_error') or final.get('subtype') != 'success': raise ValueError('CLAUDE_NOT_COMPLETE')
        models = {e.get('message', {}).get('model') for e in events if e.get('type') == 'assistant'}
        if models != {MODELS[family]}: raise ValueError('CLAUDE_MODEL_MISMATCH')
        init=next(e for e in events if e.get('type')=='system' and e.get('subtype')=='init')
        expected_tools = ([] if retrieval_runtime is None else
            ['mcp__'+retrieval.SERVER+'__'+name for name in retrieval.TOOLS])
        expected_servers = ([] if retrieval_runtime is None else
            [{'name':retrieval.SERVER,'status':'connected'}])
        permitted_tool_sets = [sorted(expected_tools)]
        if selected_output is not None:
            permitted_tool_sets.append(sorted(expected_tools + ['StructuredOutput']))
        if (not isinstance(init.get('tools'), list) or
                sorted(init['tools']) not in permitted_tool_sets or
                init.get('mcp_servers') != expected_servers or init.get('permissionMode') != 'dontAsk'):
            raise ValueError('REVIEW_TOOL_CONFIGURATION_CHANGED')
        receipt['effective_tools']=init['tools'];receipt['effective_mcp_servers']=expected_servers;receipt['permission_mode']='dontAsk'
        if selected_output is not None:
            provider_output = scientific_output.claude_value(final, selected_output)
            answer = scientific_output.project(provider_output, selected_output)
        else:
            answer = final['result']
        receipt.update(actual_model=MODELS[family], session_id=final['session_id'],
                  usage=final.get('usage'), reported_total_cost_usd=final.get('total_cost_usd'))
    else:
        completed = [e for e in events if e.get('type') == 'turn.completed']
        if not completed: raise ValueError('ASTRA_TURN_NOT_COMPLETE')
        answers = [e['item']['text'] for e in events if e.get('type') == 'item.completed'
                   and e.get('item', {}).get('type') == 'agent_message']
        if not answers: raise ValueError('ASTRA_RESPONSE_MISSING')
        answer = answers[-1]
        if selected_output is not None:
            provider_output = scientific_output.loads(answer)
            answer = scientific_output.project(provider_output, selected_output)
        receipt.update(session_id=next(e['thread_id'] for e in events if e.get('type') == 'thread.started'),
                       usage=completed[-1].get('usage'),
                       model_evidence='Requested model bound in command; resolved model not independently reported by this protocol')
    retrieval_view = events
    if selected_output is not None:
        provider_raw = scientific_output.encoded(provider_output)
        immutable(folder/(stage+'.provider-output.json'), provider_raw)
        receipt['artifact_projection'] = {
            'profile': scientific_output.PROFILE,
            'kind': selected_output['kind'],
            'schema_sha256': selected_output['schema_sha256'],
            'contract_sha256': sha(encoded(selected_output)),
            'provider_output_sha256': sha(provider_raw),
            'projected_answer_sha256': sha(answer.encode()),
            'original_protocol_preserved': True,
            'provider_field_representation': 'CANONICAL_STRUCTURED_FIELD_NOT_RAW_STDOUT'}
        if family == 'claude':
            retrieval_view, proof = scientific_output.retrieval_events(events, selected_output, provider_output,
                evidence_enabled=retrieval_runtime is not None)
            receipt['structured_output_emission'] = proof
    if retrieval_runtime is not None:
        delivered = retrieval.verify(retrieval_runtime, retrieval_view, family)
        immutable(folder/(stage+'.evidence-delivery.json'), encoded(delivered))
        receipt['scientific_evidence_delivery_sha256'] = sha(encoded(delivered))
        receipt['scientific_evidence_capture'] = retrieval_runtime['descriptor']
    if not answer.strip(): raise ValueError('EMPTY_MODEL_RESPONSE')
    receipt['answer_sha256'] = sha(answer.encode())
    scan(stage+'.md', answer.encode())
    immutable(folder/(stage+'.md'), answer.encode()); immutable(folder/(stage+'.receipt.json'), encoded(receipt))
    return answer, receipt


def verified_jobs(controller,outputs,job_ids=None):
    rows=[sanitized(row) for row in controller.status()['jobs']];events={}
    if job_ids is not None:rows=[row for row in rows if row['job_id'] in job_ids]
    for row in rows:
        if row['status'] not in ('COMPLETE','FAILED'):continue
        attempt_id=identifier(row['attempt_id'])
        event=json.loads(controller.db.execute('SELECT payload FROM events WHERE id=?',(attempt_id,)).fetchone()[0])
        request=json.loads(controller.db.execute('SELECT request FROM linux_attempts WHERE id=?',(attempt_id,)).fetchone()[0])
        validate_receipt(event,request);folder=Path(outputs)/attempt_id
        if folder.is_symlink():raise ValueError('ATTEMPT_SYMLINK')
        if event['status']=='COMPLETE':
            p=folder/'synthetic-result.txt'
            if p.is_symlink() or p.read_bytes()!=PAYLOAD:raise ValueError('ARTIFACT_CHANGED')
        for name,h in event['console_sha256'].items():
            p=folder/name
            if p.is_symlink() or sha(p.read_bytes())!=h:raise ValueError('CONSOLE_CHANGED')
        events[attempt_id]=event
    return rows,events


def select_next(answer,expected):
    decision=json.loads(answer)
    if set(decision)!={'task_id','reason'} or decision['task_id']!=expected or not isinstance(decision['reason'],str) or len(decision['reason'])>1000:
        raise ValueError('INELIGIBLE_SELECTION')
    scan('selection.json',encoded(decision));return decision


def controller_snapshot(state):
    """Read a consistent private snapshot under the controller UID, never root WAL."""
    tables=('jobs','events','inbox','linux_attempts','wakes')
    script = ('import sqlite3,sys,json;'
              'source=sqlite3.connect(sys.argv[1],uri=True);'
              'source.execute("BEGIN");'
              'json.dump({table:source.execute("SELECT * FROM "+table).fetchall() '
              'for table in '+repr(tables)+'},sys.stdout);source.close()')
    result = subprocess.run(['runuser','-u','research-controller','--',
        'env','-i','PATH=/usr/bin:/bin','python3','-c',script,
        (Path(state)/'jobs.sqlite').resolve().as_uri()+'?mode=ro'],
        check=True,capture_output=True,timeout=30)
    if len(result.stdout)>16*1024*1024:raise ValueError('CONTROLLER_SNAPSHOT_TOO_LARGE')
    data=json.loads(result.stdout)
    if set(data)!=set(tables):raise ValueError('CONTROLLER_SNAPSHOT_SCHEMA')
    controller=Controller(':memory:')
    for table in tables:
        columns=list(controller.db.execute('PRAGMA table_info('+table+')'))
        controller.db.executemany('INSERT INTO '+table+' VALUES ('+','.join('?' for _ in columns)+')',data[table])
    controller.db.execute('PRAGMA query_only=ON')
    return controller


def run(root, source, state, outputs, destination, job, day, execution_root=None, next_job=None):
    if os.getuid() != 0: raise ValueError('SUPERVISED_SETUP_TRANSPORT_REQUIRED')
    os.umask(0o077); root = checked_source(root, source)
    destination = private_root(destination)
    controller = controller_snapshot(state)
    with lock(destination/'driver.lock'):
        rows,verified_events = verified_jobs(controller,outputs)
        identifier(job)
        row = next(r for r in rows if r['job_id'] == job)
        if row['kind'] != 'synthetic_success' or row['status'] != 'COMPLETE': raise ValueError('SUCCESSFUL_SYNTHETIC_REQUIRED')
        identifier(row['attempt_id'])
        event_row = controller.db.execute('SELECT payload FROM events WHERE id=?', (row['attempt_id'],)).fetchone()
        if not event_row: raise ValueError('COMPLETION_EVENT_REQUIRED')
        event = json.loads(event_row[0])
        request = controller.db.execute('SELECT request FROM linux_attempts WHERE id=?', (row['attempt_id'],)).fetchone()
        if not request: raise ValueError('BOUND_REQUEST_REQUIRED')
        validate_receipt(event, json.loads(request[0]))
        attempt = Path(outputs)/row['attempt_id']
        if attempt.is_symlink() or (attempt/'synthetic-result.txt').is_symlink() or (attempt/'synthetic-result.txt').read_bytes() != PAYLOAD:
            raise ValueError('SYNTHETIC_ARTIFACT_CHANGED')
        for name, expected in event['console_sha256'].items():
            p = attempt/name
            if p.is_symlink() or sha(p.read_bytes()) != expected: raise ValueError('CONSOLE_CHANGED')
        # Model context contains hash-bound receipts, never original console bytes.
        binding = {'source': source, 'execution_source': row['source'], 'event': row['attempt_id'],
                   'next_job': next_job, 'event_sha256': sha(encoded(event)), 'authority': 'OPERATOR_SUPERVISED_THREE_CALL_ACCEPTANCE', 'day': day}
        folder = destination/row['attempt_id']
        if not claim(folder, binding): return json.loads((folder/'complete.json').read_text())
        queue=None;review_claim=None;report=None
        try:
            config = {}
            for unit in ('research-system-controller.service', 'research-system-worker.service'):
                raw = subprocess.check_output(['systemctl', 'show', unit, '--property=User,PrivateNetwork,ProtectSystem,ProtectHome,NoNewPrivileges,MemoryMax,CPUQuotaPerSecUSec,LoadState,ActiveState,SubState,CapabilityBoundingSet,PrivateDevices,ProtectKernelTunables'], text=True)
                config[unit] = dict(line.split('=', 1) for line in raw.splitlines() if '=' in line)
            packet = checked_packet(root, rows, event, config, execution_root, verified_events)
            packet['decision_inbox']=controller.inbox()
            packet['wakes']=[dict(r) for r in controller.db.execute('SELECT * FROM wakes ORDER BY id')]
            immutable(folder/'packet.json', encoded(packet))
            if next_job:
                identifier(next_job)
                if controller.db.execute('SELECT 1 FROM jobs WHERE id=?',(next_job,)).fetchone():raise ValueError('NEXT_JOB_ALREADY_EXISTS_RECONCILE')
                immutable(folder/'eligible-next-task.json',encoded({'job':next_job,'source':row['source'],'kind':'synthetic_success','backend':'linux','depends_on_event':row['attempt_id'],'maximum_dispatches':1}))
                continuation,_=model_call(folder,'continuation','astra',
                    'The predecessor just completed. Select the only eligible bounded synthetic Linux task '+next_job+'. Colab is unavailable; scientific tasks remain gated. Return exactly {"task_id":"'+next_job+'","reason":"brief rationale"}. The system will validate and execute this selection; you have no shell authority.\n'+json.dumps(packet),output_format='json')
                selection=select_next(continuation,next_job);immutable(folder/'selection.json',encoded(selection))
                subprocess.run(['runuser','-u','research-controller','--','env','GIT_OPTIONAL_LOCKS=0','python3','-B','-m','orchestrator.remote_supervisor','submit','--state',str(state),'--source',row['source'],'--job',next_job],cwd=root,check=True,capture_output=True,timeout=30)
                deadline=time.monotonic()+240
                while True:
                    controller.db.close();controller=controller_snapshot(state)
                    result=controller.get(next_job)
                    if result['status'] in ('COMPLETE','FAILED','BLOCKED'):break
                    if time.monotonic()>deadline:raise ValueError('NEXT_JOB_UNCERTAIN_RECONCILE_NO_RETRY')
                    time.sleep(2)
                rows,verified_events=verified_jobs(controller,outputs)
                packet=checked_packet(root,rows,event,config,execution_root,verified_events)
                packet['executed_selection']=selection
                packet['decision_inbox']=controller.inbox()
                packet['wakes']=[dict(r) for r in controller.db.execute('SELECT * FROM wakes ORDER BY id')]
                immutable(folder/'post-execution-packet.json',encoded(packet))
            else:
                continuation, _ = model_call(folder, 'continuation', 'astra',
                    'A durable synthetic completion triggered this bounded investigator turn. Assess actual completion, failure, blocked work and next eligible action; no dispatch.\n'+json.dumps(packet))
            report = finalize(folder/'reports', source, day, rows)
            queue = Queue(folder/'reports'); review_claim = queue.claim(report['id'])
            if review_claim is None: raise ValueError('REVIEW_CLAIM_UNAVAILABLE')
            immutable(folder/'review-claim.json',encoded(review_claim))
            body = (folder/'reports'/(report['id']+'.md')).read_text()
            review, receipt = model_call(folder, 'review', 'claude',
                'Fresh cross-family operational review. Inspect supplied implementation, deployed properties and primary receipt evidence, not just Astra prose. Identify concrete defects and acceptance gaps. This is not main merge approval.\n'+json.dumps(packet)+'\nASTRA:\n'+continuation+'\nREPORT:\n'+body)
            queue.attach(report['id'], review_claim['attempt_id'], review, {
                'family': 'claude', 'model': receipt['actual_model'], 'source': source,
                'report_sha256': report['id'], 'review_sha256': sha(review.encode()),
                'execution_receipt_sha256': sha(encoded(receipt)), 'session_id': receipt['session_id'], 'status': 'COMPLETE'})
            response, _ = model_call(folder, 'disposition', 'astra',
                'Record agreement/disagreement with reasons and one next action through this system disposition. Do not execute actions or claim unavailable acceptance.\n'+json.dumps(packet)+'\nREPORT:\n'+body+'\nCLAUDE REVIEW:\n'+review)
            queue.disposition(report['id'], response)
            result = {'status': 'COMPLETE', **binding, 'report': report['id'], 'real_model_calls': 3,
                      'patient_execution': False, 'unattended_activation': False, 'executed_next_job':next_job}
            immutable(folder/'complete.json', encoded(result))
            return result
        except BaseException:
            if queue is not None and review_claim is not None and queue.status(report['id'])['status']=='REVIEWING':
                queue.unavailable(report['id'],review_claim['attempt_id'],'MODEL_CALL_FAILED_RECONCILE_NO_AUTOMATIC_RETRY')
            immutable(folder/'blocked.json', encoded({'status': 'BLOCKED', 'reason': 'INSPECT_PRIVATE_EVIDENCE_NO_AUTOMATIC_RETRY'}))
            raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('root', 'source', 'state', 'outputs', 'destination', 'job', 'day'): p.add_argument('--'+name, required=True)
    p.add_argument('--execution-root');p.add_argument('--next-job')
    a = p.parse_args(); print(json.dumps(run(**vars(a))))

if __name__ == '__main__': main()
