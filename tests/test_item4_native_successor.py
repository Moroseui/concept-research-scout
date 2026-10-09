"""Exact successor failures, retained charges and cap refusal using real SQLite."""
import copy,json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import modal_native_successor as q,modal_native_synthetic as n,modal_environment_budget as budget,private_records as pr
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from test_item4_native_synthetic import unreserved,unreserved_fixture,inventory_fixture,experiment,root,reserve
from test_modal_environment_budget import asset
REAL_QUALIFY=q.qualify

@pytest.fixture
def successor(unreserved,monkeypatch,tmp_path):
 f=unreserved;monkeypatch.setattr(q,'qualify',REAL_QUALIFY)
 state=tmp_path/'original';pr.mkdir(state);pr.mkdir(state/'provider')
 oldbinding=copy.deepcopy(f.binding);oldbinding['operation_id']='item4-author11-native-synthetic-v1'
 old={'id':q.OLD_ID,'run':n.RUN,'binding':canonical(oldbinding).decode(),'status':'UNCERTAIN','reserved_micro_usd':1118950,'receipt':'{"original":"failure"}'}
 f.accounts.db.execute('INSERT INTO autonomy_assets VALUES(?,?,?,?,?,?)',tuple(old.values()))
 out={'status':'FAIL','package_unchanged':True,'native':None,'observed_environment':n.selected()['environment']['expected'],
 'patient_data':False,'network_permission':False,'gpu':False,'scientific_approval':False,'console_truncated':False,
 'failure':"TypeError: nnUNetDatasetBlosc2.__init__() got an unexpected keyword argument 'case_identifiers'"}
 records={'provider/terminal.json':{'exit_code':1},'provider/sandbox.json':{'binding_sha256':q.OLD_ID,'provider_id':'sb-01M4E2P4TXD5JZA20YTKDSNWAA'},'FAILED.json':{'provider_id':'sb-01M4E2P4TXD5JZA20YTKDSNWAA','no_automatic_retry':True},'provider/stdout.bin':out}
 for name,v in records.items():pr.write_bytes(state/name,canonical(v))
 proof={'asset':old,'asset_sha256':digest(canonical(old)),'files':{x.relative_to(state).as_posix():{'bytes':x.stat().st_size,'sha256':digest(x.read_bytes())} for x in state.rglob('*') if x.is_file()}}
 monkeypatch.setattr(q,'OLD_STATE',state);monkeypatch.setattr(q,'proof',lambda:proof)
 secondstate=tmp_path/'second-original';pr.mkdir(secondstate);pr.mkdir(secondstate/'provider')
 secondbinding=copy.deepcopy(f.binding);secondbinding['operation_id']='item4-author12-native-synthetic-v1'
 second={**old,'id':q.SECOND_ID,'binding':canonical(secondbinding).decode()}
 f.accounts.db.execute('INSERT INTO autonomy_assets VALUES(?,?,?,?,?,?)',tuple(second.values()))
 secondrecords=copy.deepcopy(records)
 secondrecords['provider/stdout.bin']['failure']="AttributeError: 'nnUNetDatasetBlosc2' object has no attribute 'keys'"
 secondrecords['provider/sandbox.json']={'binding_sha256':q.SECOND_ID,'provider_id':'sb-01M4F2SETPJC7D6C62Y0APCC06'}
 secondrecords['FAILED.json']['provider_id']='sb-01M4F2SETPJC7D6C62Y0APCC06'
 for name,v in secondrecords.items():pr.write_bytes(secondstate/name,canonical(v))
 secondproof={'asset':second,'asset_sha256':digest(canonical(second)),'files':{x.relative_to(secondstate).as_posix():{'bytes':x.stat().st_size,'sha256':digest(x.read_bytes())} for x in secondstate.rglob('*') if x.is_file()}}
 monkeypatch.setattr(q,'SECOND_STATE',secondstate);monkeypatch.setattr(q,'second_proof',lambda:secondproof)
 f.predecessor=old;f.second=second;f.proof=proof;f.secondproof=secondproof;f.oldstate=state;f.secondstate=secondstate;return f

def test_successor_admits_once_and_never_releases_original(successor):
 f=successor;assert reserve(f) is True
 rows=[dict(x) for x in f.accounts.db.execute('SELECT * FROM autonomy_assets')]
 assert next(x for x in rows if x['id']==q.OLD_ID)==f.predecessor
 assert next(x for x in rows if x['id']==q.SECOND_ID)==f.second
 assert sum(x['reserved_micro_usd'] for x in rows)==2*1118950+f.binding['envelope']['cost']['reserved_micro_usd']
 assert reserve(f) is False and not f.calls
 f.binding['installed_config_sha256']='f'*64
 with pytest.raises(ValueError,match='ALREADY_RESERVED_NO_RETRY'):reserve(f)
 assert [dict(x) for x in f.accounts.db.execute('SELECT * FROM autonomy_assets')]==rows

