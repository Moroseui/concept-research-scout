"""Offline integration fixtures; no host, provider or real approval is exercised.

The terminal loader and pure validator run on RM's synthetic original-byte
fixture. Installer tests reuse the synthetic host and mock only the accounting
leaf; its original-ledger validation is covered in test_terminal_review.
"""
from copy import deepcopy
import io
import json
import tarfile

import pytest

from orchestrator import change_requests as changes
from orchestrator import deployment_review as gate
from orchestrator import install_reviewed_deployment as install
from orchestrator import terminal_review as terminal
from orchestrator import inspection_admission_recovery as ledger
from test_deployment_review import fixture as source_deployment, SOURCE, write
from test_deployment_preparation import inputs, run as prepare
from test_inspection_deployment_gate import indexed
from test_reviewed_deployment_install import host, SHA
from test_terminal_review import evidence, rebind, encoded, validate as validated_review
from test_inspection_admission_recovery import Fixture as OriginalLedger


MANDATORY = {
    "orchestrator/terminal_review.py", "orchestrator/deployment_review.py",
    "orchestrator/prepare_deployment_bundle.py",
    "orchestrator/install_reviewed_deployment.py",
    "orchestrator/inspection_admission_recovery.py",
}
PUBLIC_BEGIN = gate.begin_install
FULL_STATE_FINGERPRINT = install.state_fingerprint


def save_archive(f):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        for name, raw in f["evidence"].source_files.items():
            item = tarfile.TarInfo("snapshot/" + name)
            item.size = len(raw)
            archive.addfile(item, io.BytesIO(raw))
    raw = write(f["bundle"] / "source.tar.gz", buffer.getvalue())
    f["proposal"]["archive_sha256"] = gate.digest(raw)
    f["proposal"]["source_files"] = {
        name: gate.digest(raw) for name, raw in f["evidence"].source_files.items()
    }


def save_terminal(f):
    """Rebind synthetic originals, preserving all real semantic validators."""
    e = f["evidence"]
    e.proposal_raw = write(f["bundle"] / "proposal.json", encoded(f["proposal"]))
    e.raw["proposal.json"] = e.proposal_raw
    e.raw["change-bindings.json"] = encoded(changes.review_bindings(
        SOURCE, gate.digest(e.proposal_raw), f["proposal"]["changes"]))
    e.manifest.update(proposal_sha256=gate.digest(e.proposal_raw),
                      changes_sha256=gate.digest(e.raw["changes.json"]),
                      change_bindings_sha256=gate.digest(e.raw["change-bindings.json"]))
    e.statement["proposal_sha256"] = gate.digest(e.proposal_raw)
    rebind(e)
    indexed(f["bundle"] / "terminal-review", {**e.raw, "manifest.json": e.manifest_raw})


@pytest.fixture
def terminal_bundle(tmp_path, monkeypatch, evidence):
    f = source_deployment(tmp_path, monkeypatch, selected=True)
    f["evidence"] = evidence
    evidence.source_files = gate.archive_inventory((f["bundle"] / "source.tar.gz").read_bytes())
    evidence.source_files.update({name: b"# Synthetic integration source only\n" for name in MANDATORY})
    f["proposal"] = json.loads((f["bundle"] / "proposal.json").read_bytes())
    f["proposal"]["review_profile"] = terminal.PROFILE
    recovery = {"schema": "reviewed-deployment-recovery/v1",
                "instructions": "Preserve originals; synthetic test only.",
                "directories": {}, "units_before": {}, "previous_active": {"state": "ABSENT"},
                "preserved_state_sha256": "d" * 64, "preserved_blocked_tasks": {}}
    evidence.raw.update({"target.json": f["new"], "previous.json": f["target"].read_bytes(),
                         "recovery.json": encoded(recovery)})
    f["proposal"]["recovery_sha256"] = gate.digest(evidence.raw["recovery.json"])
    write(f["bundle"] / "literals" / f["proposal"]["recovery_sha256"], evidence.raw["recovery.json"])
    evidence.raw["changes.json"] = encoded([{"projection": changes.review_context(
        f["bundle"] / "changes", f["proposal"]["changes"], source=SOURCE)}])
    save_archive(f)
    save_terminal(f)
    actual = terminal.validate(evidence.manifest_raw, evidence.raw,
                               evidence.proposal_raw, evidence.source_files)
    f["terminal_actor"] = {"kind": "agent", "family": "claude",
                            "model": actual["terminal_session"]["provider_model"],
                            "session_id": actual["response"]["session_id"]}
    f["terminal_payload"] = {**f["payload"], "original_review": {
        key: actual["execution"][key]
        for key in ("request_sha256", "response_sha256", "protocol_sha256")}}
    changes.record(f["change"], "REVIEW", f["terminal_actor"], f["terminal_payload"])
    return f


