"""Real admission/owner/lifecycle with a synthetic paid-provider boundary."""
import copy,json,base64,gzip
from pathlib import Path
import pytest
from orchestrator import modal_native_synthetic as rehearsal
from orchestrator import modal_environment_budget as budget,modal_environment_provider as provider
from orchestrator import modal_environment_inventory as inventory,private_records as pr
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from tools import item4_native_worker as worker
from test_modal_pinned_image import unreserved_fixture,inventory_fixture,experiment,root,view
from test_modal_environment_provider import Stream
from test_modal_direct_budget import NOW
from test_modal_environment_budget import asset,compute


class Stdin:
 def __init__(self,f):self.f=f;self.data=b'';self.eof=False;self.sent=False;self.fail=False
 def write(self,raw):
  assert (self.f.root/'sandbox.json').exists()
  assert (self.f.root/'stdin-intent.json').exists()
  self.data+=raw
 def write_eof(self):self.eof=True
 def drain(self):
  assert self.eof
  if self.fail:raise OSError('synthetic uncertain stdin send')
  self.sent=True


def result(b):
 s=b['native_synthetic']
 return {'schema':'item4-native-rehearsal-result/v1','status':'PASS','operation_sha256':digest(canonical(b)),
 'selection_sha256':digest(canonical(s)),**{k:s[k] for k in ('module_sha256','code_bundle_sha256','image_id','author_call_id')},
 'package_unchanged':True,'observed_environment':s['environment']['expected'],'native':{'schema':'item4-native-synthetic-integration/v1','module_sha256':s['module_sha256'],
 'preprocessed_files':300,'preprocessing_reuse_verified':True,'gpu_verified':False,'production_main_verified':False,'scientific_approval':False},
 'console':'synthetic fixture only','console_sha256':digest(b'synthetic fixture only'),'console_truncated':False,'failure':None,
 'patient_data':False,'network_permission':False,'gpu':False,'scientific_approval':False,'durability_scope':worker.DURABILITY_SCOPE}


@pytest.fixture
def unreserved(unreserved_fixture,monkeypatch):
 f=unreserved_fixture;b=f.binding
 # Generic lifecycle tests isolate the separate fixed-predecessor qualifier;
 # test_item4_native_successor exercises it with real SQLite and file checks.
 monkeypatch.setattr(budget.diagnostic,'retained_terminal',lambda accounts,binding:(set(),set()))
 from tools import item4_diagnostic_native_runtime
 monkeypatch.setattr(item4_diagnostic_native_runtime,'authority',lambda:{'verdict':'APPROVE','report_sha256':'a'*64})
 b.pop('image_build');b.update(purpose=rehearsal.PURPOSE,operation_id=rehearsal.OPERATION,run_id=rehearsal.RUN,
 native_synthetic=rehearsal.selected(),worker_sha256=rehearsal.worker_sha256(),image_id=rehearsal.selected()['image_id'],
 envelope=rehearsal.envelope(view()['rates']))
 f.image.object_id=b['image_id'];f.sb.stdout=Stream([canonical(result(b))])
 f.sb.stdin=Stdin(f)
 # Provider argument bytes are synthetic; worker's independent bundle tests use
 # the exact preserved code artifact. No paid SDK or patient inputs are used.
 monkeypatch.setattr(rehearsal,'bundle',lambda:b'{}')
 return f


def reserve(f):return budget.reserve(f.accounts,digest(canonical(f.binding)),rehearsal.RUN,f.binding,billing_snapshot=view(),now=NOW)


@pytest.fixture
def reserved(unreserved):
 assert reserve(unreserved);return unreserved


