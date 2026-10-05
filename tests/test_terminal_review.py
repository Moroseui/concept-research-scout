"""Synthetic original-byte fixtures only; no real review is qualified or executed."""
from copy import deepcopy
from datetime import datetime, timezone
import json
from types import SimpleNamespace

import pytest

from orchestrator import change_requests as changes
from orchestrator import deployment_review as gate
from orchestrator import dispatch_limiter as limiter
from orchestrator import terminal_review as terminal

SOURCE = "a" * 40
SESSION = "11111111-1111-4111-8111-111111111111"
HUMAN = {"kind": "human", "identity": "project-operator"}
AGENT = {"kind": "agent", "family": "codex", "model": "synthetic",
         "session_id": "synthetic-only"}
GATES = ["held-deployment", "accounting-halt", "retained-history-audit",
         "conditional-activation", "scientific-acceptance"]


def encoded(value):
    return changes.encoded(value) + b"\n"


def event_record(core):
    return {**core, "identity": gate.digest(changes.encoded(core))}


def journal(events):
    return b"".join(encoded(event) for event in events)


def session_events(report, path):
    return [
        {"type": "user", "sessionId": SESSION, "uuid": "synthetic-human-request",
         "origin": {"kind": "human"}, "promptSource": "typed",
         "isSidechain": False,
         "message": {"content": "Review this synthetic fixture only."}},
        {"type": "assistant", "sessionId": SESSION, "message": {
            "id": "synthetic-read", "model": "claude-opus-4-8",
            "usage": {"input_tokens": 2, "output_tokens": 3},
            "content": [{"type": "tool_use", "id": "read-1", "name": "Read",
                         "input": {"file_path": "/synthetic/source/example.py"}}]}},
        {"type": "user", "sessionId": SESSION, "message": {"content": [
            {"type": "tool_result", "tool_use_id": "read-1",
             "is_error": False, "content": "Synthetic source only."}]}},
        {"type": "assistant", "sessionId": SESSION, "message": {
            "id": "synthetic-final", "model": "claude-opus-4-8",
            "usage": {"input_tokens": 4, "output_tokens": 5},
            "content": [{"type": "tool_use", "id": "write-1", "name": "Write",
                         "input": {"file_path": path, "content": report.decode()}}]}},
        {"type": "user", "sessionId": SESSION, "message": {"content": [
            {"type": "tool_result", "tool_use_id": "write-1",
             "is_error": False, "content": "File created."}]}},
    ]


def rebind(f):
    """Seal changed synthetic evidence, so semantic tests get past outer hashes."""
    f.manifest["files"] = {
        name: gate.digest(raw) for name, raw in f.raw.items()
        if name not in {"report.md", "session.jsonl"}
    }
    f.manifest_raw = encoded(f.manifest)
    f.statement["manifest_sha256"] = gate.digest(f.manifest_raw)
    fence = chr(96) * 3
    f.raw["report.md"] = (
        "Synthetic review only. Historical REQUEST_CHANGES is preserved.\n"
        "Final source/integration verdict: APPROVE\n"
        + fence + "terminal-review-verdict\n"
        + json.dumps(f.statement, sort_keys=True) + "\n" + fence + "\n"
    ).encode()
    f.events = session_events(f.raw["report.md"], f.manifest["report_path"])
    f.raw["session.jsonl"] = journal(f.events)
    return f


def validate(f):
    return terminal.validate(f.manifest_raw, f.raw, f.proposal_raw, f.source_files)


