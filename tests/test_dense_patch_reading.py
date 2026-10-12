"""Lossless patch navigation under the unchanged native reader page bound."""
import hashlib
import json

import pytest
from orchestrator import manual_context as mc, context_budget as budget


def read_patch(replacement, **extra):
    original = {"schema": "safe-notebook-patch/v1", "edits": [
        {"unit": "cells/10/source", "start": 0, "end": 3, "before_sha256": "a" * 64,
         "replacement": replacement}], **extra}
    raw = json.dumps(original, ensure_ascii=False).encode()
    descriptor = {"id": "notebook_patch", "path": "unchanged-original.json",
                  "sha256": hashlib.sha256(raw).hexdigest(), "delivery": "Original."}
    copy, pretty = mc._notebook_patch_reading_copy(descriptor, raw)
    value = json.loads(pretty)
    restored = {**value["patch"], "edits": [
        {**edit, "replacement": "".join(edit["replacement"])}
        for edit in value["patch"]["edits"]]}
    assert restored == original
    assert copy["original_sha256"] == hashlib.sha256(raw).hexdigest()
    lines = pretty.splitlines(keepends=True)
    assert max(sum(map(len, lines[i:i + mc.JSON_PAGE_LINES])) for i in range(len(lines))) <= mc.JSON_PAGE_BYTES
    return value, copy


@pytest.mark.parametrize("text", [
    ("x" * 500 + "\n") * 100,
    "x" * 40000,
    ("?????" * 100 + "\r\n") * 100,
])
def test_dense_replacements_use_exact_byte_bounded_chunks(text):
    view, descriptor = read_patch(text)
    assert view["schema"] == "notebook-patch-reading/v2"
    chunks = view["patch"]["edits"][0]["replacement"]
    assert all(len(chunk.encode()) <= 128 for chunk in chunks)
    assert "UTF-8-bounded string chunks" in descriptor["delivery"]


@pytest.mark.parametrize("text", ["", "one\ntwo\n", "one\r\ntwo"])
def test_small_original_line_representation_unchanged(text):
    view, descriptor = read_patch(text)
    assert view["schema"] == "notebook-patch-reading/v1"
    assert view["patch"]["edits"][0]["replacement"] == text.splitlines(keepends=True)


def test_oversized_nonreplacement_value_still_refused():
    with pytest.raises(budget.ContextError, match="MANUAL_JSON_PAGE_TOO_LARGE"):
        read_patch("ok", unrelated="x" * 17000)


def test_generic_json_limit_unchanged():
    with pytest.raises(budget.ContextError, match="MANUAL_JSON_PAGE_TOO_LARGE"):
        mc._pageable_json(json.dumps({"x": "x" * 17000}).encode())


def test_changed_original_binding_refused():
    raw = json.dumps({"schema": "safe-notebook-patch/v1",
                      "edits": [{"replacement": "x" * 30000}]}).encode()
    descriptor = {"id": "patch", "path": "original.json", "sha256": "0" * 64,
                  "delivery": "Original"}
    with pytest.raises(budget.ContextError, match="MANUAL_PATCH_READING_ROUNDTRIP"):
        mc._notebook_patch_reading_copy(descriptor, raw)
