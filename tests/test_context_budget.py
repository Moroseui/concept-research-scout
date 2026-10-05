"""Deterministic input contracts; never contact a model or remote service."""
import hashlib
import json
from pathlib import Path
import shutil
import pytest
from orchestrator import context_budget as budget

ROOT = Path(__file__).resolve().parents[1]
from orchestrator.manual_context import STAGE_ARTIFACT_TYPES
STAGES = tuple(STAGE_ARTIFACT_TYPES)


def save_manifest(root):
    folder = root / budget.PROJECT
    manifest = json.loads((folder / "manifest.json").read_text())
    for key in ("state", "policy", "obligations"):
        manifest[key]["sha256"] = budget.sha((root / manifest[key]["path"]).read_bytes())
    (folder / "manifest.json").write_text(json.dumps(manifest))


@pytest.fixture
def root(tmp_path):
    folder = tmp_path / budget.PROJECT
    shutil.copytree(ROOT / budget.PROJECT, folder)
    manifest = json.loads((folder / "manifest.json").read_text())
    for row in manifest["sources"]:
        target = tmp_path / row["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / row["path"], target)
    return tmp_path


def compose(root, stage, target="P001"):
    return budget.assemble(root, project="isles24-prediction", idea_ids=[target],
                           stage=stage, task="Preserve the original decision and assess this task.",
                           artifacts="Original observed result: not available.")[0]


def add_obligation(root, kind="stop"):
    quote = "STOP P001: do not make a model call while this explicit stop is open."
    path = root / "new-operator-record.md"
    path.write_text(quote)
    folder = root / budget.PROJECT
    register = json.loads((folder / "obligations.json").read_text())
    register["obligations"].append({"id":"TEST-STOP", "type":kind,
        "scope":{"project":["isles24-prediction"], "idea_ids":["P001"], "stages":["*"]},
        "status":"open", "severity":"unspecified", "text":quote,
        "source":{"path":"new-operator-record.md", "sha256":budget.sha(path.read_bytes()),
                  "start":0, "end":len(path.read_bytes()), "original_path":"new-operator-record.md"},
        "disposition":None})
    (folder / "obligations.json").write_text(json.dumps(register))
    save_manifest(root)
    return quote


def test_irrelevant_append_byte_identical_for_all_scientific_stage_sections(root):
    before = {stage:compose(root,stage) for stage in STAGES}
    with (root / "evidence/decisions.md").open("a") as f:
        for i in range(1000):
            f.write(f"\n## irrelevant synthetic {i}\nidea_ids: [unrelated-{i}]\nNo authority.\n")
    assert {stage:compose(root,stage) for stage in STAGES} == before


def test_scoped_stop_literal_gate_and_close(root):
    quote = add_obligation(root)
    for stage in STAGES:
        body = compose(root,stage)
        assert quote in body
        assert quote not in compose(root,stage,"P002")
        with pytest.raises(budget.ContextError, match="SCOPED_STOP"):
            budget.dispatch_preflight(root,project="isles24-prediction",idea_ids=["P001"],stage=stage,text=body)
        budget.dispatch_preflight(root,project="isles24-prediction",idea_ids=["P002"],stage=stage,text=compose(root,stage,"P002"))
    folder = root / budget.PROJECT
    register = json.loads((folder / "obligations.json").read_text())
    release = root/'release.md'; release.write_text('Synthetic explicit operator release fixture')
    register["obligations"][-1].update(status="closed",disposition={
        'path':'release.md','sha256':budget.sha(release.read_bytes()),'start':0,
        'end':len(release.read_bytes()),'text':release.read_text()})
    (folder / "obligations.json").write_text(json.dumps(register)); save_manifest(root)
    for stage in STAGES:
        body=compose(root,stage)
        assert quote not in body
        budget.dispatch_preflight(root,project="isles24-prediction",idea_ids=["P001"],stage=stage,text=body)


@pytest.mark.parametrize("kind", ["adverse finding", "protocol amendment", "constraint", "open question"])
def test_non_stop_obligations_are_literal_and_do_not_invent_a_halt(root, kind):
    quote = add_obligation(root,kind)
    for stage in STAGES:
        body=compose(root,stage)
        assert quote in body
        budget.dispatch_preflight(root,project="isles24-prediction",idea_ids=["P001"],stage=stage,text=body)


def test_changed_or_missing_original_refuses(root):
    add_obligation(root)
    (root/"new-operator-record.md").write_text("altered")
    with pytest.raises(budget.ContextError,match="EXACT_QUOTE"):
        compose(root,"review")
    (root/"new-operator-record.md").unlink()
    with pytest.raises(budget.ContextError,match="SOURCE_MISSING"):
        compose(root,"review")


def test_changed_authoritative_seed_refuses(root):
    with (root/"docs/COLLABORATOR_RULES.md").open("a") as f:f.write("Changed policy")
    with pytest.raises(budget.ContextError,match="SOURCE_RECONCILIATION"):
        compose(root,"review")


def test_character_limit_has_section_breakdown_and_never_clips():
    with pytest.raises(budget.ContextTooLarge) as error:
        budget.measure({"task":"x", "required criticism":"a"*200000})
    assert error.value.measurement["sections"]["required criticism"]["characters"]==200000
    body, measurement=budget.measure({"task":chr(233)*100})
    assert measurement["utf8_bytes"] > measurement["characters"]
    assert chr(233)*100 in body
    with pytest.raises(budget.ContextTooLarge):budget.check_final("x"*199999,schema_text="xx")


def test_tagged_decisions_keep_full_entries_with_count_bound():
    raw="".join(f"## decision {i}\nidea_ids: [P001]\nText {i}.\n" for i in range(12))
    chosen=budget.decision_entries(raw,["P001"])
    assert len(chosen)==8 and "decision 4" in chosen[0] and "Text 11." in chosen[-1]
    assert budget.decision_entries(raw,["P002"])==[]









def test_every_register_entry_and_assembled_input_passes_unchanged_scanner(root):
    from orchestrator.git_publication import scan
    _, content, rows = budget.load(root)
    for row in rows:scan('context/obligation.json', budget.encoded(row).encode())
    scan('context/STATE.md',content['state'].encode())
    scan('context/POLICY.md',content['policy'].encode())
    for stage in STAGES:scan('context/input.md',compose(root,stage).encode())


def test_flagged_obligations_contain_no_binding_values_and_block_dependent_dispatch(root):
    flag=budget.flagged_obligations(root,'isles24',['023'],'interpret')
    assert all('text' not in row for row in flag)
    if flag:
        with pytest.raises(budget.ContextError,match='PRIVACY_DECISION_REQUIRED'):
            budget.dispatch_preflight(root,project='isles24',idea_ids=['023'],stage='interpret',text='safe input')


def test_new_tagged_decision_requires_register_reconciliation(root):
    with (root/'evidence/decisions.md').open('a') as stream:
        stream.write('\n## new binding decision\nidea_ids: [P001]\nA new condition awaiting registration.\n')
    with pytest.raises(budget.ContextError,match='TAGGED_DECISION_REQUIRES_REGISTER_RECONCILIATION'):
        compose(root,'review')


def test_operator_only_archive_is_not_silently_sent(root):
    from orchestrator.git_publication import scan
    raw=(root/'evidence/decisions.md').read_bytes()
    with pytest.raises(ValueError,match='CASE_LEVEL_RECORD_REJECTED'):
        scan('context/decisions.txt',raw)
    body=compose(root,'review')
    assert raw.decode() not in body
    scan('context/stage-input.md',body.encode())


def test_flagged_sections_keep_independent_safe_quotes(root):
    _,_,rows=budget.load(root)
    assert any(row['id'].startswith('ISLES-114-P') for row in rows)
    assert any(row['id'].startswith('ISLES-125-P') for row in rows)
    assert any(row['id'].startswith('ISLES-141-P') for row in rows)
    # Every safe subquote retains its exact source span; no redaction replaces
    # an unsafe binding with a new, supposedly equivalent statement.
    for row in rows:
        ref=row['source']
        assert (root/ref['path']).read_bytes()[ref['start']:ref['end']].decode()==row['text']


def test_scanner_rejects_unsafe_register_without_exposing_original_in_input(root):
    from orchestrator.git_publication import scan
    quote='STOP: '+ 'sub-stroke' + '9999' + ' requires operator disposition.'
    path=root/'unsafe-binding.md';path.write_text(quote)
    folder=root/budget.PROJECT
    register=json.loads((folder/'obligations.json').read_text())
    register['obligations'].append({'id':'TEST-UNSAFE','type':'stop',
        'scope':{'project':['isles24-prediction'],'idea_ids':['P001'],'stages':['*']},
        'status':'open','severity':'unspecified','text':quote,'disposition':None,
        'source':{'path':'unsafe-binding.md','original_path':'unsafe-binding.md',
                  'sha256':budget.sha(path.read_bytes()),'start':0,'end':len(path.read_bytes())}})
    (folder/'obligations.json').write_text(json.dumps(register));save_manifest(root)
    with pytest.raises(ValueError,match='CASE_LEVEL_RECORD_REJECTED'):
        compose(root,'review')
















def test_cross_charter_scopes_do_not_hide_scientific_contamination(root):
    _, _, rows = budget.load(root)
    row = next(row for row in rows if row['id']=='ISLES-107')
    assert budget.in_scope(row,'isles24',['021'],'feasibility')
    assert not budget.in_scope(row,'isles24-prediction',['P001'],'review')
    baseline_stop = next(row for row in rows if row['id']=='ISLES-083')
    assert baseline_stop['type']=='stop'
    assert budget.in_scope(baseline_stop,'baseline',['002'],'review')
    assert not budget.in_scope(baseline_stop,'isles24',['002'],'review')






def test_governing_scopes_apply_to_science_not_just_implementation():
    rows = budget.obligations(ROOT, 'isles24-prediction', ['P001'], 'review')
    assert {'ISLES-009','ISLES-010','ISLES-013','ISLES-045','ISLES-055'} <= {r['id'] for r in rows}


def test_scanner_runs_even_when_complete_input_would_exceed_cap(root):
    from orchestrator.git_publication import scan
    # Construct a synthetic refusal value; no original case identifier is used.
    unsafe = 'sub-' + 'stroke' + str(1000000000)
    with pytest.raises(ValueError): scan('context/input-section.txt', unsafe.encode())
    with pytest.raises(ValueError) as refused:
        budget.assemble(root, project='isles24-prediction', idea_ids=['P001'],
                        stage='review', task='x'*200001, artifacts=unsafe)
    assert not isinstance(refused.value, budget.ContextTooLarge)