@pytest.fixture
def evidence(monkeypatch):
    # Patch only the immutable anchor DATA to synthetic, genuinely hash-valid
    # changes.validate_originals input. No validator or gate function is mocked.
    operator = b"Synthetic operator decision; fixture grants no real authority."
    section = (b"Synthetic terminal route only. " * 100)[:2484]
    assert len(section) == 2484
    amendment = b"X" * 1641 + section + b"\nSynthetic remainder.\n"
    raw = {}

    def ref(name, body):
        name = "evidence/" + name
        raw["authority/" + name] = body
        return {"artifact": name, "sha256": gate.digest(body), "size": len(body)}

    operator_ref = ref("operator.txt", operator)
    amendment_ref = ref("amendment.md", amendment)
    section_ref = ref("section.md", section)
    core = {
        "schema": changes.SCHEMA, "submitter": HUMAN,
        "target": {"source": terminal.BASE_SOURCE, "task": "synthetic-review",
                   "files": {}},
        "requested_change": "Synthetic terminal-review tests only.",
        "scope_limits": ["No operational authority; synthetic fixture only."],
    }
    request = {**core, "identity": gate.digest(changes.encoded(core)),
               "status": "SUBMITTED", "submitted_at_utc": "2026-01-01T00:00:00Z",
               "execution_status": "NOT_EXECUTED_BY_SUBMISSION",
               "review_status": "PENDING_PROPORTIONATE_REVIEW"}
    request_raw = encoded(request)
    raw["authority/request.json"] = request_raw
    authorization = event_record({
        "schema": changes.EVENT_SCHEMA, "request_identity": request["identity"],
        "sequence": 1, "previous_sha256": gate.digest(request_raw),
        "event": "AUTHORIZED", "actor": HUMAN,
        "recorded_at_utc": "2026-01-01T00:00:01Z",
        "payload": {
            "rationale": "Synthetic exact route authorization.",
            "authority_reference": operator_ref,
            "operator_original_sha256": gate.digest(operator),
            "candidate_approved": False, "installation_approved": False,
            "activation_approved": False,
            "review_policy": {"source": terminal.BASE_SOURCE,
                              "approved_amendment": amendment_ref,
                              "approved_section": section_ref},
        },
    })
    auth_key = "authority/events/0001-" + authorization["identity"] + ".json"
    raw[auth_key] = encoded(authorization)
    anchors = {
        "AUTH_REQUEST": request["identity"], "AUTH_EVENT": authorization["identity"],
        "AUTH_EVENT_SHA": gate.digest(raw[auth_key]),
        "OPERATOR_SHA": gate.digest(operator), "AMENDMENT_SHA": gate.digest(amendment),
        "SECTION_SHA": gate.digest(section),
    }
    for name, value in anchors.items():
        monkeypatch.setattr(terminal, name, value)
    history = {name: ("Synthetic original " + name + ": REQUEST_CHANGES.\n").encode()
               for name in terminal.PRIOR_REVIEWS}
    monkeypatch.setattr(terminal, "PRIOR_REVIEWS",
                        {name: gate.digest(body) for name, body in history.items()})
    raw.update({"history/" + name: body for name, body in history.items()})
    source_files = {"orchestrator/example.py": b"# Synthetic source\n",
                    "configs/example.json": b'{"synthetic":true}\n'}
    raw.update({"target.json": b'{"new":"synthetic"}\n',
                "previous.json": b'{"previous":"synthetic"}\n',
                "recovery.json": b'{"synthetic_recovery":true}\n'})
    selected = [{"request": "1" * 64, "applied": "2" * 64}]
    proposal = {
        "source": SOURCE, "review_profile": terminal.PROFILE,
        "source_files": {name: gate.digest(body) for name, body in source_files.items()},
        "targets": {"/synthetic/controller.json": {"sha256": gate.digest(raw["target.json"])}},
        "previous_files": {"/synthetic/controller.json": {"sha256": gate.digest(raw["previous.json"])}},
        "recovery_sha256": gate.digest(raw["recovery.json"]), "changes": selected,
    }
    proposal_raw = encoded(proposal)
    raw["proposal.json"] = proposal_raw
    context = [{"projection": {"selected_applications": [{
        "request": selected[0]["request"], "event": {
            "identity": selected[0]["applied"], "event": "APPLIED",
            "payload": {"result_binding": {"source": SOURCE}}}}]}}]
    raw["changes.json"] = encoded(context)
    raw["change-bindings.json"] = encoded(changes.review_bindings(
        SOURCE, gate.digest(proposal_raw), selected))
    manifest = {
        "schema": terminal.PROFILE, "base_source": terminal.BASE_SOURCE,
        "source": SOURCE, "proposal_sha256": gate.digest(proposal_raw),
        "files": {}, "report_path": "/synthetic/reviews/final.md",
        "changes_sha256": gate.digest(raw["changes.json"]),
        "change_bindings_sha256": gate.digest(raw["change-bindings.json"]),
    }
    dispositions = {
        "C001": "held-science", "C003": "held-deployment", "C004": "preserve",
        "C005": "held-accounting", "C008": "held-deployment",
        "C009": "held-science", "C010": "deferred-nonblocking", "C011": "preserve",
    }
    statement = {
        "schema": terminal.PROFILE, "source": SOURCE,
        "proposal_sha256": gate.digest(proposal_raw), "manifest_sha256": "",
        "session_id": SESSION, "scope": "material-source-integration",
        "verdict": "APPROVE", "inspected": ["orchestrator/example.py"],
        "unavailable": [], "unverified": ["Actual installed behavior."],
        "findings": {name: {"disposition": dispositions.get(name, "resolved"),
                           "reason": "Synthetic scoped finding disposition."}
                     for name in terminal.FINDINGS},
        "resolution_of": terminal.BASE_SOURCE, "remaining_gates": GATES[:],
    }
    return rebind(SimpleNamespace(raw=raw, manifest=manifest, statement=statement,
                                  source_files=source_files, proposal_raw=proposal_raw,
                                  auth_key=auth_key))