def verify(f):
    return gate.verify_bundle(f["bundle"], f["root"], SOURCE, prospective=True)


def test_real_terminal_loader_qualifies_source_without_accounting(terminal_bundle, monkeypatch):
    f = terminal_bundle
    monkeypatch.setattr(install, "require_terminal_accounting",
                        lambda *a: pytest.fail("Source verification must not charge or reconcile accounting"))
    result = verify(f)
    assert result["terminal_profile"] == terminal.PROFILE
    assert result["review_model"] == "claude-opus-4-8"
    assert result["review_response_sha256"] == gate.digest(f["evidence"].raw["report.md"])
    assert result["terminal_native_receipts_claimed"] is False
    assert result["unattended_activation_authority"] is False
    assert not (f["bundle"] / "install-intent.json").exists()


@pytest.mark.parametrize("profile", [None, "direct-inspection/v1"])
def test_other_profiles_do_not_route_through_terminal(tmp_path, monkeypatch, profile):
    f = source_deployment(tmp_path, monkeypatch)
    monkeypatch.setattr(terminal, "load", lambda *a: pytest.fail("Wrong profile selected terminal importer"))
    if profile:
        proposal = json.loads((f["bundle"] / "proposal.json").read_bytes())
        proposal["review_profile"] = profile
        raw = write(f["bundle"] / "proposal.json", gate.encoded(proposal))
        leaf = gate.review_originals(f["raw"], SOURCE)
        leaf["private_text"][gate.digest(raw)] = raw
        monkeypatch.setattr(gate, "inspection_review", lambda *a, **k: (leaf, {}))
    assert gate.verify_bundle(f["bundle"], f["root"], SOURCE)["review_model"] == gate.MODEL


@pytest.mark.parametrize("missing", ["orchestrator/terminal_review.py",
                                      "orchestrator/inspection_admission_recovery.py"])
def test_terminal_importer_must_be_in_reviewed_source_inventory(terminal_bundle, missing):
    f = terminal_bundle
    del f["evidence"].source_files[missing]
    save_archive(f)
    save_terminal(f)
    with pytest.raises(ValueError, match="DEPLOYMENT_REQUIRED_SOURCE_MISSING"):
        verify(f)


def test_terminal_preparation_requires_importer_before_output(inputs):
    inputs["plan"]["review_profile"] = terminal.PROFILE
    inputs["plan_file"].write_bytes(gate.encoded(inputs["plan"]))
    with pytest.raises(ValueError, match="PREPARATION_REQUIRED_SOURCE_MISSING"):
        prepare(inputs)
    assert not inputs["destination"].exists()


@pytest.mark.parametrize("mutation,reason", [
    ("config", "DEPLOYMENT_CONFIGURATION_NOT_ACTUALLY_REVIEWED"),
    ("launcher", "DEPLOYMENT_LAUNCHER_IDENTITY_CHANGED"),
])
def test_terminal_review_keeps_configuration_and_launcher_checks(terminal_bundle, monkeypatch, mutation, reason):
    f = terminal_bundle
    if mutation == "config":
        write(f["bundle"] / "literals" / gate.digest(f["new"]), b"Changed config")
    else:
        monkeypatch.setattr(gate, "dependency_metadata", lambda name: {"sha256": "f" * 64})
    with pytest.raises(ValueError, match=reason):
        verify(f)


