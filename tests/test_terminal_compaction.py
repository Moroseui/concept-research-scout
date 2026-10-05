"""Synthetic compaction originals; no genuine review is qualified or charged."""
from copy import deepcopy
import json
import pytest
from orchestrator import terminal_review as tr
from test_terminal_review import SESSION, session_events, journal

REPORT = b"Synthetic report original"
PATH = "/synthetic/review.md"


def fixture():
    events = session_events(REPORT, PATH)
    for n, event in enumerate(events):
        event.update(uuid=f"original-{n}", timestamp=f"2026-01-01T00:00:0{n}Z",
                     isSidechain=False)
    events[2]["sourceToolAssistantUUID"] = "original-1"
    replay = deepcopy(events[1:3])
    replay[0]["slug"] = "new-title"
    replay[1]["toolUseResult"] = {"displayOnly": True}
    boundary = {"type": "system", "subtype": "compact_boundary", "uuid": "boundary",
                "sessionId": SESSION, "isSidechain": False, "logicalParentUuid": "original-4",
                "compactMetadata": {"trigger": "auto", "preservedSegment": {
                    "headUuid": "original-0", "tailUuid": "original-4", "anchorUuid": "summary"},
                    "preservedMessages": {"anchorUuid": "summary", "uuids": ["original-0"]}}}
    summary = {"type": "user", "uuid": "summary", "parentUuid": "boundary",
               "sessionId": SESSION, "isSidechain": False, "isCompactSummary": True,
               "isVisibleInTranscriptOnly": True, "message": {"content": "Synthetic summary."}}
    return events + replay + [boundary, summary]


def check(events):
    return tr._session(journal(events), REPORT, {"session_id": SESSION}, PATH)


def test_compaction_preserves_human_unit_write_model_and_usage():
    events = fixture()
    before = deepcopy(events)
    original = check(events[:5])
    actual = check(events)
    assert events == before
    for key in ["manual_units", "usage_fragments_by_message", "provider_model",
                "report_write_tool_use_id", "observed_models"]:
        assert actual[key] == original[key]
    assert actual["compactions"][0]["replayed_read_uuids"] == ["original-1", "original-2"]
    assert len(actual["compactions"][0]["summary_sha256"]) == 64


@pytest.mark.parametrize("mutation", [
    "changed-result", "changed-error", "changed-usage", "changed-timestamp", "changed-session",
    "new-uuid-result", "write-replay", "human-replay", "no-boundary", "wrong-caller",
    "wrong-anchor", "wrong-parent", "typed-summary", "human-summary", "unbound-summary",
    "boundary-wrong-session", "unknown-compaction-trigger", "changed-summary-model-role",
])
def test_unknown_or_changed_compaction_evidence_fails(mutation):
    e = fixture()
    if mutation == "changed-result": e[6]["message"]["content"][0]["content"] = "Changed"
    elif mutation == "changed-error": e[6]["message"]["content"][0]["is_error"] = True
    elif mutation == "changed-usage": e[5]["message"]["usage"]["input_tokens"] += 1
    elif mutation == "changed-timestamp": e[6]["timestamp"] = "changed"
    elif mutation == "changed-session": e[6]["sessionId"] = "other"
    elif mutation == "new-uuid-result": e[6]["uuid"] = "new-result"
    elif mutation == "write-replay": e[5:7] = deepcopy(e[3:5])
    elif mutation == "human-replay": e[5:7] = [deepcopy(e[0])]
    elif mutation == "no-boundary": e.pop(7)
    elif mutation == "wrong-caller": e[6]["sourceToolAssistantUUID"] = "original-3"
    elif mutation == "wrong-anchor": e[7]["compactMetadata"]["preservedSegment"]["anchorUuid"] = "other"
    elif mutation == "wrong-parent": e[8]["parentUuid"] = "other"
    elif mutation == "typed-summary": e[8]["promptSource"] = "typed"
    elif mutation == "human-summary": e[8]["origin"] = {"kind": "human"}
    elif mutation == "unbound-summary": e = e[:5] + [e[8]]
    elif mutation == "boundary-wrong-session": e[7]["sessionId"] = "other"
    elif mutation == "unknown-compaction-trigger": e[7]["compactMetadata"]["trigger"] = "unknown"
    elif mutation == "changed-summary-model-role": e[8]["type"] = "assistant"
    with pytest.raises(ValueError): check(e)


def test_human_request_after_compaction_is_still_accounted():
    e = fixture()
    next_human = deepcopy(e[0]); next_human["uuid"] = "next-human"
    next_human["message"]["content"] = "Another genuine synthetic request"
    e.append(next_human)
    assert len(check(e)["manual_units"]) == 2


def test_missing_report_original_still_fails_after_compaction():
    with pytest.raises(ValueError, match="ORIGINAL_SUCCESSFUL_CLAUDE_WRITE_REQUIRED"):
        tr._session(journal(fixture()), b"Changed report", {"session_id": SESSION}, PATH)