def test_native_existing_owner_full_charge_and_exact_provider_scope(reserved):
 f=reserved;owner=list(f.accounts.db.execute('SELECT * FROM autonomy_runs'))
 h=provider.launch(f.provider,f.accounts,f.binding,f.root)
 args,kw=next(x[1:] for x in f.calls if x[0]=='create')
 assert kw['block_network'] is True and kw['gpu'] is None and kw['cpu']==(2,2)
 assert kw['memory']==(8192,8192) and kw['timeout']==900
 assert not {'outbound_cidr_allowlist','outbound_domain_allowlist','inbound_cidr_allowlist'} & set(kw)
 assert kw['volumes']==kw['env']=={} and kw['secrets']==[] and kw['include_oidc_identity_token'] is False
 assert kw['encrypted_ports']==kw['unencrypted_ports']==kw['h2_ports']==[]
 assert args[0]==rehearsal.selected()['environment']['python_executable']
 assert args[1:4]==('-I','-B','-c') and args[4]==rehearsal.STDIN_BOOTSTRAP+Path(worker.__file__).read_text()
 assert f.sb.stdin.data==rehearsal.stdin_payload() and f.sb.stdin.sent
 assert rehearsal.verify_stdin(f.binding,f.root)['eof'] is True
 assert not any(x[0] in {'build-function','build-image'} for x in f.calls)
 v=provider.observe(f.provider,f.binding,h,f.root);assert v['status']=='VERIFIED'
 before=list(f.calls);assert provider.observe(None,f.binding,h,f.root)==v;assert before==f.calls
 with pytest.raises(ValueError,match='EXISTING_INTENT_RECONCILE'):provider.launch(f.provider,f.accounts,f.binding,f.root)
 assert before==f.calls and list(f.accounts.db.execute('SELECT * FROM autonomy_runs'))==owner
 assert f.accounts.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0


@pytest.mark.parametrize('damage',['cap','owner','pending','compute','selection','image','gpu'])
def test_refuses_before_charge_or_provider(unreserved,damage):
 f=unreserved;b=f.binding
 if damage=='cap':asset(f.accounts.batch,budget.diagnostic.STAGE_CAP-b['envelope']['cost']['reserved_micro_usd']+1)
 elif damage=='owner':f.accounts.db.execute("UPDATE autonomy_runs SET binding='{}'")
 elif damage=='pending':f.accounts.db.execute("INSERT INTO autonomy_calls VALUES('other','scientific','other',1,'2026-10-08','UNCERTAIN','{}',NULL)")
 elif damage=='compute':compute(f.accounts.batch,10,status='RUNNING')
 elif damage=='selection':b['native_synthetic']['module_sha256']='0'*64
 elif damage=='image':b['image_id']='im-Other'
 else:b['envelope']['resources']['gpu']='H100'
 before=[tuple(x) for x in f.accounts.db.execute('SELECT * FROM autonomy_assets')]
 with pytest.raises((ValueError,OSError)):reserve(f)
 assert [tuple(x) for x in f.accounts.db.execute('SELECT * FROM autonomy_assets')]==before and not f.calls


def test_changed_price_cannot_create_second_native_operation(reserved):
 f=reserved;old=[tuple(x) for x in f.accounts.db.execute('SELECT * FROM autonomy_assets')]
 f.binding['installed_config_sha256']='e'*64
 with pytest.raises(ValueError,match='ALREADY_RESERVED_NO_RETRY'):reserve(f)
 assert [tuple(x) for x in f.accounts.db.execute('SELECT * FROM autonomy_assets')]==old


def test_failed_native_output_and_original_charge_preserved(reserved):
 f=reserved;f.sb.poll=lambda:1;f.sb.stdout=Stream([b'original failure']);f.sb.stderr=Stream([b'trace'])
 h=provider.launch(f.provider,f.accounts,f.binding,f.root);v=provider.observe(f.provider,f.binding,h,f.root)
 assert v['status']=='UNCERTAIN' and (f.root/'stdout.bin').read_bytes()==b'original failure'
 assert f.accounts.db.execute('SELECT reserved_micro_usd FROM autonomy_assets').fetchone()[0]==f.binding['envelope']['cost']['reserved_micro_usd']
 assert provider.observe(None,f.binding,h,f.root)==v


