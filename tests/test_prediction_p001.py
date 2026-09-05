import importlib.util
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/'campaigns/isles24-pilot/experiments/P001/run.py'
spec=importlib.util.spec_from_file_location('p001',PATH); p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)

@unittest.skipUnless(importlib.util.find_spec('numpy'),'prediction numpy optional')
class PredictionTests(unittest.TestCase):
    def test_no_label_needed_to_predict_and_exact_patient_dice(self):
        import numpy as np
        x=np.array([0,6,6.1,10,0,0,0,0]).reshape(2,2,2)
        pred=p.predict(x); label=np.zeros_like(pred); label[0,1,0]=1
        self.assertEqual(p.metrics(pred,label,1)['dice'],2/3)
        self.assertEqual(p.metrics(pred,label,1)['absolute_volume_error_ml'],1)
        self.assertEqual(p.metrics(np.zeros_like(pred),np.zeros_like(pred),1)['dice'],1)
        with self.assertRaises(ValueError): p.predict(np.full((2,2,2),np.nan))
        with self.assertRaises(ValueError): p.metrics(pred,np.full((2,2,2),2),1)

    def test_bootstrap_patient_weight_and_repeatability(self):
        rows=[{'dice':0.,'absolute_volume_error_ml':9.,'signed_volume_error_ml':-9.},
              {'dice':1.,'absolute_volume_error_ml':1.,'signed_volume_error_ml':1.}]
        result=p.summarize(rows)
        self.assertEqual(result['mean_dice'],.5)
        self.assertEqual(result['mean_signed_volume_error_ml'],-4)
        self.assertEqual(result,p.summarize(rows))

    def test_frozen_selection_opens_no_payload_and_has_exact_cohort(self):
        selected=p.selection()
        self.assertEqual(len(selected),99)
        self.assertEqual(sum(len(x) for x in selected.values()),198)
        self.assertTrue(all('/ses-01/' in x['tmax']['path'] and '/ses-02/' in x['label']['path'] for x in selected.values()))

    @unittest.skipUnless(importlib.util.find_spec('nibabel'),'prediction nibabel optional')
    def test_synthetic_full_run_resume_and_checkpoint_tamper(self):
        import argparse, hashlib, json, tempfile, zlib
        from unittest.mock import patch
        import numpy as np
        import nibabel as nib
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); here=root/'campaign/experiments/P001'; here.mkdir(parents=True)
            campaign=here.parents[1]/'CAMPAIGN.md'; campaign.write_text('synthetic campaign')
            (here/'SPEC.md').write_text('synthetic spec'); (here/'run.py').write_text('synthetic code fixture')
            sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
            d={'authority':'campaign_delegated_investigator','actor_type':'agent','family':'codex','model':'synthetic fixture','experiment':'P001','rationale':'test only','campaign_sha256':sha(campaign),'spec_sha256':sha(here/'SPEC.md')}
            (here/'investigator_decision.json').write_text(json.dumps(d))
            (here/'review.json').write_text(json.dumps({'actor_type':'agent','family':'claude','verdict':'APPROVE','spec_sha256':sha(here/'SPEC.md'),'code_sha256':sha(here/'run.py')}))
            data=root/'data'; data.mkdir(); selected={}
            for kind,arr in [('tmax',np.full((2,2,2),7,dtype=np.float32)),('label',np.ones((2,2,2),dtype=np.uint8))]:
                f=data/(kind+'.nii.gz'); nib.save(nib.Nifti1Image(arr,np.eye(4)),f)
            for i in range(99):
                selected[f'synthetic-{i:03d}']={}
                for kind in ('tmax','label'):
                    f=data/(kind+'.nii.gz'); b=f.read_bytes()
                    selected[f'synthetic-{i:03d}'][kind]={'path':f.name,'size':len(b),'crc':f'{zlib.crc32(b)&0xffffffff:08x}'}
            args=argparse.Namespace(preflight=False,archive=None,data_root=data,output_dir=root/'out')
            with patch.object(p,'HERE',here),patch.object(p,'selection',return_value=selected),patch('orchestrator.campaign_review.verify_receipt'):
                p.run(args)
                result=json.loads((root/'out/summary.json').read_text())
                self.assertEqual(result['mean_dice'],1)
                self.assertEqual(result['n'],99)
                # Actual return validator on generated synthetic volumes/checkpoints.
                vs=importlib.util.spec_from_file_location('p001_return',PATH.with_name('validate_return.py'))
                validator=importlib.util.module_from_spec(vs); vs.loader.exec_module(validator)
                (here/'publication.json').write_text(PATH.with_name('publication.json').read_text())
                console=root/'out.console.log'; console.write_text('original synthetic execution console')
                with patch.object(validator,'HERE',here),patch.object(validator,'p',p):
                    validator.verify(root/'out',root/'out.private',console)
                    f=root/'out/summary.json'; original=f.read_text()
                    f.write_text(original[:-2]+',"unapproved_extra":"synthetic"}')
                    with self.assertRaisesRegex(ValueError,'unexpected aggregate'):
                        validator.verify(root/'out',root/'out.private',console)
                    f.write_text(original)
                # Crash between index and checkpoint installation remains resumable.
                (root/'out.private/checkpoints/synthetic-000.json').unlink()
                p.run(args)
                self.assertEqual(json.loads((root/'out/execution_receipt.json').read_text())['resumed_cases'],98)

                with patch.object(nib,'load',side_effect=AssertionError('checkpoint rerun must not reload images')):
                    p.run(args)
                self.assertEqual(json.loads((root/'out/execution_receipt.json').read_text())['resumed_cases'],99)
                f=root/'out.private/checkpoints/synthetic-000.json'
                f.write_text(f.read_text().replace('"dice": 1.0','"dice": 0.0'))
                with self.assertRaisesRegex(ValueError,'checkpoint metric bytes'): p.run(args)