@pytest.mark.parametrize("mutation,reason", [
    ("negative", "DEPLOYMENT_ACTIVE_CHANGE_PENDING_OR_NEGATIVE"),
    ("pending", "DEPLOYMENT_ACTIVE_CHANGE_PENDING_OR_NEGATIVE"),
    ("origin", "DEPLOYMENT_CHANGE_ORIGINAL_CLAUDE_REVIEW_REQUIRED"),
])
def test_terminal_review_cannot_bypass_canonical_outcome_or_origin(terminal_bundle, mutation, reason):
    f = terminal_bundle
    if mutation == "negative":
        changes.record(f["change"], "REVIEW", f["terminal_actor"], {
            **f["terminal_payload"], "verdict": "REQUEST_CHANGES", "affected_results": "Synthetic held result"})
    else:
        # Remove only synthetic terminal outcome, or every synthetic REVIEW, to
        # expose respectively a still-approved wrong-origin chain or a pending one.
        for path in (f["change"] / "events").glob("*.json"):
            event = json.loads(path.read_bytes())
            if event["event"] == "REVIEW" and (mutation == "pending" or event["actor"] == f["terminal_actor"]):
                path.unlink()
        # Pending fixture must remain a valid chain: both REVIEWs were its suffix.
    with pytest.raises(ValueError, match=reason):
        verify(f)


def test_terminal_profile_rejects_direct_recovery_exemption(terminal_bundle):
    f = terminal_bundle
    recovery = json.loads(f["evidence"].raw["recovery.json"])
    recovery.update(schema=install.DIRECT_RECOVERY, inspection_admissions={})
    raw = encoded(recovery)
    f["evidence"].raw["recovery.json"] = raw
    f["proposal"]["recovery_sha256"] = gate.digest(raw)
    write(f["bundle"] / "literals" / gate.digest(raw), raw)
    save_terminal(f)
    with pytest.raises(ValueError, match="DEPLOYMENT_TERMINAL_STRICT_RECOVERY_REQUIRED"):
        verify(f)


def terminal_host(f, monkeypatch):
    f["proposal"]["review_profile"] = terminal.PROFILE
    proof = {"terminal_profile": terminal.PROFILE, "proposal_sha256": SHA,
             "terminal_accounting_reconciled": True}  # Deliberately insufficient caller assertion.
    monkeypatch.setattr(gate.os, "getuid", lambda: 0)
    monkeypatch.setattr(gate, "verify_bundle", lambda *a, **k: proof.copy())
    return proof


def assert_no_install_mutations(f):
    assert f["target"].read_bytes() == b"old"
    assert not f["root"].parent.exists()
    assert not f["pointer"].exists()
    for name in ("install-intent.json", "upgrade-intent.json", "upgrade-receipt.json"):
        assert not (f["bundle"] / name).exists()
    assert "stop-broker" not in f["events"]
    assert not any(isinstance(e, tuple) and e[0] == "write" for e in f["events"])


def test_public_begin_install_rejects_caller_accounting_flag(host, monkeypatch):
    f = host
    terminal_host(f, monkeypatch)
    # Real accounting loader: a boolean cannot replace the required original.
    with pytest.raises(FileNotFoundError, match="terminal-accounting.json"):
        PUBLIC_BEGIN(f["bundle"], f["root"], SOURCE)
    assert_no_install_mutations(f)


