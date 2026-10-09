"""Hash-bound operator steering is delivered without changing scientific findings."""
from pathlib import Path
import pytest
from tools import item4_scientific_revision_component as c

@pytest.mark.parametrize('stage',['run_spec_author','run_spec_review'])
def test_exact_decision_delivered_to_both_roles(stage):
    raw=(Path(c.__file__).resolve().parents[1]/c.STAGING_DOCUMENT).read_bytes()
    assert c.sha(raw)==c.STAGING_SHA
    text=c.guidance(stage,'Original scientific task and findings')
    assert raw.decode() in text and text.endswith('Original scientific task and findings')
    assert 'scientific review before full training' in text


def test_changed_decision_refuses(monkeypatch):
    monkeypatch.setattr(c,'STAGING_SHA','0'*64)
    with pytest.raises(ValueError,match='OPERATOR_STAGING_CHANGED'):c.guidance('run_spec_author','task')