def test_synthetic_original_chain_and_final_write_qualify_source_only(evidence):
    f = evidence
    state = changes.validate_originals(
        f.raw["authority/request.json"],
        {f.auth_key.removeprefix("authority/events/"): f.raw[f.auth_key]},
        lambda name: f.raw["authority/" + name])
    assert state["events"][0]["identity"] == terminal.AUTH_EVENT
    result = validate(f)
    assert result["response"]["structured_output"]["verdict"] == "APPROVE"
    assert result["terminal_session"]["provider_model"] == "claude-opus-4-8"
    assert result["terminal_session"]["accounting_reconciled"] is False
    assert result["terminal_session"]["provider_attestation_claimed"] is False
    assert result["approval_confers_deployment_authority"] is False
    assert all(body in result["private_text"].values()
               for name, body in f.raw.items() if name.startswith("history/"))


@pytest.mark.parametrize("verdict", ["REQUEST_CHANGES", "IN_PROGRESS", "REVISE"])
def test_nonapproval_original_never_qualifies(evidence, verdict):
    evidence.statement["verdict"] = verdict
    rebind(evidence)
    with pytest.raises(ValueError, match="FINAL_SOURCE_APPROVAL_REQUIRED"):
        validate(evidence)


@pytest.mark.parametrize("field,value", [
    ("scope", "enabling-only"), ("inspected", []), ("unavailable", None),
    ("unverified", [""]), ("remaining_gates", []),
])
def test_explicit_scope_and_remaining_gates_required(evidence, field, value):
    evidence.statement[field] = value
    rebind(evidence)
    with pytest.raises(ValueError):
        validate(evidence)


@pytest.mark.parametrize("finding", ["C001", "C006", "C007", "C011"])
def test_every_original_finding_requires_disposition(evidence, finding):
    del evidence.statement["findings"][finding]
    rebind(evidence)
    with pytest.raises(ValueError, match="ADVERSE_FINDINGS_DISPOSITION_REQUIRED"):
        validate(evidence)


@pytest.mark.parametrize("finding", ["C006", "C007"])
def test_importer_integration_cannot_be_deferred_in_source_approval(evidence, finding):
    evidence.statement["findings"][finding]["disposition"] = "held-deployment"
    rebind(evidence)
    with pytest.raises(ValueError, match="IMPORT_INTEGRATION_UNRESOLVED"):
        validate(evidence)


@pytest.mark.parametrize("change", ["missing", "altered"])
def test_retained_negative_originals_required_even_after_rebinding(evidence, change):
    key = "history/003-claude-followup.md"
    if change == "missing":
        del evidence.raw[key]
    else:
        evidence.raw[key] = b"Synthetic substituted approval.\n"
    rebind(evidence)
    with pytest.raises(ValueError, match="ORIGINAL_ADVERSE_REVIEWS_REQUIRED"):
        validate(evidence)


def test_authority_original_cannot_be_changed_with_new_outer_manifest(evidence):
    evidence.raw["authority/evidence/operator.txt"] += b" changed"
    rebind(evidence)
    with pytest.raises(ValueError, match="CHANGE_EVIDENCE_CHANGED"):
        validate(evidence)


def test_authority_chain_link_is_verified_not_just_pinned_bytes(evidence, monkeypatch):
    event = json.loads(evidence.raw[evidence.auth_key])
    event["previous_sha256"] = "f" * 64
    evidence.raw[evidence.auth_key] = encoded(event)
    monkeypatch.setattr(terminal, "AUTH_EVENT_SHA", gate.digest(evidence.raw[evidence.auth_key]))
    rebind(evidence)
    with pytest.raises(ValueError, match="CHANGE_EVENT_CHAIN_INVALID"):
        validate(evidence)