def test_controller_keeps_original_scientific_run_active(unreserved,tmp_path):
 f=unreserved;state=tmp_path/'state';pr.mkdir(state);f.root=state/'provider'
 config={'schema':rehearsal.SCHEMA,'source':f.binding['source'],'release':'/synthetic','installation_record':'/synthetic-record',
 'installation_sha256':'a'*64,'batch_ledger':str(f.accounts.batch.folder),'state':str(state),'provider':{},'units':{},
 **{k:f.binding[k] for k in ('operation_id','image_id','base_image','worker_sha256','owner_sha256','native_synthetic')}}
 proof={'status':'PASS','source':config['source'],'installation_sha256':'a'*64,'config_sha256':f.binding['installed_config_sha256']}
 # Generated binding is identical to the fixture; refresh stream accordingly.
 v=inventory.tick(config,f.provider,f.accounts,host_proof=proof,now=NOW)
 assert v['status']=='VERIFIED';assert inventory.tick(config,None,f.accounts,host_proof=proof,now=NOW)==v
 assert f.accounts.db.execute('SELECT status FROM autonomy_runs WHERE id=?',(rehearsal.RUN,)).fetchone()[0]=='ACTIVE'
 assert sum(x[0]=='create' for x in f.calls)==1
 assert f.accounts.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0


def test_worker_exact_bundle_paths_and_posthash(tmp_path):
 # Construct non-patient source-only fixture to exercise extraction independently.
 files={'execution.py':'# exact synthetic source\n',**{f'orchestrator/module_{chr(97+i)}.py':'# support\n' for i in range(18)}}
 raw=json.dumps(files).encode();s={'files':{k:digest(v.encode()) for k,v in files.items()},'code_bundle_sha256':digest(raw),'code_bundle_bytes':len(raw)}
 encoded=base64.b64encode(gzip.compress(raw)).decode();worker.unpack(encoded,s,tmp_path);worker.check_package(tmp_path,s)
 p=tmp_path/'execution.py';p.chmod(0o600);p.write_text('changed')
 with pytest.raises(ValueError,match='PACKAGE_CHANGED'):worker.check_package(tmp_path,s)


def test_worker_refuses_bundle_tampering_and_log_overflow(tmp_path):
 s=rehearsal.selected()
 with pytest.raises(ValueError,match='BUNDLE_BINDING'):worker.unpack(base64.b64encode(gzip.compress(b'{}')).decode(),s,tmp_path)
 with pytest.raises(ValueError,match='ENCODED_BOUND'):worker.unpack('a'*120001,s,tmp_path)
 log=worker.BoundedLog();log.write('x'*worker.MAX_LOG)
 with pytest.raises(ValueError,match='LOG_BOUND'):log.write('y')
 assert len(log.data)==worker.MAX_LOG and log.exceeded


@pytest.mark.parametrize('field,value',[('package_unchanged',False),('gpu',True),('image_id','im-other'),('operation_sha256','a'*64),('scientific_approval',True),('console','changed')])
def test_changed_result_cannot_pass(reserved,field,value):
 b=reserved.binding;v=result(b);v[field]=value
 with pytest.raises(ValueError):rehearsal.validate_result(canonical(v),b)


def test_real_fit_progress_factory_binds_generated_files_and_reopens(tmp_path):
 from orchestrator.modal_fit_progress import FitProgress
 root=tmp_path/'item4-native-synthetic-test';pr.mkdir(root);inputs=root/'inputs';pr.mkdir(inputs)
 for i in range(893):pr.write_bytes(inputs/f'synthetic-{i}.bin',str(i).encode())
 factory=worker.progress_factory(rehearsal.selected());p=factory(root/'durable','synthetic-fit','a'*64,'b'*64)
 assert type(p) is FitProgress
 assert type(factory(root/'durable','synthetic-fit','a'*64,'b'*64)) is FitProgress
 with pytest.raises(ValueError,match='PROGRESS_SCOPE'):factory(root/'durable','other-fit','a'*64,'b'*64)
 (inputs/'alias').symlink_to(inputs/'synthetic-0.bin')
 with pytest.raises(ValueError,match='SYNTHETIC_ALIAS'):factory(root/'durable','synthetic-fit','a'*64,'b'*64)


