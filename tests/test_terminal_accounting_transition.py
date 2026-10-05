"""Offline terminal-charge suffix tests; no real ledger or model invocation.

The caller separately binds these admissions to validated terminal manual units.
Here the real replay and repository checks must preserve the already-reviewed
baseline; the imported fixture writes synthetic loose objects and Git only reads.
"""
from copy import deepcopy
import json

import pytest

from orchestrator import inspection_admission_recovery as recovery
from orchestrator import terminal_review as terminal
from test_inspection_admission_recovery import Fixture, SOURCE, event, write


def manual_event(number, source=SOURCE):
    unit = recovery.digest(("synthetic-manual-unit-" + str(number)).encode())
    return terminal.accounting_event(unit, source)


def verify(f, admissions):
    return recovery.verify_terminal_transition(
        f.repo, f.baseline, f.policy, admissions, f.status())


@pytest.mark.parametrize("count", [1, 3, 17])
def test_exact_manual_charges_use_unchanged_reviewed_baseline(tmp_path, count):
    f = Fixture(tmp_path, n=48)
    baseline_raw = recovery.encoded(f.baseline)
    # Current manual request source can differ from the historical canary source.
    admissions = [f.admit(manual_event(i, "b" * 40)) for i in range(count)]
    result = verify(f, admissions)
    assert result["schema"] == "terminal-accounting-ledger-transition/v1"
    assert result["status"] == "VERIFIED_ONLY_TERMINAL_ACCOUNTING_ADMISSIONS"
    assert result["original_head"] == json.loads(baseline_raw)["original_head"]
    assert result["current_head"] == f.head and len(result["suffix"]) == count
    assert result["baseline_sha256"] == recovery.digest(baseline_raw)
    assert result["admissions_sha256"] == recovery.digest(recovery.encoded(admissions))
    assert recovery.encoded(f.baseline) == baseline_raw
    assert result["git_mutations"] == result["remote_calls"] == 0
    assert result["caller_must_capture_full_state_after_return"] is True


@pytest.mark.parametrize("mutation", [
    "missing", "extra-unlisted", "reordered", "duplicate",
    "changed-event", "changed-receipt", "changed-parent",
    "failed", "duplicate-receipt", "nightly-kind", "attempt-two",
])
def test_only_the_complete_exact_manual_suffix_is_replayed(tmp_path, mutation):
    f = Fixture(tmp_path, n=48)
    admissions = [f.admit(manual_event(1)), f.admit(manual_event(2))]
    if mutation == "missing":
        admissions.pop(0)
    elif mutation == "extra-unlisted":
        f.admit(manual_event(3))
    elif mutation == "reordered":
        admissions.reverse()
    elif mutation == "duplicate":
        admissions.append(deepcopy(admissions[-1]))
    else:
        field = "event_original" if mutation in {
            "changed-event", "nightly-kind", "attempt-two"} else "receipt_original"
        value = json.loads(admissions[0][field])
        if mutation == "changed-event":
            value["turn_id"] = "f" * 64
        elif mutation == "changed-receipt":
            value["count"] += 1
        elif mutation == "changed-parent":
            value["state_before"] = "f" * 40
        elif mutation == "failed":
            value["status"] = "HALTED_OPERATOR_RESET_REQUIRED"
        elif mutation == "duplicate-receipt":
            value["duplicate_admission"] = True
        elif mutation == "nightly-kind":
            value["kind"] = "nightly_review"
        elif mutation == "attempt-two":
            value["attempt"] = "2"
        admissions[0][field] = recovery.encoded(value).decode()
    with pytest.raises(ValueError):
        verify(f, admissions)


def test_reset_commit_is_not_an_accounting_suffix(tmp_path):
    f = Fixture(tmp_path, n=48)
    admission = f.admit(manual_event(1))
    state = deepcopy(f.state)
    state["resets"].append({
        "approval_sha256": "d" * 64, "expected_sequence": state["sequence"],
        "at": "2026-09-12T00:00:00Z"})
    state.update(sequence=state["sequence"] + 1, count=0, halted=False)
    f.commit(state)
    with pytest.raises(ValueError, match="SUFFIX"):
        verify(f, [admission])


