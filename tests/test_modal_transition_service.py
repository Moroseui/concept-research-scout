"""Deterministic service-lifecycle and pre-admission recovery checks. No calls."""
import copy
import json
from pathlib import Path
import sqlite3
import pytest
from tools import modal_transition_service as service
from tools import modal_pre_admission_recovery as recovery
from orchestrator import manual_host_guard as host, modal_driver, private_records


def put(path, value):
    private_records.write_text(path, json.dumps(value))


def test_long_call_returns_before_second_admission_and_new_invocation_is_required(tmp_path, monkeypatch):
    state=tmp_path/'lane';private_records.mkdir(state)
    config=tmp_path/'runtime.json';profile=tmp_path/'profile';proof=tmp_path/'proof.json'
    private_records.write_text(config,'{}');private_records.write_text(profile,'synthetic profile')
    monkeypatch.setattr(host,'trusted',lambda p:Path(p))  # ownership is separately live-verified
    monkeypatch.setenv('RESEARCH_MANUAL_RUNTIME_CONFIG',str(config))
    monkeypatch.setenv('INVOCATION_ID','first');clock=[1000.0]
    monkeypatch.setattr(host.time,'time',lambda:clock[0])
    def renew(invocation):
        monkeypatch.setenv('INVOCATION_ID',invocation)
        put(proof,{'invocation':invocation,'runtime_sha256':host.iso.sha(config),'status':'PASS',
                   'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'time':clock[0],
                   'profile_sha256':host.iso.sha(profile),'loaded':'bwrap (unconfined)','global_userns_restriction':'1'})
    guard={'receipt':str(proof),'profile':str(profile)};admissions=[]
    class Driver:
        def advance(self):
            host.proof(guard);admissions.append(len(admissions)+1);clock[0]+=321
            return {'phase':'run_spec_review' if len(admissions)==1 else 'COMMIT_SPEC'}
    renew('first')
    assert service.advance_once(state,factory=lambda _:Driver())['phase']=='run_spec_review'
    assert admissions==[1]
    with pytest.raises(ValueError,match='^HOST_PROOF_EXPIRED$'):service.advance_once(state,factory=lambda _:Driver())
    assert admissions==[1]
    renew('second')
    assert service.advance_once(state,factory=lambda _:Driver())['phase']=='COMMIT_SPEC'
    assert admissions==[1,2]


def test_supervisor_preserves_expiry_housekeeping_and_uncertain_call_block(tmp_path, monkeypatch):
    prep=tmp_path/'preparation';state=tmp_path/'lane';private_records.mkdir(prep);private_records.mkdir(state)
    put(prep/'runtime.json',{'asset_expires_utc':'2000-01-01T00:00:00+00:00'});put(state/'lane.json',{})
    class Driver:
        def status(self):return {'calls':[{'status':'UNCERTAIN'}]}
    def forbidden(*a,**k):pytest.fail('no call, provider construction or transition')
    assert modal_driver.supervise(state,prep,factory=lambda _:Driver(),provider_factory=forbidden,run=service.advance_once)['status']=='ASSET_CLEANUP_BLOCKED_BY_UNCERTAIN_CALL'
    class Complete:
        def status(self):return {'calls':[{'status':'COMPLETE'}]}
    from orchestrator import modal_cleanup
    monkeypatch.setattr(modal_cleanup,'clear_copies',lambda *a:{'status':'CLEARED','synthetic':True})
    assert modal_driver.supervise(state,prep,factory=lambda _:Complete(),provider_factory=lambda _:object(),run=forbidden)['status']=='CLEARED'


