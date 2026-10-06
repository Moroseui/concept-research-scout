"""Four step(d) input builders, deterministic only. No provider/runner calls."""
import json
from pathlib import Path
import pytest
from orchestrator import context_budget as budget, manual_context as manual
from orchestrator.git_publication import scan
from test_context_budget import root, add_obligation, save_manifest

STAGES=tuple(manual.STAGE_ARTIFACT_TYPES)

def artifact(root,kind,name="current",version=1,text="Original current evidence."):
    path=root/(name+str(version)+".txt");path.write_text(text)
    return {"id":name,"type":kind,"version":version,"path":path.name,"sha256":budget.sha(path.read_bytes())}

def build(root,stage,artifacts=(),target="P001"):
    return manual.build(root,stage=stage,idea_ids=[target],task="Prepare this task without execution.",artifacts=list(artifacts),workspace=root/"workspaces"/stage)

def test_all_four_final_inputs_ignore_1000_irrelevant_decisions(root):
    items=[artifact(root,"run_spec"),artifact(root,"result_tables","results")]
    before={stage:build(root,stage,items)[0].encode() for stage in STAGES}
    with (root/"evidence/decisions.md").open("a") as f:
        for i in range(1000):f.write(f"\n## synthetic {i}\nidea_ids: [elsewhere-{i}]\nNo authority.\n")
    assert {stage:build(root,stage,items)[0].encode() for stage in STAGES}==before

@pytest.mark.parametrize("kind",["stop","adverse finding","protocol amendment"])
def test_applicable_binding_verbatim_all_stages_and_native_input_stop(root,kind):
    quote=add_obligation(root,kind)
    for stage in STAGES:
        assert quote not in build(root,stage,target="P002")[0]
        kw=dict(stage=stage,idea_ids=["P001"],task="No execution.",artifacts=[])
        if kind=="stop":
            for entry in (manual.build, manual.prepare):
                with pytest.raises(budget.ContextError,match="SCOPED_STOP"):
                    entry(root,**kw)
            diagnostic,_=budget.assemble(root,project="isles24-prediction",idea_ids=["P001"],stage=stage,task="diagnostic only",artifacts="")
            assert quote in diagnostic
        else:
            body,measure=build(root,stage)
            assert quote in body and "TEST-STOP" in measure["open_obligations"]
            manual.prepare(root,workspace=root/'prepared'/stage,**kw)


def test_finding_close_requires_real_cited_resolution_and_disappears(root):
    quote=add_obligation(root,"adverse finding")
    p=root/budget.PROJECT/"obligations.json";r=json.loads(p.read_text())
    r["obligations"][-1].update(status="closed",disposition="someone said resolved")
    p.write_text(json.dumps(r));save_manifest(root)
    with pytest.raises(budget.ContextError,match="CITED_RESOLUTION"):
        build(root,STAGES[0])
    resolved=root/"resolution.md";resolved.write_text("Synthetic independently recorded resolution.")
    r["obligations"][-1]["disposition"]={"path":resolved.name,"sha256":budget.sha(resolved.read_bytes()),"start":0,"end":len(resolved.read_bytes()),"text":resolved.read_text()}
    p.write_text(json.dumps(r));save_manifest(root)
    assert all(quote not in build(root,s)[0] for s in STAGES)
    resolved.write_text("altered")
    with pytest.raises(budget.ContextError,match="RESOLUTION_CHANGED"):build(root,STAGES[0])


