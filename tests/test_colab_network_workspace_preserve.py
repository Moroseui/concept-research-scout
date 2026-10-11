import json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from tools import colab_network_workspace_preserve as m

@pytest.fixture
def preservation(tmp_path,monkeypatch):
    lane=tmp_path/'lane';lane.mkdir(mode=0o700);work=tmp_path/'work';work.mkdir(mode=0o700)
    (work/'original.txt').write_bytes(b'original preparation, not patient data')
    dest=lane/'preserved';rows={'manual_calls':[{'id':'author2','status':'COMPLETE'}],'manual_account':[{'used':2}],'manual_state':[{'phase':'run_spec_review'}]}
    def inventory(folder):return {p.name:m.sha(p.read_bytes()) for p in folder.iterdir() if p.is_file()}
    inv=inventory(work);binding={'workspace':str(work),'inventory':inv,'inventory_sha256':m.sha(m.canonical(inv)),'rows_sha256':m.sha(m.canonical(rows))}
    events=[];controls={'rows':rows,'post_changed':False}
    def current(root):
        if controls['post_changed'] and dest.exists():return {'changed':True}
        return controls['rows']
    def ready():
        assert not work.exists() and inventory(dest/'workspace')==inv
        events.append('original-unchanged-ready');return {'status':'READY_SAME_REVIEW_NO_CALL'}
    recovery=NS(binding=lambda:{'workspace':str(work)},rows=current,inventory=inventory,ready=ready,LEDGER=tmp_path/'ledger.sqlite')
    runtime=NS(recovery=lambda:recovery)
    monkeypatch.setattr(m,'LANE',lane);monkeypatch.setattr(m,'DEST',dest)
    monkeypatch.setattr(m,'os',NS(getuid=lambda:1003,getgid=lambda:1003))
    monkeypatch.setattr(m,'verified',lambda review:(runtime,binding,{'report_sha256':'a'*64}))
    return NS(lane=lane,work=work,dest=dest,rows=rows,binding=binding,events=events,controls=controls)


def test_preserves_all_bytes_and_calls_original_ready_without_row_writes(preservation):
    f=preservation;before=json.dumps(f.rows,sort_keys=True)
    result=m.preserve(Path('review'))
    assert result['status']=='PRESERVED_PREMODEL_WORKSPACE' and result['model_calls']==result['new_allowance']==0
    assert (f.dest/'workspace/original.txt').read_bytes()==b'original preparation, not patient data'
    assert json.dumps(f.rows,sort_keys=True)==before and f.events==['original-unchanged-ready']
    assert (f.dest/'original-rows.json').read_bytes()==m.canonical(f.rows)
    with pytest.raises(ValueError,match='ORIGINAL_ATTEMPT_PRESERVED'):m.preserve(Path('review'))


@pytest.mark.parametrize('damage',['bytes','extra-file','rows','inventory-binding','wrong-workspace','halt','existing-destination','symlink-destination'])
def test_before_rename_refusals_preserve_original_files(preservation,damage):
    f=preservation
    if damage=='bytes':(f.work/'original.txt').write_bytes(b'changed')
    elif damage=='extra-file':(f.work/'unexpected').write_bytes(b'extra')
    elif damage=='rows':f.controls['rows']={'unmatched':True}
    elif damage=='inventory-binding':f.binding['inventory_sha256']='0'*64
    elif damage=='wrong-workspace':f.binding['workspace']=str(f.work.parent/'other')
    elif damage=='halt':(f.lane/'HALT').write_bytes(b'operator hold')
    elif damage=='existing-destination':f.dest.mkdir()
    else:f.dest.symlink_to(f.work,target_is_directory=True)
    before={p.name:p.read_bytes() for p in f.work.iterdir()}
    with pytest.raises(ValueError):m.preserve(Path('review'))
    assert f.work.exists() and {p.name:p.read_bytes() for p in f.work.iterdir()}==before
    assert f.events==[]


def test_post_rename_disagreement_stops_with_originals_and_intent_preserved(preservation):
    f=preservation;f.controls['post_changed']=True
    with pytest.raises(ValueError,match='PRESERVATION_READBACK'):m.preserve(Path('review'))
    assert (f.dest/'workspace/original.txt').exists() and (f.dest/'INTENT.json').exists()
    assert not (f.dest/'COMPLETE.json').exists() and f.events==[]
    with pytest.raises(ValueError,match='ORIGINAL_ATTEMPT_PRESERVED'):m.preserve(Path('review'))