@pytest.fixture
def recovery_case(tmp_path,monkeypatch):
    private_records.mkdir(tmp_path,exist_ok=True)
    root=tmp_path/'release';state=root/'lane';private_records.mkdir(state,parents=True)
    source=root/'repository';private_records.mkdir(source)
    spec=root/'lane-scientific-workspaces/run_spec_author-1/SPEC.proposed.md'
    private_records.write_bytes(spec,b'Synthetic completed spec')
    owner=root/'owner.json';put(owner,{'owner':'same run'})
    config={'run_id':'synthetic-run','source':'a'*40,'root':str(source),'owner_path':str(owner),
            'owner_binding':{'owner':'same run'},'engine_files':{},'scientific_files':{},'profile_files':{}}
    value={'phase':'BLOCKED','blocked_stage':'run_spec_review','reason':'ValueError: HOST_PROOF_EXPIRED',
           'rounds':{'run_spec_author':1},'interventions':[],'spec':str(spec)}
    call={'id':'synthetic-author','stage':'run_spec_author','attempt':1,'status':'COMPLETE','receipt':{'outcome':'COMPLETE','units':1}}
    put(state/'lane.json',config);private_records.write_text(state/'DECISION_REQUEST.md','Original operational block.')
    db=private_records.Connection(state/'jobs.sqlite')
    db.executescript('CREATE TABLE manual_state(id INTEGER PRIMARY KEY,payload TEXT); CREATE TABLE manual_calls(id TEXT,stage TEXT,attempt INTEGER,status TEXT,receipt TEXT); CREATE TABLE manual_account(id INTEGER,value TEXT);')
    db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps(value),));db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',(call['id'],call['stage'],1,'COMPLETE',json.dumps(call['receipt'])))
    db.execute('INSERT INTO manual_account VALUES(1,?)',('allowance must remain unchanged',));db.commit();db.close()
    binding={'run_id':config['run_id'],'source':config['source'],'call_id':call['id'],
             'output_sha256':recovery.sha(spec.read_bytes()),'state_sha256':recovery.sha(recovery.canonical(value)),
             'call_sha256':recovery.sha(recovery.canonical(call)),'config_sha256':recovery.sha((state/'lane.json').read_bytes())}
    monkeypatch.setattr(recovery,'BINDINGS',binding);monkeypatch.setattr(recovery,'ROOT',root)
    monkeypatch.setattr(recovery,'approval',lambda _: {'report_sha256':'b'*64,'source_sha':'c'*40})
    monkeypatch.setattr(recovery,'installed_entrypoint',lambda:None)
    import subprocess
    monkeypatch.setattr(subprocess,'check_output',lambda *a,**k:'inactive\n')
    return state,config,value,call,spec


def test_reconcile_once_preserves_originals_calls_allowance_and_source(recovery_case):
    state,config,value,call,spec=recovery_case
    original_config=(state/'lane.json').read_bytes();original_decision=(state/'DECISION_REQUEST.md').read_bytes()
    db=sqlite3.connect(state/'jobs.sqlite');before=recovery.table_rows(db);db.close()
    assert recovery.apply(state,'synthetic-approval')['calls_used']==1
    db=sqlite3.connect(state/'jobs.sqlite');after=json.loads(db.execute('SELECT payload FROM manual_state').fetchone()[0])
    assert after['phase']=='run_spec_review' and after['rounds']==value['rounds'] and after['reason'] is None
    assert recovery.table_rows(db)==before;db.close()
    assert (state/'lane.json').read_bytes()==original_config
    assert (state/'DECISION_REQUEST.md').read_bytes()==original_decision
    saved=state/'host-proof-reconciliation-20261003'
    db=sqlite3.connect(saved/'before.sqlite');assert json.loads(db.execute('SELECT payload FROM manual_state').fetchone()[0])==value;db.close()
    assert (saved/'DECISION_REQUEST.original.md').read_bytes()==original_decision
    assert after['interventions'][0]['additional_calls']==0
    with pytest.raises(ValueError,match='^RECONCILIATION_ALREADY_PREPARED_INSPECT_NO_RETRY$'):recovery.apply(state,'synthetic-approval')
    private_records.check_tree(saved)


