"""Synthetic history tests. No model, provider, patient data, live ledger or approval."""
import copy
import json
from pathlib import Path
import pytest
from orchestrator import preparation_interleaving as pi


def history():
    rows=[]
    for n in range(76):
        rows.append({'id':pi.sha(('historical-'+str(n)).encode()),'kind':'scientific','change_id':pi.ITEM4_RUN,
                     'round':n+1,'day':'2026-10-10','status':'COMPLETE','binding':'{}','receipt':'{}'})
    lanes={}
    for key,prefix,pin in [('aggregate_analysis','aggregate-','a'*64),('colab_preparation','colab-','b'*64)]:
        run=prefix+pi.sha((pi.AUTHORITY+':'+pin).encode())[:24]
        lanes[key]={'run_id':run,'state':'/fixture/'+prefix+'state','plan':'/fixture/'+prefix+'plan.json',
                    'plan_sha256':'c'*64,'registry_sha256':pin}
    scope={'schema':pi.SCHEMA,'authority_sha256':pi.AUTHORITY,'source_sha':'d'*40,'ledger':'/fixture/batch',
        'lanes':lanes,'frozen_rows':{r['id']:pi.sha(pi.canonical(r)) for r in rows},'terminal_rows':{},
        'item4_scope':{'path':'/fixture/old-scope','sha256':'e'*64,'review_folder':'/fixture/review',
                      'review_sha256':'f'*64,'configuration':{'path':'/fixture/lane.json','sha256':'1'*64}}}
    return scope,rows


def new_row(scope,key,stage='run_spec_author',attempt=1,ordinal=1):
    run=scope['lanes'][key]['run_id'];ident=pi.identity(run,stage,attempt)
    return {'id':ident,'kind':'scientific','change_id':run,'round':ordinal,'day':'2026-10-10','status':'COMPLETE',
            'binding':json.dumps({'run_id':run,'stage':stage,'source':scope['source_sha']}),
            'receipt':json.dumps({'id':ident,'synthetic':True})}


def test_sequence_view_preserves_original_bytes_and_actual_count():
    scope,rows=history();original=pi.canonical(rows)
    rows.append(new_row(scope,'aggregate_analysis'))
    rows.append({'id':pi.identity(pi.ITEM4_RUN,'run_spec_author',24),'kind':'scientific','change_id':pi.ITEM4_RUN,
                 'round':39,'day':'2026-10-10','status':'COMPLETE','binding':json.dumps({'stage':'run_spec_author'}),'receipt':'{}'})
    rows.append(new_row(scope,'colab_preparation'))
    before=pi.canonical(rows)
    kept,ids,counts=pi.classify(scope,rows)
    assert len(rows)==79 and len(kept)==77 and len(ids)==2
    assert pi.canonical(rows)==before and pi.canonical(rows[:76])==original
    assert counts=={'aggregate_analysis':1,'colab_preparation':1}


@pytest.mark.parametrize('field,value',[('status','RUNNING'),('status','UNCERTAIN'),('kind','review'),('round',2)])
def test_open_uncertain_misclassified_or_out_of_order_row_refuses(field,value):
    scope,rows=history();r=new_row(scope,'aggregate_analysis');r[field]=value;rows.append(r)
    with pytest.raises(ValueError,match='PREPARATION_INTERLEAVING_'):pi.classify(scope,rows)


def test_changed_frozen_row_refuses():
    scope,rows=history();rows[0]['status']='UNCERTAIN'
    with pytest.raises(ValueError,match='ORIGINAL_CHANGED'):pi.classify(scope,rows)


def test_changed_new_source_refuses():
    scope,rows=history();r=new_row(scope,'aggregate_analysis');v=json.loads(r['binding']);v['source']='e'*40;r['binding']=json.dumps(v);rows.append(r)
    with pytest.raises(ValueError,match='PREPARATION_ROW_BINDING'):pi.classify(scope,rows)


def test_unknown_new_call_cannot_borrow_old_item4_identity():
    scope,rows=history();rows.append({**rows[-1],'id':'f'*64})
    with pytest.raises(ValueError,match='UNRELATED_NEW_ROW'):pi.classify(scope,rows)


def test_duplicate_and_skipped_attempt_refuse():
    scope,rows=history();r=new_row(scope,'aggregate_analysis');rows.extend([r,r])
    with pytest.raises(ValueError,match='DUPLICATE_ROW'):pi.classify(scope,rows)
    scope,rows=history();rows.append(new_row(scope,'aggregate_analysis',attempt=2))
    with pytest.raises(ValueError,match='PREPARATION_STAGE_ORDER'):pi.classify(scope,rows)


