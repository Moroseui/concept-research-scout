import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts import colab_archive_acquire as a
from orchestrator import colab_acquire as adapter


class AcquisitionTests(unittest.TestCase):
    def test_review_required(self):
        with tempfile.TemporaryDirectory() as d, patch.object(adapter,'PREFIX',Path(d)/'missing'):
            with self.assertRaises(FileNotFoundError):adapter.reviewed()

    def test_unmounted_refuses_before_writes(self):
        with patch.dict(a.os.environ,{'COLAB_RELEASE_TAG':'synthetic'}), \
             patch.object(a.shutil,'which',return_value=None), \
             patch.object(a.os.path,'ismount',return_value=False), \
             patch.object(a.Path,'mkdir',side_effect=AssertionError('write')):
            with self.assertRaises(RuntimeError):a.start()

    def test_download_checks_identity_preserves_failed_partial(self):
        for payload,expected in [(b'synthetic',b'synthetic'),(b'bad',b'synthetic')]:
            with tempfile.TemporaryDirectory() as d:
                root=Path(d)/'input';audit=Path(d)/'audit';root.mkdir();audit.mkdir()
                ns=dict(INPUT=str(root),AUDIT=str(audit),URL='https://example.invalid/fixture',
                    SIZE=len(expected),MD5=hashlib.md5(expected).hexdigest())
                with patch('urllib.request.urlopen',return_value=contextlib.closing(io.BytesIO(payload))), \
                     contextlib.redirect_stderr(io.StringIO()):
                    if payload==expected:
                        exec(a.DOWNLOAD_CODE,ns)
                        self.assertEqual((root/'train.7z').read_bytes(),expected)
                        self.assertEqual(json.loads((audit/'status.json').read_text())['status'],'VALIDATED')
                    else:
                        with self.assertRaises(ValueError):exec(a.DOWNLOAD_CODE,ns)
                        self.assertFalse((root/'train.7z').exists())
                        self.assertEqual((root/'train.7z.part').read_bytes(),payload)
                        self.assertEqual(json.loads((audit/'status.json').read_text())['status'],'FAILED')

    def test_rerun_refuses_existing_destination(self):
        with tempfile.TemporaryDirectory() as d, patch.object(a,'INPUT',Path(d)), \
             patch.dict(a.os.environ,{'COLAB_RELEASE_TAG':'synthetic'}), \
             patch.object(a.shutil,'which',return_value=None), \
             patch.object(a.os.path,'ismount',return_value=True), \
             patch.object(a.shutil,'disk_usage',return_value=type('Usage',(),{'free':a.SIZE+(20<<30)})()):
            with self.assertRaisesRegex(RuntimeError,'destination exists'):a.start()
