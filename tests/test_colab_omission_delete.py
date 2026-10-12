
import copy,json,hashlib
import pytest
from orchestrator import notebook_revision as nr,author_output_schema as schema,scientific_intake as si
from test_notebook_revision import fixture
from test_author_visible_module_feedback import BODY

EXACT={'unit':'cells/4/source','start':2090,'end':2120,
       'before_sha256':'8ffa5399e3c59a3fee6bb8a4cca50b89b57fdcd62163dcbf20a5c289ffa0674c',
       'replacement':''}

@pytest.mark.parametrize('change',[{}, {'unit':'cells/6/source'},{'start':2089},{'end':2121},
    {'before_sha256':'0'*64},{'replacement':'pass\n'},{'replacement':'EXCLUDED=[]'},{'extra':True}])
def test_same_exact_deletion_only_in_host_and_feedback(change):
    edit={**EXACT,**change}
    expected=not change
    for function in (nr.authorized_omission_deletion,schema.authorized_omission_deletion):
        assert function(edit,nr.ORIGINAL,nr.VIEW)==expected
        assert not function(edit,'0'*64,nr.VIEW)
        assert not function(edit,nr.ORIGINAL,'0'*64)

def deletion_fixture(monkeypatch):
    raw,selection,patch=fixture()
    source=si.notebook_units(raw)['cells/4/source'][0]
    edit={**EXACT,'before_sha256':si.sha(source[2090:2120])}
    # Synthetic-only fixture identities; production exact-pin predicates are
    # exercised separately above. Never read or reconstruct original omission.
    predicate=lambda e,o,v:e==edit and o==patch['original_sha256'] and v==patch['view_sha256']
    monkeypatch.setattr(nr,'authorized_omission_deletion',predicate)
    monkeypatch.setattr(schema,'authorized_omission_deletion',predicate)
    patch['edits']=[{'unit':'cells/4/source','start':0,'end':2090,
        'before_sha256':si.sha(source[:2090]),
        'replacement':'%%writefile /content/sprint13_pipeline.py\n'+BODY},edit]
    return raw,selection,patch

def test_author_deletion_reaches_host_without_reading_or_externalizing_hidden_literal(monkeypatch):
    raw,selection,patch=deletion_fixture(monkeypatch);before=raw[:]
    monkeypatch.setattr(nr,'_external_assignment',lambda *a:pytest.fail('deleted bytes must not be externalized'))
    notebook,diff,receipt=nr.apply(raw,selection,si.canonical(patch),set(),
        original_sha256=patch['original_sha256'],view_sha256=patch['view_sha256'])
    assert raw==before
    for value in (notebook,diff,si.canonical(receipt)):
        assert b'HIDDEN' not in value and b'Excluded membership count changed' not in value
    assert receipt['membership_input']['payload_exposed'] is False
    assert all(row['compile']=='PASS'for row in receipt['compile'])
    view,manifest=si.derive(raw,selection,set())
    assert schema.visible_module(patch,view,manifest)

def test_deletion_cannot_overlap_other_edits(monkeypatch):
    raw,selection,patch=deletion_fixture(monkeypatch)
    patch['edits'].append(copy.deepcopy(patch['edits'][-1]))
    with pytest.raises(ValueError,match='OVERLAP'):
        nr.apply(raw,selection,si.canonical(patch),set(),
          original_sha256=patch['original_sha256'],view_sha256=patch['view_sha256'])
    view,manifest=si.derive(raw,selection,set())
    with pytest.raises(ValueError,match='OVERLAP'):schema.visible_module(patch,view,manifest)

def test_omission_without_author_deletion_keeps_prior_guard(monkeypatch):
    raw,selection,patch=fixture()
    notebook,_,receipt=nr.apply(raw,selection,si.canonical(patch),set(),
        original_sha256=patch['original_sha256'],view_sha256=patch['view_sha256'])
    assert b'Excluded membership count changed' in notebook
    assert 'payload_exposed' not in receipt['membership_input']



def test_installed_function_overlay_supplies_new_policy_and_feedback(monkeypatch):
    from pathlib import Path
    from orchestrator import colab_bound_revision as f,analysis_revisions as rev
    originals=(nr.apply,schema.visible_module,rev.review_transition,rev.instructions,rev.execution_instructions)
    try:
        f.activate_correction_modules(Path(f.__file__).parents[1])
        assert rev.review_transition({'verdict':'REVISE','findings':[{'category':'privacy/secret'}]},'run_spec_review',1)==('run_spec_author','REVISION_REQUIRED')
        assert rev.review_transition({'verdict':'REJECT','findings':[]},'run_spec_review',1)==('BLOCKED','REVIEW_REJECTED')
        assert b'authorized_omission_deletion' in f.runtime_libraries()['author_output_schema']
        assert nr.apply.__module__.startswith('_reviewed_colab_')
    finally:
        nr.apply,schema.visible_module,rev.review_transition,rev.instructions,rev.execution_instructions=originals