def test_valid_agent_authored_chain_is_not_operator_authorization(evidence, monkeypatch):
    event = json.loads(evidence.raw.pop(evidence.auth_key))
    event["actor"] = AGENT
    event.pop("identity")
    event = event_record(event)
    key = "authority/events/0001-" + event["identity"] + ".json"
    evidence.raw[key] = encoded(event)
    monkeypatch.setattr(terminal, "AUTH_EVENT", event["identity"])
    monkeypatch.setattr(terminal, "AUTH_EVENT_SHA", gate.digest(evidence.raw[key]))
    rebind(evidence)
    with pytest.raises(ValueError, match="OPERATOR_AUTHORIZATION_REQUIRED"):
        validate(evidence)


def test_missing_authorization_event_cannot_qualify(evidence):
    del evidence.raw[evidence.auth_key]
    rebind(evidence)
    with pytest.raises(ValueError, match="OPERATOR_AUTHORIZATION_REQUIRED"):
        validate(evidence)


@pytest.mark.parametrize("field,value", [
    ("source", "b" * 40), ("proposal_sha256", "f" * 64),
    ("base_source", "c" * 40),
])
def test_manifest_source_and_proposal_binding(evidence, field, value):
    evidence.manifest[field] = value
    rebind(evidence)
    with pytest.raises(ValueError, match="EXACT_SOURCE_PROPOSAL_REQUIRED"):
        validate(evidence)


def test_changed_source_config_rejected(evidence):
    evidence.source_files["configs/example.json"] = b'{"synthetic":"changed"}\n'
    with pytest.raises(ValueError, match="SOURCE_INVENTORY_CHANGED"):
        validate(evidence)


@pytest.mark.parametrize("name,reason", [
    ("target.json", "CONFIGURATION_ORIGINAL_MISSING"),
    ("previous.json", "CONFIGURATION_ORIGINAL_MISSING"),
    ("recovery.json", "RECOVERY_ORIGINAL_MISSING"),
    ("proposal.json", "EXACT_PROPOSAL_ORIGINAL_REQUIRED"),
])
def test_missing_bound_originals_rejected_after_manifest_rebind(evidence, name, reason):
    del evidence.raw[name]
    rebind(evidence)
    with pytest.raises(ValueError, match=reason):
        validate(evidence)


def test_changed_config_rejected_even_if_outer_hash_is_updated(evidence):
    evidence.raw["target.json"] = b'{"new":"unreviewed"}\n'
    rebind(evidence)
    with pytest.raises(ValueError, match="CONFIGURATION_ORIGINAL_MISSING"):
        validate(evidence)


def test_selected_application_cannot_name_other_source(evidence):
    context = json.loads(evidence.raw["changes.json"])
    context[0]["projection"]["selected_applications"][0]["event"]["payload"]["result_binding"]["source"] = "b" * 40
    evidence.raw["changes.json"] = encoded(context)
    evidence.manifest["changes_sha256"] = gate.digest(evidence.raw["changes.json"])
    rebind(evidence)
    with pytest.raises(ValueError, match="DEPLOYMENT_SELECTED_APPLICATION_SOURCE_CHANGED"):
        validate(evidence)


@pytest.mark.parametrize("field,value", [
    ("source", "b" * 40), ("proposal_sha256", "f" * 64),
    ("manifest_sha256", "f" * 64), ("resolution_of", "b" * 40),
])
def test_final_report_binds_exact_reviewed_inputs(evidence, field, value):
    evidence.statement[field] = value
    rebind(evidence)
    if field == "manifest_sha256":
        evidence.statement[field] = value
        fence = chr(96) * 3
        evidence.raw["report.md"] = ("Final source/integration verdict: APPROVE\n" + fence + "terminal-review-verdict\n"
            + json.dumps(evidence.statement) + "\n" + fence + "\n").encode()
        evidence.events = session_events(evidence.raw["report.md"], evidence.manifest["report_path"])
        evidence.raw["session.jsonl"] = journal(evidence.events)
    with pytest.raises(ValueError, match="REVIEWED_BINDING_CHANGED"):
        validate(evidence)