@pytest.mark.parametrize('failure',[None,'preserve','verify'])
def test_finish_requires_actual_service_preservation_and_verify_before_complete(tmp_path,monkeypatch,failure):
    record=tmp_path/'record';record.mkdir();(record/'VERIFY.stderr').write_bytes(b'original failure retained')
    monkeypatch.setattr(m,'RECORD',record);monkeypatch.setattr(m,'trusted',Path)
    monkeypatch.setattr(m,'os',NS(getuid=lambda:0))
    def put(p,raw):
        with p.open('xb') as f:f.write(raw)
    events=[]
    runtime=NS(BRANCH=tmp_path,ENTRY='tools/colab_intake_identity_runtime.py',RUNTIME=tmp_path/'runtime.json',
        load=lambda *a:NS(put=put),authority=lambda **kw:events.append(('authority',kw)))
    monkeypatch.setattr(m,'verified',lambda review:(runtime,{'prior_source':'s'*40},{'report_sha256':'a'*64}))
    def run(argv,**kw):
        action='preserve' if 'preserve' in argv else 'verify';events.append(action)
        status={'status':'PRESERVED_PREMODEL_WORKSPACE'} if action=='preserve' else {'status':'VERIFIED_HELD','scientific_calls':0,'provider_calls':0}
        return NS(returncode=1 if failure==action else 0,stdout=json.dumps(status).encode(),stderr=b'bounded diagnostic')
    monkeypatch.setattr(m,'subprocess',NS(run=run))
    if failure:
        with pytest.raises(ValueError):m.finish(tmp_path/'review')
        assert not (record/'COMPLETE.json').exists()
    else:
        assert m.finish(tmp_path/'review')['status']=='INSTALLED_HELD'
        assert (record/'COMPLETE.json').exists()
        assert events[:2]==['preserve','verify']
    assert (record/'VERIFY.stderr').read_bytes()==b'original failure retained'
    with pytest.raises(FileExistsError):m.finish(tmp_path/'review')


@pytest.mark.parametrize('damage',[None,'reject','findings','scope','source-bytes','doc-bytes','prior-source','prior-review','prior-scope','runtime','complete','active'])
def test_genuine_approval_exact_partial_install_and_no_writer_required(tmp_path,monkeypatch,damage):
    from orchestrator import autonomy_review as ar
    root=tmp_path/'partial';(root/'tools').mkdir(parents=True);record=tmp_path/'record';record.mkdir()
    current=tmp_path/'candidate';(current/'tools').mkdir(parents=True);(current/'docs').mkdir()
    script=current/m.ENTRY;script.write_bytes(b'reviewed preservation helper')
    binding={'prior_source':'a'*40,'prior_review':'b'*64};doc=current/m.DOC;doc.write_bytes(m.canonical(binding))
    old={'source_sha':binding['prior_source'],'report_sha256':binding['prior_review'],
         'change_id':'timing-entrypoint-colab-network-recovery-20261011','runtime_sha256':'r'*64}
    if damage in {'prior-source','prior-review','prior-scope'}:old[{'prior-source':'source_sha','prior-review':'report_sha256','prior-scope':'change_id'}[damage]]='wrong'
    (root/'tools/colab_intake_identity_runtime.py').write_text('def authority(held=False):return '+repr(old)+'\ndef network_predecessor():return {}\n')
    approval={'verdict':'APPROVE','findings':[],'change_id':m.CHANGE,'runtime_sha256':'r'*64}
    if damage=='reject':approval['verdict']='REJECT'
    elif damage=='findings':approval['findings']=['unresolved']
    elif damage=='scope':approval['change_id']='different'
    elif damage=='runtime':approval['runtime_sha256']='wrong'
    review=tmp_path/'review';review.mkdir();(review/'packet-manifest.json').write_text(json.dumps({'source_files':{m.ENTRY:m.sha(script.read_bytes()),m.DOC:m.sha(doc.read_bytes())}}))
    monkeypatch.setattr(m,'__file__',str(script));monkeypatch.setattr(m,'ROOT',root);monkeypatch.setattr(m,'RECORD',record)
    monkeypatch.setattr(m,'DOC_SHA',m.sha(doc.read_bytes()));monkeypatch.setattr(m,'trusted',Path)
    monkeypatch.setattr(m,'sys',NS(flags=NS(no_user_site=1),path=[]))
    monkeypatch.setattr(ar,'verify_result',lambda path:approval)
    monkeypatch.setattr(m,'subprocess',NS(check_output=lambda *a,**kw:'MainPID='+('123' if damage=='active' else '0')+'\nActiveState=inactive\n'))
    if damage=='source-bytes':script.write_bytes(b'changed')
    elif damage=='doc-bytes':doc.write_bytes(b'changed')
    elif damage=='complete':(record/'COMPLETE.json').write_bytes(b'preserved completion')
    if damage is None:assert m.verified(review)[1:]==(binding,approval)
    else:
        with pytest.raises(ValueError):m.verified(review)