def test_runtime_config_and_unit_retain_original_restrictions():
 from tools import item4_diagnostic_native_runtime as runtime
 original=budget.diagnostic.document(budget.diagnostic.RETAINED,budget.diagnostic.RETAINED_SHA)['image_config']
 original['units']={}
 selected=runtime.config_from_image(original)
 assert selected['provider']==original['provider'] and selected['source']==original['source']
 assert selected['owner_sha256']==original['owner_sha256']
 assert selected['image_id']==rehearsal.selected()['image_id']
 unit=runtime.rendered(selected)[runtime.CPU_UNIT].decode()
 for text in ('User=partho','Group=partho','UMask=0077','NoNewPrivileges=true','ProtectSystem=strict','PrivateTmp=true',
 'ProtectHome=read-only','RestrictSUIDSGID=true','LockPersonality=true','TimeoutStartSec=1200'):
  assert text in unit
 assert 'Restart=' not in unit and '.timer' not in unit
 assert 'ReadWritePaths='+str(runtime.STATE)+' '+original['batch_ledger'] in unit
 assert original['provider']['credential_file'] not in unit


def test_native_asset_counted_by_next_scientific_admission(reserved):
 from test_modal_item4_budget import bound
 f=reserved;ident=digest(canonical(f.binding));f.accounts.finish_assets(ident,'READY',{'synthetic_fixture':True})
 original=dict(f.accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone())
 scientific=bound('nextfit');scientific['cost']=budget.quote(scientific['resources'],view()['rates'],0)
 compute(f.accounts.batch,budget.SMOKE_CAP-scientific['cost']['reserved_micro_usd'],ident='oldfit',run='item4')
 f.accounts.batch.complete_run(rehearsal.RUN,{'synthetic_future_owner_fixture':True})
 f.accounts.batch.register_run('item4',{'backlog_item':4,'experiment_authority_sha256':budget.AUTHORITY})
 with pytest.raises(ValueError,match='ITEM4_HARD_COST_CAP'):
  f.accounts.reserve_item4(digest(canonical(scientific)),'item4',scientific,billing_snapshot=view(),now=NOW)
 assert dict(f.accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone())==original


def test_stdin_uncertainty_preserves_handle_and_cannot_resend(reserved):
 f=reserved;f.sb.stdin.fail=True
 with pytest.raises(OSError,match='uncertain stdin'):provider.launch(f.provider,f.accounts,f.binding,f.root)
 assert (f.root/'sandbox.json').is_file() and (f.root/'stdin-intent.json').is_file()
 assert not (f.root/'stdin-sent.json').exists()
 with pytest.raises(FileExistsError):rehearsal.send_stdin(f.sb,f.binding,f.root)
 with pytest.raises(ValueError,match='EXISTING_INTENT_RECONCILE'):provider.launch(f.provider,f.accounts,f.binding,f.root)
 assert sum(x[0]=='create' for x in f.calls)==1


def test_corrupted_stdin_confirmation_refuses_successful_result(reserved):
 f=reserved;h=provider.launch(f.provider,f.accounts,f.binding,f.root)
 sent=json.loads((f.root/'stdin-sent.json').read_text());sent['sha256']='0'*64
 pr.write_bytes(f.root/'stdin-sent.json',canonical(sent))
 with pytest.raises(ValueError,match='STDIN_RECEIPT'):provider.observe(f.provider,f.binding,h,f.root)
 assert (f.root/'terminal.json').exists() and not (f.root/'outcome.json').exists()


