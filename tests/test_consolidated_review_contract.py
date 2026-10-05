"""Structured contracts; all constructed decisions are synthetic, never approvals."""
import copy
import hashlib
import json
import os
from pathlib import Path
import pytest
from orchestrator import review_contract as c, autonomy_review as a
from test_autonomy_review import native, extract


def manifest():
    return {'prompt_version':5,'source_sha':'a'*40,'runtime_sha256':'b'*64,'source_files':{'worker.py':'c'*64}}


def report(m=None):
    m=m or manifest()
    return {'schema':c.SCHEMA,'source_sha':m['source_sha'],'runtime_sha256':m['runtime_sha256'],
            'packet_sha256':a.sha(a.canonical(m)), 'verdict':'APPROVE','findings':[],
            'rationale':'Synthetic only. BLOCKER[budget] examples and No BLOCKER[...] are prose.',
            'inspected_scope':['Synthetic worker'],'limitations':['Synthetic evidence only'],
            'analysis_entrypoint':'orchestrator.analysis_driver'}


def finding():
    return {'id':'B1','category':'budget','text':'Exceeded cap','evidence':'Synthetic receipt','resolution':'Stay within cap'}


def test_new_contract_ignores_prose_and_requires_matching_bindings():
    m=manifest();v=report(m)
    assert c.administrative(json.dumps(v),m)==v
    for key in ('source_sha','runtime_sha256','packet_sha256'):
        bad={**v,key:'wrong'}
        with pytest.raises(ValueError,match='BINDING'):c.administrative(json.dumps(bad),m)
    prompt=a.prompt_for(m)
    assert all(key in prompt for key in v)
    assert 'prose is\nnever marker-parsed' in prompt


@pytest.mark.parametrize('damage',['finding','missing','extra','duplicate','ambiguous','null','empty-scope','malformed-finding','unknown-category'])
def test_malformed_ambiguous_or_listed_findings_cannot_approve(damage):
    m=manifest();v=report(m)
    if damage=='finding':v['findings']=[finding()]
    elif damage=='missing':v.pop('findings')
    elif damage=='extra':v['other_verdict']='REJECT'
    elif damage=='ambiguous':v['verdict']='APPROVE or REVISE'
    elif damage=='null':v['findings']=None
    elif damage=='empty-scope':v['inspected_scope']=[]
    elif damage=='malformed-finding':v['findings']=[{}]
    elif damage=='unknown-category':v['findings']=[{**finding(),'category':'unknown'}]
    raw=json.dumps(v)
    if damage=='duplicate':raw=raw[:-1]+',"verdict":"REJECT"}'
    with pytest.raises(ValueError):c.administrative(raw,m)


@pytest.mark.parametrize('verdict',['REVISE','REJECT'])
def test_negative_verdict_is_preserved_even_without_findings(verdict):
    v=report();v['verdict']=verdict
    assert c.administrative(json.dumps(v),manifest())['verdict']==verdict
    v['findings']=[finding()]
    assert c.administrative(json.dumps(v),manifest())['findings']==[finding()]


def test_scientific_exact_contract_and_prose_is_not_a_decision():
    v={'verdict':'APPROVE','findings':[],'rationale':'BLOCKER[budget] sample, not a structured finding.'}
    assert c.scientific(json.dumps(v))==v
    for bad in ({'verdict':'APPROVE','rationale':'No blockers'}, {**v,'findings':[finding()]}, {**v,'findings':'None'}):
        with pytest.raises(ValueError):c.scientific(json.dumps(bad))


def test_native_identity_tool_and_usage_checks_survive_new_contract():
    m=manifest();events=native(m);raw=json.dumps(report(m))
    events[-1]['result']=raw;events[-2]['message']['content'][0]['text']=raw
    assert extract(events,m)['verdict']=='APPROVE'
    events[-2]['message']['content'].append({'type':'tool_use','name':'ExitPlanMode','id':'forbidden'})
    with pytest.raises(ValueError,match='CONFINEMENT'):extract(events,m)


def test_every_preserved_failure_is_unchanged_and_cannot_supply_missing_structure():
    path=os.environ.get('CONNECTIONS_PRESERVED_FAILURES')
    if not path:pytest.skip('Private historical originals not supplied; required in release receipt')
    index=json.loads(Path(path).read_text())
    assert {'call6','001b9','059a9','c09b','941431','71ab8','522e5b21'} <= {r['id'] for r in index}
    for row in index:
        raw=Path(row['path']).read_bytes()
        assert hashlib.sha256(raw).hexdigest()==row['sha256']
        with pytest.raises(ValueError):
            c.scientific(raw) if row['id']=='call6' else c.administrative(raw,manifest())
        # Explicitly synthetic envelope: historical prose cannot become findings.
        value=report();value['rationale']=raw.decode()
        assert c.administrative(json.dumps(value),manifest())['findings']==[]
        assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256']
