"""Synthetic API observations; no remote objects, patient data, or GPU usage."""
import hashlib,json
from types import SimpleNamespace as NS
import pytest
from orchestrator.modal_fit_progress import encoded
from orchestrator.modal_fit_provider import terminal_checkpoint
from orchestrator.modal_executor import canonical


class Volume:
    object_id='vo-progress'
    def __init__(self,files):self.files=files;self.hydrated=0;self.reads=[]
    def hydrate(self,**kw):self.hydrated+=1
    def listdir(self,path,recursive=False):
        names=[path] if path in self.files else [p for p in self.files if p.startswith(path+'/') and '/' not in p[len(path)+1:]]
        return [NS(path=p.lstrip('/'),size=len(self.files[p]),type=NS(name='FILE')) for p in names]
    def read_file(self,path):
        self.reads.append(path)
        if path not in self.files:raise FileNotFoundError(path)
        data=self.files[path];yield data[:3];yield data[3:]


@pytest.fixture
def connection():
    fit={'run_id':'run','arm':'A1','fold':0,'realization':'one','spec_sha256':'a'*64,'code_sha256':'b'*64,
         'input_contract_sha256':'c'*64,'environment_sha256':'d'*64,'plans_sha256':'e'*64}
    data=b'synthetic checkpoint bytes';token='a'*32
    record={'schema':'modal-fit-object/v1','key':'latest','binding_sha256':hashlib.sha256(encoded(fit)).hexdigest(),
            'object':token,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),
            'metadata':{'next_epoch':2,'total_epochs':5,'native_version':'2.8.1'},'at_utc':'synthetic'}
    files={'/fits/fit/identity.json':encoded({'schema':'modal-fit/v1','binding':fit}),
           '/fits/fit/latest.json':encoded(record),'/fits/fit/objects/'+token+'/record.json':encoded(record),
           '/fits/fit/objects/'+token+'/data':data}
    volume=Volume(files);lookups=[]
    def lookup(name,**kw):
        lookups.append((name,kw));assert kw['version']==2 and kw['create_if_missing'] is False
        return volume
    sandbox=NS(object_id='sb-same',poll=lambda:137)
    provider=NS(client='synthetic-client',_sandbox=lambda ident:sandbox,modal=NS(Volume=NS(from_name=lookup)))
    binding={'run_id':'run','spec_sha256':'a'*64,'code_sha256':'b'*64,'experiment':{'fit_id':'fit'},'progress':{'volume_id':'vo-progress','volume_name':'fit-progress','fit_id':'fit','fit_binding':fit}}
    return provider,binding,volume,sandbox,lookups


def test_positive_terminal_and_remote_hashes_are_not_themselves_resume_permission(connection):
    provider,binding,volume,sandbox,lookups=connection
    receipt=terminal_checkpoint(provider,'sb-same',binding)
    assert receipt['terminal_exit_code']==137 and receipt['checkpoint_record']['metadata']['next_epoch']==2
    assert receipt['binding_sha256']==hashlib.sha256(canonical(binding)).hexdigest()
    assert receipt['may_launch'] is False and receipt['termination_cause']=='not inferred from exit code'
    assert lookups==[('fit-progress',{'version':2,'create_if_missing':False,'client':'synthetic-client'})]
    assert all(p.startswith('/fits/fit/') for p in volume.reads)


@pytest.mark.parametrize('cause',['running','timeout','wrong_id','missing_checkpoint','hash','identity','volume','epoch'])
def test_uncertain_or_changed_evidence_never_qualifies(connection,cause):
    provider,binding,volume,sandbox,_=connection
    if cause=='running':sandbox.poll=lambda:None
    if cause=='timeout':
        def timeout():raise TimeoutError('synthetic observation failure')
        sandbox.poll=timeout
    if cause=='wrong_id':sandbox.object_id='sb-other'
    if cause=='missing_checkpoint':del volume.files['/fits/fit/latest.json']
    if cause=='hash':volume.files['/fits/fit/objects/'+'a'*32+'/data']=b'altered'
    if cause=='identity':binding['progress']['fit_binding']['realization']='two'
    if cause=='volume':volume.object_id='vo-other'
    if cause=='epoch':
        rec=json.loads(volume.files['/fits/fit/latest.json']);rec['metadata']['next_epoch']=6
        for path in ['/fits/fit/latest.json','/fits/fit/objects/'+'a'*32+'/record.json']:volume.files[path]=encoded(rec)
    with pytest.raises((ValueError,TimeoutError,FileNotFoundError)):terminal_checkpoint(provider,'sb-same',binding)


def test_changed_second_process_observation_refuses(connection):
    provider,binding,volume,sandbox,_=connection
    values=iter([137,None]);sandbox.poll=lambda:next(values)
    with pytest.raises(ValueError,match='MODAL_FIT_OBSERVATION_CHANGED'):terminal_checkpoint(provider,'sb-same',binding)