@pytest.mark.parametrize("mutation,reason", [
    ("missing-result", "ORIGINAL_SUCCESSFUL_CLAUDE_WRITE_REQUIRED"),
    ("failed-result", "ORIGINAL_SUCCESSFUL_CLAUDE_WRITE_REQUIRED"),
    ("early-result", "ORIGINAL_SUCCESSFUL_CLAUDE_WRITE_REQUIRED"),
    ("wrong-content", "ORIGINAL_SUCCESSFUL_CLAUDE_WRITE_REQUIRED"),
    ("wrong-path", "ORIGINAL_SUCCESSFUL_CLAUDE_WRITE_REQUIRED"),
    ("user-forgery", "ORIGINAL_SUCCESSFUL_CLAUDE_WRITE_REQUIRED"),
    ("superseded", "REPORT_WAS_SUPERSEDED"),
    ("missing-model", "ACTUAL_CLAUDE_MODEL_REQUIRED"),
    ("requested-only", "ACTUAL_CLAUDE_MODEL_REQUIRED"),
    ("wrong-session", "SESSION_ID_CHANGED"),
])
def test_final_write_provenance_failures(evidence, mutation, reason):
    events = deepcopy(evidence.events)
    write = events[3]["message"]["content"][0]
    if mutation == "missing-result":
        events.pop()
    elif mutation == "failed-result":
        events[-1]["message"]["content"][0]["is_error"] = True
    elif mutation == "early-result":
        events[3], events[4] = events[4], events[3]
    elif mutation == "wrong-content":
        write["input"]["content"] = "Unrelated synthetic report."
    elif mutation == "wrong-path":
        write["input"]["file_path"] = "/synthetic/other.md"
    elif mutation == "user-forgery":
        events[3]["type"] = "user"
    elif mutation == "superseded":
        later = deepcopy(events[3])
        later["message"]["id"] = "later"
        later["message"]["content"][0]["id"] = "write-2"
        later["message"]["content"][0]["input"]["content"] = "Later adverse report."
        events.append(later)
    elif mutation in {"missing-model", "requested-only"}:
        events[3]["message"].pop("model")
        if mutation == "requested-only":
            events[3]["requested_model"] = "claude-fable-5"
    elif mutation == "wrong-session":
        events[3]["sessionId"] = "22222222-2222-4222-8222-222222222222"
    evidence.raw["session.jsonl"] = journal(events)
    with pytest.raises(ValueError, match=reason):
        validate(evidence)


def test_arbitrary_approve_text_is_not_an_independent_verdict(evidence):
    evidence.raw["report.md"] = b"Synthetic driver summary says APPROVE.\n"
    evidence.raw["session.jsonl"] = journal(session_events(
        evidence.raw["report.md"], evidence.manifest["report_path"]))
    with pytest.raises(ValueError, match="ONE_INDEPENDENT_VERDICT_BLOCK_REQUIRED"):
        validate(evidence)


def test_multiple_verdict_blocks_rejected(evidence):
    evidence.raw["report.md"] *= 2
    evidence.raw["session.jsonl"] = journal(session_events(
        evidence.raw["report.md"], evidence.manifest["report_path"]))
    with pytest.raises(ValueError, match="ONE_INDEPENDENT_VERDICT_BLOCK_REQUIRED"):
        validate(evidence)


def test_usage_fragments_are_preserved_without_claiming_billing(evidence):
    extra = deepcopy(evidence.events[1])
    extra["message"]["content"] = [{"type": "text", "text": "Synthetic public prose."}]
    extra["message"]["usage"] = {"input_tokens": 3, "output_tokens": 4}
    evidence.events.insert(2, extra)
    evidence.raw["session.jsonl"] = journal(evidence.events)
    result = validate(evidence)["terminal_session"]
    assert result["usage_fragments_by_message"]["synthetic-read"] == [
        {"input_tokens": 2, "output_tokens": 3},
        {"input_tokens": 3, "output_tokens": 4}]
    assert result["accounting_reconciled"] is False


def test_tool_iterations_do_not_create_manual_request_units(evidence):
    result = validate(evidence)["terminal_session"]
    assert len(result["manual_units"]) == 1
    assert next(iter(result["manual_units"].values()))["request_uuid"] == "synthetic-human-request"


