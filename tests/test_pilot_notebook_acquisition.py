import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from scripts import package_pilot as p

class AcquisitionTests(unittest.TestCase):
    def test_exact_pin_fetch_does_not_acquire_other_branch_and_rejects_dirty_rerun(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); source=root/'remote'; source.mkdir()
            def git(*args): return subprocess.check_output(['git',*args],cwd=source,stderr=subprocess.PIPE).decode().strip()
            git('init','-q'); git('config','user.name','Synthetic'); git('config','user.email','synthetic@example.invalid')
            base=source/'campaigns/isles24-pilot'; (base/'colab').mkdir(parents=True); (base/'experiments/P001').mkdir(parents=True)
            (source/'safe.txt').write_text('safe fixture'); git('add','.'); git('commit','-qm','safe')
            pin=git('rev-parse','HEAD'); git('branch','astra/autonomous-isles-pilot')
            git('checkout','-qb','results/contaminated-synthetic'); (source/'patient-private-fixture').write_text('synthetic only'); git('add','.'); git('commit','-qm','unwanted branch')
            unwanted=git('rev-parse','HEAD')
            with patch.object(p,'ROOT',source): p.main(pin)
            nb=json.loads((base/'experiments/P001/colab_P001.ipynb').read_text())
            setup=''.join(nb['cells'][1]['source']).replace("'/content/scout-pilot-'",repr(str(root/'acquired-'))).replace('https://github.com/Moroseui/concept-research-scout.git',source.as_uri())
            namespace={}; exec(setup,namespace)
            acquired=namespace['REPO']
            self.assertFalse((acquired/'patient-private-fixture').exists())
            result=subprocess.run(['git','cat-file','-e',unwanted],cwd=acquired,capture_output=True)
            self.assertNotEqual(result.returncode,0)
            exec(setup,{})  # harmless repeat
            (acquired/'review.json').write_text('untracked fake approval')
            with self.assertRaisesRegex((AssertionError,RuntimeError),'untracked'): exec(setup,{})