def test_apply_checks_accounting_before_state_inventory_or_intents(host, monkeypatch):
    f = host
    terminal_host(f, monkeypatch)
    def refusal(*args):
        f["events"].append("accounting")
        raise ValueError("SYNTHETIC_ACCOUNTING_NOT_RECONCILED")
    monkeypatch.setattr(install, "require_terminal_accounting", refusal)
    monkeypatch.setattr(install, "state_fingerprint", lambda *a: pytest.fail("Accounting must precede inventory"))
    with pytest.raises(ValueError, match="SYNTHETIC_ACCOUNTING_NOT_RECONCILED"):
        install.apply(SHA, SOURCE)
    assert f["events"] == ["accounting"]
    assert_no_install_mutations(f)


def test_terminal_apply_keeps_strict_state_fingerprint_after_accounting(host, monkeypatch):
    f = host
    terminal_host(f, monkeypatch)
    monkeypatch.setattr(install, "require_terminal_accounting", lambda *a: {"synthetic_checked": True})
    f["state"]["sha256"] = "f" * 64
    with pytest.raises(ValueError, match="DEPLOYMENT_PRESERVED_STATE_MOVED"):
        install.apply(SHA, SOURCE)
    assert_no_install_mutations(f)


def test_terminal_apply_preserves_accounting_receipt_and_holds_workers(host, monkeypatch):
    f = host
    terminal_host(f, monkeypatch)
    accounting = {"schema": "synthetic-accounting-leaf", "actual_fixture_only": True}
    def checked(*args):
        f["events"].append("accounting")
        return accounting
    monkeypatch.setattr(install, "require_terminal_accounting", checked)
    receipt = install.apply(SHA, SOURCE)
    intent = json.loads((f["bundle"] / "upgrade-intent.json").read_bytes())
    assert intent["terminal_accounting"] == accounting
    assert f["events"][0] == "accounting"
    assert receipt["preserved_state"] == f["state"]
    assert receipt["models_started"] == 0
    assert receipt["timers_enabled"] is False
    assert receipt["research_activated"] is False