@pytest.mark.parametrize("mutation", ["missing", "synthetic", "duplicate"])
def test_manual_request_requires_original_unambiguous_human_unit(evidence, mutation):
    events = deepcopy(evidence.events)
    if mutation == "missing":
        events.pop(0)
    elif mutation == "synthetic":
        events[0]["isSynthetic"] = True
    else:
        events.append(deepcopy(events[0]))
    evidence.raw["session.jsonl"] = journal(events)
    with pytest.raises(ValueError, match="MANUAL_REQUEST"):
        validate(evidence)


@pytest.mark.parametrize("heading", [
    "", "Final source/integration verdict: REQUEST_CHANGES\n",
    "Final source/integration verdict: IN_PROGRESS\n",
    "Final source/integration verdict: APPROVE\n"
    "Final source/integration verdict: REQUEST_CHANGES\n",
])
def test_approving_block_cannot_hide_missing_or_contradictory_final_heading(evidence, heading):
    evidence.raw["report.md"] = evidence.raw["report.md"].replace(
        b"Final source/integration verdict: APPROVE\n", heading.encode())
    evidence.raw["session.jsonl"] = journal(session_events(
        evidence.raw["report.md"], evidence.manifest["report_path"]))
    with pytest.raises(ValueError, match="FINAL_VERDICT_HEADING_REQUIRED"):
        validate(evidence)


class SyntheticLedger:
    """In-memory CAS store for the real limiter; pins are synthetic, never Git."""
    def __init__(self):
        self.pin = None
        self.commits = {}

    def read(self):
        return self.pin, deepcopy(self.commits[self.pin]["state"])

    def cas(self, old, state):
        if old != self.pin:
            return False
        limiter.validate(state)
        self.pin = format(len(self.commits) + 1, "040x")
        self.commits[self.pin] = {
            "state": deepcopy(state), "parents": [old] if old else []}
        return True

    def read_commit(self, pin):
        return deepcopy(self.commits[pin])


def accounting_fixture(evidence, prior_count=0):
    review = validate(evidence)
    policy = {
        "status": "RATIFIED", "operator_approval": "Synthetic fixture only.",
        "state_write_permission": "OPERATOR_AUTHORIZED", "n": 48,
        "window": "UTC_CALENDAR_DAY", "state_ref": limiter.REF,
        "server_semantics": "OPERATOR_AUTHORIZED_V1",
        "reset_operators": ["synthetic-operator"],
    }
    store = SyntheticLedger()
    limiter.initialize(store, policy, {
        "actor": "synthetic-operator", "role": "operator",
        "decision_ref": "Synthetic initialization; no actual ledger."})
    now = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
    for i in range(prior_count):
        unrelated = terminal.accounting_event(gate.digest(str(i).encode()), SOURCE)
        limiter.admit_server(store, policy, unrelated, now=now)
    cases = []
    for unit in review["terminal_session"]["manual_units"]:
        event = terminal.accounting_event(unit, SOURCE)
        receipt = limiter.admit_server(store, policy, event, now=now)
        cases.append({"unit_sha256": unit, "event": event,
                      "receipt": receipt, "state_after": store.pin})
    execution = review["execution"]
    account = {
        "schema": "operator-terminal-accounting/v1",
        "manifest_sha256": execution["request_sha256"],
        "report_sha256": execution["response_sha256"],
        "journal_sha256": execution["protocol_sha256"],
        "policy_sha256": gate.digest(json.dumps(policy, sort_keys=True).encode()),
        "ledger_pin": store.pin, "cases": cases,
    }
    f = SimpleNamespace(review=review, policy=policy, store=store, now=now,
                        account=account, allowed_sources={SOURCE})
    return refresh_accounting_state(f)


def refresh_accounting_state(f):
    f.pin, f.state = f.store.read()
    f.account["ledger_pin"] = f.pin
    f.status = {"pin": f.pin, **{
        key: f.state[key] for key in ("count", "day", "sequence", "halted")}}
    return f


def validate_accounting(f):
    return terminal.validate_accounting(
        encoded(f.account), f.review, f.status, f.pin, f.state,
        f.policy, f.allowed_sources, f.store.read_commit)