@pytest.mark.parametrize("mutation", [
    "config-content", "config-mode", "directory-mode", "unknown-file",
    "unrelated-object", "object-content", "object-removed",
    "fetch", "shallow", "reflog",
])
def test_valid_manual_charges_do_not_waive_filesystem_preservation(tmp_path, mutation):
    f = Fixture(tmp_path, n=48)
    admission = f.admit(manual_event(1))
    if mutation == "config-content":
        path = f.git / "config"
        write(path, path.read_bytes() + b"\n[include]\npath = /outside\n")
    elif mutation == "config-mode":
        (f.git / "config").chmod(0o640)
    elif mutation == "directory-mode":
        (f.git / "objects").chmod(0o750)
    elif mutation == "unknown-file":
        write(f.git / "unrelated", b"Not an accounting object.\n")
    elif mutation == "unrelated-object":
        f.obj("blob", b"Unrelated synthetic blob.\n")
    elif mutation in {"object-content", "object-removed"}:
        oid = next(iter(f.baseline["snapshot"]["objects"]))
        path = f.git / "objects" / oid[:2] / oid[2:]
        if mutation == "object-content":
            path.chmod(0o600)
            write(path, b"corrupted", 0o400)
        else:
            path.unlink()
    elif mutation == "fetch":
        write(f.git / "FETCH_HEAD", b"unrelated\n")
    elif mutation == "shallow":
        write(f.git / "shallow", (f.head + "\n").encode())
    elif mutation == "reflog":
        path = f.repo / recovery.REFLOG
        write(path, path.read_bytes().replace(b"update by push", b"changed reason", 1))
    with pytest.raises(ValueError):
        verify(f, [admission])


@pytest.mark.parametrize("mutation", [
    "missing-canary", "changed-canary-receipt", "missing-object",
    "changed-control-original", "changed-baseline-status", "changed-policy",
])
def test_historical_baseline_originals_are_still_required(tmp_path, mutation):
    f = Fixture(tmp_path, n=48)
    admission = f.admit(manual_event(1))
    if mutation == "missing-canary":
        f.baseline["canary_admissions"].pop()
    elif mutation == "changed-canary-receipt":
        row = f.baseline["canary_admissions"][0]
        receipt = json.loads(row["receipt_original"])
        receipt["count"] += 1
        row["receipt_original"] = recovery.encoded(receipt).decode()
    elif mutation == "missing-object":
        oid = f.baseline["canary_commits"][0]["pin"]
        del f.baseline["snapshot"]["objects"][oid]
    elif mutation == "changed-control-original":
        f.baseline["snapshot"]["control_originals"][".git/config"] += " "
    elif mutation == "changed-baseline-status":
        f.baseline["authenticated_status"]["count"] += 1
    elif mutation == "changed-policy":
        f.policy["n"] = 49
    with pytest.raises(ValueError):
        verify(f, [admission])


def test_authenticated_endpoint_must_match_current_repository(tmp_path):
    f = Fixture(tmp_path, n=48)
    admission = f.admit(manual_event(1))
    status = f.status()
    status["pin"] = f.baseline["original_head"]
    with pytest.raises(ValueError):
        recovery.verify_terminal_transition(
            f.repo, f.baseline, f.policy, [admission], status)


def test_native_entry_point_still_refuses_manual_admissions(tmp_path):
    f = Fixture(tmp_path, n=48)
    admission = f.admit(manual_event(1))
    with pytest.raises(ValueError, match="ONLY_SUCCESSFUL_REVIEW_ADMISSION"):
        recovery.verify_transition(f.repo, f.baseline, f.policy, [admission], f.status())


def test_native_entry_point_still_accepts_one_sequential_review_session(tmp_path):
    f = Fixture(tmp_path, n=48)
    admissions = [f.admit(event(3, 1)), f.admit(event(3, 2))]
    result = recovery.verify_transition(
        f.repo, f.baseline, f.policy, admissions, f.status())
    assert result["status"] == "VERIFIED_ONLY_APPROVED_SESSION_ADMISSIONS"
    assert len(result["suffix"]) == 2


@pytest.mark.parametrize('attempt',[2,16,17])
def test_server_profile_replays_bounded_prepaid_continuation_without_relaxing_manual(tmp_path,attempt):
    f=Fixture(tmp_path,n=48)
    e={**event(90,attempt),'kind':'astra_turn'}
    admissions=[f.admit(e)]
    with pytest.raises(ValueError,match='ONLY_ORIGINAL_TERMINAL_ACCOUNTING_UNITS'):
        verify(f,admissions)
    if attempt>16:
        with pytest.raises(ValueError):
            recovery.verify_terminal_transition(f.repo,f.baseline,f.policy,admissions,f.status(),server_profile=True)
    else:
        result=recovery.verify_terminal_transition(f.repo,f.baseline,f.policy,admissions,f.status(),server_profile=True)
        assert result['server_profile'] is True and len(result['suffix'])==1
        assert result['git_mutations']==0
