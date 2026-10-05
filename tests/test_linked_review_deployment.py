"""Synthetic provenance fixtures; no review, provider, deployment or grant."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from orchestrator import change_requests as c, deployment_review as g, terminal_review as t
from orchestrator import server_review_runner as runner


@pytest.fixture
def linked(tmp_path):
    source = 'a'*40
    base = dict.fromkeys(('archive_sha256', 'source_files', 'targets', 'previous_files',
                        'recovery_sha256', 'changes', 'dependencies'))
    base.update(schema=g.SCHEMA, profile=g.PROFILE, source=source, source_root='/release',
        previous_source='b'*40, previous_source_root='/previous', review_profile='server-terminal-review/v1')
    raw = g.encoded(base)
    private = {g.digest(raw): raw}
    statement = {'schema':'server-terminal-review/v1', 'scope':'material-source-integration',
        'source':source, 'proposal_sha256':g.digest(raw), 'manifest_sha256':'c'*64,
        'session_id':'11111111-1111-1111-1111-111111111111', 'resolution_of':t.BASE_SOURCE,
        'verdict':'APPROVE', 'inspected':['Synthetic only'], 'unavailable':[], 'unverified':[],
        'findings':{k:{'disposition':'resolved' if k in {'C006','C007'} else 'preserve',
                       'reason':'Synthetic only'} for k in t.FINDINGS},
        'remaining_gates':['held-deployment','accounting-halt','retained-history-audit',
                           'conditional-activation','scientific-acceptance']}
    report = ('SYNTHETIC ONLY\nFinal source/integration verdict: APPROVE\n```terminal-review-verdict\n'+json.dumps(statement)+'\n```\n').encode()
    private[g.digest(report)] = report
    actor = {'kind':'human','identity':'synthetic-operator'}
    request = c.submit(tmp_path/'changes', Path(__file__).resolve().parents[1], 'synthetic-review',
        'Synthetic one-use review fixture.', actor, source=source, key='fixture', scope_limits=['Synthetic only.'])
    folder=tmp_path/'changes'/request['identity']
    refs={}
    for key, body in [('operator_original', b'Synthetic original reply.'),
                      ('exact_decision', b'Synthetic exact decision.')]:
        f=tmp_path/(key+'.txt');f.write_bytes(body);refs[key]=c.preserve(folder,f)
        private[g.digest(body)]=body
    event=c.record(folder,'AUTHORIZED',actor,{'rationale':'Synthetic only.',
        'authority_reference':refs, 'review_policy':'Independent review remains required.'})
    for f in [folder/'request.json', * (folder/'events').glob('*.json')]:
        body=f.read_bytes();private[g.digest(body)]=body
    link={'schema':'operator-authorized-single-successor-review/v1','authorized_event':event['identity'],
        'decision_sha256':refs['exact_decision']['sha256'],
        'operator_original_sha256':refs['operator_original']['sha256'],
        'maximum_successors':1,'automatic_retry':False,'predecessor_proposal_sha256':g.digest(raw),
        'predecessor_session':statement['session_id'],'predecessor_report_sha256':g.digest(report),
        'predecessor_manifest_sha256':statement['manifest_sha256'],'runtime_source':'d'*40}
    return {**base,'linked_recovery':link},private


def check(pair):
    proposal,private=pair
    g.proposal_shape(proposal, '/release', 'a'*40)
    return g.linked_review_provenance(proposal,private)


def test_exact_original_link_and_unlinked_compatibility(linked):
    check(linked)
    old={k:v for k,v in linked[0].items() if k!='linked_recovery'}
    g.proposal_shape(old,'/release','a'*40)
    assert g.linked_review_provenance(old,{}) is None


@pytest.mark.parametrize('key', ['predecessor_proposal_sha256','predecessor_report_sha256',
    'operator_original_sha256','decision_sha256'])
def test_missing_or_changed_original_refuses(linked,key):
    p,private=linked;identity=p['linked_recovery'][key]
    del private[identity]
    with pytest.raises(ValueError,match='ORIGINAL_REQUIRED'):check(linked)
    private[identity]=b'changed'
    with pytest.raises(ValueError,match='ORIGINAL_REQUIRED'):check(linked)


@pytest.mark.parametrize('key,value', [('maximum_successors',2),('maximum_successors',True),
    ('automatic_retry',True),('schema','other'),('predecessor_session','wrong')])
def test_link_shape_and_one_use_boundary(linked,key,value):
    linked[0]['linked_recovery'][key]=value
    with pytest.raises(ValueError):check(linked)


@pytest.mark.parametrize('field', ['source_files','targets','changes','recovery_sha256'])
def test_same_source_does_not_hide_changed_configuration_or_application(linked,field):
    linked[0][field]='changed'
    with pytest.raises(ValueError,match='UNCHANGED_SCOPE_REQUIRED'):check(linked)


@pytest.mark.parametrize('field', ['predecessor_session','predecessor_manifest_sha256'])
def test_predecessor_bindings_refuse(linked,field):
    linked[0]['linked_recovery'][field]=('22222222-2222-2222-2222-222222222222'
        if field.endswith('session') else 'e'*64)
    with pytest.raises(ValueError,match='PREDECESSOR_CHANGED'):check(linked)


def test_event_tamper_and_missing_actual_grant_refuse(linked):
    p,private=linked
    event_key=next(k for k,v in private.items() if b'"event":"AUTHORIZED"' in v)
    original=private.pop(event_key)
    with pytest.raises(ValueError,match='AUTHORIZATION_REQUIRED'):check(linked)
    event=json.loads(original);event['actor']['kind']='agent'
    altered=g.encoded(event);private[g.digest(altered)]=altered
    with pytest.raises(ValueError,match='AUTHORIZATION_CHANGED'):check(linked)


def test_link_only_on_server_profile_and_unknown_fields_refuse(linked):
    p,private=linked;p['review_profile']='operator-terminal-review/v1'
    with pytest.raises(ValueError,match='LINKED_REVIEW_SCOPE'):check(linked)
    p['review_profile']='server-terminal-review/v1';p['extra']='unknown'
    with pytest.raises(ValueError,match='PROPOSAL_SCHEMA'):check(linked)


def test_candidate_preflight_rejects_deployment_shape_before_git(tmp_path,linked,monkeypatch):
    p,_=linked;p['unreviewed_key']=True
    path=tmp_path/'proposal.json';path.write_bytes(g.encoded(p))
    monkeypatch.setattr(runner.subprocess,'run',lambda *a,**k:pytest.fail('must refuse before Git or runtime'))
    with pytest.raises(ValueError,match='DEPLOYMENT_PROPOSAL_SCHEMA'):
        runner.candidate_preflight({'candidate_root':str(tmp_path),'proposal':str(path)})
