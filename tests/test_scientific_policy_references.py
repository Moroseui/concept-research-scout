"""Source-policy originals through the existing reader; no hosted model claim."""
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
from types import SimpleNamespace

import pytest
from orchestrator import scientific_policy_references as policy
from orchestrator import scientific_evidence_access as access, scientific_evidence_runtime as runtime
from orchestrator import scientific_authority as authority, hosted_context as hosted
from orchestrator.hosted_cycle import encoded
from test_scientific_evidence_access import capture, case


@pytest.fixture
def source_root(tmp_path, monkeypatch):
    original = Path(__file__).resolve().parents[1]
    root = tmp_path / "source"
    context = authority.context(original)
    paths = {"configs/scientific-operating-context.json", context["binding"]["path"],
             context["policy"]["direction_path"], *context["operating_context"]["documents"]}
    for name in paths:
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original / name, target)
    marker = root / "orchestrator/scientific_policy_references.py"
    marker.parent.mkdir(parents=True)
    marker.write_text("SCIENTIFIC_POLICY_REFERENCE_VERSION = 1\n")
    # The real source-tree gate has independent tests. This fixture checks the
    # new immutable marker and all actual current policy/document hashes.
    monkeypatch.setattr("orchestrator.remote_supervisor.checked_source", lambda path, source: Path(path))
    return root


@pytest.fixture
def bound(capture, source_root, tmp_path):
    store, folder, request, _, _, _ = capture
    source = request["target"]["source"]
    packet = {"fixture": "Synthetic task only; no scientific authority"}
    native = access.capture_changes(store, [request["identity"]], source=source,
                                   task_binding=access.sha(encoded(packet)))
    complete = policy.capture(source_root, source, packet, native)
    directory = tmp_path / "policy-capture"
    descriptor = access.write_capture(directory, complete)
    reader = access.Reader(directory, descriptor["manifest_sha256"], source=source,
                           task_binding=descriptor["task_binding"], owner=os.getuid())
    shared = authority.context(source_root)
    original = {"shared_policy": shared, "verified_source_commit": source,
                "task_packet": {"sha256": descriptor["task_binding"]},
                "task_state": {"criticism": "REQUEST_CHANGES stays unresolved"}}
    value = {"descriptor": descriptor, "directory": str(directory), "role": "reviewer"}
    return source, packet, native, complete, reader, original, value


@pytest.mark.parametrize("role", ["author", "reviewer", "disposition"])
def test_all_roles_can_discover_search_and_page_the_originals(source_root, bound, tmp_path, role):
    source, packet, native, complete, reader, original, value = bound
    policy.verify_reader(source_root, source, reader)
    session = access.Session(reader, tmp_path / ("journal-" + role), role=role,
                             task_binding=reader.manifest["task_binding"])
    listed = session.call("list", {"capture": reader.identity, "cursor": 0, "kind": policy.KIND})
    assert listed["ok"] is True
    assert len(reader.records) == len(native["manifest"]["records"]) + 3
    rows = [row for row in reader.records if row["kind"] == policy.KIND]
    assert {row["name"] for row in rows} == {policy.PREFIX + name for name in policy.DOCUMENTS}
    for row in rows:
        offset = 0
        parts = []
        while offset is not None:
            delivered = session.call("read", {"capture": reader.identity, "name": row["name"],
                "sha256": row["sha256"], "offset": offset, "characters": access.READ_CHARACTERS})
            assert delivered["ok"] is True
            response = delivered["result"]
            assert response["content_utf8_bytes"] <= access.REPLY_BYTES
            parts.append(response["content"])
            offset = response["next_offset_characters"]
        raw = (source_root / row["provenance"]["path"]).read_bytes()
        assert "".join(parts).encode() == raw
        assert access.sha(raw) == row["sha256"]
    found = session.call("search", {"capture": reader.identity, "cursor": 0,
                                  "text": "scientific acceptance", "name": rows[0]["name"]})
    assert found["ok"] is True and "matches" in found["result"]
    calls, returned_bytes, _ = session._history()
    assert calls > 4 and returned_bytes > sum(row["utf8_bytes"] for row in rows)
    assert original["shared_policy"] == authority.context(source_root)