@pytest.fixture
def late_charge_host(host, evidence, monkeypatch, request):
    """Real limiter/Git originals and transition; only host/source observers stubbed.

    Historical canaries establish the captured ledger inventory, not terminal
    review approval. No real admission, network, systemd or Git write is run.
    The reused ledger fixture writes disposable Git object bytes in Python.
    """
    f = host
    terminal_host(f, monkeypatch)
    parent = f["bundle"].parent / "ledger-host"
    parent.mkdir()
    original = OriginalLedger(parent, n=48)
    (parent / "turns").mkdir()
    controller = f["bundle"].parent / "controller-state"
    controller.mkdir()
    scientific = controller / "scientific-result.txt"
    scientific.write_bytes(b"Preserved scientific evidence, not an accepted result.\n")
    notification = parent / "notifications.json"
    notification.write_bytes(b'{"delivered":false}\n')
    broker = {"turn_root": str(parent / "turns"), "ledger_repo": str(original.repo),
              "policy": original.policy, "sources": [SOURCE]}
    monkeypatch.setattr(install, "CONTROLLER", controller)
    monkeypatch.setattr(install, "JOBS", parent / "absent-jobs")
    monkeypatch.setattr(install, "state_fingerprint", FULL_STATE_FINGERPRINT)
    control = {"revision": 15, "paused": 1, "steering": []}
    before = install.state_inventory(broker)
    f["recovery"].update({
        "schema": install.TERMINAL_RECOVERY,
        "instructions": "Synthetic reviewed baseline; preserve all originals.",
        "preserved_state_sha256": install.inventory_fingerprint(before)["sha256"],
        "terminal_admissions": {
            "ledger": deepcopy(original.baseline),
            "policy_sha256": gate.digest(gate.encoded(original.policy)),
            "non_ledger_files": install._non_ledger(before, broker),
            "control_snapshot": deepcopy(control),
        },
    })
    f["proposal"]["recovery_sha256"] = gate.digest(gate.encoded(f["recovery"]))
    install.validate_recovery(f["recovery"], f["proposal"])
    review = validated_review(evidence)
    # Reuse the separately tested original-review leaf in the offline installer.
    # The actual pure validator above runs; terminal_bundle covers the real loader.
    # Ledger/accounting/transition and restore-intent checks below are not mocked.
    (f["bundle"] / "proposal.json").write_bytes(gate.encoded(f["proposal"]))
    monkeypatch.setattr(terminal, "load", lambda *args: (deepcopy(review), {}))
    cases = []
    if getattr(request, 'param', False):
        # Separate prior research event, not a synthetic manual review request.
        event = {'turn_id':'d'*64,'attempt':'1','source':SOURCE,
                 'branch':'astra/infrastructure-milestone-record','kind':'astra_turn'}
        raw = original.admit(event)
        f['recovery']['terminal_admissions']['preserved_admissions'] = [{
            'event':event,'receipt':json.loads(raw['receipt_original']),
            'state_after':original.head,'receipt_origin':'RECORDED_BROKER_REPLY'}]
        f['proposal']['recovery_sha256'] = gate.digest(gate.encoded(f['recovery']))
        install.validate_recovery(f['recovery'], f['proposal'])
        (f['bundle']/'proposal.json').write_bytes(gate.encoded(f['proposal']))
    for unit in review["terminal_session"]["manual_units"]:
        event = terminal.accounting_event(unit, SOURCE)
        raw = original.admit(event)
        cases.append({"unit_sha256": unit, "event": event,
                      "receipt": json.loads(raw["receipt_original"]), "state_after": original.head})
    execution = review["execution"]
    account = {"schema": "operator-terminal-accounting/v1",
               "manifest_sha256": execution["request_sha256"],
               "report_sha256": execution["response_sha256"],
               "journal_sha256": execution["protocol_sha256"],
               "policy_sha256": gate.digest(json.dumps(original.policy, sort_keys=True).encode()),
               "ledger_pin": original.head, "cases": cases}
    account_raw = encoded(account)
    (f["bundle"] / "terminal-accounting.json").write_bytes(account_raw)

    def read_commit(pin):
        row = ledger._state(original.objects, pin)
        return {"parents": [] if row["parent"] is None else [row["parent"]], "state": row["state"]}

    def checked_accounting(*args):
        f["events"].append("accounting")
        return terminal.validate_accounting(account_raw, review, original.status(), original.head,
                                            original.state, original.policy, {SOURCE}, read_commit)

    def status(_):
        f["events"].append("status")
        return original.status()

    monkeypatch.setattr(install, "require_terminal_accounting", checked_accounting)
    monkeypatch.setattr(install, "authenticated_ledger_status", status)
    monkeypatch.setattr(install, "_inspection_control", lambda: deepcopy(control))
    monkeypatch.setattr(install, "inputs", lambda *a: (f["bundle"], f["proposal"], f["recovery"], broker))
    accounting = checked_accounting()
    f["events"].clear()
    f.update(ledger=original, broker=broker, accounting=accounting, account=account,
             review=review, scientific=scientific, notification=notification, control=control,
             state=FULL_STATE_FINGERPRINT(broker))
    assert f["state"]["sha256"] != f["recovery"]["preserved_state_sha256"]
    return f


def terminal_transition(f):
    return install.terminal_preserved_state(f["bundle"], f["proposal"], f["recovery"],
                                            f["broker"], f["accounting"])


@pytest.mark.parametrize("profile", [None, "direct-inspection/v1"])
def test_terminal_recovery_cannot_be_used_by_other_profiles(late_charge_host, profile):
    f = late_charge_host
    proposal = dict(f["proposal"])
    if profile is None:
        proposal.pop("review_profile")
    else:
        proposal["review_profile"] = profile
    with pytest.raises(ValueError, match="TERMINAL.*PROFILE|RECOVERY.*PROFILE"):
        install.validate_recovery(f["recovery"], proposal)