@pytest.mark.parametrize('extra',[0,1])
def test_diagnostic_25_cap_counts_existing_fit_costs_exactly(unreserved,extra):
 f=unreserved;amount=f.binding['envelope']['cost']['reserved_micro_usd']
 compute(f.accounts.batch,budget.diagnostic.DIAGNOSTIC_CAP-amount+extra,
     ident='smoke-cpu-B32',run=rehearsal.RUN)
 before=[tuple(r) for r in f.accounts.db.execute('SELECT * FROM autonomy_compute')]
 if extra:
  with pytest.raises(ValueError,match='HARD_DIAGNOSTIC_CAP'):reserve(f)
  assert not list(f.accounts.db.execute('SELECT * FROM autonomy_assets'))
 else:
  assert reserve(f)
  event=json.loads(f.accounts.db.execute("SELECT payload FROM events WHERE id LIKE '%:assets-reserved'").fetchone()[0])
  assert event['caps']=={'smoke':150000000,'total':1275000000}
 assert before==[tuple(r) for r in f.accounts.db.execute('SELECT * FROM autonomy_compute')]
 assert not f.calls


def test_native_preparation_remains_in_diagnostic_subcap(reserved):
 f=reserved;rows=f.accounts.db.execute('SELECT * FROM autonomy_assets').fetchall()
 amount=rows[0]['reserved_micro_usd']
 with pytest.raises(ValueError,match='HARD_DIAGNOSTIC_CAP'):
  budget.diagnostic.subcap(f.accounts,rows,[],{r['id']:r['reserved_micro_usd'] for r in rows},view(),
      budget.diagnostic.DIAGNOSTIC_CAP-amount+1)
 assert budget.diagnostic.subcap(f.accounts,rows,[],{r['id']:r['reserved_micro_usd'] for r in rows},view(),
      budget.diagnostic.DIAGNOSTIC_CAP-amount)==amount
 assert rows[0]['status']=='RESERVED' and not f.calls


@pytest.mark.parametrize('field',['binding','status','reserved_micro_usd','receipt','run'])
def test_historical_native_rows_not_relabelled_or_discounted(field):
 d=budget.diagnostic;proof=d.document(d.RETAINED,d.RETAINED_SHA)
 for row in proof['native_rows'].values():
  assert d.historical_asset(row)
  changed=dict(row);changed[field]=0 if field=='reserved_micro_usd' else 'changed'
  with pytest.raises(ValueError,match='HISTORICAL_ASSET_CHANGED'):d.historical_asset(changed)
 assert d.historical_asset({'binding':'{}'}) is False


def test_native_requires_implementation_authority(unreserved,monkeypatch):
 from tools import item4_diagnostic_native_runtime as runtime
 def refuse():raise ValueError('test no implementation approval')
 monkeypatch.setattr(runtime,'authority',refuse)
 with pytest.raises(ValueError,match='no implementation approval'):reserve(unreserved)
 assert not list(unreserved.accounts.db.execute('SELECT * FROM autonomy_assets'))
 assert not unreserved.calls


def test_exact_operator_bytes_cannot_be_substituted(unreserved,tmp_path,monkeypatch):
 d=budget.diagnostic
 changed=tmp_path/'changed-operator';(changed/'docs').mkdir(parents=True)
 (changed/'docs/ITEM4_CPU_DIAGNOSTIC_OPERATOR_DECISION.txt').write_text('different decision')
 monkeypatch.setattr(d,'ROOT',changed)
 with pytest.raises(ValueError,match='OPERATOR_CHANGED'):reserve(unreserved)
 assert not list(unreserved.accounts.db.execute('SELECT * FROM autonomy_assets'))


