"""Recovery state machine with synthetic SDK and real reserved accounting."""
import json,sys
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from test_item4_native_synthetic import reserved,unreserved,unreserved_fixture,inventory_fixture,experiment,root,Stdin
from test_modal_direct_budget import NOW
from orchestrator import modal_native_synthetic as n,modal_environment_provider as provider,private_records as pr
from orchestrator.manual_executor import digest
from orchestrator.modal_executor import canonical


@pytest.fixture
def recovery(reserved,monkeypatch,tmp_path):
 f=reserved;pr.mkdir(f.root)
 original={'intent.json':{'binding':f.binding},'app.json':{'name':'original-app','app_id':'ap-private'}}
 for name,v in original.items():pr.write_bytes(f.root/name,canonical(v))
 sdk=tmp_path/'sdk';pr.mkdir(sdk/'modal',parents=True);pr.write_bytes(sdk/'modal/sandbox.py',b'synthetic pinned SDK fixture')
 f.provider.config['sdk_package']=str(sdk)
 proof={'app_id':'ap-private','image_id':f.binding['image_id'],'sandbox_py_sha256':digest((sdk/'modal/sandbox.py').read_bytes())}
 f.snapshot_calls=0
 def snapshot(binding,folder):
  f.snapshot_calls+=1
  if (folder/'stdin-recovery-intent.json').exists() or (folder/'sandbox.json').exists():raise ValueError('NATIVE_RECOVERY_ORIGINALS_CHANGED_OR_USED')
  assert binding==f.binding and folder==f.root
  return proof,['x'*96135]
 monkeypatch.setattr(n,'precreate_snapshot',snapshot)
 monkeypatch.setattr('orchestrator.manual_host_guard.trusted',pr.check)
 class Invalid(ValueError):pass
 f.provider.modal.exception.InvalidError=Invalid
 def validate(args):
  size=sum(len(x) for x in args)
  if size>65536:raise Invalid(f'Total length of CMD arguments cannot exceed 65536 bytes (ARG_MAX). Got {size} bytes.')
 monkeypatch.setitem(sys.modules,'modal.sandbox',NS(_validate_exec_args=validate))
 def lookup(name,create_if_missing,**kw):
  assert name=='original-app' and create_if_missing is False
  f.calls.append(('original-app',));return NS(app_id='ap-private')
 f.provider.modal.App.lookup=lookup
 def missing(*args,**kw):
  f.calls.append(('lookup-sandbox',));raise f.provider.modal.exception.NotFoundError()
 f.provider.modal.Sandbox.from_name=missing
 f.old_assets=[tuple(x) for x in f.accounts.db.execute('SELECT * FROM autonomy_assets')]
 return f


def test_same_reservation_one_create_and_stdin_no_new_app(recovery):
 f=recovery;h=n.recover_precreate(f.provider,f.accounts,f.binding,f.root,now=NOW)
 assert (f.root/'stdin-recovery-intent.json').exists() and n.verify_stdin(f.binding,f.root)
 assert h['provider_id']==f.sb.object_id
 assert [tuple(x) for x in f.accounts.db.execute('SELECT * FROM autonomy_assets')]==f.old_assets
 args,kw=next(x[1:] for x in f.calls if x[0]=='create')
 assert sum(len(x.encode()) for x in args)<=65536
 assert kw['block_network'] is True and kw['gpu'] is None and kw['cpu']==(2,2) and kw['memory']==(8192,8192) and kw['timeout']==900
 assert kw['volumes']==kw['env']=={} and kw['secrets']==[] and kw['include_oidc_identity_token'] is False
 assert not any(x[0]=='lookup' for x in f.calls)
 with pytest.raises(ValueError,match='CHANGED_OR_USED'):n.recover_precreate(f.provider,f.accounts,f.binding,f.root,now=NOW)
 assert sum(x[0]=='create' for x in f.calls)==1
 assert f.accounts.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0


def test_unknown_recovery_create_stops_without_second_create(recovery):
 f=recovery
 def fail(*args,**kwargs):f.calls.append(('uncertain-create',));raise TimeoutError('lost create response')
 f.provider.modal.Sandbox.create=fail
 with pytest.raises(TimeoutError):n.recover_precreate(f.provider,f.accounts,f.binding,f.root,now=NOW)
 assert (f.root/'stdin-recovery-intent.json').exists() and not (f.root/'sandbox.json').exists()
 with pytest.raises(ValueError,match='CHANGED_OR_USED'):n.recover_precreate(f.provider,f.accounts,f.binding,f.root,now=NOW)
 assert sum(x[0]=='uncertain-create' for x in f.calls)==1
 assert [tuple(x) for x in f.accounts.db.execute('SELECT * FROM autonomy_assets')]==f.old_assets