def test_real_limiter_charge_reconciles_one_request_without_minting_usage(evidence):
    f = accounting_fixture(evidence)
    before = deepcopy(f.store.commits)
    result = validate_accounting(f)
    assert result["manual_units"] == sorted(f.review["terminal_session"]["manual_units"])
    assert result["late_charge"] is True
    assert result["retroactive_pre_admission_claimed"] is False
    assert result["usage_original_sha256"] == f.review["execution"]["protocol_sha256"]
    assert f.store.commits == before
    assert f.state["count"] == 1


def test_warning_48_preserves_notice_and_is_not_hard_halt(evidence):
    f = accounting_fixture(evidence, prior_count=47)
    result = validate_accounting(f)
    assert result["late_charge"] is True
    assert f.state["count"] == 48 and f.state["halted"] is False
    assert f.account["cases"][0]["receipt"]["notification"] == "N"
    assert f.state["notifications"]["48:N"]["threshold"] == "N"


def test_actual_charge_at_96_does_not_clear_hard_halt(evidence):
    f = accounting_fixture(evidence, prior_count=95)
    assert f.account["cases"][0]["receipt"]["status"] == "ADMITTED"
    assert f.state["halted"] is True and f.state["count"] == 96
    with pytest.raises(ValueError, match="ACCOUNTING_HALT_REMAINS"):
        validate_accounting(f)


def test_charge_remains_valid_on_authenticated_later_descendant(evidence):
    f = accounting_fixture(evidence)
    event = terminal.accounting_event(gate.digest(b"later unrelated fixture request"), SOURCE)
    limiter.admit_server(f.store, f.policy, event, now=f.now)
    refresh_accounting_state(f)
    assert validate_accounting(f)["ledger_pin"] == f.store.pin
    assert f.state["count"] == 2


@pytest.mark.parametrize("mutation,reason", [
    ("missing-case", "ACCOUNTING_CASE_COVERAGE_REQUIRED"),
    ("unknown-unit", "ACCOUNTING_CASE_COVERAGE_REQUIRED"),
    ("unrelated-event", "ACCOUNTING_EXACT_CASE_EVENT_REQUIRED"),
    ("wrong-source", "ACCOUNTING_ORIGINAL_TRANSITION_CHANGED"),
    ("changed-receipt", "ACCOUNTING_ORIGINAL_TRANSITION_CHANGED"),
    ("duplicate-receipt", "ACCOUNTING_ORIGINAL_CHARGE_REQUIRED"),
    ("changed-parent", "ACCOUNTING_ORIGINAL_PARENT_REQUIRED"),
    ("changed-state", "ACCOUNTING_ORIGINAL_TRANSITION_CHANGED"),
    ("moved-pin", "ACCOUNTING_AUTHENTICATED_STATE_CHANGED"),
    ("wrong-status-count", "ACCOUNTING_AUTHENTICATED_STATE_CHANGED"),
    ("changed-policy", "ACCOUNTING_POLICY_CHANGED"),
    ("changed-report", "ACCOUNTING_REVIEW_BINDING_CHANGED"),
    ("changed-journal", "ACCOUNTING_REVIEW_BINDING_CHANGED"),
])
def test_accounting_original_bound_failures(evidence, mutation, reason):
    f = accounting_fixture(evidence)
    case = f.account["cases"][0]
    if mutation == "missing-case":
        f.account["cases"] = []
    elif mutation == "unknown-unit":
        case["unit_sha256"] = "f" * 64
    elif mutation == "unrelated-event":
        case["event"] = terminal.accounting_event("f" * 64, SOURCE)
    elif mutation == "wrong-source":
        case["event"] = terminal.accounting_event(case["unit_sha256"], "b" * 40)
    elif mutation == "changed-receipt":
        case["receipt"]["count"] += 1
    elif mutation == "duplicate-receipt":
        case["receipt"]["duplicate_admission"] = True
    elif mutation == "changed-parent":
        f.store.commits[case["state_after"]]["parents"] = ["f" * 40]
    elif mutation == "changed-state":
        f.store.commits[case["state_after"]]["state"]["sequence"] += 1
    elif mutation == "moved-pin":
        f.pin = "f" * 40
    elif mutation == "wrong-status-count":
        f.status["count"] += 1
    elif mutation == "changed-policy":
        f.policy["n"] = 49
    elif mutation == "changed-report":
        f.account["report_sha256"] = "f" * 64
    elif mutation == "changed-journal":
        f.account["journal_sha256"] = "f" * 64
    with pytest.raises(ValueError, match=reason):
        validate_accounting(f)