def test_complete_native_pages_preserve_unicode_and_all_console_bytes():
 from tools import item4_diagnostic_review_runtime as review
 raw=canonical({'console':'native ?vidence ? '*7000,'scope':'CPU only','gpu_verified':False})
 files=review.pages(raw);index=json.loads(files['index.json'])
 rebuilt=b''.join(files[p['name']] for p in index['pages'])
 assert rebuilt==raw and digest(raw)==index['sha256'] and len(raw)==index['bytes']
 assert index['omissions']==[] and len(index['pages'])>1
 for p in index['pages']:
  assert p['sha256']==digest(files[p['name']]) and p['bytes']==len(files[p['name']])
  assert len(files[p['name']].decode())<=6000


def test_current_worker_exactly_matches_the_reviewed_historical_adapter():
 # Pin reviewed worker, not scientific execution.py; keeps all hash/size bounds.
 assert digest(Path(worker.__file__).read_bytes())=='a6e10e29eb657f1aa4fb7c018282fbb0050e913def8d0156b88e75e11f3b528d'
 assert worker.MAX_BUNDLE==300000 and worker.MAX_RESULT==240000 and worker.MAX_LOG==65536


@pytest.fixture
def native_ready(unreserved,tmp_path,monkeypatch):
 from tools import item4_diagnostic_native_runtime as h
 f=unreserved;state=tmp_path/'native-state';pr.mkdir(state);f.root=state/'provider'
 cfg={'schema':rehearsal.SCHEMA,'source':f.binding['source'],'release':'/synthetic','installation_record':'/synthetic-record',
 'installation_sha256':'a'*64,'batch_ledger':str(f.accounts.batch.folder),'state':str(state),'provider':{},'units':{},
 **{k:f.binding[k] for k in ('operation_id','image_id','base_image','worker_sha256','owner_sha256','native_synthetic')}}
 config=tmp_path/'native-config.json';config.write_bytes(canonical(cfg))
 f.binding['installed_config_sha256']=digest(config.read_bytes())
 f.sb.stdout=Stream([canonical(result(f.binding))])
 proof={'status':'PASS','source':cfg['source'],'installation_sha256':'a'*64,'config_sha256':f.binding['installed_config_sha256']}
 assert inventory.tick(cfg,f.provider,f.accounts,host_proof=proof,now=NOW)['status']=='VERIFIED'
 monkeypatch.setattr(h,'STATE',state);monkeypatch.setattr(h,'CONFIG',config)
 # Root-owned installed-file checks are separately enforced by authority; this
 # generated unit fixture exercises full receipt validation as an ordinary user.
 monkeypatch.setattr(h,'trusted',lambda p:Path(p))
 return f,h


def test_native_receipt_gate_replays_actual_provider_reader_without_new_call(native_ready):
 f,h=native_ready;calls=list(f.calls)
 binding,saved=h.native_result(f.accounts)
 assert binding==f.binding and saved['status']=='VERIFIED' and f.calls==calls
 assert saved['native_synthetic']['module_sha256']==rehearsal.selected()['module_sha256']
 assert saved['native_synthetic']['scientific_approval'] is False


@pytest.mark.parametrize('damage',['missing','uncertain','charge','stdin','stdout','provider','selection'])
def test_native_receipt_corruption_cannot_admit_review(native_ready,damage):
 f,h=native_ready;calls=list(f.calls);db=f.accounts.db
 if damage=='missing':(h.STATE/'provider/outcome.json').unlink()
 elif damage=='uncertain':db.execute("UPDATE autonomy_assets SET status='UNCERTAIN'")
 elif damage=='charge':db.execute('UPDATE autonomy_assets SET reserved_micro_usd=reserved_micro_usd-1')
 elif damage=='stdin':
  p=h.STATE/'provider/stdin-sent.json';value=json.loads(p.read_bytes());value['sha256']='0'*64;pr.write_bytes(p,canonical(value))
 elif damage=='stdout':pr.write_bytes(h.STATE/'provider/stdout.bin',b'{}')
 elif damage=='provider':
  p=h.STATE/'provider/sandbox.json';value=json.loads(p.read_bytes());value['binding_sha256']='0'*64;pr.write_bytes(p,canonical(value))
 else:
  p=h.STATE/'binding.json';value=json.loads(p.read_bytes());value['native_synthetic']['module_sha256']='0'*64;pr.write_bytes(p,canonical(value))
 with pytest.raises((ValueError,FileNotFoundError)):h.native_result(f.accounts)
 assert f.calls==calls and db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0


