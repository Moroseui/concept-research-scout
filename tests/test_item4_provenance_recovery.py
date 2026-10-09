"""Synthetic exact-state recovery tests; no native/model/provider calls."""
import json
import sqlite3
from pathlib import Path
import pytest
from tools import recover_item4_provenance_20261008 as h


@pytest.fixture
def fixture(tmp_path, monkeypatch):
    root=tmp_path/'release';root.mkdir();globalroot=tmp_path/'reviews';globalroot.mkdir()
    monkeypatch.setattr(h,'ROOT',root);monkeypatch.setattr(h,'GLOBAL',globalroot)
    monkeypatch.setattr(h.os,'getuid',lambda:1003);monkeypatch.setattr(h.os,'getgid',lambda:1003)
    monkeypatch.setattr(h.subprocess,'check_output',lambda args,**k: args[2][:-6]+'.service\n' if 'Triggers' in args else ('MainPID=0\nControlGroup=\n' if '--property=MainPID,ControlGroup' in args else 'inactive\n'))
    authority=tmp_path/'authority';authority.write_bytes(b'SYNTHETIC mechanical recovery authority')
    runtime=tmp_path/'runtime.json';runtime.write_bytes(b'{"synthetic":true}')
    selected=tmp_path/'selected.json';selected.write_text(json.dumps({'source':'a'*40,'runtime':str(runtime)}))
    monkeypatch.setattr(h,'RUNTIME',runtime);monkeypatch.setattr(h,'SELECTED',selected);monkeypatch.setattr(h,'trusted',lambda x:Path(x))
    binding={'source':'a'*40,'call_id':'synthetic-author','lanes':{},'outputs':{},'authority_sha256':h.sha(authority.read_bytes()),'runtime_sha256':h.sha(runtime.read_bytes())}
    work=root/'item4/lane-scientific-workspaces/run_spec_author-3';work.mkdir(parents=True)
    outputs={'SPEC.proposed.md':b'unaccepted synthetic spec','notebook.patch.json':b'{"synthetic":true}', 'execution.plan.json':json.dumps({'preprocessing':[{'id':'prep-'+str(i),'input_contract_sha256':None,'source_capture_sha256':None} for i in range(7)]}).encode()}
    for n,raw in outputs.items():(work/n).write_bytes(raw)
    binding['outputs']={n:h.sha(v) for n,v in outputs.items()}
    globaldb=sqlite3.connect(globalroot/'jobs.sqlite');globaldb.row_factory=sqlite3.Row
    globaldb.execute('CREATE TABLE autonomy_calls(id TEXT,status TEXT,receipt TEXT)')
    globaldb.execute('INSERT INTO autonomy_calls VALUES(?,?,?)',('synthetic-author','COMPLETE','original charge'))
    globaldb.execute('CREATE TABLE autonomy_runs(id TEXT,binding TEXT,status TEXT)')
    binding['global_call_sha256']=h.sha(h.canonical(dict(globaldb.execute('SELECT * FROM autonomy_calls').fetchone())))
    configs={}
    for item,lane in [(6,root/'lane'),(4,root/'item4/lane')]:
        lane.mkdir(parents=True);context=lane/'context';context.mkdir();run='synthetic-item'+str(item)
        owner={'run_id':run,'source':binding['source']};ownerpath=lane/'owner.json';ownerpath.write_text(json.dumps(owner))
        config={'source':binding['source'],'run_id':run,'context':str(context),'owner_path':str(ownerpath),'owner_binding':owner}
        configs[item]=config;(lane/'lane.json').write_text(json.dumps(config));(lane/'DECISION_REQUEST.md').write_text('original blocked request')
        value={'phase':'BLOCKED' if item==4 else 'EXECUTE_EXPERIMENT','rounds':{'run_spec_author':3} if item==4 else {'run_spec_author':4,'run_spec_review':3},'artifacts':[],'interventions':[]}
        if item==4:value['artifacts']=[{'id':'timeout-original-'+n,'type':'configuration','version':1,'path':'old/'+n,'sha256':'0'*64} for n in ['SPEC','PLAN','PATCH','GUIDANCE']]
        if item==4:value.update(reason='OUTPUT_VALIDATION_REFUSED: EXPERIMENT_DECLARED_PREPROCESSING_SCOPE',blocked_stage='run_spec_author',pending={'id':binding['call_id'],'workspace':str(work),'stage':'run_spec_author','round':3})
        db=sqlite3.connect(lane/'jobs.sqlite');db.row_factory=sqlite3.Row
        db.execute('CREATE TABLE manual_state(id INTEGER,payload TEXT)');raw=json.dumps(value);db.execute('INSERT INTO manual_state VALUES(1,?)',(raw,))
        db.execute('CREATE TABLE manual_calls(id TEXT,stage TEXT,status TEXT,receipt TEXT)')
        if item==4:
            db.execute('INSERT INTO manual_calls VALUES(?,?,?,?)',('original-timeout','run_spec_author','UNCERTAIN','original retained charge'))
            db.execute('INSERT INTO manual_calls VALUES(?,?,?,?)',('second-complete','run_spec_author','COMPLETE','original charge'))
            db.execute('INSERT INTO manual_calls VALUES(?,?,?,?)',(binding['call_id'],'run_spec_author','COMPLETE','preserved'))
        db.execute('CREATE TABLE manual_account(id INTEGER,calls_used INTEGER)');db.execute('INSERT INTO manual_account VALUES(1,?)',(3 if item==4 else 0,));db.commit()
        binding['lanes'][str(item)]={'state_sha256':h.sha(raw.encode()),'config_sha256':h.sha((lane/'lane.json').read_bytes()),'calls_sha256':h.sha(h.canonical(h.rows(db,'manual_calls'))),'run_id':run,'accounting':h.accounting(db)};db.close()
        globaldb.execute('INSERT INTO autonomy_runs VALUES(?,?,?)',(run,json.dumps(owner),'ACTIVE'))
    globaldb.commit();globaldb.close()
    bf=tmp_path/'ITEM4_PROVENANCE_BINDINGS.json';bf.write_text(json.dumps(binding));monkeypatch.setattr(h,'BINDING_FILE',bf)
    approval=tmp_path/'approval';approval.mkdir();(approval/'packet-manifest.json').write_text(json.dumps({'source_files':{'tools/'+Path(h.__file__).name:h.sha(Path(h.__file__).read_bytes()),'tools/'+bf.name:h.sha(bf.read_bytes()),'tools/ITEM4_PROVENANCE_CONTEXT.txt':h.sha(Path(h.__file__).with_name('ITEM4_PROVENANCE_CONTEXT.txt').read_bytes())}}))
    monkeypatch.setattr(h,'verify_result',lambda _: {'verdict':'APPROVE','change_id':h.CHANGE,'report_sha256':'d'*64,'source_sha':'b'*40,'runtime_sha256':h.sha(runtime.read_bytes())})
    return root,globalroot,approval,authority,binding,outputs


