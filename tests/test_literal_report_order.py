"""Selected literal report presentation must survive independent process replay."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from orchestrator.disposition_context import _response_presentations


def test_literal_reports_have_stable_byte_order_across_processes():
    root = Path(__file__).resolve().parents[1]
    code = """import hashlib,json
from orchestrator.disposition_context import _response_presentations
originals={hashlib.sha256(x.encode()).hexdigest():x for x in ['Unresolved rejection A','Conditional approval B','Current review C']}
print(json.dumps(_response_presentations(originals,literal_text=set(originals)),separators=(',',':')))
"""
    outputs = []
    for seed in ('0', '1', '2', '7'):
        result = subprocess.run([sys.executable, '-B', '-c', code], cwd=root,
            env={**os.environ, 'PYTHONHASHSEED': seed, 'PYTHONPATH': str(root),
                 'PYTHONDONTWRITEBYTECODE': '1'}, capture_output=True, check=True)
        outputs.append(result.stdout)
    assert len(set(outputs)) == 1, 'Process hash seed changed the receipt-bound input bytes'


def test_sorting_preserves_complete_adverse_and_approval_text():
    originals = {hashlib.sha256(x.encode()).hexdigest(): x for x in
                 ['REQUEST_CHANGES: unresolved evidence.', 'APPROVE only for named scope.']}
    view = _response_presentations(originals, literal_text=set(originals))
    assert list(view) == sorted(originals)
    assert set(view) == set(originals)
    for identity, body in originals.items():
        assert view[identity]['text'] == body
        assert view[identity]['original_raw_sha256'] == identity
        assert view[identity]['schema'] == 'literal-original-review-text/v1'
    assert originals == {identity: value['text'] for identity, value in view.items()}
