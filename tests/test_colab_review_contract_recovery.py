import base64,copy,json,sqlite3
from pathlib import Path
from unittest.mock import patch
import pytest
from tools import colab_review_contract_recovery as r
from tools.deploy_manual_lane import bound
from orchestrator import private_records as pr
from orchestrator.manual_executor import ManualExecutor
from orchestrator.autonomy_accounting import BatchAccounts

def arguments():
    b=r.binding();return base64.b64decode(b['config_base64']),{'manual_state':[b['state']],'manual_account':[b['account']],'manual_calls':[]},[],False

def test_actual_exact_zero_call_original_qualifies():
    cfg,state=r.validate(*arguments());assert cfg['run_id']==r.RUN and state['rounds']=={}

@pytest.mark.parametrize('damage',['config','state','account','local_call','global_call','workspace'])
def test_changed_scope_or_any_admission_refuses(damage):
    args=copy.deepcopy(arguments())
    if damage=='config':args=list(args);args[0]+=b' '
    elif damage=='state':args[1]['manual_state'][0]['payload']='{}'
    elif damage=='account':args[1]['manual_account'][0]['payload']='{}'
    elif damage=='local_call':args[1]['manual_calls'].append({'id':'unexpected'})
    elif damage=='global_call':args[2].append({'id':'unexpected'})
    else:args=list(args);args[3]=True
    with pytest.raises(ValueError):r.validate(*args)

def test_real_sqlite_exact_config_correction_preserves_counts_owner_and_originals(tmp_path):
    raw,rows,_,_=arguments();cfg=json.loads(raw);lane=bound(tmp_path,str(r.LANE));pr.mkdir(lane,parents=True)
    local=ManualExecutor(lane/'jobs.sqlite')
    for table in ('manual_state','manual_account'):
        row=rows[table][0];keys=list(row);local.db.execute('INSERT INTO '+table+'('+','.join(keys)+') VALUES('+','.join('?' for _ in keys)+')',[row[k] for k in keys])
    local.db.close();batch=BatchAccounts(bound(tmp_path,str(r.LEDGER.parent)));batch.db.close()
    pr.write_bytes(lane/'lane.json',raw)
    owner=bound(tmp_path,cfg['owner_path']);pr.mkdir(owner.parent,parents=True,exist_ok=True);pr.write_bytes(owner,r.canonical(cfg['owner_binding']))
    root=Path(__file__).resolve().parents[1]
    original_plan=root.parent.parent/'colab-preparation-20261010/analysis-plan.server.json'
    plan=original_plan.read_bytes();assert r.sha(plan)==cfg['plan_sha256'];pr.write_bytes(lane/'preparation-plan.json',plan)
    approved={'verdict':'APPROVE','report_sha256':'a'*64,'change_id':r.CHANGE}
    with patch.object(r,'approval',return_value=approved),patch.object(r.os,'getuid',return_value=1003),patch.object(r.os,'getgid',return_value=1003):
        result=r.apply(tmp_path/'synthetic-review',root=tmp_path,check_unit=lambda:None)
        assert result['status']=='CORRECTED_READY_NO_CALL'
        current=json.loads((lane/'lane.json').read_bytes());assert current=={**cfg,'review_contract':'bound-review/v1'}
        with sqlite3.connect(lane/'jobs.sqlite') as db:
            db.row_factory=sqlite3.Row;after=r.snapshot(db)
            assert after['manual_calls']==[] and after['manual_account']==rows['manual_account']
            state=json.loads(after['manual_state'][0]['payload']);assert state['phase']=='run_spec_author' and state['rounds']=={} and not state.get('pending')
        dest=bound(tmp_path,str(r.RECORD));assert (dest/'lane.original.json').read_bytes()==raw
        assert json.loads((dest/'original-rows.json').read_bytes())==rows
        assert json.loads(owner.read_bytes())==cfg['owner_binding'] and (lane/'preparation-plan.json').read_bytes()==plan
        with pytest.raises(ValueError,match='EXISTING_OUTCOME_PRESERVED'):r.apply(tmp_path/'synthetic-review',root=tmp_path,check_unit=lambda:None)