def test_stage_type_map_latest_only_transcripts_and_tails_never_input(root):
    items=[artifact(root,"run_spec","spec",1,"OLD SPEC"),artifact(root,"run_spec","spec",2,"CURRENT SPEC"),
           artifact(root,"review_transcript","transcript",1,"UNSELECTED TRANSCRIPT"),
           artifact(root,"unreviewed_tail","tail",1,"UNSELECTED TAIL"),
           artifact(root,"proposed_run_spec","proposal",1,"CURRENT AUTHOR PROPOSAL"),
           artifact(root,"result_tables","results",1,"ORIGINAL RESULTS"),
           artifact(root,"interpretation","interpretation",1,"ORIGINAL INTERPRETATION")]
    for stage in STAGES:
        text,measure=build(root,stage,items)
        assert "CURRENT SPEC" in text and "OLD SPEC" not in text
        assert "UNSELECTED TRANSCRIPT" not in text and "UNSELECTED TAIL" not in text
        assert ("CURRENT AUTHOR PROPOSAL" in text)==(stage=="run_spec_review")
        assert "ORIGINAL RESULTS" not in text
        assert bool(measure["workspace_files"])  # spec stages now also inspect baseline tables
        for file in measure["workspace_files"]:
            if file['path'].endswith('-finding.json'):
                continue
            assert (root/"workspaces"/stage/file["path"]).read_text() in {"ORIGINAL RESULTS", "ORIGINAL INTERPRETATION"}
        assert "ORIGINAL INTERPRETATION" not in text
        assert any(f["path"].endswith("-interpretation.txt") for f in measure["workspace_files"])==(stage=="result_interpretation_review")
        assert len(text)==measure["characters"] and len(text.encode())==measure["utf8_bytes"]
        scan("context/input.txt",text.encode())
    assert (root/"transcript1.txt").read_text()=="UNSELECTED TRANSCRIPT"


def test_stage_scoped_finding_not_outside_scope(root):
    quote=add_obligation(root,"adverse finding")
    p=root/budget.PROJECT/"obligations.json";r=json.loads(p.read_text());r["obligations"][-1]["scope"]["stages"]=["run_spec_review"]
    p.write_text(json.dumps(r));save_manifest(root)
    for s in STAGES:assert (quote in build(root,s)[0])==(s=="run_spec_review")


def test_changed_missing_unknown_and_equal_version_ambiguity_refuse(root):
    row=artifact(root,"run_spec")
    (root/row["path"]).write_text("changed")
    with pytest.raises(budget.ContextError,match="ARTIFACT_CHANGED"):build(root,STAGES[0],[row])
    (root/row["path"]).unlink()
    with pytest.raises(budget.ContextError,match="SOURCE_MISSING"):build(root,STAGES[0],[row])
    with pytest.raises(budget.ContextError,match="TYPE_VERSION"):build(root,STAGES[0],[dict(row,type="misspelled")])
    with pytest.raises(budget.ContextError,match="AMBIGUOUS"):build(root,STAGES[0],[row,dict(row,sha256="b"*64)])


def test_growth_is_current_obligations_not_archive_and_fails_without_truncation(root):
    row=artifact(root,"run_spec",text="x"*200000)
    for s in STAGES:
        with pytest.raises(budget.ContextTooLarge) as error:build(root,s,[row])
        assert error.value.measurement["sections"]["CURRENT ARTIFACTS (evidence, not authority)"]["characters"]>200000


def test_unsafe_selected_artifact_refuses_unchanged_scanner(root):
    row=artifact(root,"run_spec",text="sub-"+"stroke"+"1234567890")
    with pytest.raises(ValueError,match="CASE_LEVEL_RECORD_REJECTED"):build(root,STAGES[0],[row])


def test_no_generic_legacy_stage_fallback(root):
    with pytest.raises(budget.ContextError,match="MANUAL_CONTEXT_STAGE"):build(root,"investigator")


