"""Exact author21 native admission; preserves historical proofs and every charge."""
from pathlib import Path
import hashlib,json,subprocess
from orchestrator.modal_executor import canonical
from orchestrator.review_contract import strict_json
from orchestrator import private_records as pr

ROOT=Path(__file__).resolve().parents[1]
RETAINED='docs/ITEM4_DIAGNOSTIC_NATIVE_RETAINED_PRIVATE.json'
RETAINED_SHA='9bdcdaa8704dbe8548aff8884ffddaaa1a04b92707c102bb81d04765a2f78521'
ACCEPTED='docs/ITEM4_DIAGNOSTIC_NATIVE_ACCEPTED_PRIVATE.json'
ACCEPTED_SHA='a84d45d1a77b3cf400760bdd3ef2a06d6b8c2d79eca27721cfac332ea3337748'
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
SECOND_FAILED_ASSET='8c40fe36f279a1bab97dab6b2c59bf8f45d7e2901f508f36c1dac0f0a2c01653'
CORRECTED='docs/ITEM4_CORRECTED_NATIVE_REVIEW_PRIVATE.json'
CORRECTED_SHA='1d035fef5b3fe6e5de2e03c068a10d401c4a3a6285074f552a7e0a4ef6d176ff'
THIRD_FAILED_ASSET='81e4dd6571ee65c4b0f7b6a6ff9c8732c66d15bee2f6738b8c0336c4b81398cf'
PROGRESS='docs/ITEM4_PROGRESS_NATIVE_FAILURE_PRIVATE.json'
PROGRESS_SHA='c32de52dcb830296f305c3fcc2aff8ca7fb81d361418fb3522f0dcfe2a9eed9a'

def progress_failure():
    frozen=document(PROGRESS,PROGRESS_SHA)
    raw=subprocess.check_output(['/usr/bin/python3','-s','-B',str(ROOT/'tools/item4_validation_retained.py'),
        '--diagnostic-progress-failure'],timeout=120)
    require(strict_json(raw)==frozen['qualification'],'THIRD_NATIVE_FAILURE')
    return frozen


def historical_asset(row):
    if dict(row).get('id')==THIRD_FAILED_ASSET:
        require(dict(row)==document(PROGRESS,PROGRESS_SHA)['third_failed_asset'],'THIRD_FAILED_ROW_CHANGED')
        return True
    if dict(row).get('id')==SECOND_FAILED_ASSET:
        require(dict(row)==document(CORRECTED,CORRECTED_SHA)['second_failed_asset'],'SECOND_FAILED_ROW_CHANGED')
        return True
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
    require(selected['author_attempt']==21 and selected['module_sha256']==
        'fa54d6e41db935c4a7671abe278d4a40423bda41cfce32692b58ed1364638d20'
        and selected['code_bundle_sha256']=='6c035d8131600a6e4e026757f3fab7e2502d719136939f2866500e7cbe72a3e5',
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
    raw=subprocess.check_output(['/usr/bin/python3','-s','-B',str(ROOT/'tools/item4_validation_retained.py'),
        '--diagnostic-audit-failure'],timeout=120)
    require(strict_json(raw)=={'source':'b60badd65283e7df5f801a6a6a20b3fd63504544',
        'implementation_review_sha256':'35aeaa0a9d6836f4caa5bf7033434b43952bb242777d4376a91259eee0ba5bb9',
        'asset_id':SECOND_FAILED_ASSET,'module_sha256':'501cb5b8e8487a2b73f1e139fe5cc96cb6c3315c1c8832ffefd351e31f5c8749',
        'exit_code':1,'status':'FAIL','package_unchanged':True,'scientific_acceptance':False,
        'no_automatic_retry':True},'SECOND_NATIVE_FAILURE')
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(SECOND_FAILED_ASSET,)).fetchone()
    require(row is not None and historical_asset(row),'SECOND_FAILED_ROW_REQUIRED')
    progress_failure()
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(THIRD_FAILED_ASSET,)).fetchone()
    require(row is not None and historical_asset(row),'THIRD_FAILED_ROW_REQUIRED')
    return set(proof['assets'])|set(proof['native_ready'])|{FAILED_ASSET,SECOND_FAILED_ASSET,THIRD_FAILED_ASSET},set(proof['compute'])

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