def test_exact_eight_per_lane_not_ninth_or_higher_attempt():
    scope,rows=history()
    for key in scope['lanes']:
        for index,(stage,n) in enumerate((pair for stage in pi.STAGES for pair in ((stage,1),(stage,2))),1):
            rows.append(new_row(scope,key,stage,n,index))
    kept,ids,counts=pi.classify(scope,rows)
    assert len(rows)==92 and len(ids)==16 and set(counts.values())=={8}
    rows.append(new_row(scope,'aggregate_analysis','run_spec_author',3,9))
    with pytest.raises(ValueError,match='PREPARATION_ROW_UNQUALIFIED'):pi.classify(scope,rows)


def test_scope_cannot_add_unknown_lane_or_change_authority():
    scope,rows=history();scope['lanes']['other']=scope['lanes']['aggregate_analysis']
    with pytest.raises(ValueError,match='LANES'):pi.classify(scope,rows)
    scope,rows=history();scope['authority_sha256']='0'*64
    with pytest.raises(ValueError,match='AUTHORITY'):pi.classify(scope,rows)


def test_default_hooks_leave_original_history_and_uncertainty_rules(monkeypatch):
    monkeypatch.setattr(pi,'_ACTIVE',None)
    scope,rows=history()
    assert pi.item4_sequence_view(None,rows) is rows
    assert pi.terminal_ids(None,'unknown','run_spec_author','x','y',{})==[]


@pytest.mark.parametrize('verdict,source,error',[('REVISE','d'*40,'IMPLEMENTATION_APPROVAL'),('REJECT','d'*40,'IMPLEMENTATION_APPROVAL'),('APPROVE','e'*40,'IMPLEMENTATION_APPROVAL')])
def test_runtime_refuses_missing_approval_or_wrong_source(tmp_path,monkeypatch,verdict,source,error):
    from orchestrator import autonomy_review
    scope,rows=history()
    monkeypatch.setattr(autonomy_review,'verify_result',lambda p:{'verdict':verdict,'source_sha':source})
    with pytest.raises(ValueError,match=error):pi.Overlay(scope,tmp_path)


def test_runtime_refuses_scope_not_in_approved_packet(tmp_path,monkeypatch):
    from orchestrator import autonomy_review,private_records
    scope,rows=history()
    monkeypatch.setattr(autonomy_review,'verify_result',lambda p:{'verdict':'APPROVE','source_sha':scope['source_sha']})
    private_records.write_text(tmp_path/'packet-manifest.json',json.dumps({'files':{'evidence/preparation-interleaving.json':'0'*64}}))
    with pytest.raises(ValueError,match='REVIEWED_SCOPE'):pi.Overlay(scope,tmp_path)


def test_actual_over_ceiling_rows_refuse_and_are_preserved():
    scope,rows=history()
    for n in range(20):
        rows.append({**rows[-1],'id':pi.sha(('unadmitted-'+str(n)).encode())})
    assert len(rows)==96
    before=pi.canonical(rows)
    with pytest.raises(ValueError,match='PREPARATION_INTERLEAVING_'):pi.classify(scope,rows)
    assert pi.canonical(rows)==before


@pytest.fixture
def admitted_history(tmp_path,monkeypatch):
    """Exercise real SQLite admission/owner/local receipts; only review authority stubbed."""
    from orchestrator import autonomy_accounting as aa,autonomy_limits as limits,private_records as pr
    from orchestrator import stocktake_recovery,stocktake_review_recovery,experiment_timeout_continuation,completed_run
    from orchestrator.manual_executor import ManualExecutor
    scope,rows=history()
    # Fixture rows remain frozen, with dates outside the admission UTC day.
    for row in rows:row['day']='2026-09-30'
    scope['frozen_rows']={r['id']:pi.sha(pi.canonical(r)) for r in rows}
    scope['ledger']=str(tmp_path/'batch')
    batch=aa.BatchAccounts(scope['ledger'])
    for row in rows:batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',tuple(row.values()))
    def verify(self):self.approval='f'*64;return {'verdict':'APPROVE','test_only':True}
    monkeypatch.setattr(pi.Overlay,'verify',verify)
    monkeypatch.setattr(pi,'_ACTIVE',None)
    monkeypatch.setattr(limits,'scientific_batch_allowance',lambda *a,**k:{'limit':79,'scoped_run_id':pi.ITEM4_RUN})
    monkeypatch.setattr(stocktake_recovery,'global_exception',lambda *a,**k:None)
    monkeypatch.setattr(stocktake_review_recovery,'admission',lambda *a,**k:None)
    monkeypatch.setattr(experiment_timeout_continuation,'global_exception',lambda *a,**k:None)
    monkeypatch.setattr(completed_run,'closed_ids',lambda *a,**k:[])
    old=tmp_path/'old';pr.mkdir(old)
    pr.write_text(old/'lane.json',json.dumps({'source':'e'*40}))
    ManualExecutor(old/'jobs.sqlite').db.close()
    scope['item4_scope']['configuration']['path']=str(old/'lane.json')
    locals={}
    for key,lane in scope['lanes'].items():
        state=tmp_path/key;pr.mkdir(state);raw=json.dumps({'test_only':True,'lane':key}).encode()
        lane['state']=str(state);lane['plan']=str(state/'preparation-plan.json');lane['plan_sha256']=pi.sha(raw)
        pr.write_bytes(state/'preparation-plan.json',raw)
        owner={'state':str(state),'run_id':lane['run_id'],'source':scope['source_sha'],
            'review_sha256':'f'*64,'plan_sha256':pi.sha(raw),key:{'synthetic':True}}
        pr.write_text(state/'lane.json',json.dumps({'backend':'analysis','item_number':4,'run_id':lane['run_id'],
            'source':scope['source_sha'],'owner_binding':owner,'plan_sha256':pi.sha(raw),key:{'synthetic':True}}))
        batch.db.execute("INSERT INTO autonomy_runs VALUES(?,?,'ACTIVE')",(lane['run_id'],json.dumps(owner)))
        locals[key]=ManualExecutor(state/'jobs.sqlite')
    overlay=pi.connect(scope,tmp_path/'test-review')
    yield scope,rows,batch,locals,overlay
    for local in locals.values():local.db.close()
    batch.db.close()