def test_projection_keeps_core_literal_and_exact_guards_and_restores(source_root, bound):
    source, _, _, _, _, original, value = bound
    before = deepcopy(original)
    view, prompt = policy.presentation(source_root, before, original, "unchanged prompt", source,
                                       evidence_access=value)
    assert prompt == "unchanged prompt"
    assert policy.restore(source_root, view, before, original, source, value) == before
    for name, original_row in original["shared_policy"]["operating_context"]["documents"].items():
        shown = view["shared_policy"]["operating_context"]["documents"][name]
        if name not in policy.DOCUMENTS:
            assert shown == original_row
            continue
        reference = shown["text"]
        lines = original_row["text"].splitlines(keepends=True)
        for guard, (first, last) in zip(reference["literal_safeguards"], policy.DOCUMENTS[name][1]):
            assert guard["text"] == "".join(lines[first - 1:last])
        assert reference["capture"] == value["descriptor"]["manifest_sha256"]
    for key in ("policy", "binding", "direction"):
        assert view["shared_policy"][key] == original["shared_policy"][key]
    assert view["shared_policy"]["operating_context"]["manifest"] == original["shared_policy"]["operating_context"]["manifest"]
    assert view["task_state"] == before["task_state"]
    assert len(encoded(view)) < len(encoded(before)) - 30000


@pytest.mark.parametrize("change", ["guard", "reference", "core", "task", "metadata"])
def test_changed_presentation_never_restores(source_root, bound, change):
    source, _, _, _, _, original, value = bound
    view, _ = policy.presentation(source_root, original, original, "", source, evidence_access=value)
    name = next(iter(policy.DOCUMENTS))
    if change == "guard": view["shared_policy"]["operating_context"]["documents"][name]["text"]["literal_safeguards"][0]["text"] = "Approve"
    elif change == "reference": view["shared_policy"]["operating_context"]["documents"][name]["text"]["name"] = "/etc/passwd"
    elif change == "core": view["shared_policy"]["direction"] = "New authority"
    elif change == "task": view["task_state"]["criticism"] = "APPROVE"
    else: view[policy.META]["capture"] = "f" * 64
    with pytest.raises(ValueError, match="PRESENTATION_CHANGED"):
        policy.restore(source_root, view, original, original, source, value)