def test_real_late_charge_transition_allows_offline_upgrade_and_frozen_restore(late_charge_host, monkeypatch):
    f = late_charge_host
    before = deepcopy(f["recovery"])
    receipt = install.apply(SHA, SOURCE)
    intent = json.loads((f["bundle"] / "upgrade-intent.json").read_bytes())
    transition = intent["terminal_admission_transition"]
    assert receipt["terminal_admission_transition"] == transition
    assert transition["original_preserved_state_sha256"] == before["preserved_state_sha256"]
    assert transition["post_review_state"] == receipt["preserved_state"] == f["state"]
    assert intent["terminal_accounting"] == f["accounting"]
    assert receipt["research_activated"] is False and receipt["models_started"] == 0
    assert f["recovery"] == before

    def no_reconciliation(*args):
        pytest.fail("Restore must use the frozen original transition, not refresh accounting or ledger")

    monkeypatch.setattr(install, "require_terminal_accounting", no_reconciliation)
    monkeypatch.setattr(install, "authenticated_ledger_status", no_reconciliation)
    monkeypatch.setattr(install, "terminal_preserved_state", no_reconciliation)
    restored = install.restore(SHA, SOURCE)
    assert restored["preserved_state"] == f["state"]
    assert f["target"].read_bytes() == b"old"
    assert f["root"].exists()  # Preserve the applied source too.
    assert f["scientific"].read_bytes() == b"Preserved scientific evidence, not an accepted result.\n"


@pytest.mark.parametrize("changed", ["scientific", "notification"])
def test_late_accounting_never_exempts_nonledger_state(late_charge_host, changed):
    f = late_charge_host
    f[changed].write_bytes(b"Changed unrelated state\n")
    with pytest.raises(ValueError, match="NON_LEDGER_STATE_CHANGED"):
        install.apply(SHA, SOURCE)
    assert_no_install_mutations(f)


def test_late_transition_refuses_an_unlisted_ordinary_charge(late_charge_host):
    f = late_charge_host
    f["ledger"].admit(terminal.accounting_event("f" * 64, SOURCE))
    with pytest.raises(ValueError, match="ACCOUNTING|SUFFIX|STATE"):
        terminal_transition(f)
    assert_no_install_mutations(f)


def test_changed_control_cannot_enter_terminal_transition(late_charge_host):
    f = late_charge_host
    f["control"]["revision"] += 1
    with pytest.raises(ValueError, match="CONTROL_CHANGED"):
        terminal_transition(f)
    assert "status" not in f["events"]
    assert_no_install_mutations(f)


def test_restore_after_new_charge_refuses_without_reconciliation(late_charge_host, monkeypatch):
    f = late_charge_host
    install.apply(SHA, SOURCE)
    f["ledger"].admit(terminal.accounting_event("e" * 64, SOURCE))
    def forbidden(*args):
        pytest.fail("Restoration cannot fetch, re-account, or rebase")
    monkeypatch.setattr(install, "require_terminal_accounting", forbidden)
    monkeypatch.setattr(install, "authenticated_ledger_status", forbidden)
    monkeypatch.setattr(install, "terminal_preserved_state", forbidden)
    with pytest.raises(ValueError, match="RESULTS_CHANGED_RESTORE_REFUSED"):
        install.restore(SHA, SOURCE)
    assert not (f["bundle"] / "restore-intent.json").exists()


def test_restore_rejects_changed_original_terminal_transition(late_charge_host):
    f = late_charge_host
    install.apply(SHA, SOURCE)
    path = f["bundle"] / "upgrade-intent.json"
    intent = json.loads(path.read_bytes())
    intent["terminal_admission_transition"]["recovery_sha256"] = "0" * 64
    path.write_bytes(gate.encoded(intent))
    with pytest.raises(ValueError, match="ORIGINAL.*TRANSITION_CHANGED"):
        install.restore(SHA, SOURCE)
    assert not (f["bundle"] / "restore-intent.json").exists()


