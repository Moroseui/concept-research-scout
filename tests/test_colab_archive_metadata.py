import contextlib
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from scripts import colab_archive_metadata as m


class MetadataTests(unittest.TestCase):
    def test_metadata_only_search_and_resume(self):
        root = '/content/drive/MyDrive'
        def entry(name, directory=False):
            return SimpleNamespace(name=name, path=root+'/'+name,
                is_symlink=lambda:False, is_dir=lambda **kw:directory,
                is_file=lambda **kw:not directory,
                stat=lambda **kw:SimpleNamespace(st_size=123))
        tree = {root:[entry('train.7z'), entry('private.csv')]}
        with tempfile.TemporaryDirectory() as d:
            state = Path(d)/'state.json'
            with patch.object(m.os.path,'ismount',return_value=True), \
                 patch.object(m.os.path,'isdir',side_effect=lambda p:p==root), \
                 patch.object(m.os,'scandir',side_effect=lambda p:contextlib.nullcontext(iter(tree[p]))):
                first=m.search(state,seconds=0)
                self.assertFalse(first['scan_complete'])
                result=m.search(state)
                self.assertEqual(result,dict(drive_mounted=True,scan_complete=True,
                    archive_candidates=[dict(path=root+'/train.7z',size_bytes=123)]))
                self.assertEqual(state.stat().st_mode & 0o777,0o600)
                self.assertEqual(m.search(state),result)

    def test_no_mount_no_checkpoint(self):
        with tempfile.TemporaryDirectory() as d, patch.object(m.os.path,'ismount',return_value=False):
            state=Path(d)/'state.json'
            self.assertFalse(m.search(state)['drive_mounted'])
            self.assertFalse(state.exists())
