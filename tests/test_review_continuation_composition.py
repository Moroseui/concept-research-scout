"""Connect the exact original callbacks before replacing reviewed leaf components."""
import json,sys
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from tools import item4_diagnostic_review_runtime as m
from orchestrator import preparation_interleaving as pi,manual_runtime,item4_smoke_response as helper

@pytest.mark.parametrize('fault',[None,'native-approval','prior-bytes','prior-approval','sequence-path','helper-path','missing-helper','original-refusal','binding','scope','scoped-path','missing-scoped','connected-scoped','cap-refusal'])
def test_native_composition_preserves_original_connection(tmp_path,monkeypatch,fault):
    root=tmp_path/'new';root.mkdir();priorfile=tmp_path/'prior.py';priorfile.write_text('original source')
    doc=root/'frozen.json';doc.write_text('{"frozen":true}')
    events=[];approved={'report_sha256':'b'*64}
    monkeypatch.setattr(m,'ROOT',root);monkeypatch.setattr(m,'trusted',Path)
    bundle=NS(NATIVE_PREVIOUS=tmp_path/'native')
    monkeypatch.setattr(m,'authority',lambda held=True:(bundle,approved))
    native=NS(PRIOR=priorfile,PRIOR_SHA=m.sha(priorfile.read_bytes()),PRIOR_REVIEW='pinned',ROOT=bundle.NATIVE_PREVIOUS,
        authority=lambda:{'source_sha':'bad' if fault=='native-approval' else '1f2243448ca452abcad92ca355bead042cc731d2',
        'report_sha256':'c27eaa20e857449d1d054621848fd63084dc811a092f98128e63c9a99797ba93'},
        overlay=lambda path:events.append(('overlay',path)))
    bundle.preserved_native=lambda:(native,native.authority())
    bundle.colab_recovery_review=lambda:'original-recovery-review'
    monkeypatch.setattr(m,'native',m.native)
    if fault=='prior-bytes':priorfile.write_text('changed')
    callback=object()
    helper=NS(delivery_recovery=lambda p:fault!='scope',profile=lambda p:{'author':24,'reviewer':16},original_callback=callback)
    connection=(object(),object(),object(),object(),helper,{'scope':'original'},'original-approval')
    original_loader=lambda name,path:(events.append(('original-load',name,path)) or pi)
    prior=NS(REPAIRED=tmp_path/'old-sequence',authority=lambda:{'source_sha':'bad' if fault=='prior-approval' else '72c48cb69af87b760c4da9f246c1d1cab10735e1','report_sha256':'pinned'},load=original_loader)
    import orchestrator
    monkeypatch.setattr(orchestrator,'item4_scoped_calls',orchestrator.item4_scoped_calls)
    predecessor=NS(_validate=object() if fault=='connected-scoped' else None)
    replacement=NS(_validate=None)
    def original_module(name,path):
        events.append(('original-module',name,path))
        if name=='orchestrator.item4_scoped_calls':
            if fault=='cap-refusal':raise ValueError('original cap guard refused')
            return predecessor
        return helper
    route=NS(ROOT=tmp_path/'old-helper',module=original_module)
    def connected():
        if fault=='original-refusal':raise ValueError('original guard refused')
        prior.load('orchestrator.preparation_interleaving',(tmp_path if fault=='sequence-path' else prior.REPAIRED)/'orchestrator/preparation_interleaving.py')
        if fault!='missing-helper':route.module('orchestrator.item4_smoke_response',(tmp_path if fault=='helper-path' else route.ROOT)/'orchestrator/item4_smoke_response.py')
        if fault!='missing-scoped':route.module('orchestrator.item4_scoped_calls',(tmp_path if fault=='scoped-path' else route.ROOT)/'orchestrator/item4_scoped_calls.py')
        route.module('unrelated',tmp_path/'unchanged.py')
        return connection
    route.connect=connected;prior.route=lambda:route
    repair=NS(TURN_DOCUMENT=doc.name,TURN_DOCUMENT_SHA=m.sha(doc.read_bytes()),retained_review=lambda *a:True,extra_attempt=lambda *a:(events.append(('extra-attempt-approval',a[-1])) or False))
    if fault=='binding':doc.write_text('changed')
    def load(name,path):
        if name=='_native_review_passed_runtime':return native
        if name=='_native_review_prior_author24':return prior
        if name=='orchestrator.item4_scoped_calls':
            events.append(('candidate-scoped',path));assert path==root/'orchestrator/item4_scoped_calls.py'
            return replacement
        if name=='orchestrator.colab_reader_recovery':return repair
        if name=='orchestrator.colab_author_terminal':return NS(connect_sequence=lambda pi:events.append('terminal-sequence'),connect_timing_admission=lambda:events.append('terminal-admission'))
        raise AssertionError(name)
    monkeypatch.setattr(m,'load',load)
    monkeypatch.setattr(pi,'_REVIEW_TERMINAL',None);monkeypatch.setattr(pi,'_EXTRA_ATTEMPT',None)
    from tools import reviewer_connection_timing
    monkeypatch.setattr(reviewer_connection_timing,'bind',lambda value:events.append(('transport',value)))
    if fault:
        with pytest.raises(ValueError):m.connect(held=False)
    else:
        owner,result=m.connect(held=False)
        assert owner is route and result is connection and result[4].original_callback is callback
        assert ('original-load','orchestrator.preparation_interleaving',root/'orchestrator/preparation_interleaving.py') in events
        assert ('original-module','orchestrator.item4_smoke_response',root/'orchestrator/item4_smoke_response.py') in events
        assert ('original-module','unrelated',tmp_path/'unchanged.py') in events
        assert orchestrator.item4_scoped_calls is replacement
        assert events.index(('original-module','orchestrator.item4_scoped_calls',route.ROOT/'orchestrator/item4_scoped_calls.py')) < events.index(('candidate-scoped',root/'orchestrator/item4_scoped_calls.py'))
        assert pi._REVIEW_TERMINAL({}, {}, None) and not pi._EXTRA_ATTEMPT({},'x','y','z')
        assert ('transport',manual_runtime) in events
        assert events.index('terminal-sequence')<events.index('terminal-admission')<events.index(('transport',manual_runtime))
        assert events[-1]==('extra-attempt-approval','original-recovery-review')