def complete_fixture_call(scope,batch,local,key,stage='run_spec_author',attempt=1):
    run=scope['lanes'][key]['run_id'];ident=pi.identity(run,stage,attempt)
    receipt={'input_sha256':'1'*64,'test_only':True}
    admission=batch.reserve_scientific(ident,run,stage,scope['source_sha'],receipt)
    final={**receipt,'id':ident,'batch_accounting':admission}
    local.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',(ident,stage,attempt,'COMPLETE',json.dumps(final)))
    batch.finish_scientific(ident,final,'COMPLETE')
    return admission,ident


def test_real_admission_interleaves_two_lanes_preserves_all_originals(admitted_history):
    scope,rows,batch,local,overlay=admitted_history
    before=pi.canonical(rows)
    a,_=complete_fixture_call(scope,batch,local['aggregate_analysis'],'aggregate_analysis')
    b,_=complete_fixture_call(scope,batch,local['colab_preparation'],'colab_preparation')
    assert a['batch_limit']==b['batch_limit']==95 and a['run_limit']==b['run_limit']==8
    allrows=overlay.rows(batch)
    assert len(allrows)==78 and pi.canonical(allrows[:76])==before
    assert overlay.sequence_view(batch,allrows)==rows
    assert overlay.extend(batch,{'limit':79,'scoped_run_id':pi.ITEM4_RUN})['preparation_interleaving']['actual_scientific_calls']==78


@pytest.mark.parametrize('status',['RUNNING','UNCERTAIN'])
def test_real_admission_refuses_unknown_open_row_without_reserving(admitted_history,status):
    scope,rows,batch,local,overlay=admitted_history
    batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('foreign','administrative','x',1,'2026-09-30',status,'{}',None))
    run=scope['lanes']['aggregate_analysis']['run_id'];ident=pi.identity(run,'run_spec_author',1)
    with pytest.raises(ValueError,match='BATCH_UNCERTAIN_OR_RUNNING_CALL'):
        batch.reserve_scientific(ident,run,'run_spec_author',scope['source_sha'],{})
    assert batch.status(ident)['status']=='NOT_RESERVED'
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==77
    assert not batch.db.in_transaction


def test_local_global_receipt_disagreement_blocks_next_lane(admitted_history):
    scope,rows,batch,local,overlay=admitted_history
    _,ident=complete_fixture_call(scope,batch,local['aggregate_analysis'],'aggregate_analysis')
    local['aggregate_analysis'].db.execute("UPDATE manual_calls SET receipt='{}' WHERE id=?",(ident,))
    run=scope['lanes']['colab_preparation']['run_id'];nextid=pi.identity(run,'run_spec_author',1)
    with pytest.raises(ValueError,match='LOCAL_GLOBAL_HISTORY'):
        batch.reserve_scientific(nextid,run,'run_spec_author',scope['source_sha'],{})
    assert batch.status(nextid)['status']=='NOT_RESERVED'


def test_real_ninth_call_refused_all_eight_still_count(admitted_history):
    scope,rows,batch,local,overlay=admitted_history
    for stage in pi.STAGES:
        for attempt in (1,2):complete_fixture_call(scope,batch,local['aggregate_analysis'],'aggregate_analysis',stage,attempt)
    run=scope['lanes']['aggregate_analysis']['run_id'];ident=pi.identity(run,'run_spec_author',3)
    with pytest.raises(ValueError,match='PREPARATION_INTERLEAVING_'):
        batch.reserve_scientific(ident,run,'run_spec_author',scope['source_sha'],{})
    assert batch.db.execute("SELECT count(*) FROM autonomy_calls WHERE change_id=?",(run,)).fetchone()[0]==8
    assert batch.status(ident)['status']=='NOT_RESERVED'
