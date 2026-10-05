"""A named native terminal report is complete criticism, never an approval."""
import copy
import pytest
from orchestrator.disposition_context import _literal_descriptors

def fixture():
    report={'artifact':'evidence/'+'a'*64+'-report.original.md','sha256':'a'*64,'size':123}
    return {'request':{'identity':'b'*64},'events':[{'identity':'c'*64,'event':'REVIEW','payload':{'verdict':'REQUEST_CHANGES','review_evidence':{'original_report':report,'genuine_binding':{'artifact':'evidence/binding.json','sha256':'d'*64}}}}]}

def test_named_report_without_redundant_digest_is_literal():
    s=fixture();rows=_literal_descriptors(s);assert rows==[{'request':'b'*64,'event':'c'*64,'descriptor':s['events'][0]['payload']['review_evidence']['original_report']}]

@pytest.mark.parametrize('damage',['missing_report','wrong_sha','non_markdown','extra_field','conflicting_original','empty_original','unsafe_path','missing_artifact'])
def test_unknown_or_inconsistent_criticism_refused(damage):
    s=fixture();p=s['events'][0]['payload'];r=p['review_evidence']['original_report']
    if damage=='missing_report':p['review_evidence'].pop('original_report')
    if damage=='wrong_sha':r['sha256']='bad'
    if damage=='non_markdown':r['artifact']='evidence/report.json'
    if damage=='extra_field':r['unsupported']=True
    if damage=='conflicting_original':p['original_review']={'response_sha256':'e'*64}
    if damage=='empty_original':p['original_review']={}
    if damage=='unsafe_path':r['artifact']='evidence/../report.md'
    if damage=='missing_artifact':r.pop('artifact')
    with pytest.raises(ValueError):_literal_descriptors(s)
