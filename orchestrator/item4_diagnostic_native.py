"""Exact author20 native admission; preserves historical proofs and every charge."""
from pathlib import Path
import hashlib,json,subprocess
from orchestrator.modal_executor import canonical
from orchestrator.review_contract import strict_json
from orchestrator import private_records as pr

ROOT=Path(__file__).resolve().parents[1]
RETAINED='docs/ITEM4_DIAGNOSTIC_NATIVE_RETAINED_PRIVATE.json'
RETAINED_SHA='9bdcdaa8704dbe8548aff8884ffddaaa1a04b92707c102bb81d04765a2f78521'
ACCEPTED='docs/ITEM4_DIAGNOSTIC_NATIVE_ACCEPTED_PRIVATE.json'
ACCEPTED_SHA='fca5931dd8fba48d54a63a94e084633dc5feed4708cf12ff7bbdbc78d0772675'
OPERATOR='5748a56f92c8aa0048fdd94194038749737eb648e62da097a128ffa85c68ca33'
STAGE_CAP=150_000_000
DIAGNOSTIC_CAP=25_000_000
FITS=frozenset({'smoke-cpu-A16','smoke-cpu-B32'})
OLD_NATIVE=frozenset({'5679c16fedb876f53ac9fcc39fac4c885c1cb245292e3fde7cc0664403b3a46f',
 '1b516eb5c8472d29d95c9795b8cd37fd722ab45f52bc244531c9786b6c1e7ccf',
 '40860aa053572ffc0571e45c89b950eaf813725b107f981ad18d5b9921cdb59c'})

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('DIAGNOSTIC_NATIVE_'+why)

def document(name,pin):
    raw=(ROOT/name).read_bytes();require(sha(raw)==pin,'DOCUMENT_CHANGED')
    return strict_json(raw)

FAILED_ASSET='27146f38f1722579ed096a880f59cc607bc36e993fe57634b6ffe271ae92c157'
CORRECTED='docs/ITEM4_CORRECTED_NATIVE_REVIEW_PRIVATE.json'
CORRECTED_SHA='b8988329f73cc1838829b68750a36fdf661039782276f3183d70c851a8751e67'

def historical_asset(row):
    if dict(row).get('id')==FAILED_ASSET:
        require(dict(row)==document(CORRECTED,CORRECTED_SHA)['original_failed_asset'],'FAILED_ROW_CHANGED')
        return True
    if dict(row).get('id') not in OLD_NATIVE:return False
    proof=document(RETAINED,RETAINED_SHA)
    require(dict(row)==proof['native_rows'][row['id']],'HISTORICAL_ASSET_CHANGED')
    return True

def limit(binding):
    from orchestrator import modal_native_synthetic as n,item4_stage1_cap
    require(binding.get('purpose')==n.PURPOSE and binding.get('operation_id')==n.OPERATION
        and binding.get('run_id')==n.RUN,'FIXED_OPERATION')
    selected=n.selected(binding.get('native_synthetic'))
    require(selected['author_attempt']==20 and selected['module_sha256']==
        '501cb5b8e8487a2b73f1e139fe5cc96cb6c3315c1c8832ffefd351e31f5c8749'
        and selected['code_bundle_sha256']=='dc145614124687fea4fa4c4386720866259f1bae6b26f3a16f21f8a8a1495159',
        'ACCEPTED_SELECTION')
    require(sha((ROOT/'docs/ITEM4_CPU_DIAGNOSTIC_OPERATOR_DECISION.txt').read_bytes())==OPERATOR
        and sha((ROOT/item4_stage1_cap.DOCUMENT).read_bytes())==item4_stage1_cap.OPERATOR_SHA,'OPERATOR_CHANGED')
    from tools.item4_diagnostic_native_runtime import authority
    authority()  # Genuine independent APPROVE and exact installed closure.
    return STAGE_CAP

def retained_terminal(accounts,binding):
    limit(binding)
    frozen=document(RETAINED,RETAINED_SHA)
    raw=subprocess.check_output(['/usr/bin/python3','-s','-B',str(ROOT/'tools/item4_validation_retained.py'),
        '--diagnostic-native'],timeout=120)
    proof=strict_json(raw)
    require(proof==frozen,'RETAINED_PROOF_CHANGED')
    for kind,table in [('assets','autonomy_assets'),('native_ready','autonomy_assets'),('compute','autonomy_compute'),('closed_calls','autonomy_calls')]:
        for ident,pin in proof[kind].items():
            row=accounts.db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone()
            require(row is not None and sha(canonical(dict(row)))==pin,'RETAINED_ROW_CHANGED')
    # Qualify this one positively terminal FAIL through its original installed
    # verifier. Its UNCERTAIN row and full reservation remain immutable.
    raw=subprocess.check_output(['/usr/bin/python3','-s','-B',str(ROOT/'tools/item4_validation_retained.py'),
        '--diagnostic-failure'],timeout=120)
    require(strict_json(raw)=={'source':'81cd8225365a26944128ab5eb3fceda9e36d5f3d',
        'implementation_review_sha256':'b5dfa4bf3c7d3bb45733dd7bffcf8aa5a4344cfc99a16dbdb7468e292f28679a',
        'asset_id':FAILED_ASSET,'module_sha256':'8a6e446bfc96f2240c25716a2f56e2b367c56c9d220647805efd701f627c092b',
        'exit_code':1,'status':'FAIL','package_unchanged':True,'scientific_acceptance':False,
        'no_automatic_retry':True},'ORIGINAL_NATIVE_FAILURE')
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(FAILED_ASSET,)).fetchone()
    require(row is not None and historical_asset(row),'FAILED_ROW_REQUIRED')
    return set(proof['assets'])|set(proof['native_ready'])|{FAILED_ASSET},set(proof['compute'])

def subcap(accounts,assets,compute,asset_amounts,snapshot,amount):
    """Count diagnostic preparations and fits, including every unreleased row.

    No release rule is added: assets use the existing qualified effective cost,
    compute uses existing terminal/billing high-water logic on the selected rows.
    """
    from orchestrator import modal_native_synthetic as n,modal_terminal_cost
    selected_assets=[r for r in assets if strict_json(r['binding']).get('purpose')==n.PURPOSE]
    selected_compute=[r for r in compute if strict_json(r['binding']).get('experiment',{}).get('fit_id') in FITS]
    require(all(r['run']==n.RUN for r in [*selected_assets,*selected_compute]),'DIAGNOSTIC_COST_OWNER')
    costs=modal_terminal_cost.exposure(accounts.db,selected_compute,snapshot)
    used=sum(asset_amounts[r['id']] for r in selected_assets)+sum(costs['run_cost'].values())
    require(type(amount) is int and amount>=0 and used+amount<=DIAGNOSTIC_CAP,'HARD_DIAGNOSTIC_CAP')
    require(not costs['underestimated_apps'],'DIAGNOSTIC_COST_BOUND_BELOW_BILLING')
    return used