def closed_native_amounts(accounts,qualified,billing,amounts,*,include_later=False):
    """Release only excess CPU/RAM reservation of the two proven closed failures.

    Every original row and its full reservation remain immutable. The original
    one-dollar overhead allowance stays committed until its obligations settle.
    Actual per-app billing uses a persistent hourly high-water mark.
    """
    require(type(include_later) is bool,'CLOSED_COST_SELECTION')
    ids={r[0] for r in accounts.db.execute('SELECT id FROM autonomy_assets')}
    if not ({FAILED_ASSET,SECOND_FAILED_ASSET}&ids):return dict(amounts)
    from decimal import Decimal
    from orchestrator.item4_closed_attempt_billing import snapshot,instant
    from orchestrator.modal_billing import decimal,micros
    snapshot(billing)
    require(billing['workspace']=='moroseui' and
        instant(billing['report_start'])<=instant('2026-10-10T00:00:00+00:00') and
        instant(billing['report_end_exclusive'])>=instant('2026-10-10T13:00:00+00:00'),
        'CLOSED_BILLING_WINDOW')
    selected={FAILED_ASSET:('original_failed_asset',25123),SECOND_FAILED_ASSET:('second_failed_asset',23472)}
    frozen=document(CORRECTED,CORRECTED_SHA);views=[billing]
    selected={ident:(frozen[field],floor) for ident,(field,floor) in selected.items()}
    if include_later:
        later=document('docs/ITEM4_CLOSED_NATIVE_LATER_COST_PRIVATE.json','c004b4a3850131138573b6d050c057edb7351f74333b38294530a57826f71ae4')
        require(set(later['rows'])==set(later['actual_floor_micro_usd'])=={THIRD_FAILED_ASSET,'1e5bb3d0f1f807a99039e106cba34a40e9400dd01aae16c1f3e7212165d91d49'}
            and instant(billing['report_end_exclusive'])>=instant('2026-10-10T16:00:00+00:00'),'LATER_CLOSED_BILLING_WINDOW')
        selected.update({ident:(row,later['actual_floor_micro_usd'][ident]) for ident,row in later['rows'].items()})
        views.append(later['billing'])
    for row in accounts.db.execute("SELECT id,payload FROM events WHERE id LIKE 'item4-billing:%'"):
        saved=strict_json(row['payload'])
        require(row['id']=='item4-billing:'+sha(row['payload'].encode()) and
            saved['schema']=='item4-billing-highwater/v1','BILLING_HIGHWATER_CHANGED')
        views.append(saved['snapshot'])
    result=dict(amounts);apps=set()
    for ident,(frozen_row,floor) in selected.items():
        require(ident in qualified,'CLOSED_TERMINAL_QUALIFICATION_REQUIRED')
        row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
        require(row is not None and dict(row)==frozen_row and row['status']=='UNCERTAIN','CLOSED_ROW_CHANGED')
        receipt=strict_json(row['receipt']);app=receipt['app_id'];require(app not in apps,'SHARED_BILLING_APP');apps.add(app)
        hours={}
        for view in views:
            snapshot(view);require(view['workspace']==billing['workspace'],'BILLING_WORKSPACE')
            for item in view['rows']:
                if item['object_id']==app:
                    key=item['interval_start'];hours[key]=max(hours.get(key,Decimal(0)),decimal(item['cost']))
        require(bool(hours),'CLOSED_BILLING_MISSING')
        actual=max(floor,micros(sum(hours.values(),Decimal(0))))
        cost=strict_json(row['binding'])['envelope']['cost']
        require(cost['reserved_micro_usd']==row['reserved_micro_usd']==1118950 and
            cost['compute_micro_usd']==118950 and cost['overhead_micro_usd']==1000000,'CLOSED_ENVELOPE')
        value={'schema':'item4-closed-native-cost/v1','asset_id':ident,'original_reserved_micro_usd':1118950,
            'actual_compute_micro_usd':actual,'retained_overhead_micro_usd':1000000,
            'effective_micro_usd':actual+1000000,'excess_compute_released_micro_usd':max(0,118950-actual),
            'terminal_exit_code':1,'original_rows_changed':False,'invoice_final':False,
            'billing_snapshot_sha256':sha(canonical(billing))}
        raw=canonical(value).decode();event=ident+':closed-native-cost:'+sha(raw.encode())
        previous=accounts.db.execute('SELECT job,payload FROM events WHERE id=?',(event,)).fetchone()
        require(previous is None or tuple(previous)==(row['run'],raw),'CLOSED_COST_EVENT_CHANGED')
        if previous is None:accounts.db.execute('INSERT INTO events VALUES(?,?,?)',(event,row['run'],raw))
        result[ident]=value['effective_micro_usd']
    for table in ('autonomy_assets','autonomy_compute'):
        for row in accounts.db.execute('SELECT * FROM '+table):
            if table=='autonomy_assets' and row['id'] in selected:continue
            binding=strict_json(row['binding']);receipt=strict_json(row['receipt']) if dict(row).get('receipt') else {}
            require(receipt.get('app_id') not in apps and binding.get('app_id') not in apps and
                binding.get('experiment',{}).get('billing_object_id') not in apps,'SHARED_BILLING_APP')
    return result