def test_final_checkpoint_has_validation_only_meaning(connection):
    provider,binding,volume,sandbox,_=connection
    rec=json.loads(volume.files['/fits/fit/latest.json']);rec['key']='final';rec['metadata']['next_epoch']=5
    volume.files['/fits/fit/final.json']=encoded(rec);volume.files['/fits/fit/objects/'+'a'*32+'/record.json']=encoded(rec)
    receipt=terminal_checkpoint(provider,'sb-same',binding)
    assert receipt['mode']=='validation-only' and receipt['may_launch'] is False


def test_real_provider_reader_and_existing_ledger_link_one_resume(connection,tmp_path):
    from copy import deepcopy
    from orchestrator.modal_provider import ModalProvider
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator.modal_budget import ComputeAccounts
    from orchestrator import modal_item4_budget as budget
    from orchestrator import private_records
    from orchestrator.modal_billing import canonical as billing_canonical
    from datetime import datetime,timezone
    fake,binding,volume,sandbox,_=connection
    provider=object.__new__(ModalProvider);provider.__dict__.update(fake.__dict__)
    now=datetime(2026,10,6,2,30,tzinfo=timezone.utc)
    rates={'gpu_hour_cost_a100_80gb':'2.5','cpu_hour_cost_sandbox':'.1419','mem_gib_hour_cost_sandbox':'.024'}
    body={'schema':'modal-billing-snapshot/v1','workspace':'moroseui','observed_at':now.isoformat(),
          'rates':rates,'rows':[],'summary':{'metered_cost':'0','billed_cost':'0','adjustments':{}}}
    snap={**body,'sha256':hashlib.sha256(billing_canonical(body)).hexdigest()}
    batch=BatchAccounts(tmp_path/'ledger');batch.register_run('run',{'backlog_item':4,'experiment_authority_sha256':budget.AUTHORITY})
    accounts=ComputeAccounts(batch)
    binding.update(spec_sha256='a'*64,code_sha256='b'*64,
                   resources={'gpu':'A100-80GB','cpu':4,'memory_mib':8192,'timeout_seconds':60},overhead_micro_usd=0)
    binding['cost']=budget.quote(binding['resources'],rates,0)
    binding['experiment'].update(backlog_item=4,authority_sha256=budget.AUTHORITY,team_authority_sha256=budget.TEAM_AUTHORITY,
                                 stage='SMOKE',segment=1,billing_object_id='ap-fit')
    ident=hashlib.sha256(canonical(binding)).hexdigest()
    accounts.reserve_item4(ident,'run',binding,billing_snapshot=snap,now=now)
    accounts.observe(ident,'CREATED','sb-same');accounts.observe(ident,'RUNNING','sb-same')
    old=dict(batch.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone())
    reason=tmp_path/'reason.json'
    private_records.write_bytes(reason,encoded({'schema':'modal-interruption-cause/v1','segment_id':ident,'provider_id':'sb-same',
          'reason':'PROVIDER_LIMIT','evidence':{'synthetic_provider_limit_event':True}}))
    receipt=accounts.record_item4_interruption(ident,provider,reason_record=reason)
    reads=list(volume.reads)
    assert accounts.record_item4_interruption(ident,provider,reason_record=reason)==receipt
    assert volume.reads==reads
    saved=batch.db.execute('SELECT payload FROM events WHERE id=?',(ident+':fit-interruption',)).fetchone()[0]
    new=deepcopy(binding);new['experiment']['segment']=2
    new['resume']={'previous_segment_id':ident,'terminal_receipt_sha256':hashlib.sha256(saved.encode()).hexdigest(),
                   'checkpoint_record_sha256':receipt['proof']['checkpoint_record_sha256']}
    new_id=hashlib.sha256(canonical(new)).hexdigest()
    assert accounts.reserve_item4(new_id,'run',new,billing_snapshot=snap,now=now)
    assert not accounts.reserve_item4(new_id,'run',new,billing_snapshot=snap,now=now)
    preserved=dict(batch.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone())
    assert preserved=={**old,'status':'ACCOUNTED'}
    assert batch.db.execute('SELECT sum(reserved_micro_usd) FROM autonomy_compute').fetchone()[0]==2*old['reserved_micro_usd']
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
    altered=deepcopy(new);altered['experiment']['segment']=3
    with pytest.raises(ValueError,match='ITEM4_RESUME_TERMINAL_PROOF_REQUIRED'):
        accounts.reserve_item4(hashlib.sha256(canonical(altered)).hexdigest(),'run',altered,billing_snapshot=snap,now=now)


@pytest.mark.parametrize('field',['spec_sha256','code_sha256'])
def test_provider_refuses_checkpoint_for_different_reviewed_input(connection,field):
    provider,binding,*_=connection
    binding[field]='f'*64
    with pytest.raises(ValueError,match='^MODAL_FIT_SCIENTIFIC_BINDING_CHANGED$'):
        terminal_checkpoint(provider,'sb-same',binding)


def test_provider_uses_worker_identity_contract(connection):
    provider,binding,*_=connection
    binding['progress']['fit_binding']['fold']=-1
    with pytest.raises(ValueError,match='^FIT_FOLD$'):
        terminal_checkpoint(provider,'sb-same',binding)