def test_completion_default_stays_closed(monkeypatch):
    monkeypatch.setattr(helper,'fixture_audit',lambda p:True)
    monkeypatch.setattr(helper,'_native_review_complete',None)
    with pytest.raises(ValueError,match='AUDIT_AUTHOR_ONLY'):helper.finish_review(None,{}, {},'a'*64)


def test_review_guidance_preserves_scientific_independence():
    assert 'independent scientific reviewer16' in m.REVIEW_GUIDANCE
    assert 'no verdict is requested' in m.REVIEW_GUIDANCE
    assert 'not GPU or production evidence' in m.REVIEW_GUIDANCE


@pytest.mark.parametrize('action',['start','pulse'])
def test_host_reuses_live_invocation_checks_and_hard_bounds(tmp_path,monkeypatch,action):
    import subprocess
    root=tmp_path/'root';root.mkdir();record=tmp_path/'record';record.mkdir()
    (root/'host.json').write_text('{"hashes":{"original":"original-pin"}}')
    installed={'files':{'one.py':'file-pin'},'units':{'new-unit':'unit-pin'}}
    (record/'installed.json').write_text(json.dumps(installed))
    monkeypatch.setattr(m,'ROOT',root);monkeypatch.setattr(m,'trusted',Path)
    monkeypatch.setattr(m,'__file__',str(root/'tools/item4_diagnostic_review_runtime.py'))
    monkeypatch.setattr(m,'os',NS(getuid=lambda:0));monkeypatch.setattr(m,'sys',NS(flags=NS(no_user_site=1)))
    approval={'source_sha':'a'*40,'report_sha256':'b'*64};bundle=NS(RECORD=record,NATIVE_UNIT='exact-reviewed-unit')
    monkeypatch.setattr(m,'authority',lambda:(bundle,approval));events=[]
    h=NS(DOCUMENT='host.json',hashes=lambda proof:events.append(('hashes',proof)),RUNTIME=tmp_path/'runtime',MAX_SECONDS=3700,MAX_REFRESHES=62)
    original_live=object();h.live=original_live
    def run(proof,approved):
        assert h.live is original_live and (h.MAX_SECONDS,h.MAX_REFRESHES)==(3700,62)
        assert h.UNIT==bundle.NATIVE_UNIT and h.STAGE=='review'
        assert h.RECORD==record/'native-review-operation/review'
        assert proof['hashes']=={'original':'original-pin','new-unit':'unit-pin',str(root/'one.py'):'file-pin'}
        if action=='start':assert h.starting_state(proof,approved)['status']=='READY_REVIEW16'
        return {'status':'original-'+action}
    h.start=h.pulse=run;monkeypatch.setattr(m,'load',lambda name,path:h)
    def output(args,**kw):
        assert args[0:4]==['runuser','-u','partho','--'] and args[-1]=='ready'
        assert args[-2]==str(root/'tools/item4_diagnostic_review_runtime.py')
        events.append(('ready',args));return '{"status":"READY_REVIEW16","model_calls":0,"provider_calls":0}'
    monkeypatch.setattr(subprocess,'check_output',output)
    assert m.host(action)=={'status':'original-'+action}
    assert sum(e[0]=='ready' for e in events)==(action=='start')