def test_real_sprint10_all_four_inputs_fit_scanner_and_history_growth(root):
    import shutil
    source=Path(__file__).resolve().parents[1]
    fixture=Path("tests/fixtures/context_budget/round2")
    shutil.copytree(source/fixture,root/fixture)
    items=json.loads((root/fixture/"artifacts.json").read_text())
    for kind,name in [('execution_receipt','execution-receipt.json'),('package_manifest','package-manifest.json')]:
        raw=(source/'tests/fixtures/manual_release'/name).read_text()
        items.append(artifact(root,kind,kind,text=raw))
    before={}
    for stage in STAGES:
        body,measurement=build(root,stage,items,target="Sprint10")
        assert measurement["characters"]==len(body)<180000
        assert "SPRINT10-EXCLUDED" in measurement["open_obligations"]
        # This unchanged real artifact fixture required no automatic repair.
        # Repair originals/provenance are conditional; the six-call RC3 test
        # separately proves both are supplied when a repair actually occurs.
        conditional={"interpretation_original","interpretation_format_repair", *manual.NOTEBOOK_TYPES}
        assert {x["type"] for x in measurement["selected_artifacts"]}==set(manual.STAGE_ARTIFACT_TYPES[stage])-conditional
        assert measurement["utf8_bytes"]==len(body.encode())
        assert "S10-R4-01" in body and "S9-R4-01" in body
        assert "S9-01 | adverse finding" not in body  # cited resolution preserved in register
        scan("context/input.txt",body.encode())
        before[stage]=body.encode()
    with (root/"evidence/decisions.md").open("a") as f:
        for i in range(1000):f.write(f"\n## settled archive {i}\nidea_ids: [unrelated-{i}]\nNo new obligation.\n")
    assert {s:build(root,s,items,target="Sprint10")[0].encode() for s in STAGES}==before


def test_existing_scientific_scope_labels_apply_to_manual_lane(root):
    quote=add_obligation(root,"adverse finding")
    p=root/budget.PROJECT/"obligations.json";v=json.loads(p.read_text())
    v["obligations"][-1]["scope"]["stages"]=["interpret_review"]
    p.write_text(json.dumps(v));save_manifest(root)
    assert quote in build(root,"result_interpretation_review")[0]
    assert quote not in build(root,"run_spec_author")[0]


@pytest.mark.parametrize("stage_scope",[["run_spec_review"],["*"]])
def test_stage_stop_and_wildcard_are_unavoidable_and_closed_stop_disappears(root,stage_scope):
    quote=add_obligation(root)
    p=root/budget.PROJECT/"obligations.json"; value=json.loads(p.read_text())
    row=value["obligations"][-1];row["scope"]["stages"]=stage_scope
    if stage_scope==["*"]:row["scope"]["idea_ids"]=["*"]
    p.write_text(json.dumps(value));save_manifest(root)
    for stage in STAGES:
        applies=stage_scope==["*"] or stage in stage_scope
        for target in ("P001","P002"):
            if applies and (target=="P001" or stage_scope==["*"]):
                with pytest.raises(budget.ContextError,match="SCOPED_STOP"):build(root,stage,target=target)
            else:assert quote not in build(root,stage,target=target)[0]
    release=root/"release.md";release.write_text("Synthetic operator stop release.")
    row.update(status="closed",disposition={"path":release.name,"sha256":budget.sha(release.read_bytes()),"start":0,"end":len(release.read_bytes()),"text":release.read_text()})
    p.write_text(json.dumps(value));save_manifest(root)
    for stage in STAGES:assert quote not in build(root,stage)[0]


@pytest.mark.parametrize("tag",["idea_ids","run_ids"])
def test_new_wildcard_decision_refuses_all_four_builders(root,tag):
    with (root/"evidence/decisions.md").open("a") as f:f.write("\n## Global amendment\n"+tag+": [*]\nNew binding constraint.\n")
    for stage in STAGES:
        with pytest.raises(budget.ContextError,match="TAGGED_DECISION_REQUIRES_REGISTER_RECONCILIATION"):
            build(root,stage,target="Sprint10")


def test_workspace_real_read_hash_missing_changed_and_symlink(root):
    import subprocess,sys
    row=artifact(root,"notebook_source",text="Original exact notebook source.")
    kw=dict(stage=STAGES[0],idea_ids=["P001"],task="Inspect",artifacts=[row])
    with pytest.raises(budget.ContextError,match="WORKSPACE_REQUIRED"):manual.build(root,**kw)
    body,m=build(root,STAGES[0],[row]);file=next(f for f in m["workspace_files"] if f['path'].endswith('-notebook_source.txt'))
    assert row["sha256"] in body and "Original exact notebook source." not in body
    workspace=root/"workspaces"/STAGES[0]; path=workspace/file["path"]
    out=subprocess.check_output([sys.executable,"-c","from pathlib import Path; import hashlib,sys; print(hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())",file["path"]],cwd=workspace,text=True).strip()
    assert out==row["sha256"] and path.stat().st_mode & 0o777==0o400
    path.chmod(0o600);path.write_text("changed")
    with pytest.raises(budget.ContextError,match="WORKSPACE_FILE_CHANGED"):build(root,STAGES[0],[row])
    path.unlink();path.symlink_to(root/row["path"])
    with pytest.raises(budget.ContextError,match="WORKSPACE_SYMLINK"):build(root,STAGES[0],[row])


