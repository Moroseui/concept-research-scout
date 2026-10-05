"""Bounded collected-only reconciliation; all provider/model effects synthetic."""
import copy,json,sqlite3
from pathlib import Path
import pytest
from orchestrator import modal_cleanup,private_records,modal_provider
from orchestrator.manual_executor import read,digest,inventory,atomic
from orchestrator.modal_executor import canonical as binding_bytes
from tools import modal_collected_recovery as recovery
from tools import install_m3_post_smoke_host as host
from test_modal_driver import modal_lane,lane,root,policy,private_copied_fixture


@pytest.fixture
def completed(modal_lane,monkeypatch):
    d,p=modal_lane
    original_collect=p.collect
    p.collect=lambda provider_id,binding,folder:{**original_collect(provider_id,binding,folder),'provider_id':provider_id}
    for _ in range(6):d.advance()
    assert d.current()['phase']=='WAIT_OUTPUTS'
    p.state='COMPLETE'
    def failed_cleanup(*a,**kw):raise KeyError('wheels_volume_id')
    monkeypatch.setattr(modal_cleanup,'clear_copies',failed_cleanup)
    assert d.advance()['phase']=='BLOCKED'
    state=d.state;config=read(state/'lane.json');value=d.current();work=state/'modal-executions'/config['run_id']
    # Synthetic driver fixture has one author/reviewer pair. The real recovery
    # requires exactly four completed calls; add two preserved synthetic records.
    for n in [3,4]:d.store.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',('synthetic-'+str(n),'run_spec_author' if n==3 else 'run_spec_review',2,'COMPLETE','{}'))
    value['rounds']={'run_spec_author':2,'run_spec_review':2};d.save(value)
    config.setdefault('scientific_files',{})
    config['owner_path']=str(state/'synthetic-owner.json');config['owner_binding']={'synthetic':True}
    atomic(config['owner_path'],config['owner_binding']);atomic(state/'lane.json',config)
    pins={'run_id':config['run_id'],'source':config['source'],'config_sha256':digest((state/'lane.json').read_bytes()),
      'state_sha256':digest(recovery.canonical(value)),'tables_sha256':digest(recovery.canonical(recovery.table_rows(d.store.db))),
      'validation_sha256':digest((state/'validation.json').read_bytes()),'collection_sha256':digest((work/'collection-receipt.json').read_bytes()),
      'provider_id':read(work/'terminated.json')['provider_id'],'compute_id':digest(binding_bytes(value['manifest']['binding']))}
    monkeypatch.setattr(recovery,'PINS',pins);monkeypatch.setattr(recovery,'ROOT',state.parent)
    monkeypatch.setattr(recovery,'approval',lambda f:{'source_sha':'a'*40,'report_sha256':'b'*64})
    monkeypatch.setattr(recovery.subprocess,'check_output',lambda *a,**k:'inactive\n')
    monkeypatch.setattr(modal_provider,'ModalProvider',lambda cfg:p)
    # Native cleanup integration is exercised separately, using actual prepare output.
    def cleanup(*args,**kwargs):
        return {'status':'CLEARED','runtime_sha256':digest(binding_bytes(config['modal']))}
    monkeypatch.setattr(modal_cleanup,'clear_copies',cleanup)
    return d,p,config


def test_recovery_preserves_calls_results_and_accounting_without_resubmission(completed):
    d,p,config=completed;before=recovery.table_rows(d.store.db);effects=list(p.calls)
    result=recovery.apply(d.state,'synthetic')
    assert result['status']=='RECONCILED' and d.current()['phase']=='WAIT_OUTPUTS'
    assert recovery.table_rows(d.store.db)==before and p.calls==effects
    assert (d.state/'collected-cleanup-reconciliation-20261003/DECISION_REQUEST.original.md').read_text()==(d.state/'DECISION_REQUEST.md').read_text()
    with pytest.raises(ValueError,match='RECOVERY_EXISTS_RECONCILE_NO_BLIND_RETRY'):recovery.apply(d.state,'synthetic')
    assert p.calls==effects and recovery.table_rows(d.store.db)==before


@pytest.mark.parametrize('damage,expected',[
 ('halt','HALT_REMAINS_EFFECTIVE'),('config','ORIGINAL_CONFIG_CHANGED'),('state','ORIGINAL_STATE_OR_CALLS_CHANGED'),
 ('call','ORIGINAL_STATE_OR_CALLS_CHANGED'),('result','COLLECTED_BYTES_CHANGED'),('termination','TERMINATION_REQUIRED'),
 ('validation','VALIDATION_CHANGED')])
def test_changed_saved_evidence_never_releases_or_submits(completed,damage,expected):
    d,p,config=completed;work=d.state/'modal-executions'/config['run_id'];effects=list(p.calls)
    if damage=='halt':private_records.write_text(d.state/'HALT','operator stop')
    if damage=='config':private_records.write_text(d.state/'lane.json',(d.state/'lane.json').read_text()+' ')
    if damage=='state':
        value=d.current();value['interventions'].append({'changed':True});d.save(value)
    if damage=='call':d.store.db.execute("UPDATE manual_calls SET status='UNCERTAIN' WHERE id='synthetic-3'")
    if damage=='result':private_records.write_text(work/'incoming/summary.json','{}')
    if damage=='termination':private_records.write_text(work/'terminated.json','{}')
    if damage=='validation':private_records.write_text(d.state/'validation.json','{}')
    before=recovery.table_rows(d.store.db)
    with pytest.raises(ValueError) as failure:recovery.apply(d.state,'synthetic')
    assert str(failure.value)==expected
    assert d.current()['phase']=='BLOCKED' and p.calls==effects and recovery.table_rows(d.store.db)==before
    assert not (d.state/'collected-cleanup-reconciliation-20261003').exists()


def test_live_host_override_contains_only_original_release_in_root_path():
    pre='+/usr/bin/python3 -s -B /opt/release/tools/manual_host_control.py before --runtime /etc/runtime --lane /var/state'
    start='/usr/bin/python3 -B /var/immutable/modal_provider_transition.py --state /var/state --preparation /var/prep'
    value=host.render(pre,start).decode()
    assert 'ExecStartPre=+/usr/bin/env PYTHONPATH=/opt/research-system/manual-sprint10/'+recovery.ROOT.name+' /usr/bin/python3 -s -B ' in value
    assert 'ExecStart=/usr/bin/python3 -s -B /var/immutable/modal_provider_transition.py' in value
    assert 'site-packages' not in value and 'Environment=' not in value
    with pytest.raises(ValueError,match='ORIGINAL_ROOT_COMMAND_CHANGED'):host.render(pre.replace('-s ',''),start)
