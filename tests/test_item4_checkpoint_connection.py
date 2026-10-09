"""Synthetic checkpoint records; real exact historical checks and resume validation."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import item4_checkpoint_connection as helper
from orchestrator import item4_private_staging_retry as staging
from orchestrator import preprocessing_recovery as recovery, preprocessing_continuation as native
from orchestrator.preprocessing_checkpoints import hash_value
from orchestrator import private_records as pr
from test_item4_staging_retry import setup as historical_setup
from test_item4_preprocessing_fresh_start import setup as first_setup

@pytest.fixture
def setup(historical_setup,tmp_path,monkeypatch):
    prior,db=historical_setup
    row={'id':prior['new_compute_id'],'run':prior['old_row']['run'],
        'binding':helper.encoded(prior['new_binding']).decode(),'status':'RUNNING',
        'reserved_micro_usd':10_342_400,'provider_id':'sb-synthetic',
        'actual_micro_usd':None,'month':'2026-10'}
    snap={'schema':'preprocessing-steps/v1','binding_sha256':row['id'],
        'steps':{'synthetic'+str(i):{'record_sha256':'a'*64,'files':{}} for i in range(92)}}
    proof={'schema':'preprocessing-terminal-proof/v1','provider_id':row['provider_id'],
        'binding_sha256':row['id'],'terminal_exit_code':124,
        'volume_id':prior['new_binding']['preprocessing_output_volume_id'],
        'snapshot':snap,'steps_record_sha256':hash_value(snap),'observed_at':'synthetic timestamp','may_launch':False}
    original=tmp_path/'original';pr.write_bytes(original,b'synthetic original submission')
    saved={'row':row,'initial_binding':prior['new_initial_binding'],'runtime':prior['new_runtime'],
        'terminal_proof':proof,'originals':{str(original):{'sha256':helper.sha(original.read_bytes()),'text':original.read_text()}}}
    observation=tmp_path/'observation.json';pr.write_bytes(observation,helper.encoded(saved))
    cfg={'schema':'fixed-preprocessing-checkpoint-connection/v1',
        'observation':{'path':str(observation),'sha256':helper.sha(observation.read_bytes())},
        'current_id':row['id'],'current_job':prior['new_job'],'provider_id':row['provider_id'],
        'terminal_exit_code':124,'steps_record_sha256':proof['steps_record_sha256'],'completed_steps':92}
    root=tmp_path/'root';pr.mkdir(root/'docs',parents=True)
    pr.write_bytes(root/'docs/ITEM4_CHECKPOINT_CONNECTION.json',helper.encoded(cfg))
    monkeypatch.setattr(helper,'ROOT',root);monkeypatch.setattr(helper,'CONTRACT_SHA',hash_value(cfg))
    monkeypatch.setattr(helper,'authority',lambda:{'verdict':'APPROVE','label':'synthetic authority'})
    accounted={**row,'status':'ACCOUNTED'}
    db.execute('INSERT INTO autonomy_compute VALUES(?,?,?,?,?,?,?,?)',tuple(accounted[k] for k in ['id','run','binding','status','reserved_micro_usd','provider_id','actual_micro_usd','month']))
    event={'kind':'PREPROCESSING_INTERRUPTED_WITH_COMMITTED_STEPS','proof':proof,
        'resume_reason':'LIFETIME_TIMEOUT','reason_record_sha256':'b'*64,'prior_status':'RUNNING',
        'prior_reserved_micro_usd':row['reserved_micro_usd'],'charge_disposition':'synthetic original'}
    raw=helper.encoded(event).decode()
    db.execute('INSERT INTO events VALUES(?,?,?)',(row['id']+':preprocessing-interruption',row['run'],raw));db.commit()
    binding=copy.deepcopy(prior['new_binding']);binding['experiment']['segment']=2
    binding['resume']={'previous_segment_id':row['id'],'terminal_receipt_sha256':helper.sha(raw.encode()),
        'steps_record_sha256':proof['steps_record_sha256']}
    return cfg,saved,prior,db,binding,observation,original

def pairs(db):
    return [(r,json.loads(r['binding'])) for r in db.execute('SELECT * FROM autonomy_compute')]

def test_exact_historical_attempts_do_not_become_scientific_segments_or_lose_charges(setup):
    cfg,saved,prior,db,binding,*_=setup
    assert helper.contract()==(cfg,saved,prior)
    before=[dict(r) for r,_ in pairs(db)];changes=db.total_changes
    selected=helper.predecessors(NS(db=db),pairs(db),binding)
    assert len(selected)==1 and selected[0][0]['id']==cfg['current_id']
    assert [dict(r) for r,_ in pairs(db)]==before and db.total_changes==changes
    assert sum(r['reserved_micro_usd'] for r,_ in pairs(db))==31_027_200
    recovery.validate_reservation(db,*selected[0],binding)

@pytest.mark.parametrize('damage',['current-live','historical-live','historical-charge','historical-event',
    'missing','extra','input','science','image','resources','full','third-segment','resume','terminal','observation','original'])
def test_every_unqualified_or_changed_predecessor_refuses_without_accounting_change(setup,damage):
    cfg,saved,prior,db,binding,observation,original=setup
    if damage=='current-live':db.execute("UPDATE autonomy_compute SET status='RUNNING' WHERE id=?",(cfg['current_id'],))
    if damage=='historical-live':db.execute("UPDATE autonomy_compute SET status='UNCERTAIN' WHERE id=?",(prior['old_row']['id'],))
    if damage=='historical-charge':db.execute("UPDATE autonomy_compute SET reserved_micro_usd=1 WHERE id=?",(prior['old_row']['id'],))
    if damage=='historical-event':db.execute('DELETE FROM events WHERE id=?',(prior['old_row']['id']+':pre-science-stop',))
    if damage=='input':binding['source_volume_id']='vo-changed'
    if damage=='science':binding['execution']['module_sha256']='c'*64
    if damage=='image':binding['image_id']='im-changed'
    if damage=='resources':binding['resources']['cpu']=1
    if damage=='full':binding['experiment']['stage']='FULL'
    if damage=='third-segment':binding['experiment']['segment']=3
    if damage=='resume':binding['resume']['steps_record_sha256']='c'*64
    if damage=='terminal':db.execute('DELETE FROM events WHERE id=?',(cfg['current_id']+':preprocessing-interruption',))
    if damage=='observation':observation.write_bytes(b'changed')
    if damage=='original':original.write_bytes(b'changed')
    selected=pairs(db)
    if damage=='missing':selected=selected[1:]
    if damage=='extra':selected=selected+selected[:1]
    before=[dict(r) for r,_ in pairs(db)];changes=db.total_changes
    with pytest.raises(ValueError):helper.predecessors(NS(db=db),selected,binding)
    assert [dict(r) for r,_ in pairs(db)]==before and db.total_changes==changes

def test_fixed_replacements_precede_actual_native_continuation_and_preserve_history(setup,monkeypatch):
    cfg,saved,prior,db,binding,*_=setup
    job={'job':cfg['current_job'],'binding':prior['new_initial_binding'],'runtime':prior['new_runtime']}
    event=db.execute('SELECT payload FROM events WHERE id=?',(cfg['current_id']+':preprocessing-interruption',)).fetchone()[0]
    terminal={'ident':cfg['current_id'],'event_sha256':helper.sha(event.encode()),'proof':saved['terminal_proof']}
    # Terminal provider/manifest projection synthetic here; native resolve/successor are real.
    monkeypatch.setattr(native,'terminal',lambda *args:terminal)
    value={helper.KEY:{},'preprocessing_dispatch':{cfg['current_job']:{'phase':'INTERRUPTED'}},
        'preprocessing_continuations':{cfg['current_job']:[{'previous_job':cfg['current_job'],'event_sha256':terminal['event_sha256']}]}}
    before=copy.deepcopy(value);calls=[]
    def fixed(driver,initial,selected):
        assert 'preprocessing_continuations' not in initial
        calls.append('fixed')
        return {'jobs':[job],'all_jobs':['historical-first','historical-second',cfg['current_job']],'continuations':[]}
    resolved=helper.resolve(NS(),value,{},fixed,native.resolve)
    assert calls==['fixed'] and value==before
    assert resolved['jobs'][0]['binding']['experiment']['segment']==2
    assert resolved['jobs'][0]['binding']['resume']==binding['resume']
    assert set(resolved['all_jobs'])=={'historical-first','historical-second',cfg['current_job'],resolved['jobs'][0]['job']}
    assert resolved['continuations'][0]['completed_steps']==92

@pytest.mark.parametrize('chains',[{'foreign':[]},{'CURRENT':[]},{'CURRENT':[{},{}]}])
def test_chain_scope_cannot_remove_a_guard(setup,chains):
    cfg,*_=setup
    chains={cfg['current_job'] if k=='CURRENT' else k:v for k,v in chains.items()}
    with pytest.raises(ValueError):
        helper.resolve(NS(),{helper.KEY:{},'preprocessing_continuations':chains},{},
            lambda *args:pytest.fail('must refuse before prior resolver'),lambda *args:pytest.fail('must refuse before native resolver'))

@pytest.mark.parametrize('damage',['none','fresh-link','segment','resume-previous','resume-steps','science','quote'])
def test_exact_job_identity_accepts_only_the_approved_checkpoint_successor(setup,damage):
    from orchestrator.modal_executor import item4_job
    cfg,saved,prior,db,binding,*_=setup
    if damage=='fresh-link':binding['fresh_start']['terminal_event_sha256']='d'*64
    if damage=='segment':binding['experiment']['segment']=3
    if damage=='resume-previous':binding['resume']['previous_segment_id']='d'*64
    if damage=='resume-steps':binding['resume']['steps_record_sha256']='d'*64
    if damage=='science':binding['execution']['module_sha256']='d'*64
    if damage=='quote':binding['cost']['reserved_micro_usd']=1
    if damage=='none':
        assert item4_job(binding)!=cfg['current_job']
        assert item4_job(binding)==item4_job({k:v for k,v in binding.items() if k not in staging.DERIVED})
    else:
        with pytest.raises(ValueError):item4_job(binding)
