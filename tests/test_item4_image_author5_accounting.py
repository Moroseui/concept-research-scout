import json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from tools import item4_image_runtime as adapter
from tools import install_item4_image_runtime as installer
from orchestrator import spending_continuation as continuation
from orchestrator import modal_environment_budget as budget
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from test_modal_pinned_image import unreserved_fixture,inventory_fixture,experiment,root,view
from test_modal_direct_budget import NOW
from test_modal_environment_budget import asset


def connect(monkeypatch):
    old=continuation.closed_ids
    monkeypatch.setattr(adapter,'author5_terminal',lambda batch:adapter.AUTHOR5)
    monkeypatch.setattr(continuation,'closed_ids',lambda batch,run:adapter.qualified_closed(old,batch,run))


def test_other_runs_and_original_failure_remain_closed_failures(monkeypatch):
    monkeypatch.setattr(adapter,'author5_terminal',lambda b:pytest.fail('out-of-scope qualification'))
    old={'prior'}
    assert adapter.qualified_closed(lambda b,r:old,object(),'other')==old
    assert old=={'prior'}


def test_missing_or_changed_original_qualification_refuses(monkeypatch):
    def fail(b):raise ValueError('qualification changed')
    monkeypatch.setattr(adapter,'author5_terminal',fail)
    with pytest.raises(ValueError,match='qualification changed'):
        adapter.qualified_closed(lambda b,r:set(),object(),adapter.RUN)


@pytest.mark.parametrize('block',[None,'running','uncertain','over_cap'])
def test_actual_image_reservation_preserves_rows_and_refusals(unreserved_fixture,monkeypatch,block):
    f=unreserved_fixture;connect(monkeypatch);db=f.accounts.db
    db.execute("INSERT INTO autonomy_calls VALUES(?, 'scientific', ?,5,'2026-10-08','UNCERTAIN','{}','{}')",(adapter.AUTHOR5,adapter.RUN))
    if block in {'running','uncertain'}:
        db.execute("INSERT INTO autonomy_calls VALUES('unknown','scientific','other',1,'2026-10-08',?,'{}',NULL)",(block.upper(),))
    if block=='over_cap':asset(f.accounts.batch,budget.SMOKE_CAP)
    calls=[tuple(x) for x in db.execute('SELECT * FROM autonomy_calls')]
    assets=[tuple(x) for x in db.execute('SELECT * FROM autonomy_assets')]
    def reserve():return budget.reserve(f.accounts,digest(canonical(f.binding)),adapter.RUN,f.binding,billing_snapshot=view(),now=NOW)
    if block:
        with pytest.raises(ValueError,match='ITEM4_HARD_COST_CAP' if block=='over_cap' else 'BATCH_UNCERTAIN_OR_RUNNING_CALL'):reserve()
        assert [tuple(x) for x in db.execute('SELECT * FROM autonomy_assets')]==assets
    else:
        assert reserve()
        assert db.execute('SELECT reserved_micro_usd FROM autonomy_assets').fetchone()[0]==f.binding['envelope']['cost']['reserved_micro_usd']
    assert [tuple(x) for x in db.execute('SELECT * FROM autonomy_calls')]==calls