def test_application_preserves_calls_counters_and_outputs_and_refuses_repeat(fixture):
    root,globalroot,approval,authority,binding,outputs=fixture
    result=h.apply(approval,authority,'b'*40);assert result['model_calls']==0 and result['additional_allowance']==0
    for item,lane in [(6,root/'lane'),(4,root/'item4/lane')]:
        db=sqlite3.connect(lane/'jobs.sqlite');db.row_factory=sqlite3.Row
        value=json.loads(db.execute('SELECT payload FROM manual_state').fetchone()[0])
        assert value['phase']==('run_spec_author' if item==4 else 'EXECUTE_EXPERIMENT')
        assert value['rounds']==({'run_spec_author':3} if item==4 else {'run_spec_author':4,'run_spec_review':3})
        assert db.execute('SELECT calls_used FROM manual_account').fetchone()[0]==(3 if item==4 else 0)
        assert h.sha(h.canonical(h.rows(db,'manual_calls')))==binding['lanes'][str(item)]['calls_sha256']
        assert 'pending' not in value
        if item==4:
            assert any(a['id']=='provenance-guidance' for a in value['artifacts'])
            assert not any(a['id'].startswith('timeout-original-') for a in value['artifacts'])
            assert (root/'provenance-recovery-20261008/item4-before.sqlite').exists()
        else:
            assert value['artifacts']==[] and value['interventions']==[]
        db.close()
    for n,raw in outputs.items():assert (root/'item4/lane-scientific-workspaces/run_spec_author-3'/n).read_bytes()==raw
    with pytest.raises(ValueError,match='EXISTING_RECOVERY'):h.apply(approval,authority,'b'*40)