@pytest.mark.parametrize('defect,code',[
 ('run','EXACT_M3_RUN_REQUIRED'),('source','EXACT_M3_RUN_REQUIRED'),('pending','EXACT_PRE_ADMISSION_BLOCK_REQUIRED'),
 ('reason','EXACT_PRE_ADMISSION_BLOCK_REQUIRED'),('phase','EXACT_PRE_ADMISSION_BLOCK_REQUIRED'),('state','ORIGINAL_STATE_CHANGED'),
 ('review-call','ONLY_COMPLETED_AUTHOR_NO_REVIEW_CALL'),('uncertain','ONLY_COMPLETED_AUTHOR_NO_REVIEW_CALL'),
 ('receipt','ORIGINAL_CALL_CHANGED'),('spec','COMPLETED_SPEC_CHANGED')])
def test_recovery_refuses_drift_or_any_reserved_review(recovery_case,defect,code):
    state,config,value,call,spec=recovery_case;calls=[copy.deepcopy(call)];body=spec.read_bytes()
    if defect in ('run','source'):config['run_id' if defect=='run' else 'source']='different'
    elif defect=='pending':value['pending']={'id':'reserved'}
    elif defect=='reason':value['reason']='some other failure'
    elif defect=='phase':value['phase']='MODEL_RUNNING'
    elif defect=='state':value['interventions'].append('changed')
    elif defect=='review-call':calls.append({**call,'stage':'run_spec_review'})
    elif defect=='uncertain':calls[0]['status']='UNCERTAIN'
    elif defect=='receipt':calls[0]['receipt']['units']=0
    elif defect=='spec':body+=b' changed'
    with pytest.raises(ValueError,match='^'+code+'$'):recovery.validate(config,value,calls,body)


def test_config_drift_and_halt_refuse_before_write(recovery_case):
    state,*_=recovery_case
    private_records.write_text(state/'HALT','Stop')
    with pytest.raises(ValueError,match='^HALT_REMAINS_EFFECTIVE$'):recovery.apply(state,'synthetic')
    (state/'HALT').unlink();private_records.write_text(state/'lane.json','{}')
    with pytest.raises(ValueError,match='^ORIGINAL_CONFIG_CHANGED$'):recovery.apply(state,'synthetic')
    assert not (state/'host-proof-reconciliation-20261003').exists()


def test_override_changes_only_execstart_and_uses_original_state():
    from tools import install_modal_transition as install
    body=install.render(Path('/reviewed/version/modal_transition_service.py')).decode()
    assert body.splitlines()==['[Service]','ExecStart=', 'ExecStart=/usr/bin/python3 -B /reviewed/version/modal_transition_service.py --state '+str(recovery.ROOT/'lane')+' --preparation '+str(recovery.ROOT/'modal-preparation')]
    assert not any(k in body for k in ['ExecStartPre','Environment=','ReadWritePaths','User=','Group='])


@pytest.mark.parametrize('defect,code', [('verdict','FOCUSED_APPROVAL_REQUIRED'),('scope','FOCUSED_APPROVAL_REQUIRED'),('helper','REVIEWED_HELPER_BYTES_REQUIRED')])
def test_genuine_qualification_and_helper_bindings_are_required(tmp_path,monkeypatch,defect,code):
    result={'verdict':'APPROVE','change_id':recovery.CHANGE}
    source={ 'tools/'+name:recovery.sha(Path(recovery.__file__).with_name(name).read_bytes()) for name in ['modal_transition_service.py','modal_pre_admission_recovery.py']}
    if defect=='verdict':result['verdict']='CHANGES REQUIRED'
    elif defect=='scope':result['change_id']='unrelated'
    else:source['tools/modal_transition_service.py']='0'*64
    monkeypatch.setattr(recovery,'verify_result',lambda _:result)
    put(tmp_path/'packet-manifest.json',{'source_files':source})
    with pytest.raises(ValueError,match='^'+code+'$'):recovery.approval(tmp_path)


def test_refused_native_qualification_cannot_be_substituted(tmp_path,monkeypatch):
    def refuse(_):raise ValueError('NATIVE_STREAM_CHANGED')
    monkeypatch.setattr(recovery,'verify_result',refuse)
    with pytest.raises(ValueError,match='^NATIVE_STREAM_CHANGED$'):recovery.approval(tmp_path)