@pytest.mark.parametrize('damage',['existing-sandbox','sdk','model-running','worker','image','app'])
def test_unrelated_or_changed_evidence_cannot_continue(recovery,damage):
 f=recovery
 if damage=='existing-sandbox':f.provider.modal.Sandbox.from_name=lambda *a,**k:NS(object_id='sb-already')
 elif damage=='sdk':pr.write_bytes(Path(f.provider.config['sdk_package'])/'modal/sandbox.py',b'changed')
 elif damage=='model-running':f.accounts.db.execute("INSERT INTO autonomy_calls VALUES('active','scientific','other',1,'2026-10-08','RUNNING','{}',NULL)")
 elif damage=='worker':f.binding['worker_sha256']='0'*64
 elif damage=='image':f.image.object_id='im-other'
 else:f.provider.modal.App.lookup=lambda *a,**k:NS(app_id='ap-other')
 with pytest.raises(ValueError):n.recover_precreate(f.provider,f.accounts,f.binding,f.root,now=NOW)
 assert not any(x[0]=='create' for x in f.calls)
 assert [tuple(x) for x in f.accounts.db.execute('SELECT * FROM autonomy_assets')]==f.old_assets


@pytest.mark.parametrize('damage',['prior-source','active-unit','config','history'])
def test_upgrade_refuses_wrong_or_uncertain_install_before_writes(tmp_path,monkeypatch,damage):
 from tools import install_item4_native_runtime as install
 from tools import item4_native_runtime as h
 from orchestrator.autonomy_review import canonical as installed_bytes
 record=tmp_path/'record';pr.mkdir(record);config_path=tmp_path/'config.json';config={'synthetic_config':True}
 old={'source':install.PRIOR_SOURCE,'config_sha256':digest(installed_bytes(config)),'unit':'synthetic.service'}
 if damage=='prior-source':old['source']='0'*40
 if damage=='config':old['config_sha256']='0'*64
 pr.write_bytes(record/'installed.json',canonical(old));pr.write_bytes(config_path,installed_bytes(config))
 monkeypatch.setattr(h,'RECORD',record);monkeypatch.setattr(h,'CONFIG',config_path);monkeypatch.setattr(h,'STATE',tmp_path/'state')
 monkeypatch.setattr('orchestrator.manual_host_guard.trusted',pr.check)
 monkeypatch.setattr(n,'precreate_snapshot',lambda *a:None)
 checked={'proof':{'helper_source':install.PRIOR_SOURCE},'config':config,'asset':{'binding':'{}'},'files':[]}
 def output(cmd,**kw):
  if cmd[0]=='systemctl':return 'MainPID=42\nActiveState=active\n' if damage=='active-unit' else 'MainPID=0\nActiveState=failed\n'
  assert cmd[:4]==['runuser','-u','partho','--']
  assert 'mode=ro' in cmd[-1] and 'os.getuid()==os.getgid()==1003' in cmd[-1]
  return json.dumps(checked)
 monkeypatch.setattr(install.subprocess,'check_output',output)
 if damage=='history':pr.mkdir(record/'history'/install.PRIOR_SOURCE,parents=True)
 before={str(p.relative_to(tmp_path)):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}
 expected={'prior-source':'EXACT_PRIOR_SOURCE','active-unit':'RUNNING','config':'CONFIG_CHANGED','history':'EXISTS_RECONCILE'}[damage]
 with pytest.raises(ValueError,match='^NATIVE_RUNTIME_UPGRADE_'+expected+'$'):
  install.upgrade(tmp_path/'packet',tmp_path/'review','a'*40,{}, {},config)
 assert {str(p.relative_to(tmp_path)):p.read_bytes() for p in tmp_path.rglob('*') if p.is_file()}==before


def test_exact_live_configuration_matches_original_installer_serializer():
 from tools import item4_native_runtime as h
 from orchestrator.autonomy_review import canonical as installed_bytes
 original=json.loads((Path(__file__).parents[1]/'docs/ITEM4_PINNED_IMAGE_SELECTION_20261008.json').read_bytes())
 config=h.config_from_image(original)
 assert digest(installed_bytes(config))=='5fbe6f7f915e43d0cf1565884d6eba1bbfee90e0c5acc4e8afd47c59e1ced1ab'
 assert digest(canonical(config))!=digest(installed_bytes(config))