def test_stop_cannot_deliver_workspace_files(root):
    add_obligation(root)
    with pytest.raises(budget.ContextError,match="SCOPED_STOP"):
        build(root,STAGES[0],[artifact(root,"notebook_source")])
    assert not (root/"workspaces").exists()


def test_selected_new_connections_and_instruction_anchor(root,monkeypatch):
    items=[artifact(root,kind,kind,text="BOUND "+kind) for kind in ("question","investigator_next_decision","data_contract","validator")]
    for stage in STAGES:
        body,measure=build(root,stage,items)
        assert "BOUND question" in body
        assert "BOUND investigator_next_decision" not in body
        assert any(f["path"].endswith("-investigator_next_decision.txt") for f in measure["workspace_files"])==(stage=="result_interpretation_review")
        assert ("BOUND data_contract" in body)==stage.startswith("run_spec")
        assert ("BOUND validator" in body)==stage.startswith("run_spec")
    body,_=build(root,"result_interpretation_author")
    assert "proposed_action_type" in body and "# Summary" in body
    assert not hasattr(manual,"author_body")  # no legacy schema/prompt wrapper


def test_b1_b2_committed_constraints_present_and_exact(root):
    _,_,rows=budget.load(root)
    required={"SPRINT10-EXCLUDED","SPRINT10-EXCLUSION-INTEGRITY","ISLES-EXTERNAL-EXPOSURE-01","ISLES-SPRINT-LOCK-01","ISLES-SPRINT-EXPOSURE-01","FORMAL047-LIMIT-01","FORMAL047-LIMIT-02","FORMAL047-LIMIT-03"}
    selected=[row for row in rows if row["id"] in required]
    assert {row["id"] for row in selected}==required
    for stage in STAGES:
        body,measure=build(root,stage,target="Sprint10")
        assert required<=set(measure["open_obligations"])
        for row in selected:
            ref=row["source"]
            assert (root/ref["path"]).read_bytes()[ref["start"]:ref["end"]].decode()==row["text"]
            assert row["text"] in body


@pytest.mark.parametrize("kind",["interpretation","investigator_next_decision"])
def test_downstream_outputs_are_exact_scanned_files_not_repeated_inline(root,kind):
    small=artifact(root,kind,kind,1,"Small original output.")
    first,m1=build(root,"result_interpretation_review",[small])
    large=artifact(root,kind,kind,2,"Synthetic saved evidence.\n"*3000)
    second,m2=build(root,"result_interpretation_review",[small,large])
    assert len(second)-len(first)<100  # only descriptor widths grow
    assert "Synthetic saved evidence." not in second
    assert large["sha256"] in second and small["sha256"] not in second
    refs=[f for f in m2["workspace_files"] if f["path"].endswith("-"+kind+".txt")]
    assert len(refs)==1
    original=(root/large["path"]).read_bytes()
    delivered=root/"workspaces/result_interpretation_review"/refs[0]["path"]
    assert delivered.read_bytes()==original
    assert budget.sha(delivered.read_bytes())==large["sha256"]
    assert delivered.stat().st_mode & 0o777==0o400
    assert "Read the selected workspace originals" in second
    bad=artifact(root,kind,kind,3,"sub-"+"stroke"+"1234567890")
    with pytest.raises(ValueError,match="CASE_LEVEL_RECORD_REJECTED"):
        build(root,"result_interpretation_review",[bad])