@pytest.mark.parametrize('damage',['missing','active','amount','receipt','file','extra','symlink','cause','model','unknown-asset','image','gpu','owner','authority'])
def test_unknown_changed_or_active_previous_cannot_admit(successor,monkeypatch,damage):
 f=successor
 if damage=='missing':f.accounts.db.execute('DELETE FROM autonomy_assets WHERE id=?',(q.OLD_ID,))
 elif damage=='active':f.accounts.db.execute("UPDATE autonomy_assets SET status='RESERVED' WHERE id=?",(q.OLD_ID,))
 elif damage=='amount':f.accounts.db.execute('UPDATE autonomy_assets SET reserved_micro_usd=0 WHERE id=?',(q.OLD_ID,))
 elif damage=='receipt':f.accounts.db.execute("UPDATE autonomy_assets SET receipt='{}' WHERE id=?",(q.OLD_ID,))
 elif damage=='file':pr.write_bytes(f.oldstate/'provider/terminal.json',b'{}')
 elif damage=='extra':pr.write_bytes(f.oldstate/'unexpected.json',b'{}')
 elif damage=='symlink':(f.oldstate/'alias').symlink_to(f.oldstate/'FAILED.json')
 elif damage=='cause':
  v=json.loads((f.oldstate/'provider/stdout.bin').read_bytes());v['failure']='different cause';raw=canonical(v);pr.write_bytes(f.oldstate/'provider/stdout.bin',raw)
  f.proof['files']['provider/stdout.bin']={'bytes':len(raw),'sha256':digest(raw)}
 elif damage=='model':f.accounts.db.execute("INSERT INTO autonomy_calls VALUES('active','scientific','run',1,'2026-10-09','RUNNING','{}',NULL)")
 elif damage=='unknown-asset':asset(f.accounts.batch,1,ident='unknown',status='UNCERTAIN')
 elif damage=='image':f.binding['image_id']='im-other'
 elif damage=='gpu':f.binding['envelope']['resources']['gpu']='H100'
 elif damage=='owner':f.binding['owner_sha256']='e'*64
 else:monkeypatch.setattr(q,'proof',lambda:(_ for _ in ()).throw(ValueError('NATIVE_SUCCESSOR_AUTHORITY_CHANGED')))
 rows=[tuple(x) for x in f.accounts.db.execute('SELECT * FROM autonomy_assets')]
 with pytest.raises((ValueError,OSError)):reserve(f)
 assert rows==[tuple(x) for x in f.accounts.db.execute('SELECT * FROM autonomy_assets')] and not f.calls

def test_retry_that_exceeds_smoke_cap_still_refused(successor):
 f=successor;amount=f.binding['envelope']['cost']['reserved_micro_usd']
 asset(f.accounts.batch,budget.SMOKE_CAP-2*1118950-amount+1)
 rows=[tuple(x) for x in f.accounts.db.execute('SELECT * FROM autonomy_assets')]
 with pytest.raises(ValueError,match='ITEM4_HARD_COST_CAP'):reserve(f)
 assert rows==[tuple(x) for x in f.accounts.db.execute('SELECT * FROM autonomy_assets')] and not f.calls

def test_production_proof_and_authority_are_byte_pinned(tmp_path,monkeypatch):
 original=q.proof();assert original['asset']['reserved_micro_usd']==1118950
 assert digest(canonical(original['asset']))==original['asset_sha256']
 changed=tmp_path/'proof.json';changed.write_bytes(q.PROOF.read_bytes()+b' ');monkeypatch.setattr(q,'PROOF',changed)
 with pytest.raises(ValueError,match='PROOF_CHANGED'):q.proof()

def test_production_authority_tamper_refuses(tmp_path,monkeypatch):
 altered=tmp_path/'authority.txt';altered.write_bytes(q.AUTHORITY.read_bytes()+b' ');monkeypatch.setattr(q,'AUTHORITY',altered)
 with pytest.raises(ValueError,match='AUTHORITY_CHANGED'):q.proof()

@pytest.mark.parametrize('damage',['source','running','state'])
def test_installer_refuses_before_writes(tmp_path,monkeypatch,damage):
 from tools import install_item4_native_runtime as install,item4_native_runtime as h
 record=tmp_path/'record';pr.mkdir(record);state=tmp_path/'new-state'
 old={'source':install.PRIOR_SOURCE,'unit':'synthetic.service'}
 if damage=='source':old['source']='0'*40
 if damage=='state':pr.mkdir(state)
 pr.write_bytes(record/'installed.json',canonical(old));monkeypatch.setattr(h,'RECORD',record);monkeypatch.setattr(h,'STATE',state)
 monkeypatch.setattr('orchestrator.manual_host_guard.trusted',pr.check)
 monkeypatch.setattr(install.subprocess,'check_output',lambda *a,**kw:'MainPID=9\nActiveState=active\n' if damage=='running' else 'MainPID=0\nActiveState=failed\n')
 before={str(x):x.read_bytes() for x in tmp_path.rglob('*') if x.is_file()}
 with pytest.raises(ValueError):install.upgrade(tmp_path/'packet',tmp_path/'review','a'*40,{}, {},{},b'{}')
 assert before=={str(x):x.read_bytes() for x in tmp_path.rglob('*') if x.is_file()}



