"""The one dependency lock remains subject to all normal content/history checks."""
from pathlib import Path
import pytest
from orchestrator.git_publication import scan

PATH='deploy/research-system/drive-requirements.lock'


def test_actual_pinned_lock_and_unrelated_lock_refusal():
    scan(PATH,Path(PATH).read_bytes())
    with pytest.raises(ValueError,match='TYPE_REJECTED'):
        scan('other.lock',b'example==1.0\n')


@pytest.mark.parametrize('raw',[
    b'example>=1\n', b'-e https://example.org/project\n',b'example @ https://example.org/file\n',
    b'example==1\nExample==2\n',b'example-name==1\nexample_name==2\n',b'age,value\n42,3\n',b'example==1\x00\n',
])
def test_non_lock_payloads_refused(raw):
    with pytest.raises(ValueError):scan(PATH,raw)


def test_case_and_credential_checks_still_apply():
    for raw in [(b'sub-'+b'stroke'+b'0000==1\n'),(b'gh'+b'p_'+b'x'*30+b'==1\n')]:
        with pytest.raises(ValueError):scan(PATH,raw)