def test_retained_charge_object_must_be_on_current_ledger_ancestry(evidence):
    f = accounting_fixture(evidence)
    original_pin = f.pin
    # Same JSON on an independent branch cannot authenticate a retained charge.
    fork = "f" * 40
    f.store.commits[fork] = {"state": deepcopy(f.state), "parents": []}
    f.store.pin = fork
    refresh_accounting_state(f)
    assert original_pin in f.store.commits
    with pytest.raises(ValueError, match="ACCOUNTING_ANCESTRY_REQUIRED"):
        validate_accounting(f)


def test_operator_reset_after_charge_requires_new_reconciliation(evidence):
    f = accounting_fixture(evidence)
    limiter.reset(f.store, f.policy, {
        "actor": "synthetic-operator", "role": "operator",
        "decision_ref": "Synthetic reset only.",
        "expected_sequence": f.state["sequence"]}, now=f.now)
    refresh_accounting_state(f)
    with pytest.raises(ValueError, match="ACCOUNTING_ORIGINAL_TRANSITION_CHANGED"):
        validate_accounting(f)


def test_removed_threshold_notice_cannot_pass_with_retained_charge(evidence):
    f = accounting_fixture(evidence, prior_count=47)
    old, state = f.store.read()
    state["notifications"] = {}
    f.store.cas(old, state)
    refresh_accounting_state(f)
    with pytest.raises(ValueError, match="ACCOUNTING_ORIGINAL_TRANSITION_CHANGED"):
        validate_accounting(f)


@pytest.mark.parametrize('prefix', ['', '## '])
@pytest.mark.parametrize('verdict', ['APPROVE', 'REQUEST_CHANGES', 'IN_PROGRESS'])
def test_supported_heading_preserves_independent_verdict(evidence, prefix, verdict):
    f = evidence
    f.statement['verdict'] = verdict
    fence = chr(96) * 3
    report = (prefix + 'Final source/integration verdict: ' + verdict + '\n'
              + fence + 'terminal-review-verdict\n' + json.dumps(f.statement) + '\n' + fence + '\n').encode()
    assert terminal._statement(report, approval_required=False)['verdict'] == verdict
    if verdict != 'APPROVE':
        with pytest.raises(ValueError): terminal._statement(report)


def test_markdown_heading_still_requires_actual_matching_successful_write(evidence):
    f = evidence
    original = f.raw['report.md']
    f.raw['report.md'] = original.replace(b'Final source/integration verdict:', b'## Final source/integration verdict:')
    with pytest.raises(ValueError): validate(f)  # Genuine journal still binds old bytes.
    f.events = session_events(f.raw['report.md'], f.manifest['report_path'])
    f.raw['session.jsonl'] = journal(f.events)
    validate(f)
    f.events[-1]['message']['content'][0]['is_error'] = True
    f.raw['session.jsonl'] = journal(f.events)
    with pytest.raises(ValueError): validate(f)


@pytest.mark.parametrize('extra', ['Final source/integration verdict: APPROVE',
    '## Final source/integration verdict: APPROVE', '## Final source/integration verdict: REQUEST_CHANGES'])
def test_duplicate_or_conflicting_headings_still_refused(evidence, extra):
    with pytest.raises(ValueError, match='FINAL_VERDICT_HEADING_REQUIRED'):
        terminal._statement(evidence.raw['report.md'] + extra.encode() + b'\n')


@pytest.mark.parametrize('prefix', ['# ', '### ', '> ', '    ', '**', '##  '])
def test_other_heading_or_quotation_shapes_are_not_new_authority(evidence, prefix):
    report = evidence.raw['report.md'].replace(b'Final source/integration verdict:',
        prefix.encode() + b'Final source/integration verdict:')
    with pytest.raises(ValueError, match='FINAL_VERDICT_HEADING_REQUIRED'): terminal._statement(report)


def test_markdown_approve_cannot_overrule_rejected_json(evidence):
    f = evidence
    f.statement['verdict'] = 'REQUEST_CHANGES'
    fence = chr(96) * 3
    report = ('## Final source/integration verdict: APPROVE\n' + fence + 'terminal-review-verdict\n'
              + json.dumps(f.statement) + '\n' + fence + '\n').encode()
    with pytest.raises(ValueError, match='FINAL_SOURCE_APPROVAL_REQUIRED'):
        terminal._statement(report, approval_required=False)
