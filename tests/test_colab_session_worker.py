import io
import time
from types import SimpleNamespace
import pytest
from orchestrator.colab_session_worker import Session


def test_pending_duplicate_and_submission_cap_preserve_intent(tmp_path):
    s=Session.__new__(Session)
    s.destination=tmp_path;s.closed=False;s.pending=False;s.submissions=0;s.deadline=time.monotonic()+60
    s.process=SimpleNamespace(poll=lambda:None,stdin=io.StringIO())
    s.submit('bounded-request','Synthetic only')
    evidence=(tmp_path/'bounded-request.request.json').read_bytes()
    with pytest.raises(ValueError,match='STILL_PENDING'):s.submit('another','Do not execute')
    s.pending=False
    with pytest.raises(FileExistsError):s.submit('bounded-request','Do not repeat')
    assert s.submissions==1
    assert (tmp_path/'bounded-request.request.json').read_bytes()==evidence
    s.submissions=3
    with pytest.raises(ValueError,match='BOUND_EXHAUSTED'):s.submit('last','Do not execute')