@pytest.mark.parametrize('late_charge_host', [True], indirect=True)
def test_exact_prior_research_charge_survives_held_install_and_frozen_restore(late_charge_host, monkeypatch):
    test_real_late_charge_transition_allows_offline_upgrade_and_frozen_restore(late_charge_host, monkeypatch)
    f = late_charge_host
    intent = json.loads((f['bundle']/'upgrade-intent.json').read_bytes())
    proof = intent['terminal_admission_transition']['ledger_transition']
    assert proof['status'] == 'VERIFIED_TERMINAL_AND_PINNED_PRIOR_ADMISSIONS'
    assert proof['preserved_admissions_count'] == 1
    assert len(proof['suffix']) == len(f['account']['cases']) + 1


@pytest.mark.parametrize('late_charge_host', [True], indirect=True)
def test_prior_research_count_cannot_be_erased_from_frozen_restore(late_charge_host):
    f = late_charge_host; install.apply(SHA, SOURCE)
    path = f['bundle']/'upgrade-intent.json'; intent = json.loads(path.read_bytes())
    intent['terminal_admission_transition']['ledger_transition']['preserved_admissions_count'] = 0
    path.write_bytes(gate.encoded(intent))
    with pytest.raises(ValueError, match='PRIOR_ADMISSION_COUNT_CHANGED'):
        install.restore(SHA, SOURCE)


def test_server_prepaid_continuation_install_and_restore_keep_prior_accounting(late_charge_host,monkeypatch):
    # Reuse validated source/session leaf fixtures; exercise real limiter, native
    # full-history replay, preservation, installation intent and frozen restore.
    # All filesystem/service effects are disposable offline host fixtures.
    f=late_charge_host; original=f['ledger'];review=f['review']
    baseline=f['recovery']['terminal_admissions']
    baseline['preserved_admissions']=[{k:case[k] for k in ('event','receipt','state_after')} |
        {'receipt_origin':'RECORDED_BROKER_REPLY'} for case in f['account']['cases']]
    units={};cases=[]
    for attempt in (1,2):
        event={'turn_id':'9'*64,'attempt':str(attempt),'source':SOURCE,
               'branch':'astra/infrastructure-milestone-record','kind':'astra_turn'}
        raw=original.admit(event);receipt=json.loads(raw['receipt_original'])
        unit=gate.digest(gate.encoded({'event':event,'receipt':receipt}))
        units[unit]={'event':event,'receipt':receipt}
        cases.append({'unit_sha256':unit,'event':event,'receipt':receipt,'state_after':original.head})
    review['terminal_profile']='server-terminal-review/v1'
    review['terminal_session']['manual_units']={};review['terminal_session']['prepaid_units']=units
    f['proposal']['review_profile']='server-terminal-review/v1'
    f['proposal']['recovery_sha256']=gate.digest(gate.encoded(f['recovery']))
    install.validate_recovery(f['recovery'],f['proposal'])
    (f['bundle']/'proposal.json').write_bytes(gate.encoded(f['proposal']))
    account={**f['account'],'schema':'server-terminal-accounting/v1','cases':cases,'ledger_pin':original.head}
    account_raw=encoded(account);(f['bundle']/'terminal-accounting.json').write_bytes(account_raw)
    def read_commit(pin):
        row=ledger._state(original.objects,pin)
        return {'parents':[] if row['parent'] is None else [row['parent']],'state':row['state']}
    def checked(*args):
        return terminal.validate_accounting(account_raw,review,original.status(),original.head,
            original.state,original.policy,{SOURCE},read_commit)
    monkeypatch.setattr(install,'require_terminal_accounting',checked)
    checked_result=checked()
    assert checked_result['late_charge'] is False and set(checked_result['prepaid_units'])==set(units)
    assert 'manual_units' not in checked_result
    before=original.status();receipt=install.apply(SHA,SOURCE)
    assert receipt['research_activated'] is False and original.status()==before
    assert receipt['terminal_admission_transition']['ledger_transition']['server_profile'] is True
    restored=install.restore(SHA,SOURCE)
    assert restored['preserved_state']==receipt['preserved_state'] and original.status()==before
    assert f['scientific'].read_bytes()==b'Preserved scientific evidence, not an accepted result.\n'