def test_candidate_preflight_uses_installed_guard_despite_review_copy(tmp_path):
 import ast,subprocess,sys
 from types import SimpleNamespace
 from tools import install_item4_native_runtime as installer
 base=tmp_path/'installed';packet=tmp_path/'packet'
 for folder in [base/'orchestrator',base/'tools',packet/'source/orchestrator',packet/'source/tools']:
  folder.mkdir(parents=True,exist_ok=True);(folder/'__init__.py').write_text('')
 guard=base/'orchestrator/spending_continuation.py'
 guard.write_text('from pathlib import Path\nassert Path(__file__).resolve()==Path('+repr(str(guard))+')\n')
 (packet/'source/orchestrator/spending_continuation.py').write_text("raise RuntimeError('review copy must never execute')\n")
 tree=ast.parse(Path(installer.__file__).read_text())
 expression=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='candidate' for t in n.targets))
 program=eval(compile(ast.Expression(expression),'<installer-fixture>','eval'),{'h':SimpleNamespace(BASE=base),'packet':packet})
 # Execute the actual import prefix in a fresh process, with the same two
 # competing module locations. Remaining production DB work is not needed here.
 prefix=program[:program.index('from orchestrator import modal_native_successor')]
 prefix=prefix.replace('assert os.getuid()==os.getgid()==1003','assert True # test process identity')
 check="\nimport importlib\nm=importlib.import_module('orchestrator.spending_continuation')\nassert Path(m.__file__)==Path("+repr(str(guard))+")\n"
 subprocess.run([sys.executable,'-s','-B','-c',prefix+check],check=True,capture_output=True)
 unsafe=prefix.replace('from orchestrator import spending_continuation\n','')
 result=subprocess.run([sys.executable,'-s','-B','-c',unsafe+check],capture_output=True,text=True)
 assert result.returncode!=0 and 'review copy must never execute' in result.stderr

@pytest.mark.parametrize('damage',['missing','active','cost','receipt','file','cause','scope','extra'])
def test_second_predecessor_must_also_be_exact_and_terminal(successor,damage):
 f=successor
 if damage=='missing':f.accounts.db.execute('DELETE FROM autonomy_assets WHERE id=?',(q.SECOND_ID,))
 elif damage=='active':f.accounts.db.execute("UPDATE autonomy_assets SET status='RESERVED' WHERE id=?",(q.SECOND_ID,))
 elif damage=='cost':f.accounts.db.execute('UPDATE autonomy_assets SET reserved_micro_usd=1 WHERE id=?',(q.SECOND_ID,))
 elif damage=='receipt':f.accounts.db.execute("UPDATE autonomy_assets SET receipt='{}' WHERE id=?",(q.SECOND_ID,))
 elif damage=='file':pr.write_bytes(f.secondstate/'provider/terminal.json',b'{}')
 elif damage=='extra':pr.write_bytes(f.secondstate/'extra.json',b'{}')
 elif damage=='scope':
  v=json.loads(f.second['binding']);v['image_id']='im-changed';f.second['binding']=canonical(v).decode()
  f.secondproof['asset_sha256']=digest(canonical(f.second))
  f.accounts.db.execute('UPDATE autonomy_assets SET binding=? WHERE id=?',(f.second['binding'],q.SECOND_ID))
 else:
  v=json.loads((f.secondstate/'provider/stdout.bin').read_bytes());v['failure']='same original cause, not the diagnosed keys failure'
  raw=canonical(v);pr.write_bytes(f.secondstate/'provider/stdout.bin',raw)
  f.secondproof['files']['provider/stdout.bin']={'bytes':len(raw),'sha256':digest(raw)}
 rows=[tuple(x) for x in f.accounts.db.execute('SELECT * FROM autonomy_assets')]
 with pytest.raises(ValueError):reserve(f)
 assert rows==[tuple(x) for x in f.accounts.db.execute('SELECT * FROM autonomy_assets')] and not f.calls

def test_second_production_proof_tamper_refuses(tmp_path,monkeypatch):
 v=q.second_proof();assert v['asset']['id']==q.SECOND_ID and v['asset']['reserved_micro_usd']==1118950
 p=tmp_path/'second.json';p.write_bytes(q.SECOND_PROOF.read_bytes()+b' ');monkeypatch.setattr(q,'SECOND_PROOF',p)
 with pytest.raises(ValueError,match='SECOND_PROOF_CHANGED'):q.second_proof()