def test_existing_trusted_policy_reference_names_both_restoration_layers(source_root, bound):
    source, _, _, _, _, original, value = bound
    previous = {**hosted.trusted_policy_reference(original["shared_policy"], source),
                "schema": hosted.RESTORED_POLICY_SCHEMA,
                "presented_policy_sha256": access.sha(encoded(original["shared_policy"]))}
    prompt = hosted.TRUSTED_POLICY_MARKER + json.dumps(previous) + "\nunchanged suffix"
    view, rendered = policy.presentation(source_root, original, original, prompt, source,
                                        evidence_access=value)
    updated, _ = json.JSONDecoder().raw_decode(rendered.split(hosted.TRUSTED_POLICY_MARKER)[1])
    assert updated["schema"] == policy.TRUSTED_REFERENCE
    assert updated["policy_sha256"] == previous["policy_sha256"]
    assert updated["presented_policy_sha256"] == access.sha(encoded(view["shared_policy"]))
    assert "same-prompt outer-document" in updated["trust"]
    assert rendered.endswith("unchanged suffix")
    previous["policy_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="TRUSTED_REFERENCE_CHANGED"):
        policy.presentation(source_root, original, original,
            hosted.TRUSTED_POLICY_MARKER + json.dumps(previous), source, evidence_access=value)


@pytest.mark.parametrize("change", ["missing", "changed", "extra", "source", "provenance"])
def test_actual_reader_refuses_missing_changed_or_extra_procedures(source_root, bound, change):
    source, _, _, _, reader, _, _ = bound
    row = next(row for row in reader.records if row["kind"] == policy.KIND)
    if change == "missing": reader.records.remove(row); del reader.rows[row["name"]]
    elif change == "changed":
        artifact = reader.directory / "objects" / (row["sha256"] + ".txt")
        artifact.chmod(0o600)
        artifact.write_text("changed")
        artifact.chmod(0o400)
    elif change == "extra":
        extra = {**deepcopy(row), "name": policy.PREFIX + "unreviewed.txt"}
        reader.records.append(extra); reader.rows[extra["name"]] = extra
    elif change == "source": reader.manifest["source"] = "f" * 40
    else: row["provenance"]["path"] = "private/unrelated.txt"
    with pytest.raises(ValueError): policy.verify_reader(source_root, source, reader)


def test_changed_source_document_has_full_text_fallback_after_complete_authentication(source_root, bound):
    source, packet, native, _, _, original, value = bound
    name = next(iter(policy.DOCUMENTS))
    path = source_root / name
    path.write_bytes(path.read_bytes() + b"\nNew source text must not inherit old selections.\n")
    with pytest.raises(ValueError, match="CONTEXT_CHANGED"):
        policy.capture(source_root, source, packet, native)
    manifest_path = source_root / "configs/scientific-operating-context.json"
    manifest = json.loads(manifest_path.read_bytes())
    manifest["documents"][name] = access.sha(path.read_bytes())
    manifest_path.write_bytes(encoded(manifest))
    changed = {**deepcopy(original), "shared_policy": authority.context(source_root)}
    view, prompt = policy.presentation(source_root, changed, changed, "same", source,
                                       evidence_access=value)
    assert view is changed and prompt == "same"
    assert policy.META not in view
    assert view["shared_policy"]["operating_context"]["documents"][name]["text"].endswith("old selections.\n")


def test_legacy_or_no_retrieval_keeps_full_originals(source_root, bound):
    source, packet, native, _, _, original, value = bound
    assert policy.presentation(source_root, original, original, "same", source) == (original, "same")
    (source_root / "orchestrator/scientific_policy_references.py").unlink()
    assert policy.capture(source_root, source, packet, native) is native
    assert policy.presentation(source_root, original, original, "same", source, evidence_access=value) == (original, "same")


@pytest.mark.parametrize("marker", ["SCIENTIFIC_POLICY_REFERENCE_VERSION = True", "SCIENTIFIC_POLICY_REFERENCE_VERSION = 2",
    "SCIENTIFIC_POLICY_REFERENCE_VERSION: int = 1", "SCIENTIFIC_POLICY_REFERENCE_VERSION = 1\nSCIENTIFIC_POLICY_REFERENCE_VERSION = 1",
    "if True:\n SCIENTIFIC_POLICY_REFERENCE_VERSION = 1"])
def test_source_marker_is_exact(source_root, marker):
    (source_root / "orchestrator/scientific_policy_references.py").write_text(marker)
    with pytest.raises(ValueError, match="SOURCE_PROFILE_CHANGED"):
        policy.enabled(source_root, "a" * 40)


def test_native_capture_constructor_appends_policy_after_original_checks(source_root, bound, monkeypatch):
    source, packet, native, complete, _, _, _ = bound
    calls = []
    monkeypatch.setattr(runtime, "_capture_originals", lambda *args, **kwargs: deepcopy(native))
    monkeypatch.setattr("orchestrator.investigator_eligibility263_reconsideration.capture_original_history",
                        lambda config, packet, source, captured, client, **kwargs: captured)
    monkeypatch.setattr("orchestrator.scientific_runtime_prerequisites.verify", lambda *args, **kwargs: calls.append("prerequisites"))
    result = runtime._capture({"source_root": str(source_root)}, packet, source, root=source_root)
    assert result == complete and calls == ["prerequisites"]


def test_role_preparation_refuses_missing_policy_before_any_cache_write(source_root, bound, tmp_path, monkeypatch):
    source, packet, native, _, _, _, value = bound
    directory = tmp_path / "missing-policy-capture"
    descriptor = access.write_capture(directory, native)
    reader = access.Reader(directory, descriptor["manifest_sha256"], source=source,
                           task_binding=descriptor["task_binding"], owner=os.getuid())
    monkeypatch.setattr(runtime.evidence, "Reader", lambda *args, **kwargs: reader)
    monkeypatch.setattr(runtime.os, "getuid", lambda: 0)
    work = tmp_path / "must-not-be-created"
    with pytest.raises(ValueError, match="READER_SCOPE_CHANGED"):
        runtime.prepare({**value, "descriptor": descriptor, "directory": str(directory)}, source=source,
            source_root=source_root, work=work, account=SimpleNamespace(pw_uid=1000, pw_gid=1000))
    assert not work.exists()
