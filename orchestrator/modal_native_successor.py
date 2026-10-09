"""Exact closed-failure qualification for the accepted author13 synthetic retry.

Original UNCERTAIN row and full reservation stay untouched. No generic retry,
no cost release, no provider calls. All unknown or changed predecessors refuse.
"""
from pathlib import Path
import json
from orchestrator.manual_executor import digest
from orchestrator.modal_executor import canonical
from orchestrator import private_records as pr
from orchestrator.review_contract import strict_json

OLD_ID='5679c16fedb876f53ac9fcc39fac4c885c1cb245292e3fde7cc0664403b3a46f'
OLD_STATE=Path('/var/lib/research-system-manual-sprint10/environment-inventory/item4-author11-native-synthetic-v1')
PROOF=Path(__file__).resolve().parents[1]/'docs/ITEM4_NATIVE_AUTHOR12_PREDECESSOR_20261009.json'
PROOF_SHA='ec5cbc4340edc82a43b7d4aac2a67eebd8764337d01b0f5d33726b54c1c5794f'
SECOND_ID='1b516eb5c8472d29d95c9795b8cd37fd722ab45f52bc244531c9786b6c1e7ccf'
SECOND_STATE=OLD_STATE.with_name('item4-author12-native-synthetic-v1')
SECOND_PROOF=PROOF.with_name('ITEM4_NATIVE_AUTHOR13_PREDECESSOR_20261009.json')
SECOND_PROOF_SHA='dcbcbe4a5b2ad6500c5da95ba2f2816e1eca503fe16294e2b4bae01e25760914'
AUTHORITY=PROOF.with_name('ITEM4_SMOKE_RETRY_OPERATOR_DECISION_20261009.txt')
AUTHORITY_SHA='8f645432a26ba2030392d2d390950252c4c8be075c87c3fca9d3dd9646ff1ec1'

def require(ok,why):
 if not ok:raise ValueError('NATIVE_SUCCESSOR_'+why)

def proof():
 raw=PROOF.read_bytes();require(digest(raw)==PROOF_SHA,'PROOF_CHANGED')
 require(digest(AUTHORITY.read_bytes())==AUTHORITY_SHA,'AUTHORITY_CHANGED')
 return strict_json(raw)

def second_proof():
 raw=SECOND_PROOF.read_bytes();require(digest(raw)==SECOND_PROOF_SHA,'SECOND_PROOF_CHANGED')
 proof() # Original authority and prior proof remain independently pinned.
 return strict_json(raw)

def previous_asset(row):
 ident=dict(row).get('id')
 if ident not in {OLD_ID,SECOND_ID}:return False
 expected=proof() if ident==OLD_ID else second_proof();value=dict(row)
 require(value==expected['asset'] and digest(canonical(value))==expected['asset_sha256'],'OLD_ASSET_CHANGED')
 require(value['status']=='UNCERTAIN' and value['reserved_micro_usd']==1118950,'OLD_RESERVATION')
 return True

def _qualify_one(accounts,binding,ident,root,v,provider_id,cause):
 from orchestrator import modal_native_synthetic as n
 n.selected(binding['native_synthetic'])
 require(binding['operation_id']=='item4-author13-native-synthetic-v1','FIXED_SUCCESSOR')
 row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
 require(row is not None and previous_asset(row),'PREDECESSOR_REQUIRED')
 old=strict_json(row['binding']);s=n.selected()
 require(all(binding[k]==old[k] for k in ('purpose','run_id','authority_sha256','team_authority_sha256','owner_sha256','image_id','base_image','worker_sha256','envelope')),'SCOPE_CHANGED')
 require(s['environment']==old['native_synthetic']['environment'] and s['author_attempt']==13,'SCIENTIFIC_ENVIRONMENT_CHANGED')
 pr.check_tree(root)
 require(not any(p.is_symlink() for p in root.rglob('*')),'OLD_ALIAS')
 files={p.relative_to(root).as_posix():{'bytes':p.stat().st_size,'sha256':digest(pr.check(p).read_bytes())} for p in root.rglob('*') if p.is_file()}
 require(files==v['files'],'ORIGINAL_FILES_CHANGED')
 terminal=strict_json(pr.check(root/'provider/terminal.json').read_bytes())
 handle=strict_json(pr.check(root/'provider/sandbox.json').read_bytes())
 failure=strict_json(pr.check(root/'FAILED.json').read_bytes())
 raw=pr.check(root/'provider/stdout.bin').read_bytes();result=strict_json(raw)
 require(terminal['exit_code']==1 and handle['binding_sha256']==ident
  and handle['provider_id']==provider_id
  and failure['provider_id']==handle['provider_id'] and failure['no_automatic_retry'] is True,'TERMINAL_FAILURE')
 require(result['status']=='FAIL' and result['package_unchanged'] is True
  and result['native'] is None and result['observed_environment']==s['environment']['expected']
  and all(result[k] is False for k in ('patient_data','network_permission','gpu','scientific_approval','console_truncated'))
  and cause in result['failure'],'DIAGNOSED_CAUSE')
 require(not accounts.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'MODEL_RUNNING')
 return ident


def qualify(accounts,binding):
 # Both terminal failures qualify separately; neither row or reservation changes.
 first=_qualify_one(accounts,binding,OLD_ID,OLD_STATE,proof(),
  'sb-01M4E2P4TXD5JZA20YTKDSNWAA',
  "TypeError: nnUNetDatasetBlosc2.__init__() got an unexpected keyword argument 'case_identifiers'")
 second=_qualify_one(accounts,binding,SECOND_ID,SECOND_STATE,second_proof(),
  'sb-01M4F2SETPJC7D6C62Y0APCC06',
  "AttributeError: 'nnUNetDatasetBlosc2' object has no attribute 'keys'")
 return {first,second}