@pytest.mark.parametrize('damage',['halt','running','global_charge','config','state','output','review','authority','active_service','helper_source','runtime','selected_source','local_allowance','item6_state'])
def test_other_outcomes_and_drift_refuse_before_recovery_writes(fixture,monkeypatch,damage):
    root,globalroot,approval,authority,_,_=fixture
    if damage=='halt':(globalroot/'HALT').write_text('stop')
    if damage in ('running','global_charge'):
        db=sqlite3.connect(globalroot/'jobs.sqlite');db.execute("UPDATE autonomy_calls SET status=?",('RUNNING' if damage=='running' else 'UNCERTAIN',));db.commit();db.close()
    if damage=='config':(root/'item4/lane/lane.json').write_text('{}')
    if damage=='state':
        db=sqlite3.connect(root/'item4/lane/jobs.sqlite');v=json.loads(db.execute('SELECT payload FROM manual_state').fetchone()[0]);v['reason']='GENUINE_REJECT';db.execute('UPDATE manual_state SET payload=?',(json.dumps(v),));db.commit();db.close()
    if damage=='local_allowance':
        db=sqlite3.connect(root/'item4/lane/jobs.sqlite');db.execute('UPDATE manual_account SET calls_used=0');db.commit();db.close()
    if damage=='item6_state':
        db=sqlite3.connect(root/'lane/jobs.sqlite');db.execute("UPDATE manual_state SET payload='{}'");db.commit();db.close()
    if damage=='output':(root/'item4/lane-scientific-workspaces/run_spec_author-3/SPEC.proposed.md').write_text('changed')
    if damage=='review':monkeypatch.setattr(h,'verify_result',lambda _: {'verdict':'REVISE','change_id':h.CHANGE})
    if damage=='authority':authority.write_text('changed')
    if damage=='active_service':monkeypatch.setattr(h.subprocess,'check_output',lambda *a,**k:'activating\n')
    if damage=='helper_source':monkeypatch.setattr(h,'verify_result',lambda _: {'verdict':'APPROVE','change_id':h.CHANGE,'source_sha':'c'*40})
    if damage=='runtime':h.RUNTIME.write_bytes(b'changed runtime')
    if damage=='selected_source':h.SELECTED.write_text(json.dumps({'source':'c'*40,'runtime':str(h.RUNTIME)}))
    with pytest.raises(ValueError):h.apply(approval,authority,'b'*40)
    assert not (root/'provenance-recovery-20261008').exists()


def test_guidance_preserves_author_ownership_and_existing_gates():
    assert '12000' in h.GUIDANCE and '11000' in h.GUIDANCE
    assert 'The author owns' in h.GUIDANCE and 'Ordinary scientific' in h.GUIDANCE
    assert 'not a placeholder or invented hash' in h.GUIDANCE


@pytest.mark.parametrize('property_text',['MainPID=12\nControlGroup=\n','MainPID=0\nControlGroup=/live\n'])
def test_live_process_refused_before_any_context_write(fixture,monkeypatch,property_text):
    root,globalroot,approval,authority,_,_=fixture
    monkeypatch.setattr(h.subprocess,'check_output',lambda args,**k: args[2][:-6]+'.service\n' if 'Triggers' in args else (property_text if '--property=MainPID,ControlGroup' in args else 'inactive\n'))
    with pytest.raises(ValueError,match='LANE_PROCESS_MUST_BE_ABSENT'):
        h.apply(approval,authority,'b'*40)
    assert not (root/'provenance-recovery-20261008').exists()


def test_prior_failed_cpu_unit_is_preserved_and_does_not_block_unrelated_author(fixture,monkeypatch):
    root,globalroot,approval,authority,_,_=fixture
    def show(args,**kwargs):
        if 'Triggers' in args:return args[2][:-6]+'.service\n'
        if '--property=MainPID,ControlGroup' in args:return 'MainPID=0\nControlGroup=\n'
        return 'failed\n' if 'research-item6-input-provisioning-20261007-execute.service' in args else 'inactive\n'
    monkeypatch.setattr(h.subprocess,'check_output',show)
    assert h.apply(approval,authority,'b'*40)['item6_unchanged'] is True


def test_real_timer_property_shape_checks_triggered_service(fixture,monkeypatch):
    root,globalroot,approval,authority,_,_=fixture
    observed=[]
    def show(args,**kwargs):
        unit=args[2];observed.append(tuple(args))
        if 'Triggers' in args:return unit[:-6]+'.service\n'
        if '--property=MainPID,ControlGroup' in args:
            return '' if unit.endswith('.timer') else 'MainPID=0\nControlGroup=\n'
        return 'inactive\n'
    monkeypatch.setattr(h.subprocess,'check_output',show)
    assert h.apply(approval,authority,'b'*40)['item4_next']=='run_spec_author round4'
    assert any('Triggers' in a for a in observed)
    assert not any(a[2].endswith('.timer') and '--property=MainPID,ControlGroup' in a for a in observed)


def test_unexpected_timer_target_refuses_before_writes(fixture,monkeypatch):
    root,globalroot,approval,authority,_,_=fixture
    def show(args,**kwargs):
        if 'Triggers' in args:return 'unbound.service\n'
        if '--property=MainPID,ControlGroup' in args:return 'MainPID=0\nControlGroup=\n'
        return 'inactive\n'
    monkeypatch.setattr(h.subprocess,'check_output',show)
    with pytest.raises(ValueError,match='TIMER_SERVICE_BINDING'):h.apply(approval,authority,'b'*40)
    assert not (root/'provenance-recovery-20261008').exists()