@pytest.mark.parametrize('damage',[None,'source','selection','active','reserved','repeat'])
def test_upgrade_preserves_original_bytes_and_requires_unspent_stopped(tmp_path,monkeypatch,damage):
    import subprocess
    from orchestrator import manual_host_guard
    monkeypatch.setattr(manual_host_guard,'trusted',lambda p:Path(p))
    monkeypatch.setattr(installer.os,'chown',lambda *a:None)
    contract=NS(ROOT=tmp_path/'code',RECORD=tmp_path/'record',CONFIG=tmp_path/'config.json',FILES=adapter.FILES,require=adapter.require)
    old={'source':'94be84ee3406996a397ba7ac57b7c681da5ca660','config_sha256':'old-config','base_receipt_sha256':'base','review_sha256':'old-review'}
    if damage=='source':old['source']='wrong'
    contract.ROOT.mkdir();contract.RECORD.mkdir();(contract.RECORD/'review').mkdir()
    (contract.CONFIG).write_text(json.dumps({'schema':'unchanged','units':{}}))
    raw={name:b'new-source' for name in contract.FILES};raw[contract.FILES[-2]]=json.dumps({'schema':'changed' if damage=='selection' else 'unchanged'}).encode()
    for name in raw:
        p=contract.ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'original-source:'+name.encode())
    for name,value in [('installed.json',json.dumps(old).encode()),('COMPLETE.json',b'old-complete'),('START_INTENT.json',b'old-intent'),('RETRY_AUTHOR5_START_INTENT.json',b'old-retry-intent')]:
        (contract.RECORD/name).write_bytes(value)
    (contract.RECORD/'review/receipt.json').write_bytes(b'old-genuine-review')
    review=tmp_path/'new-review';review.mkdir();(review/'receipt.json').write_bytes(b'new-genuine-review')
    if damage=='repeat':(contract.RECORD/'history'/old['source']).mkdir(parents=True)
    before={str(p.relative_to(tmp_path)):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
    verified=[];monkeypatch.setattr(installer,'load',lambda path,name:NS(verify=lambda:verified.append(name),FILES=adapter.FILES))
    commands=[]
    def command(argv,**kw):
        commands.append(argv)
        if argv[0]=='systemctl':return 'MainPID=1\nActiveState=active\n' if damage=='active' else 'MainPID=0\nActiveState=failed\n'
        assert argv[:7]==['runuser','-u','partho','--','python3','-s','-B']
        assert '?mode=ro' in argv[-1] and 'M4_ITEM4_PINNED_IMAGE_BUILD' in argv[-1]
        if damage=='reserved':raise subprocess.CalledProcessError(1,argv)
        return 'UNRESERVED_NO_PROVIDER_INTENT\n'
    monkeypatch.setattr(subprocess,'check_output',command)
    if damage:
        with pytest.raises((ValueError,subprocess.CalledProcessError)):installer.upgrade(contract,raw,review,{'report_sha256':'new-review'},'new-source',{})
        assert {str(p.relative_to(tmp_path)):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}==before
    else:
        assert installer.upgrade(contract,raw,review,{'report_sha256':'new-review'},'new-source',{})['status']=='UPDATED_HELD'
        history=contract.RECORD/'history'/old['source']
        for name,value in raw.items():
            assert (contract.ROOT/name).read_bytes()==value
            assert (history/'source'/name).read_bytes()==before[str((contract.ROOT/name).relative_to(tmp_path))]
        assert (history/'START_INTENT.json').read_bytes()==b'old-intent'
        assert (history/'original-review-directory/receipt.json').read_bytes()==b'old-genuine-review'
        assert contract.CONFIG.read_bytes()==before[str(contract.CONFIG.relative_to(tmp_path))]
        assert verified==['_prior_image_adapter','_updated_image_adapter']


def test_main_connects_existing_admission_and_restores_on_failure(monkeypatch):
    import sys
    from orchestrator import modal_provider,modal_environment_inventory
    monkeypatch.setattr(adapter.os,'getuid',lambda:1003);monkeypatch.setattr(adapter.os,'getgid',lambda:1003)
    monkeypatch.setattr(sys,'argv',['runtime','--config',str(adapter.CONFIG)])
    monkeypatch.setattr(adapter,'verify',lambda:{})
    original_provider=modal_provider.ModalProvider;old=continuation.closed_ids
    prior_reserve=budget.reserve;new_reserve=object()
    monkeypatch.setattr(adapter,'load_source',lambda *a:NS(reserve=new_reserve))
    observed=[]
    monkeypatch.setattr(adapter,'qualified_closed',lambda original,batch,run:observed.append((original,batch,run)) or {'qualified'})
    def main():
        assert modal_provider.ModalProvider is not original_provider
        assert budget.reserve is new_reserve
        assert continuation.closed_ids('batch',adapter.RUN)=={'qualified'}
        raise RuntimeError('native admission remains authoritative')
    monkeypatch.setattr(modal_environment_inventory,'main',main)
    with pytest.raises(RuntimeError,match='native admission remains authoritative'):adapter.main()
    assert observed==[(old,'batch',adapter.RUN)]
    assert modal_provider.ModalProvider is original_provider and continuation.closed_ids is old
    assert budget.reserve is prior_reserve