@pytest.mark.parametrize('fault',[None,'stage','work','pending','local','global','shape'])
def test_reviewer_reader_turn_allowance_requires_exact_dual_admission(monkeypatch,tmp_path,fault):
 import sqlite3
 from types import SimpleNamespace as NS
 from tools import item4_diagnostic_review_runtime as runtime
 from orchestrator import manual_stage,item4_smoke_response as helper
 local=sqlite3.connect(':memory:');batch=sqlite3.connect(':memory:')
 local.execute('CREATE TABLE manual_calls(id TEXT,status TEXT)')
 batch.execute('CREATE TABLE autonomy_calls(id TEXT,status TEXT)')
 p={'schema':helper.CORRECTED_REVIEW_SCHEMA};ident=helper.call(p,'review')
 local.execute('INSERT INTO manual_calls VALUES(?,?)',(ident,'COMPLETE' if fault=='local' else 'RUNNING'))
 batch.execute('INSERT INTO autonomy_calls VALUES(?,?)',(ident,'COMPLETE' if fault=='global' else 'RUNNING'))
 work=tmp_path/'run_spec_review-16';pending={'id':ident,'round':16,'stage':'run_spec_review'}
 if fault=='pending':pending['round']=14
 store=NS(db=local,batch=NS(db=batch));driver=NS(store=store,state=tmp_path/'state',
  config={'workspace_root':str(tmp_path)},current=lambda:{'pending':pending})
 monkeypatch.setattr(manual_stage,'reviewer_command',lambda *args:['claude','--max-turns','60' if fault=='shape' else '30'])
 restore=runtime.bind_admission(driver,None,None,helper,p,'a'*64)
 try:
  if fault:
   with pytest.raises(ValueError):manual_stage.reviewer_command(tmp_path/'other' if fault=='work' else work,
       'run_spec_author' if fault=='stage' else 'run_spec_review')
  else:assert manual_stage.reviewer_command(work,'run_spec_review')==['claude','--max-turns','60']
 finally:restore();local.close();batch.close()


@pytest.mark.parametrize('extra',[0,1])
def test_corrected_native_total_cap_still_refuses_full_stage_exposure(unreserved,extra):
 f=unreserved;amount=f.binding['envelope']['cost']['reserved_micro_usd']
 compute(f.accounts.batch,budget.TOTAL_CAP-amount+extra,ident='old-full-fit',stage='FULL',run=rehearsal.RUN)
 old=[tuple(r) for r in f.accounts.db.execute('SELECT * FROM autonomy_compute')]
 # At the item boundary the independent provider headroom gate still holds;
 # one micro-dollar above it is refused by the item gate first.
 with pytest.raises(ValueError,match='ITEM4_HARD_COST_CAP' if extra else 'ITEM4_PROVIDER_HEADROOM_WAIT'):reserve(f)
 assert not list(f.accounts.db.execute('SELECT * FROM autonomy_assets'))
 assert [tuple(r) for r in f.accounts.db.execute('SELECT * FROM autonomy_compute')]==old
 assert not f.calls

@pytest.mark.parametrize('field',['status','receipt','reserved_micro_usd','binding','run'])
def test_exact_failed_native_row_cannot_be_discounted_or_relabelled(field):
 d=budget.diagnostic;row=d.document(d.CORRECTED,d.CORRECTED_SHA)['original_failed_asset']
 assert d.historical_asset(row) and row['reserved_micro_usd']==1118950 and row['status']=='UNCERTAIN'
 changed=dict(row);changed[field]=0 if field=='reserved_micro_usd' else 'changed'
 with pytest.raises(ValueError,match='FAILED_ROW_CHANGED'):d.historical_asset(changed)
